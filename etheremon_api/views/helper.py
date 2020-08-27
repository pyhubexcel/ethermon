# coding=utf-8
import copy
from common.logger import log
from etheremon_lib.utils import *
from etheremon_lib.ema_monster_manager import get_monster_data
from etheremon_lib.contract_manager import *
from etheremon_lib.monster_config import *
from etheremon_lib.ema_egg_manager import get_egg_data_by_obj


def get_battle_monster(monster_id, exp=None, basic_info=None):
	if not basic_info:
		monster_data_record = get_monster_data(monster_id)
		class_id = monster_data_record.class_id
		trainer = monster_data_record.trainer
		monster_exp = monster_data_record.exp
		create_index = monster_data_record.create_index
		battle_stats = [monster_data_record.b0, monster_data_record.b1, monster_data_record.b2, monster_data_record.b3,
						monster_data_record.b4, monster_data_record.b5]
	else:
		class_id = basic_info["class_id"]
		trainer = basic_info["trainer"]
		monster_exp = basic_info["monster_exp"]
		create_index = basic_info["create_index"]
		battle_stats = basic_info["base_stats"]

	if exp is not None:
		level = get_level(exp)
	else:
		level = get_level(monster_exp)

	monster_config = MONSTER_CLASS_STATS[class_id]
	step_config = monster_config["steps"]
	index = 0
	bp = 0
	while index < 6:
		battle_stats[index] = battle_stats[index] + step_config[index] * level * 3
		bp += battle_stats[index]
		index += 1
	bp = bp / 6
	return {
		"bp": bp,
		"trainer": trainer,
		"monster_id": monster_id,
		"class_id": class_id,
		"level": level,
		"battle_stats": battle_stats,
		"types": monster_config["types"],
		"ancestors": monster_config["ancestors"],
		"exp": get_exp_by_level(level),
		"create_index": create_index}


def get_battle_supporter(monster_id):
	if not monster_id or monster_id == 0:
		return {"monster_id": 0, "class_id": 0, "types": [], "is_gason": False}
	monster_data_record = get_monster_data(monster_id)
	class_id = monster_data_record.class_id
	trainer = monster_data_record.trainer
	monster_config = MONSTER_CLASS_STATS[class_id]
	return {
		"trainer": trainer,
		"monster_id": monster_id,
		"class_id": class_id,
		"types": monster_config["types"],
		"is_gason": monster_config["is_gason"]
	}


def get_ancestor_buff(a1, s1, s2, s3):
	count = 0
	for ancestor in a1["ancestors"]:
		if s1 and s1["monster_id"] > 0 and s1["class_id"] == ancestor:
			count += 1
		elif s2 and s2["monster_id"] > 0 and s2["class_id"] == ancestor:
			count += 1
		elif s3 and s3["monster_id"] > 0 and s3["class_id"] == ancestor:
			count += 1
	return count * ANCESTOR_BUFF_PER


def get_gason_buff(a1, s1, s2, s3):
	count = 0
	for type in a1["types"]:
		if s1 and s1["monster_id"] > 0 and s1["is_gason"] and s1["types"][0] == type:
			count += 1
		elif s2 and s2["monster_id"] > 0 and s2["is_gason"] and s2["types"][0] == type:
			count += 1
		elif s3 and s3["monster_id"] > 0 and s3["is_gason"] and s3["types"][0] == type:
			count += 1
	return count * GASON_BUFF_PER


def get_type_buff(monster1, monster2, is_new):
	buff_value = TYPE_BUFF_PER
	if is_new:
		buff_value = TYPE_BUFF_PER_NEW
	for type1 in monster1["types"]:
		for type2 in monster2["types"]:
			if MONSTER_AGAINST_CONFIG[type1] == type2:
				return buff_value
	return 0


def safe_deduct(a, b):
	if a > b:
		return (a - b)
	return 0


