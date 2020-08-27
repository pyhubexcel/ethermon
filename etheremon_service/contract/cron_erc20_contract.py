import os
import sys
import time

curr_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curr_dir)
sys.path.append(os.path.join(curr_dir, '../../'))

from common import context
from django.core.wsgi import get_wsgi_application
from web3 import Web3, HTTPProvider

context.init_django('../', 'settings')
application = get_wsgi_application()

from common.logger import log
from common.utils import get_timestamp
from etheremon_lib.config import *
from etheremon_lib import ema_settings_manager
from etheremon_lib.etherscan_client import get_txn_list
from etheremon_lib.infura_client import InfuraClient
from etheremon_lib.constants import PayServiceType
from etheremon_lib.models import EtheremonDB
from helper import _sync_player_dex

SMART_CONTRACT_METHOD_ID_LENGTH = 10
SMART_CONTRACT_BLOCK_STEP = 100000

EXPLORE_MIN_BLOCK_GAP = 240

INFURA_API_URL = INFURA_API_URLS["cron_task"]
ETHERSCAN_API_KEY = ETHERSCAN_API_KEYS["cron_1"]

PAY_SERVICE_METHOD = "0xf8788382"

def update_erc20_contract():
	infura_client = InfuraClient(INFURA_API_URL)
	current_block = infura_client.getCurrentBlock() - 2

	start_block = ema_settings_manager.get_setting_value(EmaSetting.SETTING_CONTRACT_ERC20_BLOCK)
	end_block = start_block + SMART_CONTRACT_BLOCK_STEP

	start_time = time.time()
	transaction_list = get_txn_list(EtheremonEMONTContract.ADDRESS, start_block, end_block, ETHERSCAN_API_KEY)
	if transaction_list is None:
		return

	log.data("start_update_erc20_contract|current_block=%s,start_block=%s,end_block=%s,len_txn=%s", current_block, start_block, end_block, len(transaction_list))

	latest_load_block = start_block
	egg_sender_set = set()
	energy_sender_set = set()
	adventure_explore_contract = infura_client.getAdventureExploreContract()
	adventure_data_contract = infura_client.getAdventureDataContract()
	site_id_set = set()
	current_ts = get_timestamp()
	deck_sender_set = set()
	for transaction in transaction_list:
		if len(transaction["input"]) < SMART_CONTRACT_METHOD_ID_LENGTH:
			log.warn("invalid_smart_contract_txn|transaction=%s", transaction)
			continue
		if int(transaction.get("isError", 1)) != 0:
			continue
		if int(transaction.get("txreceipt_status")) != 1:
			continue
		latest_load_block = max(latest_load_block, int(transaction["blockNumber"]))
		if latest_load_block > current_block:
			return
		method_id = transaction["input"][0:SMART_CONTRACT_METHOD_ID_LENGTH]
		sender = str(transaction["from"]).lower()

		if method_id == PAY_SERVICE_METHOD:
			type_id_hash = "0x" + transaction["input"][SMART_CONTRACT_METHOD_ID_LENGTH + 64:SMART_CONTRACT_METHOD_ID_LENGTH + 128]
			type_id = Web3.toInt(hexstr=type_id_hash)

			if type_id == PayServiceType.FAST_HATCHING or type_id == PayServiceType.RANDOM_EGG:
				egg_sender_set.add(sender)
			elif type_id == PayServiceType.ENERGY_TOPUP:
				energy_sender_set.add(sender)
			elif type_id == PayServiceType.ADVENTURE:
				adventure_sub_id_hash = "0x" + transaction["input"][SMART_CONTRACT_METHOD_ID_LENGTH + 192:SMART_CONTRACT_METHOD_ID_LENGTH + 256]
				adventure_sub_id = Web3.toInt(hexstr=adventure_sub_id_hash)

				if adventure_sub_id == 1:
					# explore using emont
					pending_explore_data = adventure_explore_contract.call().getPendingExploreItem(sender)
					explore_id = pending_explore_data[0]
					if explore_id == 0:
						log.info("no_pending_txn|sender=%s", sender)
						continue
					current_record = EtheremonDB.EmaAdventureExploreTab.objects.filter(explore_id=explore_id).first()
					if not current_record:
						'''
						EtheremonDB.EmaAdventureExploreTab.objects.create(
							explore_id=explore_id,
							fee_type=EmaAdventureExploreFee.EMONT,
							sender=sender,
							monster_type=pending_explore_data[1],
							monster_id=pending_explore_data[2],
							site_id=pending_explore_data[3],
							reward_monster_class=0,
							reward_item_class=0,
							reward_item_value='0',
							start_block=pending_explore_data[4],
							end_block=pending_explore_data[5],
							claim_txn_hash='',
							create_time=current_ts
						)
						log.info("adding_new_explore|explore_id=%s,sender=%s,txn_hash=%s", explore_id, sender, transaction["hash"])
						'''
						return
					else:
						if current_record.fee_type == 0:
							current_record.fee_type = EmaAdventureExploreFee.EMONT
							current_record.save()
					site_id_set.add(pending_explore_data[3])
				else:
					# claim explore
					explore_id_hash = "0x" + transaction["input"][SMART_CONTRACT_METHOD_ID_LENGTH + 256:SMART_CONTRACT_METHOD_ID_LENGTH + 320]
					explore_id = Web3.toInt(hexstr=explore_id_hash)
					current_record = EtheremonDB.EmaAdventureExploreTab.objects.filter(explore_id=explore_id).first()
					explore_data = adventure_explore_contract.call().getExploreItem(explore_id)
					if explore_data[5] == 0 and explore_data[6] == 0 and explore_data[7] == 0:
						log.warn("invalid_explore_data_claim|explore_id=%s,explore_data=%s,txn_hash=%s", explore_id, explore_data, transaction["hash"])
						return
					if not current_record:
						log.warn("unable_to_find_explore|explore_id=%s,txn_hash=%s,adventure_sub_id=%s", explore_id, transaction["hash"], adventure_sub_id)
						'''
						explore_ending_block = explore_data[4] + EXPLORE_MIN_BLOCK_GAP + explore_data[4] % EXPLORE_MIN_BLOCK_GAP
						EtheremonDB.EmaAdventureExploreTab.objects.create(
							explore_id=explore_id,
							fee_type=EmaAdventureExploreFee.ETH,
							sender=explore_data[0].lower(),
							monster_type=explore_data[1],
							monster_id=explore_data[2],
							site_id=explore_data[3],
							reward_monster_class=explore_data[5],
							reward_item_class=explore_data[6],
							reward_item_value=str(explore_data[7]),
							start_block=explore_data[4],
							end_block=explore_ending_block,
							claim_txn_hash=transaction["hash"].lower(),
							create_time=current_ts
						)
						site_id_set.add(explore_data[3])
						'''
						return
					else:
						current_record.claim_txn_hash = transaction["hash"].lower()
						current_record.reward_monster_class = explore_data[5]
						current_record.reward_item_class = explore_data[6]
						current_record.reward_item_value = str(explore_data[7])
						current_record.save()

					site_id_set.add(current_record.site_id)

					if explore_data[5] > 0:
						deck_sender_set.add(current_record.sender)


	if egg_sender_set:
		log.info("update_erc20_egg_info|len_sender=%s,latest_load_block=%s", len(egg_sender_set), latest_load_block)
		transform_data_contract = infura_client.getTransformDataContract()
		for sender in egg_sender_set:
			egg_records = EtheremonDB.EmaEggDataTab.objects.filter(trainer=sender).filter(new_obj_id=0).all()
			for egg_record in egg_records:
				(egg_id, mother_id, class_id, trainer_address, hatch_time, monster_id) = transform_data_contract.call().getEggDataById(egg_record.egg_id)
				egg_record.mother_id = mother_id
				egg_record.class_id = class_id
				egg_record.trainer = str(trainer_address).lower()
				egg_record.hatch_time = int(hatch_time)
				egg_record.new_obj_id = monster_id
				egg_record.save()
				log.info("erc20_update_egg|trainer=%s,egg_id=%s", sender, egg_id)

		# sync new egg
		max_egg_record = EtheremonDB.EmaEggDataTab.objects.all().order_by("-egg_id").first()
		max_id = 0
		if max_egg_record:
			max_id = max_egg_record.egg_id
		current_total = transform_data_contract.call().totalEgg()
		index = max_id + 1
		while index <= current_total:
			(egg_id, mother_id, class_id, trainer_address, hatch_time, monster_id) = transform_data_contract.call().getEggDataById(index)
			if class_id is 0:
				log.warn("invalid_egg_data|egg_id=%s", index)
				return
			EtheremonDB.EmaEggDataTab.objects.create(
				egg_id=index,
				mother_id=mother_id,
				class_id=class_id,
				trainer=str(trainer_address).lower(),
				hatch_time=int(hatch_time),
				new_obj_id=monster_id,
				create_time=start_time
			)
			index += 1
			log.info("erc20_add_egg|egg_id=%s", egg_id)

	if energy_sender_set:
		log.info("update_erc20_energy_info|len_sender=%s,latest_load_block=%s", len(energy_sender_set), latest_load_block)
		energy_contract = infura_client.getEnergyContract()
		current_ts = get_timestamp()
		for sender in energy_sender_set:
			(free_amount, paid_amount, last_claim) = energy_contract.call().getPlayerEnergy(sender)
			record = EtheremonDB.EmaPlayerEnergyTab.objects.filter(trainer=sender).first()
			if record:
				record.free_amount = free_amount
				record.paid_amount = paid_amount
				record.last_claim_time = last_claim
				record.update_time = current_ts
				record.save()
			else:
				EtheremonDB.EmaPlayerEnergyTab.objects.create(
					trainer=sender,
					init_amount=0,
					free_amount=free_amount,
					paid_amount=paid_amount,
					consumed_amount=0,
					last_claim_time=last_claim,
					create_time=current_ts,
					update_time=current_ts
				)

	# check revenue
	if site_id_set:
		for site_id in site_id_set:
			site_revenue = adventure_data_contract.call().getLandRevenue(site_id)
			log.info("update_site_revenue|site_id=%s,revenue=%s", site_id, site_revenue)
			if site_revenue[0] > 0 or site_revenue[1] > 0:
				emont_amount = (1.0 * site_revenue[0]) / 10**8
				eth_amount = (1.0 * site_revenue[1]) / 10**18
				site_revenue_record = EtheremonDB.EmaAdventureRevenueSiteTab.objects.filter(site_id=site_id).first()
				if not site_revenue_record:
					EtheremonDB.EmaAdventureRevenueSiteTab.objects.create(
						site_id=site_id,
						eth_amount=eth_amount,
						emont_amount=emont_amount,
						update_time=current_ts
					)
				else:
					if site_revenue_record.eth_amount < eth_amount:
						site_revenue_record.eth_amount = eth_amount
					if site_revenue_record.emont_amount < emont_amount:
						site_revenue_record.emont_amount = emont_amount
					site_revenue_record.update_time = current_ts
					site_revenue_record.save()

	# reload sender
	if deck_sender_set:
		log.info("update_deck_erc20|len_sender=%s,latest_load_block=%s", len(deck_sender_set), latest_load_block)
		data_contract = infura_client.getDataContract()
		for player in deck_sender_set:
			result = _sync_player_dex(data_contract, player)
			if result is False:
				log.warn("sync_player_fail|player=%s", player)

	record_block = latest_load_block
	if len(transaction_list) > 0:
		record_block += 1
		if record_block > current_block:
			record_block = current_block

	ema_settings_manager.set_setting(EmaSetting.SETTING_CONTRACT_ERC20_BLOCK, record_block)
	elapsed = time.time() - start_time
	if elapsed < 5:
		time.sleep(5-elapsed)
	log.data("end_update_erc20_contract|record_block=%s,total_txn=%s,total_egg_sender=%s,total_energy_sender=%s,elapsed=%s",
		record_block, len(transaction_list), len(egg_sender_set), len(energy_sender_set), elapsed)


if __name__ == "__main__":
	update_erc20_contract()