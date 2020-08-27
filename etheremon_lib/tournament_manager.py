import json

from common.jsonutils import from_json
from common.utils import get_timestamp
from etheremon_lib import user_manager, emont_bonus_manager
from etheremon_lib.ema_monster_manager import get_mon_info
from etheremon_lib.models import EtheremonDB


class TournamentTypes:
	BEGINNER = 1
	ROOKIE = 2
	# LEGENDARY = 3


class TournamentRewards:
	MONS = {
		TournamentTypes.BEGINNER: {
			0: [81, 106, 33, 97],
			1: [81, 106, 33, 97],
			2: [],
			3: [],
		},
		TournamentTypes.ROOKIE: {
			0: [151, 146, 140, 131],
			1: [151, 146, 140, 131],
			2: [],
			3: [],
		},
		# TournamentTypes.LEGENDARY: {
		# 	0: [1, 2, 3],
		# 	1: [4, 5],
		# 	2: [6, 7],
		# 	3: [6, 7],
		# },
	}
	TOKENS = {
		0: 0.5,
		1: 0.3,
		2: 0.1,
		3: 0.1,
	}


class TournamentStatus:
	INIT = 0
	REGISTRATION = 1
	ON_GOING = 2
	FINISHED = 3


class TournamentRegistrationStatus:
	REGISTERED = 0
	DISQUALIFIED = 1


TournamentMonLevel = {
	TournamentTypes.BEGINNER: [1, 26],
	TournamentTypes.ROOKIE: [26, 100],
	# TournamentTypes.LEGENDARY: [60, 100],
}

TournamentTeamLimit = 32


def create_new_tournament(tournament_type, start_time, status=TournamentStatus.REGISTRATION):
	assert start_time > get_timestamp()

	tournament = EtheremonDB.TournamentInfoTab(
		tournament_type=tournament_type,
		mon_level_min=TournamentMonLevel[tournament_type][0],
		mon_level_max=TournamentMonLevel[tournament_type][1],
		registrations=0,
		price_pool_emont=0,
		price_pool_eth=0,
		start_time=start_time,
		status=status,
		result="",
		reward="",
		create_time=get_timestamp(),
		update_time=get_timestamp(),
	)

	tournament.save()
	return tournament


def get_tournament_by_id(tournament_id):
	return EtheremonDB.TournamentInfoTab.objects.filter(id=tournament_id).first()


def get_newest_tournament(tournament_type):
	return EtheremonDB.TournamentInfoTab.objects.filter(tournament_type=tournament_type).order_by("id").last()


def register_team(uid, address, tournament_id, fee_emont, fee_eth, team_info, status=0, extra=""):
	team = EtheremonDB.TournamentRegistrationTab.objects.filter(player_id=uid).filter(tournament_id=tournament_id).first()

	if not team:
		emont_balance = emont_bonus_manager.get_emont_balance(uid)
		if emont_balance < fee_emont:
			return None

		# Deduct EMONT
		if fee_emont > 0:
			emont_bonus_manager.deduct_emont_in_game_balance(uid, fee_emont)

		team = EtheremonDB.TournamentRegistrationTab(
			player_id=uid,
			player_address=address,
			tournament_id=tournament_id,
			fee_paid_emont=fee_emont,
			fee_paid_eth=fee_eth,
			team_info=team_info,
			status=status,
			extra=extra,
			create_time=get_timestamp(),
			update_time=get_timestamp(),
		)

		tournament = get_tournament_by_id(tournament_id)
		tournament.registrations += 1
		tournament.price_pool_emont += fee_emont
		tournament.price_pool_eth += fee_eth
		tournament.update_time = get_timestamp()
		tournament.save()

	else:
		team.team_info = team_info
		team.update_time = get_timestamp()

	team.save()
	return team


def get_tournament_info(tournament_id, tournament):
	if not tournament and tournament_id:
		tournament = get_tournament_by_id(tournament_id)

	data = {
		"id": tournament.id,
		"type": tournament.tournament_type,
		"mon_level_min": tournament.mon_level_min,
		"mon_level_max": tournament.mon_level_max,
		"registrations": tournament.registrations,
		"price_pool_emont": tournament.price_pool_emont,
		"price_pool_eth": tournament.price_pool_eth,
		"start_time": tournament.start_time,
		"register_time_left": tournament.start_time - get_timestamp(),
		"status": tournament.status,
		"team": {},
		"result": None if tournament.result == "" else from_json(tournament.result),
		"reward": None if tournament.reward == "" else from_json(tournament.reward),
	}

	registrations = EtheremonDB.TournamentRegistrationTab.objects.filter(tournament_id=tournament.id)
	for r in registrations:
		team = json.loads(r.team_info)
		team_details = [get_mon_info(mon_id) for mon_id in team]

		data["team"][r.player_id] = {
			"register_id": r.id,
			"player_id": r.player_id,
			"player_address": r.player_address,
			"name": user_manager.get_user_name_with_cache(r.player_address),
			"team_info": team_details,
			"status": r.status,
		}
		
	return data


def count_registrations(tournament_id):
	return EtheremonDB.TournamentRegistrationTab.objects.filter(tournament_id=tournament_id).count()
