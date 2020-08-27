from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from common.utils import parse_params, log_request
from etheremon_lib.decorators.auth_decorators import sign_in_required
from etheremon_lib.ema_monster_manager import get_mon_info
from etheremon_lib.form_schema import *
from etheremon_lib import user_manager, tournament_manager, ema_battle_manager, emont_bonus_manager
from etheremon_lib.preprocessor import pre_process_header
from etheremon_lib.tournament_manager import TournamentTypes, TournamentStatus, TournamentRewards
from etheremon_api.views.helper import *


TOURNAMENT_FEE_EMONT = 0


@csrf_exempt
@log_request()
@parse_params(form=TournamentGetInfoSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_tournament_info(request, data):
	trainer_address = data.get("trainer_address", "0x").lower()

	response_data = {
		"extra": {
			"fee_emont": TOURNAMENT_FEE_EMONT,
			"reward_list": {
				"mon": TournamentRewards.MONS,
				"token": TournamentRewards.TOKENS,
			}
		}
	}

	if Web3.isAddress(trainer_address):
		player_info = user_manager.get_user_general_info(address=trainer_address)
		response_data["personal_data"] = {
			"tournament_win": player_info.tournament_win or 0,
			"tournament_loss": player_info.tournament_loss or 0
		}

	if data.get("tournament_id", 0):
		response_data["requested_tournament"] = tournament_manager.get_tournament_info(data["tournament_id"], None)
	else:

		for typ in [TournamentTypes.BEGINNER, TournamentTypes.ROOKIE]:
			tournament = tournament_manager.get_newest_tournament(typ)
			if tournament:
				response_data[typ] = tournament_manager.get_tournament_info(None, tournament)

	return api_response_result(request, ResultCode.SUCCESS, response_data)


@csrf_exempt
@log_request()
@parse_params(form=TournamentRegisterTeamSchema, method='POST', data_format='JSON', error_handler=api_response_error_params)
@pre_process_header()
@sign_in_required()
def register_team(request, data):
	trainer_address = data["trainer_address"].lower()
	tournament_id = data["tournament_id"]
	team = data["team"]

	# verify information
	if not Web3.isAddress(trainer_address):
		log.warn("invalid_address|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_address"})

	if team[0] == 0 or team[1] == 0 or team[2] == 0:
		log.warn("invalid_team|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_attackers"})

	tournament = tournament_manager.get_tournament_by_id(tournament_id)
	if not tournament:
		log.warn("invalid_tournament|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_tournament_id"})

	if tournament.start_time < get_timestamp() or tournament.status != TournamentStatus.REGISTRATION:
		log.warn("invalid_tournament|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "tournament_not_for_registration"})

	team_details = [get_mon_info(mon_id) for mon_id in team]
	for mon in team_details[:3]:
		if not tournament.mon_level_min <= mon["total_level"] <= tournament.mon_level_max:
			log.warn("invalid_team|data=%s", data)
			return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "mon_out_of_level_range"})

	# Validate team
	is_valid, error = ema_battle_manager.is_valid_team(team_details, trainer_address)
	if not is_valid:
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": error})

	# Check team limit
	num_registrations = tournament_manager.count_registrations(tournament_id)
	if num_registrations >= tournament_manager.TournamentTeamLimit:
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "already full"})

	# Finish validation, start updating
	with transaction.atomic():
		uid = user_manager.get_uid_by_address_default_0(trainer_address)

		registered_team = tournament_manager.register_team(
			uid, trainer_address, tournament_id, fee_emont=TOURNAMENT_FEE_EMONT, fee_eth=0, team_info=json.dumps(team)
		)

		if not registered_team:
			return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "cannot register team, may be no emont left"})

		return api_response_result(request, ResultCode.SUCCESS, {
			"player_id": registered_team.player_id,
			"player_address": registered_team.player_address,
			"tournament_id": registered_team.tournament_id,
			"team_info": team_details,
			"status": registered_team.status,
		})
