# coding=utf-8
from django.views.decorators.csrf import csrf_exempt
from common.utils import parse_params, log_request
from etheremon_lib.form_schema import *
from etheremon_lib.preprocessor import pre_process_header
from etheremon_lib import user_manager, quest_manager, quest_config, ema_energy_manager, emont_bonus_manager, \
	cache_manager, user_balance_manager
from etheremon_lib.quest_config import QUEST_LIST, QuestTypes
from etheremon_lib.user_balance_manager import BalanceTypes
from etheremon_api.views.helper import *


@csrf_exempt
@log_request()
@parse_params(form=QuestGetPlayerQuestsSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_player_quests(request, data):
	player_address = data['trainer_address'].lower()

	# verify trainer address
	if not Web3.isAddress(player_address):
		log.warn("send_to_address_invalid|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_send_to_address"})

	# verify quest type
	if data['quest_type'] not in quest_config.QuestTypes.TYPE_LIST:
		log.warn("invalid_quest_type|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_quest_type"})

	player_uid = user_manager.get_uid_by_address(player_address)
	if player_uid == '':
		# Case user hasn't registered
		return api_response_result(request, ResultCode.SUCCESS, {'quests': [], 'emont_balance': 0, 'energy_balance': 0})

	try:
		# quests = cache_manager.get_player_quests(player_uid, data['quest_type'])
		# if quests is None:
		# 	_quests = quest_manager.get_player_quests(player_uid, player_address, data['quest_type']).values()
		# 	quests = {}
		# 	for quest in _quests:
		# 		quests[quest.id] = {
		# 			"id": quest.id,
		# 			"player_address": quest.player_address,
		# 			"player_uid": quest.player_uid,
		# 			"quest_id": quest.quest_id,
		# 			"quest_type": quest.quest_type,
		# 			"quest_level": quest.quest_level,
		# 			"total_level": len(QUEST_LIST[quest.quest_id]["quest_target"]),
		# 			"quest_name": quest.quest_name,
		# 			"quest_target": quest.quest_target,
		# 			"quest_progress": quest.quest_progress,
		# 			"reward_type": quest.reward_type,
		# 			"reward_value": quest.reward_value,
		# 			"status": quest.status,
		# 			"extra_info": json.loads(quest.extra or "{}")
		# 		}
		# 	cache_manager.set_player_quests(player_uid, data['quest_type'], json.dumps(quests))
		# else:
		# 	quests = json.loads(quests)
		_quests = quest_manager.get_player_quests(player_uid, player_address, data['quest_type']).values()
		quests = {}
		for quest in _quests:
			quests[quest.id] = {
				"id": quest.id,
				"player_address": quest.player_address,
				"player_uid": quest.player_uid,
				"quest_id": quest.quest_id,
				"quest_type": quest.quest_type,
				"quest_level": quest.quest_level,
				"total_level": len(QUEST_LIST[quest.quest_id]["quest_target"]),
				"quest_name": quest.quest_name,
				"quest_target": quest.quest_target,
				"quest_progress": quest.quest_progress,
				"reward_type": quest.reward_type,
				"reward_value": quest.reward_value,
				"status": quest.status,
				"extra_info": json.loads(quest.extra or "{}")
			}

		return api_response_result(request, ResultCode.SUCCESS, {
			"quests": quests,
			"emont_balance": emont_bonus_manager.get_emont_balance(player_uid),
			"energy_balance": ema_energy_manager.get_available_energy(player_address),
			# "hongbao_balance": user_balance_manager.get_balance(player_uid, BalanceTypes.HONGBAO)
		})

	except Exception as ex:
		logging.exception("get_player_quests_fail|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": str(ex)})


@csrf_exempt
@log_request()
@parse_params(form=QuestClaimQuestSchema, method='POST', data_format='JSON', error_handler=api_response_error_params)
@pre_process_header()
def claim_player_quest(request, data):
	player_address = data['trainer_address'].lower()
	quest_id = data['quest_id']

	# verify trainer address
	if not Web3.isAddress(player_address):
		log.warn("send_to_address_invalid|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_send_to_address"})

	player_uid = user_manager.get_uid_by_address(player_address)
	if player_uid == '':
		# Case user hasn't registered
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "unregistered_user"})

	try:
		quest = quest_manager.get_player_quest(player_uid, quest_id)
		if quest is None or quest.status != quest_config.QuestStatus.TO_CLAIM:
			return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_quest"})

		# Claim quest
		quest = quest_manager.claim_quest(quest)

		# Remove cache
		cache_manager.delete_player_quests(player_uid, QuestTypes.ALL_TYPES)

		return api_response_result(request, ResultCode.SUCCESS, {
			"quest": {
				"id": quest.id,
				"player_address": quest.player_address,
				"player_uid": quest.player_uid,
				"quest_id": quest.quest_id,
				"quest_type": quest.quest_type,
				"quest_level": quest.quest_level,
				"total_level": len(QUEST_LIST[quest.quest_id]["quest_target"]),
				"quest_name": quest.quest_name,
				"quest_target": quest.quest_target,
				"quest_progress": quest.quest_progress,
				"reward_type": quest.reward_type,
				"reward_value": quest.reward_value,
				"status": quest.status,
				"extra_info": json.loads(quest.extra or "{}")
			},
			"emont_balance": emont_bonus_manager.get_emont_balance(player_uid),
			"energy_balance": ema_energy_manager.get_available_energy(player_address),
			# "hongbao_balance": user_balance_manager.get_balance(player_uid, BalanceTypes.HONGBAO)
		})

	except Exception as ex:
		logging.exception("claim_quest_fail|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": str(ex)})


@csrf_exempt
@log_request()
@parse_params(form=QuestClaimAllSchema, method='POST', data_format='JSON', error_handler=api_response_error_params)
@pre_process_header()
def claim_all_player_quests(request, data):
	player_address = data['trainer_address'].lower()

	# verify trainer address
	if not Web3.isAddress(player_address):
		log.warn("send_to_address_invalid|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_send_to_address"})

	player_uid = user_manager.get_uid_by_address(player_address)
	if player_uid == '':
		# Case user hasn't registered
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "unregistered_user"})

	try:
		updated_quests = {}

		quests = quest_manager.get_player_to_claim_quests(player_uid)
		for quest in quests:
			updated_quest = quest_manager.claim_quest(quest)
			if updated_quest:
				updated_quests[updated_quest.id] = {
					"id": updated_quest.id,
					"player_address": updated_quest.player_address,
					"player_uid": updated_quest.player_uid,
					"quest_id": updated_quest.quest_id,
					"quest_type": updated_quest.quest_type,
					"quest_level": updated_quest.quest_level,
					"total_level": len(QUEST_LIST[quest.quest_id]["quest_target"]),
					"quest_name": updated_quest.quest_name,
					"quest_target": updated_quest.quest_target,
					"quest_progress": updated_quest.quest_progress,
					"reward_type": updated_quest.reward_type,
					"reward_value": updated_quest.reward_value,
					"status": updated_quest.status,
					"extra_info": json.loads(updated_quest.extra or "{}")
				}

		# Remove cache
		cache_manager.delete_player_quests(player_uid, QuestTypes.ALL_TYPES)

		return api_response_result(request, ResultCode.SUCCESS, {
			"quests": updated_quests,
			"emont_balance": emont_bonus_manager.get_emont_balance(player_uid),
			"energy_balance": ema_energy_manager.get_available_energy(player_address),
			# "hongbao_balance": user_balance_manager.get_balance(player_uid, BalanceTypes.HONGBAO)
		})

	except Exception as ex:
		logging.exception("claim_quest_fail|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": str(ex)})

