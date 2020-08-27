from etheremon_lib.models import *
from common.utils import get_timestamp
from django.db import transaction
from etheremon_lib.monster_config import MONSTER_CLASS_STATS
from etheremon_lib.utils import get_level
from etheremon_lib.constants import *

WIN_EMONT_REWARD = 0.2 * 10 ** 8
RANK_TOP_ENERGY_REQUIRES = {
	1: 30,
	2: 24,
	3: 20,
	4: 16,
	5: 10
}

def get_pending_exp_claim(monster_id):
	return EtheremonDB.EmaClaimMonExpTab.objects.filter(monster_id=monster_id).filter(status=EmaClaimStatus.STATUS_PENDING).first()

def add_pending_exp_claim(monster_id):
	record = EtheremonDB.EmaClaimMonExpTab(
		monster_id=monster_id,
		exp=0,
		status=EmaClaimStatus.STATUS_INIT,
		update_time=get_timestamp()
	)
	record.save()
	with transaction.atomic():
		exp_record = EtheremonDB.EmaMonsterExpTab.objects.select_for_update().filter(monster_id=monster_id).first()
		if not exp_record or exp_record.adding_exp == 0:
			return record
		# check pending
		init_records = list(EtheremonDB.EmaClaimMonExpTab.objects.select_for_update().filter(monster_id=monster_id).filter(status=EmaClaimStatus.STATUS_INIT).all())
		pending_record = EtheremonDB.EmaClaimMonExpTab.objects.select_for_update().filter(monster_id=monster_id).filter(status=EmaClaimStatus.STATUS_PENDING).first()
		if pending_record:
			for init_record in init_records:
				init_record.status = EmaClaimStatus.STATUS_FAIL
				init_record.save()
			return pending_record
		first_record = init_records[0]
		for init_record in init_records[1:]:
			init_record.status = EmaClaimStatus.STATUS_FAIL
			init_record.save()
		first_record.exp = exp_record.adding_exp
		first_record.status = EmaClaimStatus.STATUS_PENDING
		first_record.save()
	return first_record

def proceed_pending_exp_claim(request_id):
	current_ts = get_timestamp()
	with transaction.atomic():
		request_record = EtheremonDB.EmaClaimMonExpTab.objects.select_for_update().get(id=request_id)
		if request_record.status != EmaClaimStatus.STATUS_PENDING:
			return False
		exp_record = EtheremonDB.EmaMonsterExpTab.objects.select_for_update().filter(monster_id=request_record.monster_id).first()
		exp_record.adding_exp -= request_record.exp
		exp_record.added_exp += request_record.exp
		exp_record.update_time = current_ts
		exp_record.save()
		request_record.status = EmaClaimStatus.STATUS_COMPLETE
		request_record.update_time = current_ts
		request_record.save()
	return True

def get_pending_win_claim(player_id):
	return EtheremonDB.EmaClaimRankWinTab.objects.filter(player_id=player_id).filter(status=EmaClaimStatus.STATUS_PENDING).first()

def add_pending_win_claim(player_id):
	record = EtheremonDB.EmaClaimRankWinTab(
		player_id=player_id,
		count_win=0,
		count_emont=0,
		status=EmaClaimStatus.STATUS_INIT,
		update_time=get_timestamp()
	)
	record.save()
	with transaction.atomic():
		player_data = EtheremonDB.EmaPlayerRankData.objects.select_for_update().filter(player_id=player_id).first()
		if not player_data:
			return record
		available_win = player_data.total_win - player_data.total_claimed
		if available_win < 1:
			return record
		init_records = list(EtheremonDB.EmaClaimRankWinTab.objects.select_for_update().filter(player_id=player_id).filter(status=EmaClaimStatus.STATUS_INIT).all())
		pending_record = EtheremonDB.EmaClaimRankWinTab.objects.select_for_update().filter(player_id=player_id).filter(status=EmaClaimStatus.STATUS_PENDING).first()
		if pending_record:
			for init_record in init_records:
				init_record.status = EmaClaimStatus.STATUS_FAIL
				init_record.save()
			return pending_record
		first_record = init_records[0]
		for init_record in init_records[1:]:
			init_record.status = EmaClaimStatus.STATUS_FAIL
			init_record.save()
		first_record.count_win = available_win
		first_record.count_emont = WIN_EMONT_REWARD * available_win
		first_record.status = EmaClaimStatus.STATUS_PENDING
		first_record.save()

		player_data.total_claimed += available_win
		player_data.save()
	return first_record

def proceed_pending_win_claim(request_id):
	current_ts = get_timestamp()
	with transaction.atomic():
		request_record = EtheremonDB.EmaClaimRankWinTab.objects.select_for_update().get(id=request_id)
		if request_record.status != EmaClaimStatus.STATUS_PENDING:
			return False
		request_record.status = EmaClaimStatus.STATUS_COMPLETE
		request_record.update_time = current_ts
		request_record.save()
	return True

def get_pending_top_claim(player_id):
	return EtheremonDB.EmaClaimRankTopTab.objects.filter(player_id=player_id).filter(status=EmaClaimStatus.STATUS_PENDING).first()

def add_pending_top_claim(player_id, rank):
	record = EtheremonDB.EmaClaimRankTopTab(
		player_id=player_id,
		rank=rank,
		status=EmaClaimStatus.STATUS_INIT,
		update_time=get_timestamp()
	)
	record.save()
	player_data = EtheremonDB.EmaPlayerRankData.objects.filter(player_id=player_id).first()
	if not player_data:
		return record
	energy_require = RANK_TOP_ENERGY_REQUIRES[rank]
	with transaction.atomic():
		energy_record = EtheremonDB.EmaPlayerEnergyTab.objects.select_for_update().filter(trainer=player_data.trainer).first()
		if not energy_record:
			return record
		available_energy = energy_record.init_amount + energy_record.free_amount + energy_record.paid_amount - energy_record.consumed_amount - energy_record.invalid_amount
		if available_energy < energy_require:
			return record

		init_records = list(EtheremonDB.EmaClaimRankTopTab.objects.select_for_update().filter(player_id=player_id).filter(status=EmaClaimStatus.STATUS_INIT).all())
		pending_record = EtheremonDB.EmaClaimRankTopTab.objects.select_for_update().filter(player_id=player_id).filter(status=EmaClaimStatus.STATUS_PENDING).first()
		if pending_record:
			for init_record in init_records:
				init_record.status = EmaClaimStatus.STATUS_FAIL
				init_record.save()
			return pending_record

		first_record = init_records[0]
		for init_record in init_records[1:]:
			init_record.status = EmaClaimStatus.STATUS_FAIL
			init_record.save()

		energy_record.consumed_amount += energy_require
		energy_record.save()

		first_record.status = EmaClaimStatus.STATUS_PENDING
		first_record.save()
	return first_record

def proceed_pending_top_claim(request_id):
	current_ts = get_timestamp()
	with transaction.atomic():
		request_record = EtheremonDB.EmaClaimRankTopTab.objects.select_for_update().get(id=request_id)
		if request_record.status != EmaClaimStatus.STATUS_PENDING:
			return False
		request_record.status = EmaClaimStatus.STATUS_COMPLETE
		request_record.update_time = current_ts
		request_record.save()
	return True