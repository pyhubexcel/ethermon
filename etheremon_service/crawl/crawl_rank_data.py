import os
import sys
import time

curr_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curr_dir)
sys.path.append(os.path.join(curr_dir, '../../'))

from common import context
from django.core.wsgi import get_wsgi_application

context.init_django('../', 'settings')
application = get_wsgi_application()

from common.logger import log
from etheremon_lib.config import *
from etheremon_lib.infura_client import InfuraClient
from etheremon_lib.ladder_manager import *
from etheremon_lib.utils import get_level

INFURA_API_URL = INFURA_API_URLS["general"]

def crawl_rank_data():
	start_time = time.time()

	infura_client = InfuraClient(INFURA_API_URL)
	rank_data_contract = infura_client.getRankDataContract()
	rank_reward_contract = infura_client.getRankRewardContract()
	ladder_contract = infura_client.getLadderContract()

	current_block = infura_client.getCurrentBlock()
	total_player = rank_data_contract.call().totalPlayer()

	log.data("start_crawl_rank_data|total=%s,block_number=%s", total_player, current_block)

	for index in range(total_player):
		player_id = index + 1
		player_contract_data = rank_data_contract.call().getPlayerData(player_id)
		if not player_contract_data[4]:
			log.warn("invalid_contract_data|player_contract_data=%s", player_contract_data)
			continue

		player_record = get_rank_data(player_id)
		if not player_record:
			player_record = EtheremonDB.UserLadderTab(player_id=player_id)
		trainer_address = player_contract_data[0]
		trainer_address = trainer_address.lower()
		player_record.trainer = trainer_address
		player_record.point = player_contract_data[3]
		player_record.total_win = player_contract_data[1]
		player_record.total_lose = player_contract_data[2]
		player_record.a0 = player_contract_data[4]
		player_record.a1 = player_contract_data[5]
		player_record.a2 = player_contract_data[6]
		player_record.s0 = player_contract_data[7] if player_contract_data[7] else 0
		player_record.s1 = player_contract_data[8] if player_contract_data[8] else 0
		player_record.s2 = player_contract_data[9] if player_contract_data[9] else 0

		# total claim match
		total_win_claim = rank_reward_contract.call().getWinClaim(player_id)
		player_record.total_match = player_record.total_win + player_record.total_lose + total_win_claim

		# calculate avg bp
		total_bp = ladder_contract.call().getMonsterCP(player_record.a0)
		total_bp += ladder_contract.call().getMonsterCP(player_record.a1)
		total_bp += ladder_contract.call().getMonsterCP(player_record.a2)

		# calculate avg level
		total_level = 0
		level_info = ladder_contract.call().getMonsterLevel(player_record.a0)
		total_level += level_info[1]
		level_info = ladder_contract.call().getMonsterLevel(player_record.a1)
		total_level += level_info[1]
		level_info = ladder_contract.call().getMonsterLevel(player_record.a2)
		total_level += level_info[1]

		player_record.avg_bp = total_bp / 3
		player_record.avg_level = total_level / 3

		player_record.energy = player_contract_data[10]
		player_record.last_claim = player_contract_data[11]
		player_record.update_time = get_timestamp()
		player_record.save()

	elapsed = time.time() - start_time
	log.data("end_crawl_rank_data|elapsed=%s,total_player=%s,start_block=%s", elapsed, total_player, current_block)

def clone_player_data():
	user_ladder = EtheremonDB.UserLadderTab.objects.all()
	current_ts = get_timestamp()
	for user in user_ladder:
		ema_player_record = EtheremonDB.EmaPlayerRankData.objects.filter(player_id=user.player_id).first()
		if not ema_player_record:
			ema_player_record = EtheremonDB.EmaPlayerRankData(
				player_id=user.player_id
			)
		ema_player_record.trainer = user.trainer.lower()
		ema_player_record.point = user.point
		ema_player_record.total_win = user.total_match - user.total_lose
		ema_player_record.total_lose = user.total_lose
		ema_player_record.total_claimed = ema_player_record.total_win - user.total_win
		ema_player_record.a0 = user.a0
		ema_player_record.a1 = user.a1
		ema_player_record.a2 = user.a2
		ema_player_record.s0 = user.s0
		ema_player_record.s1 = user.s1
		ema_player_record.s2 = user.s2

		a0_record = EtheremonDB.EmaMonsterDataTab.objects.get(monster_id=ema_player_record.a0)
		a1_record = EtheremonDB.EmaMonsterDataTab.objects.get(monster_id=ema_player_record.a1)
		a2_record = EtheremonDB.EmaMonsterDataTab.objects.get(monster_id=ema_player_record.a2)

		avg_bp = (a0_record.bp + a1_record.bp + a2_record.bp) / 3
		avg_level = (get_level(a0_record.exp) + get_level(a1_record.exp) + get_level(a2_record.exp)) / 3

		ema_player_record.avg_bp = avg_bp
		ema_player_record.avg_level = avg_level
		ema_player_record.update_time = current_ts
		ema_player_record.save()

		# update energy
		player_energy_record = EtheremonDB.EmaPlayerEnergyTab.objects.filter(trainer=ema_player_record.trainer).first()
		if not player_energy_record:
			EtheremonDB.EmaPlayerEnergyTab.objects.create(
				trainer=ema_player_record.trainer,
				init_amount=user.energy,
				free_amount=0,
				paid_amount=0,
				consumed_amount=0,
				last_claim_time=0,
				create_time=current_ts,
				update_time=current_ts
			)
		else:
			ladder_amount = user.energy
			if player_energy_record.init_amount < ladder_amount:
				player_energy_record.init_amount = ladder_amount
				player_energy_record.save()

def re_craw_energy():
	user_ladder = EtheremonDB.UserLadderTab.objects.all()
	for user in user_ladder:
		EtheremonDB.EmaPlayerEnergyTab.objects.filter(trainer=user.trainer).update(init_amount=user.energy)

if __name__ == "__main__":
	crawl_rank_data()
	re_craw_energy()
	clone_player_data()
