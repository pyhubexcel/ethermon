# After moving win reward to quest, some forgot to claim the old win reward.
# This script is to add this amount back to the emont balance.
import json
import random

import os
import sys

curr_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curr_dir)
sys.path.append(os.path.join(curr_dir, '../../'))

from common import context
from django.core.wsgi import get_wsgi_application

context.init_django('../', 'settings')
application = get_wsgi_application()

from django.db import transaction

from common.jsonutils import to_json
from common.utils import get_timestamp
from etheremon_lib import tournament_manager, ema_battle_manager, general_battle_manager, \
	user_manager, emont_bonus_manager, transaction_manager
from etheremon_lib.constants import BattleResult
from etheremon_lib.ema_monster_manager import get_mon_info
from etheremon_lib.models import EtheremonDB
from etheremon_lib.tournament_manager import TournamentTypes, TournamentStatus, TournamentRegistrationStatus, \
	TournamentRewards
from etheremon_lib.transaction_manager import TxnTypes, TxnAmountTypes, TxnStatus


def add_tournament():
	with transaction.atomic():
		# try start pending tournaments
		start_tournaments()

		# add new tournaments
		for typ in [TournamentTypes.BEGINNER, TournamentTypes.ROOKIE]:
			t = EtheremonDB.TournamentInfoTab.objects.filter(tournament_type=typ).filter(status=TournamentStatus.REGISTRATION).first()
			if not t:
				tournament_manager.create_new_tournament(typ, start_time=get_timestamp()+48*60*60)


def start_tournament(tournament, tournament_id=None, force_restart=False):
	if tournament_id is not None:
		tournament = tournament_manager.get_tournament_by_id(tournament_id)

	if tournament.status in [TournamentStatus.FINISHED] and not force_restart:
		return

	with transaction.atomic():
		# Validate teams
		qualified_teams = []
		disqualified_teams = []

		registrations = EtheremonDB.TournamentRegistrationTab.objects.filter(tournament_id=tournament.id)
		for r in registrations:
			team_info = json.loads(r.team_info)
			team_details = [get_mon_info(mon_id) for mon_id in team_info]
			is_valid, error = ema_battle_manager.is_valid_team(team_details, r.player_address)

			for mon in team_details[:3]:
				if not tournament.mon_level_min <= mon["total_level"] <= tournament.mon_level_max:
					is_valid = False

			team_info = {
				"player_id": r.player_id,
				"player_address": r.player_address,
				"username": user_manager.get_user_name_with_cache(r.player_address),
				"team_info": team_info,
			}

			if not is_valid:
				r.status = TournamentRegistrationStatus.DISQUALIFIED
				r.save()
				disqualified_teams.append(team_info)
			else:
				qualified_teams.append(team_info)

		random.shuffle(qualified_teams)

		current_players = [{"team": team, "battle_id": -1, "children": []} for team in qualified_teams]

		while len(current_players) > 1:
			next_round_players = []

			for i in range(0, len(current_players), 2):
				if i == len(current_players)-1:
					next_round_players.append(current_players[i])

				else:
					attacker = current_players[i]
					defender = current_players[i+1]

					result = general_battle_manager.start_battle(
						attacker["team"]["player_id"], attacker["team"]["player_address"], attacker["team"]["team_info"],
						defender["team"]["player_id"], defender["team"]["player_address"], defender["team"]["team_info"],
						battle_type=general_battle_manager.BattleTypes.TOURNAMENT
					)

					winner = attacker if result["result"] == BattleResult.ATTACKER_WIN else defender
					loser = defender if result["result"] == BattleResult.ATTACKER_WIN else attacker

					# Update
					winner_info = user_manager.get_user_general_info(address=winner["team"]["player_address"])
					winner_info.tournament_win += 1
					winner_info.save()

					loser_info = user_manager.get_user_general_info(address=loser["team"]["player_address"])
					loser_info.tournament_loss += 1
					loser_info.save()

					next_round_players.append({
						"team": winner["team"],
						"battle_id": result["battle_id"],
						"children": [
							attacker,
							defender
						]
					})

			current_players = next_round_players

		top4 = []
		if current_players and len(current_players) > 0:
			top4.append((current_players[0]["team"]["player_id"], current_players[0]["team"]["player_address"]))

			for t in current_players[0]["children"]:
				if t and t["team"]["player_id"] != top4[0][0]:
					top4.append((t["team"]["player_id"], t["team"]["player_address"]))
					break

			for t1 in current_players[0]["children"]:
				if t1:
					for t2 in t1["children"]:
						if t2 and t2["team"]["player_id"] not in [top4[0][0], top4[1][0]]:
							top4.append((t2["team"]["player_id"], t2["team"]["player_address"]))

		reward_data = {}
		prize_pool = tournament.price_pool_emont

		for i, (player_id, player_address) in enumerate(top4):
			reward_data[i] = {
				"player": player_id,
				"address": player_address,
				"token_reward": int(prize_pool * TournamentRewards.TOKENS[i]),
				"mon_reward": None if len(TournamentRewards.MONS[tournament.tournament_type][i]) == 0 else random.choice(TournamentRewards.MONS[tournament.tournament_type][i]),
			}

			emont_bonus_manager.add_bonus(player_id, {emont_bonus_manager.EmontBonusType.EVENT_BONUS: reward_data[i]["token_reward"]})

			if reward_data[i]["mon_reward"]:
				transaction_manager.create_transaction(
					player_uid=player_id,
					player_address=player_address,
					txn_type=TxnTypes.GENERAL_REWARD,
					txn_info="tournament #%s - rank #%s" % (tournament.id, i+1),
					amount_type=TxnAmountTypes.MON,
					amount_value=reward_data[i]["mon_reward"],
					status=TxnStatus.INIT,
				)

		# Update tournament
		tournament.status = TournamentStatus.FINISHED
		tournament.result = "" if len(current_players) == 0 else to_json(current_players[0])
		tournament.reward = to_json(reward_data)
		tournament.save()


def start_tournaments():
	current_time = get_timestamp()
	tournaments = EtheremonDB.TournamentInfoTab.objects.filter(status=TournamentStatus.REGISTRATION).filter(start_time__lte=current_time)

	for tournament in tournaments:
		start_tournament(tournament)
