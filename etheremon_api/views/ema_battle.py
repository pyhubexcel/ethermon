# coding=utf-8
from random import randint

from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from common.utils import parse_params, log_request
from etheremon_lib.decorators.auth_decorators import sign_in_required
from etheremon_lib.utils import *
from common.jsonutils import *
from etheremon_lib.form_schema import *
from etheremon_lib.preprocessor import pre_process_header
from etheremon_lib.ema_player_manager import *
from etheremon_lib.ema_energy_manager import *
from etheremon_lib.ema_battle_manager import *
from etheremon_lib.contract_manager import sign_single_token
from etheremon_lib import ema_monster_manager, ema_energy_manager, constants, ema_player_manager, ema_battle_manager
from etheremon_lib import user_manager
from etheremon_lib import ema_claim_manager
from etheremon_lib.crypt import *
from etheremon_lib.constants import *
from etheremon_lib.ema_monster_manager import get_mon_info
from helper import get_battle_details
from web3 import Web3
from etheremon_lib.infura_client import InfuraClient


def _safe_deduct(a, b):
	return a - b if a > b else 0


# K = 20
# result = 0 (p1 wins), 1 (p2 wins)
def _get_elo_change(p1, p2, result):
	if p1 > p2:
		diff = p1 - p2
	else:
		diff = p2 - p1
	score_change = 10
	if diff > 636:
		score_change = 20
	elif diff > 436:
		score_change = 19
	elif diff > 338:
		score_change = 18
	elif diff > 269:
		score_change = 17
	elif diff > 214:
		score_change = 16
	elif diff > 168:
		score_change = 15
	elif diff > 126:
		score_change = 14
	elif diff > 88:
		score_change = 13
	elif diff > 52:
		score_change = 12
	elif diff > 17:
		score_change = 11

	if result == 0:
		# 1 wins 2
		if p1 > p2:
			score_change = 20 - score_change
			return p1 + score_change, _safe_deduct(p2, score_change)
		else:
			return p1 + score_change, _safe_deduct(p2, score_change)
	else:
		if p1 > p2:
			return _safe_deduct(p1, score_change), p2 + score_change
		else:
			score_change = 20 - score_change
			return _safe_deduct(p1, score_change), p2 + score_change


@csrf_exempt
@log_request()
@parse_params(form=EmaBattleGetUserStatsSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_user_stats(request, data):
	# verify information
	if not Web3.isAddress(data["trainer_address"]):
		data["trainer_address"] = EMPTY_ADDRESS

	infura_client = InfuraClient(config.INFURA_API_URLS["general"])
	emont_contract = infura_client.getEmontContract()
	total_emont = emont_contract.call().balanceOf(data['trainer_address'])
	total_emont = (total_emont * 1.0) / 10**8

	current_block_time = data.get("current_block_time", get_timestamp() - 3 * 60)
	trainer_address = data["trainer_address"].lower()

	response_data = {
		"username": user_manager.get_user_name(trainer_address),
		"trainer_address": data["trainer_address"],
		"count_rank_battle": 0,
		"count_rank_win": 0,
		"count_rank_lose": 0,
		"total_player": count_total_rank(),
		"total_player_rkt": count_total_rank_rkt(),
		"current_rank": 0,
		"current_rank_rkt": 0,
		"current_point": 0,
		"current_energy": 0,
		"current_emont": total_emont,
		"current_energy_claimable": 0,
		"latest_battles": [],
		"claimed_free_mon": 0,
	}

	# Check free mon claimed
	free_mons = ema_monster_manager.get_offchain_mons(trainer_address)
	response_data["claimed_free_mon"] = int(free_mons.count() > 0)

	player_data = get_player_rank_by_address(trainer_address)
	player_data_rkt = get_rkt_player_rank_by_address(trainer_address)
	if player_data:
		response_data["count_rank_battle"] = player_data.total_win + player_data.total_lose
		response_data["count_rank_win"] = player_data.total_win
		response_data["count_rank_lose"] = player_data.total_lose

		response_data["current_rank"] = cal_current_rank(player_data.point)
		response_data["current_point"] = player_data.point

	if player_data_rkt:
		response_data["current_rank_rkt"] = cal_current_rank_rkt(player_data_rkt.point)

	response_data["current_energy"] = get_available_energy(trainer_address)

	energy_data = get_energy_by_trainer(trainer_address)
	if energy_data:
		response_data["current_energy_claimable"] = get_claimable_energy(energy_data.last_claim_time, current_block_time)
	else:
		response_data["current_energy_claimable"] = 10

	# get latest battle
	latest_battles_records = get_lates_rank_battles(5)
	for battle_record in latest_battles_records:
		item = {
			"battle_id": battle_record.id,
			"attacker_address": "",
			"attacker_username": "",
			"attacker_before_point": battle_record.attacker_before_point,
			"attacker_after_point": battle_record.attacker_after_point,
			"defender_address": "",
			"defender_username": "",
			"defender_before_point": battle_record.defender_before_point,
			"defender_after_point": battle_record.defender_after_point,
		}
		attacker_player_record = get_player_rank_by_id(battle_record.attacker_id)
		defender_player_record = get_player_rank_by_id(battle_record.defender_id)
		item["attacker_address"] = attacker_player_record.trainer
		item["attacker_username"] = user_manager.get_user_name(attacker_player_record.trainer)
		item["defender_address"] = defender_player_record.trainer
		item["defender_username"] = user_manager.get_user_name(defender_player_record.trainer)
		response_data["latest_battles"].append(item)

	return api_response_result(request, ResultCode.SUCCESS, response_data)


@csrf_exempt
@log_request()
@parse_params(form=EmaBattleGetRankCastlesSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_rank_castles(request, data):
	# verify information
	if not Web3.isAddress(data["trainer_address"]):
		log.warn("send_to_address_invalid|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_send_to_address"})

	trainer_address = data["trainer_address"].lower()
	response_data = {
		"player_info": {
			"player_id": 0,
			"trainer_address": trainer_address,
			"username": user_manager.get_user_name(trainer_address),
			"current_rank": 0,
			"current_point": 0,
			"current_energy": 0,
			"monsters": []
		},
		"defender_list": []
	}

	player_data = get_player_rank_by_address(trainer_address)
	if not player_data:
		return api_response_result(request, ResultCode.SUCCESS, response_data)

	# populate player info
	response_data["player_info"]["player_id"] = player_data.player_id
	response_data["player_info"]["current_rank"] = cal_current_rank(player_data.point)
	response_data["player_info"]["current_point"] = player_data.point
	response_data["player_info"]["current_energy"] = get_available_energy(trainer_address)
	response_data["player_info"]["monsters"] = [
		get_mon_info(player_data.a0),
		get_mon_info(player_data.a1),
		get_mon_info(player_data.a2),
		get_mon_info(player_data.s0),
		get_mon_info(player_data.s1),
		get_mon_info(player_data.s2),
	]

	# populate defender list
	defender_record_list = get_defenders_by_point(player_data.point, player_data.player_id)
	for defender_record in defender_record_list:
		defender_username = user_manager.get_user_name(defender_record.trainer)
		monster_info = [
			get_mon_info(defender_record.a0),
			get_mon_info(defender_record.a1),
			get_mon_info(defender_record.a2),
			get_mon_info(defender_record.s0),
			get_mon_info(defender_record.s1),
			get_mon_info(defender_record.s2),
		]
		avg_level = (monster_info[0]["level"] + monster_info[1]["level"] + monster_info[2]["level"]) / 3
		avg_bp = (monster_info[0]["bp"] + monster_info[1]["bp"] + monster_info[2]["bp"]) / 3

		defender_is_valid, err = ema_battle_manager.is_valid_team(monster_info, defender_record.trainer)
		if defender_is_valid:
			response_data["defender_list"].append({
				"player_id": defender_record.player_id,
				"address": defender_record.trainer,
				"username": defender_username,
				"point": defender_record.point,
				"rank": cal_current_rank(defender_record.point),
				"monster_info": monster_info,
				"avg_level": avg_level,
				"avg_bp": avg_bp,
			})

	request.session[SessionKeys.RANK_OPPONENTS] = [d["player_id"] for d in response_data["defender_list"]]
	return api_response_result(request, ResultCode.SUCCESS, response_data)





@csrf_exempt
@log_request()
@parse_params(form=EmaBattleSetRankTeamSchema, method='POST', data_format='JSON', error_handler=api_response_error_params)
@pre_process_header()
@sign_in_required()
def set_rank_team_rkt(request, data):
	trainer_address = data["trainer_address"].lower()
	team = data["team"]

	# verify information
	if not Web3.isAddress(trainer_address):
		log.warn("invalid_address|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_address"})

	if team[0] == 0 or team[1] == 0 or team[2] == 0:
		log.warn("invalid_team|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_team"})

	team_details = [get_mon_info(mon_id) for mon_id in team]

	# Validate team
	is_valid, error = ema_battle_manager.is_valid_team(team_details, trainer_address)
	if not is_valid:
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": error})

	# Finish validation, start updating
	with transaction.atomic():
		avg_level = (team_details[0]["total_level"]+team_details[1]["total_level"]+team_details[2]["total_level"]) / 3
		avg_bp = (team_details[0]["total_bp"] + team_details[1]["total_bp"] + team_details[2]["total_bp"]) / 3
		current_ts = get_timestamp()

		player_rank_data = ema_player_manager.get_rkt_player_rank_by_address(trainer_address)
		if not player_rank_data:
			# Init rank data
			player_rank_data = EtheremonDB.EmaPlayerRankRKTData(
				trainer=trainer_address,
				point=ema_player_manager.get_initial_elo_point(avg_bp),
				total_win=0,
				total_lose=0,
				total_claimed=0,
			)

			# Init energy record if not exist
			ema_energy_manager.initialize_energy_if_not_exist(trainer_address)

		else:
			# Consume energy
			ema_energy_manager.consume_energy(trainer_address, constants.RANK_CHANGE_TEAM_ENERGY_REQUIRE)

		# Update data
		player_rank_data.a0 = (team_details[0] or {}).get("monster_id", 0)
		player_rank_data.a1 = (team_details[1] or {}).get("monster_id", 0)
		player_rank_data.a2 = (team_details[2] or {}).get("monster_id", 0)
		player_rank_data.s0 = (team_details[3] or {}).get("monster_id", 0)
		player_rank_data.s1 = (team_details[4] or {}).get("monster_id", 0)
		player_rank_data.s2 = (team_details[5] or {}).get("monster_id", 0)
		player_rank_data.avg_level = avg_level
		player_rank_data.avg_bp = avg_bp
		player_rank_data.update_time = current_ts
		player_rank_data.save()
		return api_response_result(request, ResultCode.SUCCESS, {})