def cal_hp_deducted(attack, special_attack, defense, special_defense, lucky, is_new):
	if lucky:
		attack = attack * 13 / 10
		special_attack = special_attack * 13 / 10
	if not is_new:
		hp_deducted = safe_deduct(attack, defense * 3 / 4)
		hp_special_deducted = safe_deduct(special_attack, special_defense * 3 / 4)
	else:
		hp_deducted = safe_deduct(attack, defense)
		hp_special_deducted = safe_deduct(special_attack, special_defense)
	if hp_deducted < MIN_HP_DEDUCTED and hp_special_deducted < MIN_HP_DEDUCTED:
		return MIN_HP_DEDUCTED
	if hp_deducted > hp_special_deducted:
		return hp_deducted
	return hp_special_deducted


def get_battle_flow(a1, a2, ran, is_new):
	round = 0
	turns = []
	castle_battle_stats = copy.deepcopy(a1["battle_stats"])
	attacker_battle_stats = copy.deepcopy(a2["battle_stats"])
	max_round = MAX_RANDOM_ROUND
	if is_new:
		max_round = MAX_RANDOM_ROUND_NEW

	while round < max_round and a1["battle_stats"][0] > 0 and a2["battle_stats"][0] > 0:
		if a1["battle_stats"][5] > a2["battle_stats"][5]:
			if round % 2 == 0:
				deduct_hp = cal_hp_deducted(a1["battle_stats"][1], a1["battle_stats"][3], a2["battle_stats"][2],
											a2["battle_stats"][4], round == ran, is_new)
				a2["battle_stats"][0] = safe_deduct(a2["battle_stats"][0], deduct_hp)
				turns.append({
					"attack": "castle",
					"defense": "attacker",
					"deduct_hp": deduct_hp,
					"critical_attack": round == ran
				})
			else:
				deduct_hp = cal_hp_deducted(a2["battle_stats"][1], a2["battle_stats"][3], a1["battle_stats"][2],
											a1["battle_stats"][4], round == ran, is_new)
				a1["battle_stats"][0] = safe_deduct(a1["battle_stats"][0], deduct_hp)
				turns.append({
					"attack": "attacker",
					"defense": "castle",
					"deduct_hp": deduct_hp,
					"critical_attack": round == ran
				})
		else:
			if round % 2 > 0:
				deduct_hp = cal_hp_deducted(a1["battle_stats"][1], a1["battle_stats"][3], a2["battle_stats"][2],
											a2["battle_stats"][4], round == ran, is_new)
				a2["battle_stats"][0] = safe_deduct(a2["battle_stats"][0], deduct_hp)
				turns.append({
					"attack": "castle",
					"defense": "attacker",
					"deduct_hp": deduct_hp,
					"critical_attack": round == ran
				})
			else:
				deduct_hp = cal_hp_deducted(a2["battle_stats"][1], a2["battle_stats"][3], a1["battle_stats"][2],
											a1["battle_stats"][4], round == ran, is_new)
				a1["battle_stats"][0] = safe_deduct(a1["battle_stats"][0], deduct_hp)
				turns.append({
					"attack": "attacker",
					"defense": "castle",
					"deduct_hp": deduct_hp,
					"critical_attack": round == ran
				})
		round += 1

	win = a1["battle_stats"][0] >= a2["battle_stats"][0]
	response_data = {
		"turns": turns,
		"win": win,
		"castle_exp_gain": get_gain_exp(a1["level"], a2["level"], win, is_new) * CASTLE_EXP_ADJUSTMENT / 100,
		"attacker_exp_gain": get_gain_exp(a2["level"], a1["level"], (not win), is_new) * CASTLE_EXP_ATTACKER_ADJUSTMENT / 100,
		"castle_battle_stats": castle_battle_stats,
		"attacker_battle_stats": attacker_battle_stats
	}
	return response_data


