from random import randint

from django.db.models import F

from common.logger import log
from etheremon_lib.constants import FREE_MONSTERS
from etheremon_lib.models import *
from common.utils import get_timestamp
from django.db import transaction
from etheremon_lib.monster_config import MONSTER_CLASS_STATS
from etheremon_lib.utils import get_level, get_class_name, DUMMY_MONS


class OffchainMonStatus:
	ACTIVE = 1

def wtt():
	print ("tade")

def update_ema_monster_bp(monster_id, class_id, base_stats, data_exp, status):
	class_info = MONSTER_CLASS_STATS[int(class_id)]
	current_ts = get_timestamp()
	with transaction.atomic():
		exp_record = EtheremonDB.EmaMonsterExpTab.objects.select_for_update().filter(monster_id=monster_id).first()
		if not exp_record:
			exp_record = EtheremonDB.EmaMonsterExpTab(
				monster_id=monster_id,
				adding_exp=0,
				added_exp=0,
				bp=0,
				status=status,
				create_time=current_ts,
				update_time=current_ts)
		# calculate bp
		total_exp = data_exp + exp_record.adding_exp
		bp = 0
		level = get_level(int(total_exp))
		final_stat = []
		for index in xrange(0, 6):
			final_stat.append(base_stats[index] + level * class_info['steps'][index] * 3)
			bp += final_stat[index]
		bp /= 6
		exp_record.bp = bp
		exp_record.status = status
		exp_record.update_time = current_ts
		exp_record.save()




def calculate_ema_monster_exp(monster_id):

	with transaction.atomic():
		exp_record = EtheremonDB.EmaMonsterExpTab.objects.select_for_update().filter(monster_id=monster_id).first()
		if not exp_record:
			return
		monster_data = EtheremonDB.EmaMonsterDataTab.objects.select_for_update().filter(monster_id=monster_id).first()
		if not monster_data:
			return
		current_ts = get_timestamp()
	
		class_info = MONSTER_CLASS_STATS[monster_data.class_id]
		total_exp = monster_data.exp + exp_record.adding_exp
		base_stats = [monster_data.b0, monster_data.b1, monster_data.b2, monster_data.b3, monster_data.b4, monster_data.b5]
		bp = 0
		level = get_level(int(total_exp))
		final_stat = []
		for index in xrange(0, 6):
			final_stat.append(base_stats[index] + level * class_info['steps'][index] * 3)
			bp += final_stat[index]
		bp /= 6
		exp_record.bp = bp
		exp_record.update_time = current_ts

		exp_record.save()
	return bp


def get_monster_ids(address):

	records = EtheremonDB.EmaMonsterDataTab.objects.filter(trainer=address).all()
	monster_ids = set()
	for record in records:
		monster_ids.add(record.monster_id)
	return list(monster_ids)


def get_monster_data(monster_id):
	return EtheremonDB.EmaMonsterDataTab.objects.filter(monster_id=monster_id).first()

def get_monster_dcl_data(monster_id):
	return EtheremonDB.DCLMonsterData.objects.filter(Mon_ID=monster_id).first()


def get_monster_data_by_trainer(trainer):
	return EtheremonDB.EmaMonsterDataTab.objects.filter(trainer=trainer).all()


def count_monster_data_by_trainer(trainer):
	return EtheremonDB.EmaMonsterDataTab.objects.filter(trainer=trainer).count()


def get_pending_exp(monster_id):
	return EtheremonDB.EmaMonsterExpTab.objects.filter(monster_id=monster_id).first()


def get_pending_exp_amount(monster_id):
	record = EtheremonDB.EmaMonsterExpTab.objects.filter(monster_id=monster_id).first()
	if not record:
		return 0
	return record.adding_exp


def get_monster_by_ids(monster_ids):
	return EtheremonDB.EmaMonsterDataTab.objects.filter(monster_id__in=monster_ids).all()