@csrf_exempt
@log_request()
@parse_params(form=EmaBattleSetRankTeamSchema, method='POST', data_format='JSON', error_handler=api_response_error_params)
@pre_process_header()
@sign_in_required()
def set_rank_team(request, data):
	trainer_address = data["trainer_address"].lower()
	team = data["team"]

	# verify information
	if not Web3.isAddress(trainer_address):
		log.warn("invalid_address|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_address"})

	if team[0] == 0 or team[1] == 0 or team[2] == 0:
		log.warn("invalid_team|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_team"})

	team_details = [get_mon_info(mon_id) for mon_id in team]

	# Validate team
	is_valid, error = ema_battle_manager.is_valid_team(team_details, trainer_address)
	if not is_valid:
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": error})

	# Finish validation, start updating
	with transaction.atomic():
		avg_level = (team_details[0]["total_level"]+team_details[1]["total_level"]+team_details[2]["total_level"]) / 3
		avg_bp = (team_details[0]["total_bp"] + team_details[1]["total_bp"] + team_details[2]["total_bp"]) / 3
		current_ts = get_timestamp()

		player_rank_data = ema_player_manager.get_player_rank_by_address(trainer_address)
		if not player_rank_data:
			# Init rank data
			player_rank_data = EtheremonDB.EmaPlayerRankData(
				trainer=trainer_address,
				point=ema_player_manager.get_initial_elo_point(avg_bp),
				total_win=0,
				total_lose=0,
				total_claimed=0,
			)

			# Init energy record if not exist
			ema_energy_manager.initialize_energy_if_not_exist(trainer_address)

		else:
			# Consume energy
			ema_energy_manager.consume_energy(trainer_address, constants.RANK_CHANGE_TEAM_ENERGY_REQUIRE)

		# Update data
		player_rank_data.a0 = (team_details[0] or {}).get("monster_id", 0)
		player_rank_data.a1 = (team_details[1] or {}).get("monster_id", 0)
		player_rank_data.a2 = (team_details[2] or {}).get("monster_id", 0)
		player_rank_data.s0 = (team_details[3] or {}).get("monster_id", 0)
		player_rank_data.s1 = (team_details[4] or {}).get("monster_id", 0)
		player_rank_data.s2 = (team_details[5] or {}).get("monster_id", 0)
		player_rank_data.avg_level = avg_level
		player_rank_data.avg_bp = avg_bp
		player_rank_data.update_time = current_ts
		player_rank_data.save()

		return api_response_result(request, ResultCode.SUCCESS, {})


