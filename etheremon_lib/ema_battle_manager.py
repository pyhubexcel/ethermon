from django.db.models import Q

from etheremon_lib.monster_config import DUMMY_MONS
from etheremon_lib.models import *
from etheremon_lib.constants import BattleResult


def get_rank_battles(player_id):
	return EtheremonDB.EmaRankBattleTab.objects.filter(Q(defender_id=player_id) | Q(attacker_id=player_id)).order_by('-id')[:15]

def get_rank_battles_rkt(player_id):
	return EtheremonDB.EmaRankBattleRKTTab.objects.filter(Q(defender_id=player_id) | Q(attacker_id=player_id)).order_by('-id')[:15]


# player as attacker
def count_rank_battles(player_id):
	return EtheremonDB.EmaRankBattleTab.objects.filter(attacker_id=player_id).count()


# player as attacker
def count_rank_battles_by_time(player_id, from_time, to_time):
	return EtheremonDB.EmaRankBattleTab.objects\
		.filter(attacker_id=player_id) \
		.filter(create_time__gte=from_time) \
		.filter(create_time__lte=to_time).count()


def count_rank_wins(attacker_id):
	return EtheremonDB.EmaRankBattleTab.objects.filter(attacker_id=attacker_id).filter(result=BattleResult.ATTACKER_WIN).count()


def count_rank_wins_by_time(attacker_id, from_time, to_time):
	return EtheremonDB.EmaRankBattleTab.objects \
		.filter(attacker_id=attacker_id) \
		.filter(result=BattleResult.ATTACKER_WIN) \
		.filter(create_time__gte=from_time) \
		.filter(create_time__lte=to_time).count()


def get_rank_attack_battles(attacker_id):
	return EtheremonDB.EmaRankBattleTab.objects.filter(attacker_id=attacker_id)\
		.order_by("id").all()


def get_rank_attack_battles_by_time(attacker_id, from_time, to_time):
	return EtheremonDB.EmaRankBattleTab.objects.filter(attacker_id=attacker_id)\
		.order_by("id") \
		.filter(create_time__gte=from_time) \
		.filter(create_time__lte=to_time).all()


def get_practice_battles(trainer):
	return EtheremonDB.EmaPracticeBattleTab.objects.filter(trainer=trainer).order_by('-id')[:10]


def count_practice_battles(trainer):
	return EtheremonDB.EmaPracticeBattleTab.objects.filter(trainer=trainer).count()


def count_practice_battles_by_time(trainer, from_time, to_time):
	return EtheremonDB.EmaPracticeBattleTab.objects\
		.filter(trainer=trainer)\
		.filter(create_time__gte=from_time)\
		.filter(create_time__lte=to_time).count()


def get_lates_rank_battles(limit):
	return EtheremonDB.EmaRankBattleTab.objects.order_by('-id')[:limit]


def get_rank_battle_data(battle_id):
	return EtheremonDB.EmaRankBattleTab.objects.filter(id=battle_id).first()

def get_rank_battle_data_bp(battle_id):
	return EtheremonDB.EmaRankBattleTabBP.objects.filter(id=battle_id).first()


def is_on_ema_battle(monster_id):
	record = EtheremonDB.EmaPlayerRankData.objects.filter(Q(a0=monster_id) | Q(a1=monster_id) | Q(a2=monster_id) | Q(s0=monster_id) | Q(s1=monster_id) | Q(s2=monster_id)).first()
	return record is not None


def is_valid_team(team, trainer_address):
	# Notes: DUMMY_MONS doesnt count

	if any(mon is None for mon in team[0:3]):
		return False, "invalid_attackers"

	if any(mon is not None and mon["monster_id"] not in DUMMY_MONS and mon["trainer"] != trainer_address for mon in team):
		return False, "invalid_mons"

	for i in xrange(len(team)):
		for mon2 in team[i + 1:]:
			if team[i] and mon2 and team[i]["monster_id"] not in DUMMY_MONS and mon2["monster_id"] not in DUMMY_MONS and team[i]["class_id"] == mon2["class_id"]:
				return False, "same_species"

	return True, ''
