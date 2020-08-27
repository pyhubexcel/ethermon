import time
from common.logger import log
from common.utils import get_timestamp
from etheremon_lib import ema_player_manager, utils
from etheremon_lib.config import *
from etheremon_lib.models import EtheremonDB
from etheremon_lib.ema_monster_manager import get_monster_ids
from etheremon_lib.ema_monster_manager import wtt

from etheremon_lib import dcl_manager
from etheremon_lib.ema_monster_manager import update_ema_monster_bp
from etheremon_lib.utils import get_stats



# status, add_count, update_count
def _sync_monster_id(data_contract, monster_id, transform_contract=None, base_stats_refresh=False):
	add_count = 0
	update_count = 0

	# check monster is existed or not
	monster_record = EtheremonDB.EmaMonsterDataTab.objects.filter(monster_id=monster_id).first()
	if monster_record and monster_record.class_id == 21:
		# skip non important monster
		return True, 0, 0

	(monster_return_id, class_id, owner_address, exp, create_index, last_claim_index, monster_create_time) = data_contract.call().getMonsterObj(monster_id)
	if int(class_id) == 0:  # Bug, break
		log.error('update_ema_monster_error|monster_id=%s', monster_id)
		return False, 0, 0

	log.info("sync_monster_id|contract_data|monster_id=%s,owner_address=%s,exp=%s", monster_id, owner_address, owner_address)

	owner_address = owner_address.lower()
	name = data_contract.call().getMonsterName(monster_id)
	name = name.encode("latin1").decode("utf8").strip()
	name = (name[:100] + '..') if len(name) > 100 else name

	egg_bonus = None
	if transform_contract and class_id <= 24:
		egg_bonus = transform_contract.call().getBonusEgg(monster_id)

	current_ts = get_timestamp()
	exp_flag = False
	trainer_flag = None

	# update information
	if monster_record:
		if egg_bonus is None:
			egg_bonus = monster_record.egg_bonus

		if base_stats_refresh:
			base_stats = []
			for index in xrange(0, 6):
				stat_value = data_contract.call().getElementInArrayType(DataArrayType.STAT_BASE, monster_id, index)
				base_stats.append(stat_value)
			# if 0 in base_stats:
			# 	log.error('update_ema_monster_error|monster_id=%s,base_stats=%s', monster_id, base_stats)
			# 	return False, 0, 0
			monster_record.b0 = base_stats[0]
			monster_record.b1 = base_stats[1]
			monster_record.b2 = base_stats[2]
			monster_record.b3 = base_stats[3]
			monster_record.b4 = base_stats[4]
			monster_record.b5 = base_stats[5]
			monster_record.save()

		# Nothing to update
		if monster_record.trainer == owner_address \
				and monster_record.exp == exp \
				and monster_record.name == name \
				and monster_record.last_claim_index == last_claim_index \
				and monster_record.egg_bonus == egg_bonus:
			return True, 0, 0

		# update exp
		if monster_record.exp != exp:
			exp_flag = True
			monster_record.exp = exp

			# get bp
			stats, bp, level = get_stats(
				monster_record.class_id,
				monster_record.exp,
				[monster_record.b0, monster_record.b1, monster_record.b2, monster_record.b3, monster_record.b4, monster_record.b5]
			)
			monster_record.bp = bp

		# Update rank team if necessary
		if monster_record.trainer != owner_address:
			trainer_flag = monster_record.trainer

		monster_record.egg_bonus = egg_bonus
		monster_record.trainer = owner_address
		monster_record.name = name
		monster_record.last_claim_index = last_claim_index
		monster_record.update_time = current_ts
		monster_record.save()
		log.info("update_ema_monster_info|monster_id=%s", monster_id)
		update_count += 1
		dcl_manager.dcl_update_transferred_mon(monster_id, owner_address)
	else:
		# Case new mon
		exp_flag = True
		base_stats = []
		for index in xrange(0, 6):
			stat_value = data_contract.call().getElementInArrayType(DataArrayType.STAT_BASE, monster_id, index)
			base_stats.append(stat_value)

		if 0 in base_stats:
			log.error('update_ema_monster_error|monster_id=%s,base_stats=%s', monster_id, base_stats)
			return False, 0, 0

		# get bp
		stats, bp, level = get_stats(
			class_id,
			exp,
			[base_stats[0], base_stats[1], base_stats[2], base_stats[3], base_stats[4], base_stats[5]]
		)

		if egg_bonus is None:
			egg_bonus = 0

		monster_record = EtheremonDB.EmaMonsterDataTab(
			monster_id=monster_id,
			class_id=class_id,
			trainer=owner_address,
			name=name,
			exp=exp,
			b0=base_stats[0],
			b1=base_stats[1],
			b2=base_stats[2],
			b3=base_stats[3],
			b4=base_stats[4],
			b5=base_stats[5],
			bp=bp,
			egg_bonus=egg_bonus,
			create_index=create_index,
			last_claim_index=last_claim_index,
			create_time=monster_create_time,
			update_time=current_ts
		)
		monster_record.save()
		log.info("add_ema_monster_info|monster_id=%s", monster_id)
		add_count += 1

	# update exp
	if exp_flag:
		monster_stats = [monster_record.b0, monster_record.b1, monster_record.b2, monster_record.b3, monster_record.b4, monster_record.b5]
		status = EmaMonsterStatus.Normal
		if monster_record.trainer == EMPTY_ADDRESS:
			status = EmaMonsterStatus.Deleted
		update_ema_monster_bp(monster_id, class_id, monster_stats, monster_record.exp, status)

	# Update old_player_rank
	if trainer_flag:
		ema_player_manager.try_disband_team(trainer_flag)

	log.info("sync_monster_id|monster_id=%s,exp=%s,class_id=%s", monster_id, exp, class_id)

	return True, add_count, update_count


def _sync_player_dex(data_contract, address, transform_contract=None, base_stats_refresh=False):
	# get monster dex size
	dex_size = data_contract.call().getMonsterDexSize(address)
	dex_size = int(dex_size)
	if dex_size == 0:
		first_monster_id = int(data_contract.call().getMonsterObjId(address, 0))
		if first_monster_id != 0:
			log.warn("sync_player_invalid|address=%s,dex_size=%s,first_monster_id=%s", address, dex_size, first_monster_id)
			return False
		return True

	monster_id_set = set()
	for index in range(dex_size):
		monster_id = data_contract.call().getMonsterObjId(address, index)
		monster_id_set.add(int(monster_id))

	#log.info("sync_player_dex|monster_id_set=%s", monster_id_set)

	# get monster id which that user current has in db
	current_monster_ids = get_monster_ids(address)
	for current_monster_id in current_monster_ids:
		monster_id_set.add(current_monster_id)

	total_add = 0
	total_update = 0
	for monster_id in monster_id_set:
		result, add_flag, update_flag = _sync_monster_id(data_contract, monster_id, transform_contract, base_stats_refresh)
		if result is False:
			return False
		total_add += add_flag
		total_update += update_flag

	#log.info("sync_player_dex|address=%s,total_add=%s,total_update=%s", address, total_add, total_update)

	return True