@csrf_exempt
@log_request()
@parse_params(form=EmaBattleAttackRankCastleSchema, method='POST', data_format='JSON', error_handler=api_response_error_params)
@pre_process_header()
@sign_in_required()
def attack_rank_castle(request, data):
	defender_player_id = data["defender_player_id"]
	attacker_player_id = data["attacker_player_id"]
	attack_count = data.get("attack_count", 1)




	# Case too many attacks
	if attack_count > 5:
		log.warn("invalid_attack_count|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS)

	# Case invalid defender
	if defender_player_id == attacker_player_id:
		log.error("self_attack|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS)

	# Case invalid defender
	if defender_player_id not in request.session.get(SessionKeys.RANK_OPPONENTS, []):
		log.error("invalid_defender|defender_player_id=%s,attacker_player_data=%s", defender_player_id, attacker_player_id)
		return api_response_result(request, ResultCode.ERROR_PARAMS)

	defender_player_data = get_player_rank_by_id(defender_player_id)
	attacker_player_data = get_player_rank_by_id(attacker_player_id)

	
	blocked = EtheremonDB.EmaBattleBlockedUsers.objects.filter(trainer=attacker_player_data.trainer).first()

	if blocked is not None :
		return api_response_result(request, ResultCode.ERROR_FORBIDDEN)

	# Case attacker hasn't logged in
	if attacker_player_data.trainer != request.session.get(SessionKeys.SIGNED_IN_ADDRESS, None):
		return api_response_result(request, ResultCode.ERROR_FORBIDDEN)

	# Case no player data
	if not defender_player_data or not attacker_player_data:
		log.error("invalid_player|defender_player_id=%s,attacker_player_data=%s", defender_player_id, attacker_player_id)
		return api_response_result(request, ResultCode.ERROR_SERVER)

	# Case invalid energy
	attacker_energy_available = get_available_energy(attacker_player_data.trainer)
	if attacker_energy_available < RANK_BATTLE_ENERGY_REQUIRE * attack_count:
		log.warn("invalid_energy|attacker=%s,attacker_energy=%s,defender=%s,attack_count=%s", attacker_player_data.trainer, attacker_energy_available, defender_player_data.trainer, attack_count)
		return api_response_result(request, ResultCode.ERROR_INVALID_ENERGY)

	for attack_index in range(0, attack_count):
		attacker_monsters = [
			get_mon_info(attacker_player_data.a0),
			get_mon_info(attacker_player_data.a1),
			get_mon_info(attacker_player_data.a2),
			get_mon_info(attacker_player_data.s0),
			get_mon_info(attacker_player_data.s1),
			get_mon_info(attacker_player_data.s2),
		]

		defender_monsters = [
			get_mon_info(defender_player_data.a0),
			get_mon_info(defender_player_data.a1),
			get_mon_info(defender_player_data.a2),
			get_mon_info(defender_player_data.s0),
			get_mon_info(defender_player_data.s1),
			get_mon_info(defender_player_data.s2),
		]

		# Validate teams
		if attack_index == 0:
			is_valid, err = ema_battle_manager.is_valid_team(attacker_monsters, attacker_player_data.trainer)
			if not is_valid:
				return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "attack_%s" % err})
			is_valid, err = ema_battle_manager.is_valid_team(defender_monsters, defender_player_data.trainer)
			if not is_valid:
				return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "attack_%s" % err})

		# generate random number
		random_factors = [randint(0, MAX_RANDOM_ROUND+2), randint(0, MAX_RANDOM_ROUND+2), randint(0, MAX_RANDOM_ROUND+2)]
		monster_data = {
			"attacker_monsters": attacker_monsters,
			"defender_monsters": defender_monsters,
			"random_factors": random_factors
		}
		monster_data_str = to_json(monster_data)
		result, battle_details = get_battle_details(defender_monsters, attacker_monsters, random_factors, True)

		monster_exp_list = [
			(attacker_player_data.a0, battle_details[0]["attacker_exp_gain"]),
			(attacker_player_data.a1, battle_details[1]["attacker_exp_gain"]),
			(attacker_player_data.a2, battle_details[2]["attacker_exp_gain"]),
			(defender_player_data.a0, battle_details[0]["castle_exp_gain"]),
			(defender_player_data.a1, battle_details[1]["castle_exp_gain"]),
			(defender_player_data.a2, battle_details[2]["castle_exp_gain"])
		]
		monster_exp_list.sort()

		# make db transaction to
		# 1. deduct energy
		# 2. update point
		# 3. update monster exp
		# 4. add battle details
		current_ts = get_timestamp()
		arank_before = cal_current_rank(attacker_player_data.point)
		drank_before = cal_current_rank(defender_player_data.point)
		with transaction.atomic():
			# update exp
			attacker_energy_record = EtheremonDB.EmaPlayerEnergyTab.objects.select_for_update().get(trainer=attacker_player_data.trainer)
			available_energy = attacker_energy_record.init_amount + attacker_energy_record.free_amount + attacker_energy_record.paid_amount - attacker_energy_record.consumed_amount - attacker_energy_record.invalid_amount
			if available_energy < RANK_BATTLE_ENERGY_REQUIRE:
				log.warn("invalid_energy|attacker=%s,attacker_energy=%s", attacker_player_data.trainer, available_energy)
				return api_response_result(request, ResultCode.ERROR_INVALID_ENERGY)
			attacker_energy_record.consumed_amount += RANK_BATTLE_ENERGY_REQUIRE
			attacker_energy_record.update_time = current_ts
			attacker_energy_record.save()

			# update rank data
			defender_rank_record = EtheremonDB.EmaPlayerRankData.objects.select_for_update().get(player_id=defender_player_id)
			attacker_rank_record = EtheremonDB.EmaPlayerRankData.objects.select_for_update().get(player_id=attacker_player_id)
			dpoint_before = defender_rank_record.point
			apoint_before = attacker_rank_record.point
			dpoint_after, apoint_after = _get_elo_change(dpoint_before, apoint_before, result)
			defender_rank_record.point = dpoint_after
			attacker_rank_record.point = apoint_after
			if result == BattleResult.CASTLE_WIN:
				defender_rank_record.total_win += 1
				attacker_rank_record.total_lose += 1
			else:
				defender_rank_record.total_lose += 1
				attacker_rank_record.total_win += 1
			defender_rank_record.update_time = current_ts
			attacker_rank_record.update_time = current_ts
			defender_rank_record.save()
			attacker_rank_record.save()

			# add exp
			for (monster_id, exp_gain) in monster_exp_list:
				# EtheremonDB.EmaMonsterExpTab.objects.filter(monster_id=monster_id).update(adding_exp=F('adding_exp')+exp_gain)
				ema_monster_manager.add_exp(monster_id, exp_gain)

			# add data
			battle_record = EtheremonDB.EmaRankBattleTab(
				attacker_id=attacker_player_id,
				defender_id=defender_player_id,
				attacker_before_point=apoint_before,
				attacker_after_point=apoint_after,
				defender_before_point=dpoint_before,
				defender_after_point=dpoint_after,
				result=result,
				monster_data=monster_data_str,
				status=0,
				exp_gain=json.dumps(monster_exp_list),
				create_time=current_ts,
				update_time=current_ts
			)
			battle_record.save()

		for (monster_id, exp_gain) in monster_exp_list:
			ema_monster_manager.calculate_ema_monster_exp(monster_id)

		# update player avg data
		calculate_avg_data(defender_player_id)
		calculate_avg_data(attacker_player_id)

		#log.data("attack_rank_castle|battle_id=%s", battle_record.id)

		arank_after = cal_current_rank(attacker_player_data.point)
		drank_after = cal_current_rank(defender_player_data.point)

		# battle update rank info
		monster_data["rank_data"] = {
			"attacker_before_rank": arank_after,
			"attacker_after_rank": arank_after,
			"defender_before_rank": drank_before,
			"defender_after_rank": drank_after
		}
		battle_record.monster_data = to_json(monster_data)
		battle_record.save()

		current_energy = attacker_energy_record.init_amount + attacker_energy_record.free_amount + attacker_energy_record.paid_amount - attacker_energy_record.consumed_amount - attacker_energy_record.invalid_amount

	response_data = {
		"battle_id": battle_record.id,
		"defender_address": defender_player_data.trainer,
		"defender_username": user_manager.get_user_name(defender_player_data.trainer),
		"attacker_address": attacker_player_data.trainer,
		"attacker_username": user_manager.get_user_name(attacker_player_data.trainer),
		"attacker_monsters": attacker_monsters,
		"defender_monsters": defender_monsters,
		"random_factors": random_factors,
		"details": battle_details,
		"result": result,
		"attacker_before_point": apoint_before,
		"attacker_after_point": apoint_after,
		"attacker_before_rank": arank_before,
		"attacker_after_rank": arank_after,
		"defender_before_point": dpoint_before,
		"defender_after_point": dpoint_after,
		"defender_before_rank": drank_before,
		"defender_after_rank": drank_after,
		"current_energy": current_energy
	}

	return api_response_result(request, ResultCode.SUCCESS, response_data)


