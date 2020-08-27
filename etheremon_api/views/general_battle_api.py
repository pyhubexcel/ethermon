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
from etheremon_lib import ema_monster_manager, ema_energy_manager, constants, ema_player_manager, ema_battle_manager, \
	general_battle_manager
from etheremon_lib import user_manager
from etheremon_lib import ema_claim_manager
from etheremon_lib.crypt import *
from etheremon_lib.constants import *
from etheremon_lib.ema_monster_manager import get_mon_info
from etheremon_api.views.helper import get_battle_details
from web3 import Web3
from etheremon_lib.infura_client import InfuraClient
import logging

@csrf_exempt
@log_request()
@parse_params(form=EmaBattleGetRankBattleSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_battle_info(request, data):
	battle_id = data["battle_id"]
	battle_record = general_battle_manager.get_battle_record(battle_id)

	if not battle_record:
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid battle id"})

	defender_player_data = user_manager.get_user_info(battle_record.defender_address)
	attacker_player_data = user_manager.get_user_info(battle_record.attacker_address)
	monster_data = from_json(battle_record.monster_data)

	result, battle_details = get_battle_details(
		monster_data["defender_monsters"],
		monster_data["attacker_monsters"],
		monster_data["random_factors"],
		True
	)
	response_data = {
		"battle_id": battle_record.id,
		"defender_address": defender_player_data.address,
		"defender_username": defender_player_data.username,
		"attacker_address": attacker_player_data.address,
		"attacker_username": attacker_player_data.username,
		"attacker_monsters": monster_data["attacker_monsters"],
		"defender_monsters": monster_data["defender_monsters"],
		"random_factors": monster_data["random_factors"],
		"details": battle_details,
		"result": result,
	}

	return api_response_result(request, ResultCode.SUCCESS, response_data)