def get_battle_details(castle_monsters, attacker_monsters, random_factors, is_new=False):
	castle_monsters = copy.deepcopy(castle_monsters)
	attacker_monsters = copy.deepcopy(attacker_monsters)
	battle_details = {}
	count = 0
	castle_win_count = 0
	while count < 3:
		castle_bp = 0
		attacker_bp = 0
		for stat in castle_monsters[count]["battle_stats"]:
			castle_bp += stat
		for stat in attacker_monsters[count]["battle_stats"]:
			attacker_bp += stat
		castle_bp = castle_bp / 6
		attacker_bp = attacker_bp / 6

		# calculate castle monster buff
		attack_buff = get_ancestor_buff(castle_monsters[count], castle_monsters[3], castle_monsters[4], castle_monsters[5])
		defense_buff = get_gason_buff(castle_monsters[count], castle_monsters[3], castle_monsters[4], castle_monsters[5])

		type_buff = get_type_buff(castle_monsters[count], attacker_monsters[count], is_new)
		attack_buff += type_buff
		if is_new:
			defense_buff += type_buff

		if attack_buff > 0:
			castle_monsters[count]["battle_stats"][1] += castle_monsters[count]["battle_stats"][1] * attack_buff / 100
			castle_monsters[count]["battle_stats"][3] += castle_monsters[count]["battle_stats"][3] * attack_buff / 100
		if defense_buff > 0:
			castle_monsters[count]["battle_stats"][2] += castle_monsters[count]["battle_stats"][2] * defense_buff / 100
			castle_monsters[count]["battle_stats"][4] += castle_monsters[count]["battle_stats"][4] * defense_buff / 100

		# calculate attacker buff
		attack_buff = get_ancestor_buff(attacker_monsters[count], attacker_monsters[3], attacker_monsters[4], attacker_monsters[5])
		defense_buff = get_gason_buff(attacker_monsters[count], attacker_monsters[3], attacker_monsters[4], attacker_monsters[5])

		type_buff = get_type_buff(attacker_monsters[count], castle_monsters[count], is_new)
		attack_buff += type_buff
		if is_new:
			defense_buff += type_buff

		if attack_buff > 0:
			attacker_monsters[count]["battle_stats"][1] += attacker_monsters[count]["battle_stats"][1] * attack_buff / 100
			attacker_monsters[count]["battle_stats"][3] += attacker_monsters[count]["battle_stats"][3] * attack_buff / 100
		if defense_buff > 0:
			attacker_monsters[count]["battle_stats"][2] += attacker_monsters[count]["battle_stats"][2] * defense_buff / 100
			attacker_monsters[count]["battle_stats"][4] += attacker_monsters[count]["battle_stats"][4] * defense_buff / 100

		castle_bp_buff = 0
		attacker_bp_buff = 0
		for stat in castle_monsters[count]["battle_stats"]:
			castle_bp_buff += stat
		for stat in attacker_monsters[count]["battle_stats"]:
			attacker_bp_buff += stat
		castle_bp_buff = castle_bp_buff / 6
		attacker_bp_buff = attacker_bp_buff / 6

		battle_details[count] = get_battle_flow(castle_monsters[count], attacker_monsters[count], random_factors[count], is_new)
		battle_details[count]["castle_bp"] = castle_bp
		battle_details[count]["castle_bp_buff"] = castle_bp_buff
		battle_details[count]["attacker_bp"] = attacker_bp
		battle_details[count]["attacker_bp_buff"] = attacker_bp_buff

		if battle_details[count]["win"]:
			castle_win_count += 1
		count += 1

	if castle_win_count > 1:
		result = BattleResult.CASTLE_WIN
	else:
		result = BattleResult.CASTLE_LOSE

	return result, battle_details


def is_from_egg(monster_id):
	return get_egg_data_by_obj(monster_id) is not None


def get_start_time_of_the_day(current_ts):
	return (current_ts // 86400) * 86400


def get_end_time_of_the_day(current_ts):
	return (current_ts // 86400 + 1) * 86400 - 1