@csrf_exempt
@log_request()
@parse_params(form=EmaBattleGetRankHistorySchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_rank_history(request, data):
	# verify information
	if not Web3.isAddress(data["trainer_address"]):
		log.warn("send_to_address_invalid|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invald_send_to_address"})

	trainer_address = data["trainer_address"].lower()
	response_data = []

	player_data = get_player_rank_by_address(trainer_address)
	if not player_data:
		return api_response_result(request, ResultCode.SUCCESS, response_data)

	battle_records = get_rank_battles(player_data.player_id)
	for battle_record in battle_records:
		defender_player_data = get_player_rank_by_id(battle_record.defender_id)
		attacker_player_data = get_player_rank_by_id(battle_record.attacker_id)
		monster_data = from_json(battle_record.monster_data)

		result, battle_details = get_battle_details(
			monster_data["defender_monsters"],
			monster_data["attacker_monsters"],
			monster_data["random_factors"],
			True
		)

		item = {
			"battle_id": battle_record.id,
			"defender_address": defender_player_data.trainer,
			"defender_username": user_manager.get_user_name(defender_player_data.trainer),
			"attacker_address": attacker_player_data.trainer,
			"attacker_username": user_manager.get_user_name(attacker_player_data.trainer),
			"attacker_monsters": monster_data["attacker_monsters"],
			"defender_monsters": monster_data["defender_monsters"],
			"random_factors": monster_data["random_factors"],
			"details": battle_details,
			"result": result,
			"attacker_before_point": battle_record.attacker_before_point,
			"attacker_after_point": battle_record.attacker_after_point,
			"defender_before_point": battle_record.defender_before_point,
			"defender_after_point": battle_record.defender_after_point,
		}

		if "rank_data" in monster_data:
			item["attacker_before_rank"] = monster_data["rank_data"]["attacker_before_rank"]
			item["attacker_after_rank"] = monster_data["rank_data"]["attacker_after_rank"]
			item["defender_before_rank"] = monster_data["rank_data"]["defender_before_rank"]
			item["defender_after_rank"] = monster_data["rank_data"]["defender_after_rank"]

		response_data.append(item)

	return api_response_result(request, ResultCode.SUCCESS, response_data)





@csrf_exempt
@log_request()
@parse_params(form=EmaBattleGetRankHistorySchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_rank_history_rkt(request, data):
	# verify information
	if not Web3.isAddress(data["trainer_address"]):
		log.warn("send_to_address_invalid|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invald_send_to_address"})

	trainer_address = data["trainer_address"].lower()
	response_data = []

	player_data = get_rkt_player_rank_by_address(trainer_address)
	if not player_data:
		return api_response_result(request, ResultCode.SUCCESS, response_data)

	battle_records = get_rank_battles_rkt(player_data.player_id)
	for battle_record in battle_records:
		defender_player_data = get_rkt_player_rank_by_id(battle_record.defender_id)
		attacker_player_data = get_rkt_player_rank_by_id(battle_record.attacker_id)
		monster_data = from_json(battle_record.monster_data)

		result, battle_details = get_battle_details(
			monster_data["defender_monsters"],
			monster_data["attacker_monsters"],
			monster_data["random_factors"],
			True
		)

		item = {
			"battle_id": battle_record.id,
			"defender_address": defender_player_data.trainer,
			"defender_username": user_manager.get_user_name(defender_player_data.trainer),
			"attacker_address": attacker_player_data.trainer,
			"attacker_username": user_manager.get_user_name(attacker_player_data.trainer),
			"attacker_monsters": monster_data["attacker_monsters"],
			"defender_monsters": monster_data["defender_monsters"],
			"random_factors": monster_data["random_factors"],
			"details": battle_details,
			"result": result,
			"attacker_before_point": battle_record.attacker_before_point,
			"attacker_after_point": battle_record.attacker_after_point,
			"defender_before_point": battle_record.defender_before_point,
			"defender_after_point": battle_record.defender_after_point,
		}

		if "rank_data" in monster_data:
			item["attacker_before_rank"] = monster_data["rank_data"]["attacker_before_rank"]
			item["attacker_after_rank"] = monster_data["rank_data"]["attacker_after_rank"]
			item["defender_before_rank"] = monster_data["rank_data"]["defender_before_rank"]
			item["defender_after_rank"] = monster_data["rank_data"]["defender_after_rank"]

		response_data.append(item)

	return api_response_result(request, ResultCode.SUCCESS, response_data)









