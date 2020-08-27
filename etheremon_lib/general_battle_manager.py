import random

from django.db import transaction

from common.jsonutils import to_json
from etheremon_api.views.helper import get_battle_details, get_timestamp
from etheremon_lib import ema_monster_manager, user_manager
from etheremon_lib.ema_monster_manager import get_mon_info
from etheremon_lib.models import *
from etheremon_lib.constants import MAX_RANDOM_ROUND


class BattleTypes:
	TOURNAMENT = 1


def start_battle(attacker_id, attacker_address, attacker_monster_ids, defender_id, defender_address, defender_monster_ids, battle_type, add_mon_exp=True):
	attacker_monsters = [get_mon_info(mon_id) for mon_id in attacker_monster_ids]
	defender_monsters = [get_mon_info(mon_id) for mon_id in defender_monster_ids]

	# generate random number
	random_factors = [
		random.randint(0, MAX_RANDOM_ROUND + 2),
		random.randint(0, MAX_RANDOM_ROUND + 2),
		random.randint(0, MAX_RANDOM_ROUND + 2)
	]
	monster_data = {
		"attacker_monsters": attacker_monsters,
		"defender_monsters": defender_monsters,
		"random_factors": random_factors
	}
	monster_data_str = to_json(monster_data)
	result, battle_details = get_battle_details(
		defender_monsters, attacker_monsters, random_factors, True
	)

	monster_exp_list = [
		(attacker_monsters[0]["monster_id"], battle_details[0]["attacker_exp_gain"]),
		(attacker_monsters[1]["monster_id"], battle_details[1]["attacker_exp_gain"]),
		(attacker_monsters[2]["monster_id"], battle_details[2]["attacker_exp_gain"]),
		(defender_monsters[0]["monster_id"], battle_details[0]["castle_exp_gain"]),
		(defender_monsters[1]["monster_id"], battle_details[1]["castle_exp_gain"]),
		(defender_monsters[2]["monster_id"], battle_details[2]["castle_exp_gain"])
	]
	monster_exp_list.sort()

	# make db transaction to
	# 1. update monster exp
	# 2. add battle details
	current_ts = get_timestamp()
	with transaction.atomic():
		# add exp
		if add_mon_exp:
			for (monster_id, exp_gain) in monster_exp_list:
				ema_monster_manager.add_exp(monster_id, exp_gain)

		# add battle record
		battle_record = EtheremonDB.BattleMatchTab(
			attacker_id=attacker_id,
			attacker_address=attacker_address,
			defender_id=defender_id,
			defender_address=defender_address,
			battle_type=battle_type,
			monster_data=monster_data_str,
			before_battle_data="",
			result=result,
			after_battle_data="",
			status=0,
			extra="",
			create_time=current_ts,
			update_time=current_ts
		)
		battle_record.save()

		# add exp
		if add_mon_exp:
			for (monster_id, exp_gain) in monster_exp_list:
				ema_monster_manager.calculate_ema_monster_exp(monster_id)

	return {
		"battle_id": battle_record.id,

		"attacker_id": attacker_id,
		"attacker_address": attacker_address,
		"attacker_username": user_manager.get_user_name(attacker_address),
		"attacker_monsters": attacker_monsters,

		"defender_id": defender_id,
		"defender_address": defender_address,
		"defender_username": user_manager.get_user_name_with_cache(defender_address),
		"defender_monsters": defender_monsters,

		"random_factors": random_factors,

		"details": battle_details,
		"result": result,
	}


def get_battle_record(battle_id):
	return EtheremonDB.BattleMatchTab.objects.filter(id=battle_id).first()