def get_mon_info(monster_id, exp=None):
	if monster_id == 0:
		return None

	if monster_id < 0:
		# Case off-chain mon
		monster_data = get_offchain_mon_by_id(mon_id=-monster_id)
		total_exp = monster_data.exp
		create_index = 0
	else:
		# Case on-chain mon
		monster_data = get_monster_data(monster_id)
		if monster_data is None:
			print ("monster_not_exist|monster_id=%s", monster_id)
			return None

		total_exp = exp
		if total_exp is None:
			total_exp = monster_data.exp
			pending_exp = get_pending_exp(monster_id)
			if pending_exp:
				total_exp += pending_exp.adding_exp

		create_index = monster_data.create_index

	mon_class_id = monster_data.class_id
	print monster_data.id
	monster_config = MONSTER_CLASS_STATS[mon_class_id]
	step_config = monster_config["steps"]
	battle_stats = [monster_data.b0, monster_data.b1, monster_data.b2, monster_data.b3, monster_data.b4, monster_data.b5]
	level = get_level(total_exp)
	bp = 0
	for index in xrange(6):
		battle_stats[index] = battle_stats[index] + step_config[index] * level * 3
		bp += battle_stats[index]
	bp = bp / 6

	return {
		"trainer": monster_data.trainer,
		"monster_id": monster_id,
		"class_id": mon_class_id,
		"exp": total_exp,
		"level": level,
		"total_level": level,
		"bp": bp,
		"total_bp": bp,
		"battle_stats": battle_stats,
		"total_battle_stats": battle_stats,
		"types": monster_config["types"],
		"ancestors": monster_config["ancestors"],
		"is_gason": monster_config["is_gason"],
		"create_index": create_index
	}


def create_offchain_mons(player_address, class_id=None):
	if class_id is None:
		for mon_class in FREE_MONSTERS:
			create_offchain_mons(player_address, mon_class)
	else:
		mon = get_offchain_mons(player_address, class_id)

		if mon.count() == 0:
			stats = get_random_stats(class_id)
			exp = 1
			level = get_level(exp)
			bp = 0
			for index in xrange(6):
				bp += stats[index] + MONSTER_CLASS_STATS[class_id]['steps'][index] * level * 3
			bp = bp / 6

			return EtheremonDB.EmaMonsterOffchainTab.objects.create(
				class_id=class_id,
				trainer=player_address,
				name=get_class_name(class_id=class_id, language='en'),
				exp=1,
				bp=bp,
				b0=stats[0],
				b1=stats[1],
				b2=stats[2],
				b3=stats[3],
				b4=stats[4],
				b5=stats[5],
				status=OffchainMonStatus.ACTIVE,
				extra="",
				create_time=get_timestamp(),
				update_time=get_timestamp()
			)


def get_offchain_mons(player_address, class_id=None):
	mons = EtheremonDB.EmaMonsterOffchainTab.objects.filter(trainer=player_address)
	if class_id is not None:
		mons = mons.filter(class_id=class_id)
	return mons


def get_offchain_mon_by_id(mon_id):
	return EtheremonDB.EmaMonsterOffchainTab.objects.filter(id=mon_id).first()


def get_random_stats(class_id):
	return [base + randint(0, 31) for base in MONSTER_CLASS_STATS[class_id]['stats']]



def add_exp(monster_id, exp_gain):
	if monster_id in DUMMY_MONS:
		return
	if is_onchain_mon(monster_id):
		EtheremonDB.EmaMonsterExpTab.objects.filter(monster_id=monster_id).update(adding_exp=F('adding_exp') + exp_gain)

	elif is_offchain_mon(monster_id):

		mon = EtheremonDB.EmaMonsterOffchainTab.objects.select_for_update().filter(id=-monster_id).first()
		if not mon:
			return

		class_info = MONSTER_CLASS_STATS[mon.class_id]
		exp = mon.exp + exp_gain
		base_stats = [mon.b0, mon.b1, mon.b2, mon.b3, mon.b4, mon.b5]
		bp = 0
		level = get_level(int(exp))
		final_stat = []
		for index in xrange(0, 6):
			final_stat.append(base_stats[index] + level * class_info['steps'][index] * 3)
			bp += final_stat[index]
		bp /= 6
		mon.exp = exp
		mon.bp = bp
		mon.save()


def is_onchain_mon(monster_id):
	return monster_id > 0


def is_offchain_mon(monster_id):
	return monster_id < 0