@csrf_exempt
@log_request()
@parse_params(form=EmaBattleGetRankBattleSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_rank_battle(request, data):
	battle_id = data["battle_id"]
	battle_record = get_rank_battle_data(battle_id)
	if not battle_record:
		log.info("battle_id_invalid|battle_id=%s")
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid battle id"})

	defender_player_data = get_player_rank_by_id(battle_record.defender_id)
	attacker_player_data = get_player_rank_by_id(battle_record.attacker_id)
	monster_data = from_json(battle_record.monster_data)

	result, battle_details = get_battle_details(
		monster_data["defender_monsters"],
		monster_data["attacker_monsters"],
		monster_data["random_factors"],
		True
	)
	response_data = {
		"battle_id": battle_record.id,
		"defender_address": defender_player_data.trainer,
		"defender_username": user_manager.get_user_name(defender_player_data.trainer),
		"attacker_address": attacker_player_data.trainer,
		"attacker_username": user_manager.get_user_name(attacker_player_data.trainer),
		"attacker_monsters": monster_data["attacker_monsters"],
		"defender_monsters": monster_data["defender_monsters"],
		"random_factors": monster_data["random_factors"],
		"details": battle_details,
		"result": result,
		"attacker_before_point": battle_record.attacker_before_point,
		"attacker_after_point": battle_record.attacker_after_point,
		"defender_before_point": battle_record.defender_before_point,
		"defender_after_point": battle_record.defender_after_point,
	}

	if "rank_data" in monster_data:
		response_data["attacker_before_rank"] = monster_data["rank_data"]["attacker_before_rank"]
		response_data["attacker_after_rank"] = monster_data["rank_data"]["attacker_after_rank"]
		response_data["defender_before_rank"] = monster_data["rank_data"]["defender_before_rank"]
		response_data["defender_after_rank"] = monster_data["rank_data"]["defender_after_rank"]

	return api_response_result(request, ResultCode.SUCCESS, response_data)


@csrf_exempt
@log_request()
@parse_params(form=EmaBattleGetRankBattleSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_rank_battle_bp(request, data):
	battle_id = data["battle_id"]
	battle_record = get_rank_battle_data_bp(battle_id)
	if not battle_record:
		log.info("battle_id_invalid|battle_id=%s")
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid battle id"})

	defender_player_data = get_player_rank_by_id(battle_record.defender_id)
	attacker_player_data = get_player_rank_by_id(battle_record.attacker_id)
	monster_data = from_json(battle_record.monster_data)

	result, battle_details = get_battle_details(
		monster_data["defender_monsters"],
		monster_data["attacker_monsters"],
		monster_data["random_factors"],
		True
	)
	response_data = {
		"battle_id": battle_record.id,
		"defender_address": defender_player_data.trainer,
		"defender_username": user_manager.get_user_name(defender_player_data.trainer),
		"attacker_address": attacker_player_data.trainer,
		"attacker_username": user_manager.get_user_name(attacker_player_data.trainer),
		"attacker_monsters": monster_data["attacker_monsters"],
		"defender_monsters": monster_data["defender_monsters"],
		"random_factors": monster_data["random_factors"],
		"details": battle_details,
		"result": result,
		"attacker_before_point": battle_record.attacker_before_point,
		"attacker_after_point": battle_record.attacker_after_point,
		"defender_before_point": battle_record.defender_before_point,
		"defender_after_point": battle_record.defender_after_point,
	}

	if "rank_data" in monster_data:
		response_data["attacker_before_rank"] = monster_data["rank_data"]["attacker_before_rank"]
		response_data["attacker_after_rank"] = monster_data["rank_data"]["attacker_after_rank"]
		response_data["defender_before_rank"] = monster_data["rank_data"]["defender_before_rank"]
		response_data["defender_after_rank"] = monster_data["rank_data"]["defender_after_rank"]

	return api_response_result(request, ResultCode.SUCCESS, response_data)

@csrf_exempt
@log_request()
@parse_params(form=EmaBattleGetPracticeCastlesSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_practice_castles(request, data):
	# verify information
	if not Web3.isAddress(data["trainer_address"]):
		log.warn("send_to_address_invalid|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invald_send_to_address"})

	trainer_address = data["trainer_address"].lower()
	avg_level = data["avg_level"]
	player_data = get_player_rank_by_address(trainer_address)
	player_id = 0
	if player_data:
		player_id = player_data.player_id

	practice_records = get_practice_castles_by_level(player_id, avg_level)
	response_data = []
	for practice_record in practice_records:
		monster_info = [
			get_mon_info(practice_record.a0),
			get_mon_info(practice_record.a1),
			get_mon_info(practice_record.a2),
			get_mon_info(practice_record.s0),
			get_mon_info(practice_record.s1),
			get_mon_info(practice_record.s2),
		]
		avg_level = (monster_info[0]["level"] + monster_info[1]["level"] + monster_info[2]["level"]) / 3
		avg_bp = (monster_info[0]["bp"] + monster_info[1]["bp"] + monster_info[2]["bp"]) / 3

		defender_is_valid, err = ema_battle_manager.is_valid_team(monster_info, practice_record.trainer)
		if defender_is_valid:
			response_data.append({
				"player_id": practice_record.player_id,
				"address": practice_record.trainer,
				"username": user_manager.get_user_name(practice_record.trainer),
				"point": practice_record.point,
				"rank": cal_current_rank(practice_record.point),
				"monster_info": monster_info,
				"avg_level": avg_level,
				"avg_bp": avg_bp,
			})

	request.session[SessionKeys.PRACTICE_OPPONENTS] = [d["player_id"] for d in response_data]
	return api_response_result(request, ResultCode.SUCCESS, response_data)


@csrf_exempt
@log_request()
@parse_params(form=EmaBattleGetRankCastlesSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_rank_castles_rkt(request, data):
	# verify information
	if not Web3.isAddress(data["trainer_address"]):
		log.warn("send_to_address_invalid|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_send_to_address"})
	
	trainer_address = data["trainer_address"].lower()
	response_data = {
		"player_info": {
			"player_id": 0,
			"trainer_address": trainer_address,
			"username": user_manager.get_user_name(trainer_address),
			"current_rank": 0,
			"current_point": 0,
			"current_energy": 0,
			"monsters": []
		},
		"defender_list": []
	}

	player_data = get_rkt_player_rank_by_address(trainer_address)
	print player_data
	if not player_data:
		return api_response_result(request, ResultCode.SUCCESS, response_data)

	
	# populate player info
	response_data["player_info"]["player_id"] = player_data.player_id
	response_data["player_info"]["current_rank"] = cal_current_rank(player_data.point)
	response_data["player_info"]["current_point"] = player_data.point
	response_data["player_info"]["current_energy"] = get_available_energy(trainer_address)
	response_data["player_info"]["monsters"] = [
		get_mon_info(player_data.a0),
		get_mon_info(player_data.a1),
		get_mon_info(player_data.a2),
		get_mon_info(player_data.s0),
		get_mon_info(player_data.s1),
		get_mon_info(player_data.s2),
	]

	# populate defender list
	defender_record_list = get_defenders_by_point_rkt(player_data.point, player_data.player_id)
	for defender_record in defender_record_list:
		defender_username = user_manager.get_user_name(defender_record.trainer)
		monster_info = [
			get_mon_info(defender_record.a0),
			get_mon_info(defender_record.a1),
			get_mon_info(defender_record.a2),
			get_mon_info(defender_record.s0),
			get_mon_info(defender_record.s1),
			get_mon_info(defender_record.s2),
		]
		avg_level = (monster_info[0]["level"] + monster_info[1]["level"] + monster_info[2]["level"]) / 3
		avg_bp = (monster_info[0]["bp"] + monster_info[1]["bp"] + monster_info[2]["bp"]) / 3

		defender_is_valid, err = ema_battle_manager.is_valid_team(monster_info, defender_record.trainer)
		if defender_is_valid:
			response_data["defender_list"].append({
				"player_id": defender_record.player_id,
				"address": defender_record.trainer,
				"username": defender_username,
				"point": defender_record.point,
				"rank": cal_current_rank_rkt(defender_record.point),
				"monster_info": monster_info,
				"avg_level": avg_level,
				"avg_bp": avg_bp,
			})

	request.session[SessionKeys.RANK_OPPONENTS] = [d["player_id"] for d in response_data["defender_list"]]
	return api_response_result(request, ResultCode.SUCCESS, response_data)




@csrf_exempt
@log_request()
@parse_params(form=EmaBattleAttackRankCastleSchema, method='POST', data_format='JSON', error_handler=api_response_error_params)
@pre_process_header()
@sign_in_required()
def attack_rookie_tournament(request, data):
	defender_player_id = data["defender_player_id"]
	attacker_player_id = data["attacker_player_id"]
	attack_count = data.get("attack_count", 1)

	# Case too many attacks
	if attack_count > 5:
		logging.warn("invalid_attack_count|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS)

	# Case invalid defender
	if defender_player_id == attacker_player_id:
		logging.error("self_attack|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS)

	# Case invalid defender
	if defender_player_id not in request.session.get(SessionKeys.RANK_OPPONENTS, []):
		logging.error("invalid_defender|defender_player_id=%s,attacker_player_data=%s", defender_player_id, attacker_player_id)
		return api_response_result(request, ResultCode.ERROR_PARAMS)

	defender_player_data = get_rkt_player_rank_by_id(defender_player_id)
	attacker_player_data = get_rkt_player_rank_by_id(attacker_player_id)

	print (attacker_player_data.trainer)
	# Case attacker hasn't logged in
	if attacker_player_data.trainer != request.session.get(SessionKeys.SIGNED_IN_ADDRESS, None):
		return api_response_result(request, ResultCode.ERROR_FORBIDDEN)

	# Case no player data
	if not defender_player_data or not attacker_player_data:
		print("invalid_player|defender_player_id=%s,attacker_player_data=%s", defender_player_id, attacker_player_id)
		return api_response_result(request, ResultCode.ERROR_SERVER)


	# Case invalid energy
	attacker_energy_available = get_available_energy(attacker_player_data.trainer)
	if attacker_energy_available < RANK_BATTLE_ENERGY_REQUIRE * attack_count:
		logging.warn("invalid_energy|attacker=%s,attacker_energy=%s,defender=%s,attack_count=%s", attacker_player_data.trainer, attacker_energy_available, defender_player_data.trainer, attack_count)
		return api_response_result(request, ResultCode.ERROR_INVALID_ENERGY)


	for attack_index in range(0, attack_count):
		attacker_monsters = [
			get_mon_info(attacker_player_data.a0),
			get_mon_info(attacker_player_data.a1),
			get_mon_info(attacker_player_data.a2),
			get_mon_info(attacker_player_data.s0),
			get_mon_info(attacker_player_data.s1),
			get_mon_info(attacker_player_data.s2),
		]

		defender_monsters = [
			get_mon_info(defender_player_data.a0),
			get_mon_info(defender_player_data.a1),
			get_mon_info(defender_player_data.a2),
			get_mon_info(defender_player_data.s0),
			get_mon_info(defender_player_data.s1),
			get_mon_info(defender_player_data.s2),
		]

		# Validate teams
		if attack_index == 0:
			is_valid, err = ema_battle_manager.is_valid_team(attacker_monsters, attacker_player_data.trainer)
			if not is_valid:
				return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "attack_%s" % err})
			is_valid, err = ema_battle_manager.is_valid_team(defender_monsters, defender_player_data.trainer)
			if not is_valid:
				return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "attack_%s" % err})

		# generate random number
		random_factors = [randint(0, MAX_RANDOM_ROUND+2), randint(0, MAX_RANDOM_ROUND+2), randint(0, MAX_RANDOM_ROUND+2)]
		monster_data = {
			"attacker_monsters": attacker_monsters,
			"defender_monsters": defender_monsters,
			"random_factors": random_factors
		}
		monster_data_str = to_json(monster_data)
		result, battle_details = get_battle_details(defender_monsters, attacker_monsters, random_factors, True)

		monster_exp_list = [
			(attacker_player_data.a0, battle_details[0]["attacker_exp_gain"]),
			(attacker_player_data.a1, battle_details[1]["attacker_exp_gain"]),
			(attacker_player_data.a2, battle_details[2]["attacker_exp_gain"]),
			(defender_player_data.a0, battle_details[0]["castle_exp_gain"]),
			(defender_player_data.a1, battle_details[1]["castle_exp_gain"]),
			(defender_player_data.a2, battle_details[2]["castle_exp_gain"])
		]
		monster_exp_list.sort()

		# make db transaction to
		# 1. deduct energy
		# 2. update point
		# 3. update monster exp
		# 4. add battle details
		current_ts = get_timestamp()
		arank_before = cal_current_rank(attacker_player_data.point)
		drank_before = cal_current_rank(defender_player_data.point)
		with transaction.atomic():
			# update exp
			attacker_energy_record = EtheremonDB.EmaPlayerEnergyTab.objects.select_for_update().get(trainer=attacker_player_data.trainer)
			available_energy = attacker_energy_record.init_amount + attacker_energy_record.free_amount + attacker_energy_record.paid_amount - attacker_energy_record.consumed_amount - attacker_energy_record.invalid_amount
			if available_energy < RANK_BATTLE_ENERGY_REQUIRE:
				logging.warn("invalid_energy|attacker=%s,attacker_energy=%s", attacker_player_data.trainer, available_energy)
				return api_response_result(request, ResultCode.ERROR_INVALID_ENERGY)
			attacker_energy_record.consumed_amount += RANK_BATTLE_ENERGY_REQUIRE
			attacker_energy_record.update_time = current_ts
			attacker_energy_record.save()
			# update rank data
			defender_rank_record = EtheremonDB.EmaPlayerRankRKTData.objects.select_for_update().get(player_id=defender_player_id)
			attacker_rank_record = EtheremonDB.EmaPlayerRankRKTData.objects.select_for_update().get(player_id=attacker_player_id)
			dpoint_before = defender_rank_record.point
			apoint_before = attacker_rank_record.point
			dpoint_after, apoint_after = _get_elo_change(dpoint_before, apoint_before, result)
			defender_rank_record.point = dpoint_after
			attacker_rank_record.point = apoint_after
			if result == BattleResult.CASTLE_WIN:
				defender_rank_record.total_win += 1
				attacker_rank_record.total_lose += 1
			else:
				defender_rank_record.total_lose += 1
				attacker_rank_record.total_win += 1
			defender_rank_record.update_time = current_ts
			attacker_rank_record.update_time = current_ts
			defender_rank_record.save()
			attacker_rank_record.save()

			# add exp
			for (monster_id, exp_gain) in monster_exp_list:
				# EtheremonDB.EmaMonsterExpTab.objects.filter(monster_id=monster_id).update(adding_exp=F('adding_exp')+exp_gain)
				ema_monster_manager.add_exp(monster_id, exp_gain)


			battle_record = EtheremonDB.EmaRankBattleRKTTab(
				attacker_id=attacker_player_id,
				defender_id=defender_player_id,
				attacker_before_point=apoint_before,
				attacker_after_point=apoint_after,
				defender_before_point=dpoint_before,
				defender_after_point=dpoint_after,
				result=result,
				monster_data=monster_data_str,
				status=0,
				exp_gain=json.dumps(monster_exp_list),
				create_time=current_ts,
				update_time=current_ts
			)
			battle_record.save()

		for (monster_id, exp_gain) in monster_exp_list:
			#update exp and rkt_exp as well
			ema_monster_manager.calculate_ema_monster_exp(monster_id)

		# update player avg data
		calculate_avg_data(defender_player_id)
		calculate_avg_data(attacker_player_id)

		print ("attack_rank_castle|battle_id=%s", battle_record.id)
		#logging.data("attack_rank_castle|battle_id=%s", battle_record.id)

		arank_after = cal_current_rank(attacker_player_data.point)
		drank_after = cal_current_rank(defender_player_data.point)

		# battle update rank info
		monster_data["rank_data"] = {
			"attacker_before_rank": arank_before,
			"attacker_after_rank": arank_after,
			"defender_before_rank": drank_before,
			"defender_after_rank": drank_after
		}
		battle_record.monster_data = to_json(monster_data)
		battle_record.save()

		current_energy = attacker_energy_record.init_amount + attacker_energy_record.free_amount + attacker_energy_record.paid_amount - attacker_energy_record.consumed_amount - attacker_energy_record.invalid_amount

	response_data = {
		"battle_id": battle_record.id,
		"defender_address": defender_player_data.trainer,
		"defender_username": user_manager.get_user_name(defender_player_data.trainer),
		"attacker_address": attacker_player_data.trainer,
		"attacker_username": user_manager.get_user_name(attacker_player_data.trainer),
		"attacker_monsters": attacker_monsters,
		"defender_monsters": defender_monsters,
		"random_factors": random_factors,
		"details": battle_details,
		"result": result,
		"attacker_before_point": apoint_before,
		"attacker_after_point": apoint_after,
		"attacker_before_rank": arank_before,
		"attacker_after_rank": arank_after,
		"defender_before_point": dpoint_before,
		"defender_after_point": dpoint_after,
		"defender_before_rank": drank_before,
		"defender_after_rank": drank_after,
		
		"current_energy": current_energy
	}

	return api_response_result(request, ResultCode.SUCCESS, response_data)
	

