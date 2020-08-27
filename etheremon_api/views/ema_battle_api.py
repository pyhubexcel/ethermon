from django.views.decorators.csrf import csrf_exempt
from common.utils import parse_params, log_request
from etheremon_lib.burn_manager import BURN_MON_REWARDS, BurnStatus
from etheremon_lib.decorators.auth_decorators import sign_in_required
from etheremon_lib.form_schema import *
from etheremon_lib.preprocessor import pre_process_header
from etheremon_lib.ema_claim_manager import get_pending_exp_claim
from etheremon_lib import ema_market_manager
from etheremon_api.views.helper import *
from etheremon_lib.models import EtheremonDB


@csrf_exempt
@log_request()
@parse_params(form=AllEmaBattlesGetDataSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_all_battle(request, data):
	page_id = data["page_id"]
	page_size = 30
	start_index = (page_id - 1) * page_size
	response_data = {}

	battles = EtheremonDB.EmaRankBattleTab.objects.all().order_by("id")[start_index:start_index+page_size]

	for battle in battles:


		response_data[battle.id] = {

			"attacker_id": battle.attacker_id,
			"defender_id": battle.defender_id,
			"attacker_before_point": battle.attacker_before_point,
			"attacker_after_point": battle.attacker_after_point,
			"defender_before_point": battle.defender_before_point,
			"defender_after_point": battle.defender_after_point,
			"result": battle.result,
			"monster_data": battle.monster_data,
			"exp_gain": battle.exp_gain,
			"status": battle.status,
			"create_time": battle.create_time,
			"update_time": battle.update_time,
			
		}
	return api_response_result(request, ResultCode.SUCCESS, response_data)


@csrf_exempt
@log_request()
@parse_params(form=EmaBattleGetDataSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_battle(request, data):
	try:
		id = data['id']
		# verify trainer address
	

		response_data = {}


		battle = EtheremonDB.EmaRankBattleTab.objects.filter(id=id).first()

		return api_response_result(request, ResultCode.SUCCESS, {
			"id": battle.id,
			"attacker_id": battle.attacker_id,
			"defender_id": battle.defender_id,
			"attacker_before_point": battle.attacker_before_point,
			"attacker_after_point": battle.attacker_after_point,
			"defender_before_point": battle.defender_before_point,
			"defender_after_point": battle.defender_after_point,
			"result": battle.result,
			"monster_data": battle.monster_data,
			"exp_gain": battle.exp_gain,
			"status": battle.status,
			"create_time": battle.create_time,
			"update_time": battle.update_time,
			
		})
	except Exception as ex:
			return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": ex.message})




@csrf_exempt
@log_request()
@parse_params(form=AllPlayersRankGetDataSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_all_rank_data(request, data):
	page_id = data["page_id"]
	page_size = 30
	start_index = (page_id - 1) * page_size
	response_data = {}

	players = EtheremonDB.EmaPlayerRankData.objects.all().order_by("player_id")[start_index:start_index+page_size]

	for player in players:


		response_data[battle.player_id] = {
			"trainer": battle.trainer,
			"point": battle.point,
			"total_win": battle.total_win,
			"total_lose": battle.total_lose,
			"total_claimed": battle.total_claimed,
			"a0": battle.a0,
			"a1": battle.a1,
			"a2": battle.a2,
			"s0": battle.s0,
			"s1": battle.s1,
			"s2": battle.s2,
			"avg_bp": battle.avg_bp,
			"avg_level": battle.avg_level,
			"update_time": battle.update_time
			
		}
	return api_response_result(request, ResultCode.SUCCESS, response_data)


@csrf_exempt
@log_request()
@parse_params(form=PlayerRankGetDataSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_rank_data(request, data):
	try:
		trainer = data['trainer_address'].lower()
		# verify trainer address
		if not Web3.isAddress(trainer):
			return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_send_to_address"})


		response_data = {}


		player = EtheremonDB.EmaPlayerRankData.objects.filter(trainer=trainer).first()

		return api_response_result(request, ResultCode.SUCCESS, {

			"player_id": battle.player_id,
			"trainer": battle.trainer,
			"point": battle.point,
			"total_win": battle.total_win,
			"total_lose": battle.total_lose,
			"total_claimed": battle.total_claimed,
			"a0": battle.a0,
			"a1": battle.a1,
			"a2": battle.a2,
			"s0": battle.s0,
			"s1": battle.s1,
			"s2": battle.s2,
			"avg_bp": battle.avg_bp,
			"avg_level": battle.avg_level,
			"update_time": battle.update_time
			
		})
	except Exception as ex:
			return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": ex.message})
