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
@parse_params(form=AllPlayersEnergyGetDataSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_all_energy(request, data):
	page_id = data["page_id"]
	page_size = 30
	start_index = (page_id - 1) * page_size
	response_data = {}

	players = EtheremonDB.EmaPlayerEnergyTab.objects.all().order_by("id")[start_index:start_index+page_size]

	for player in players:


		response_data[player.id] = {
			"trainer": player.trainer,
			"init_amount": player.init_amount,
			"free_amount": player.free_amount,
			"paid_amount": player.paid_amount,
			"invalid_amount": player.invalid_amount,
			"consumed_amount": player.consumed_amount,
			"last_claim_time": player.last_claim_time,
			"create_time": player.create_time,
			"update_time": player.update_time,
			
		}
	return api_response_result(request, ResultCode.SUCCESS, response_data)


@csrf_exempt
@log_request()
@parse_params(form=PlayerEnergyGetDataSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_energy(request, data):
	try:
		trainer = data['trainer_address'].lower()
		# verify trainer address
		if not Web3.isAddress(trainer):
			return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_send_to_address"})


		response_data = {}


		player = EtheremonDB.EmaPlayerEnergyTab.objects.filter(trainer=trainer).first()

		return api_response_result(request, ResultCode.SUCCESS, {
			"id": player.id,
			"trainer": player.trainer,
			"init_amount": player.init_amount,
			"free_amount": player.free_amount,
			"paid_amount": player.paid_amount,
			"invalid_amount": player.invalid_amount,
			"consumed_amount": player.consumed_amount,
			"last_claim_time": player.last_claim_time,
			"create_time": player.create_time,
			"update_time": player.update_time,
			
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


		response_data[player.player_id] = {
			"trainer": player.trainer,
			"point": player.point,
			"total_win": player.total_win,
			"total_lose": player.total_lose,
			"total_claimed": player.total_claimed,
			"a0": player.a0,
			"a1": player.a1,
			"a2": player.a2,
			"s0": player.s0,
			"s1": player.s1,
			"s2": player.s2,
			"avg_bp": player.avg_bp,
			"avg_level": player.avg_level,
			"update_time": player.update_time
			
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

			"player_id": player.player_id,
			"trainer": player.trainer,
			"point": player.point,
			"total_win": player.total_win,
			"total_lose": player.total_lose,
			"total_claimed": player.total_claimed,
			"a0": player.a0,
			"a1": player.a1,
			"a2": player.a2,
			"s0": player.s0,
			"s1": player.s1,
			"s2": player.s2,
			"avg_bp": player.avg_bp,
			"avg_level": player.avg_level,
			"update_time": player.update_time
			
		})
	except Exception as ex:
			return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": ex.message})