@csrf_exempt
@log_request()
@parse_params(form=EmaBattleAttackPracticeCastleSchema, method='POST', data_format='JSON', error_handler=api_response_error_params)
@pre_process_header()
@sign_in_required()
def attack_practice_castle(request, data):
	# verify information
	if not Web3.isAddress(data["trainer_address"]):
		log.warn("send_to_address_invalid|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_send_to_address"})

	trainer_address = data["trainer_address"].lower()

	# Case Invalid Defender 1
	defender_id = data["defender_player_id"]
	defender_player_data = get_player_rank_by_id(defender_id)
	if not defender_player_data:
		log.warn("invalid_defender_id|defender_id=%s", defender_id)
		return api_response_result(request, ResultCode.ERROR_PARAMS)

	# Case invalid defender 2
	if defender_id not in request.session.get(SessionKeys.PRACTICE_OPPONENTS, []):
		log.error("invalid_defender|defender_player_id=%s,attacker=%s", defender_id, trainer_address)
		return api_response_result(request, ResultCode.ERROR_PARAMS)

	# Case Invalid Attack Count
	attack_count = data.get("attack_count", 1)
	if attack_count > 10:
		log.warn("invalid_attack_count|data=%s")
		return api_response_result(request, ResultCode.ERROR_PARAMS)

	# Case invalid Energy
	attacker_energy_available = get_available_energy(trainer_address)
	if attacker_energy_available < RANK_PRACTICE_ENERGY_REQUIRE * attack_count:
		log.warn("invalid_energy|attacker=%s,attacker_energy=%s,defender=%s,attack_count=%s", trainer_address, attacker_energy_available, defender_player_data.trainer, attack_count)
		return api_response_result(request, ResultCode.ERROR_INVALID_ENERGY)

	# Case wrong team
	monster_non_0 = [monster_id for monster_id in data["monster_ids"] if monster_id > 0]
	if len(set(monster_non_0)) != len(monster_non_0):
		log.warn("duplicate_monster_id|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "duplicate_monster_id"})

	for attack_index in range(0, attack_count):

		attacker_monsters = [
			get_mon_info(data["monster_ids"][0]),
			get_mon_info(data["monster_ids"][1]),
			get_mon_info(data["monster_ids"][2]),
			get_mon_info(data["monster_ids"][3]),
			get_mon_info(data["monster_ids"][4]),
			get_mon_info(data["monster_ids"][5]),
		]

		defender_monsters = [
			get_mon_info(defender_player_data.a0),
			get_mon_info(defender_player_data.a1),
			get_mon_info(defender_player_data.a2),
			get_mon_info(defender_player_data.s0),
			get_mon_info(defender_player_data.s1),
			get_mon_info(defender_player_data.s2),
		]

		# verify level of attacker
		if attacker_monsters[0]["level"] > 20 or attacker_monsters[1]["level"] > 20 or attacker_monsters[2]["level"] > 20:
			log.warn("attacker_monster_level_too_high|attacker_monsters=%s,data=%s", attacker_monsters, data)
			return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "The level of monsters are higher than 20!!"})

		# Validate teams
		if attack_index == 0:
			is_valid, err = ema_battle_manager.is_valid_team(attacker_monsters, trainer_address)
			if not is_valid:
				return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "attack_%s" % err})
			is_valid, err = ema_battle_manager.is_valid_team(defender_monsters, defender_player_data.trainer)
			if not is_valid:
				return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "attack_%s" % err})

		# generate random number
		random_factors = [randint(0, MAX_RANDOM_ROUND+2), randint(0, MAX_RANDOM_ROUND+2), randint(0, MAX_RANDOM_ROUND+2)]
		monster_data = {
			"attacker_monsters": attacker_monsters,
			"defender_monsters": defender_monsters,
			"random_factors": random_factors
		}
		monster_data_str = to_json(monster_data)
		result, battle_details = get_battle_details(defender_monsters, attacker_monsters, random_factors, True)

		monster_exp_list = [
			(data["monster_ids"][0], battle_details[0]["attacker_exp_gain"]),
			(data["monster_ids"][1], battle_details[1]["attacker_exp_gain"]),
			(data["monster_ids"][2], battle_details[2]["attacker_exp_gain"]),
		]

		monster_exp_list.sort()

		# make db transaction to
		# 1. deduct energy
		# 2. update point
		# 3. update monster exp
		# 4. add battle details
		current_ts = get_timestamp()
		with transaction.atomic():
			# update exp
			attacker_energy_record = EtheremonDB.EmaPlayerEnergyTab.objects.select_for_update().get(trainer=trainer_address)
			available_energy = attacker_energy_record.init_amount + attacker_energy_record.free_amount + attacker_energy_record.paid_amount - attacker_energy_record.consumed_amount - attacker_energy_record.invalid_amount
			if available_energy < RANK_BATTLE_ENERGY_REQUIRE:
				log.warn("invalid_energy|attacker=%s,attacker_energy=%", trainer_address, available_energy)
				return api_response_result(request, ResultCode.ERROR_INVALID_ENERGY)
			attacker_energy_record.consumed_amount += RANK_PRACTICE_ENERGY_REQUIRE
			attacker_energy_record.update_time = current_ts
			attacker_energy_record.save()

			# add exp
			for (monster_id, exp_gain) in monster_exp_list:
				# EtheremonDB.EmaMonsterExpTab.objects.filter(monster_id=monster_id).update(adding_exp=F('adding_exp')+exp_gain)
				ema_monster_manager.add_exp(monster_id, exp_gain)

			# add data
			battle_record = EtheremonDB.EmaPracticeBattleTab(
				trainer=trainer_address,
				defender_id=defender_id,
				result=result,
				monster_data=monster_data_str,
				status=0,
				create_time=current_ts,
				update_time=current_ts
			)
			battle_record.save()

		for (monster_id, exp_gain) in monster_exp_list:
			ema_monster_manager.calculate_ema_monster_exp(monster_id)

		# update player avg data
		calculate_avg_data_by_address(trainer_address)

		log.data("attack_practice_castle|battle_id=%s", battle_record.id)

		current_energy = attacker_energy_record.init_amount + attacker_energy_record.free_amount + attacker_energy_record.paid_amount - attacker_energy_record.consumed_amount - attacker_energy_record.invalid_amount

	response_data = {
		"battle_id": battle_record.id,
		"defender_address": defender_player_data.trainer,
		"defender_username": user_manager.get_user_name(defender_player_data.trainer),
		"attacker_address": trainer_address,
		"attacker_username": user_manager.get_user_name(trainer_address),
		"attacker_monsters": attacker_monsters,
		"defender_monsters": defender_monsters,
		"random_factors": random_factors,
		"details": battle_details,
		"result": result,
		"current_energy": current_energy
	}

	return api_response_result(request, ResultCode.SUCCESS, response_data)


@csrf_exempt
@log_request()
@parse_params(form=EmaBattleGetPracticeHistorySchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_practice_history(request, data):
	# verify information
	if not Web3.isAddress(data["trainer_address"]):
		log.warn("send_to_address_invalid|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invald_send_to_address"})

	trainer_address = data["trainer_address"].lower()
	response_data = []

	battle_records = get_practice_battles(trainer_address)
	for battle_record in battle_records:
		defender_player_data = get_player_rank_by_id(battle_record.defender_id)
		monster_data = from_json(battle_record.monster_data)

		result, battle_details = get_battle_details(
			monster_data["defender_monsters"],
			monster_data["attacker_monsters"],
			monster_data["random_factors"],
			True
		)
		response_data.append({
			"battle_id": battle_record.id,
			"defender_address": defender_player_data.trainer,
			"defender_username": user_manager.get_user_name(defender_player_data.trainer),
			"attacker_address": trainer_address,
			"attacker_username": user_manager.get_user_name(trainer_address),
			"attacker_monsters": monster_data["attacker_monsters"],
			"defender_monsters": monster_data["defender_monsters"],
			"random_factors": monster_data["random_factors"],
			"details": battle_details,
			"result": result,
		})

	return api_response_result(request, ResultCode.SUCCESS, response_data)


@csrf_exempt
@log_request()
@parse_params(form=EmaBattleClaimMonsterExpSchema, method='POST', data_format='JSON', error_handler=api_response_error_params)
@pre_process_header()
def claim_monster_exp(request, data):
	monster_id = data["monster_id"]
	if ema_monster_manager.get_pending_exp_amount(monster_id) < 1:
		log.warn("no_pending_exp|monster_id=%s", monster_id)
		return api_response_result(request, ResultCode.ERROR_PARAMS)

	pending_claim = ema_claim_manager.get_pending_exp_claim(monster_id)

	if not pending_claim:
		pending_claim = ema_claim_manager.add_pending_exp_claim(monster_id)

	if pending_claim.exp == 0:
		log.warn("monster_no_pending_exp|monster_id=%s", monster_id)
		return api_response_result(request, ResultCode.ERROR_PARAMS)

	# create token
	nonce1 = randint(0, 429496729)
	nonce2 = randint(0, 429496729)
	claim_exp_token = create_claim_exp_token(pending_claim.id, monster_id, pending_claim.exp, nonce1, nonce2)
	r, s, v = sign_single_token(claim_exp_token)
	response_data = {"token": "0x" + claim_exp_token, "r": r, "s": s, "v": v}

	return api_response_result(request, ResultCode.SUCCESS, response_data)
