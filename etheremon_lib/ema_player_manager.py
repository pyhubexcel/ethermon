import random
from django.db.models import Q

import etheremon_lib.ema_monster_manager
from common.utils import get_timestamp
from etheremon_lib import utils, ema_monster_manager
from etheremon_lib.models import *
from etheremon_lib.constants import *
from etheremon_lib.monster_config import MONSTER_CLASS_STATS
from etheremon_lib.utils import get_level

FREE_CLAIM_MAX_AMOUNT = 10
FREE_CLAIM_AMOUNT = 1
FREE_CLAIM_TIME = 30 * 60


def get_player_rank_by_address(trainer):
	return EtheremonDB.EmaPlayerRankData.objects.filter(trainer=trainer).first()

def get_rkt_player_rank_by_address(trainer):
	return EtheremonDB.EmaPlayerRankRKTData.objects.filter(trainer=trainer).first()


def get_player_bid_by_address(trainer):
	data = get_player_rank_by_address(trainer)
	if data:
		return data.player_id
	else:
		return 0


def get_player_rank_by_id(player_id):
	return EtheremonDB.EmaPlayerRankData.objects.filter(player_id=player_id).first()

def get_rkt_player_rank_by_id(player_id):
	return EtheremonDB.EmaPlayerRankRKTData.objects.filter(player_id=player_id).first()


def cal_current_rank(point):
	return EtheremonDB.EmaPlayerRankData.objects.filter(point__gte=point).count()

def cal_current_rank_rkt(point):
	return EtheremonDB.EmaPlayerRankRKTData.objects.filter(point__gte=point).count()


def count_total_rank():
	return EtheremonDB.EmaPlayerRankData.objects.count()

def count_total_rank_rkt():
	return EtheremonDB.EmaPlayerRankRKTData.objects.count()


def get_rank_data_list(from_index, to_index):
	return EtheremonDB.EmaPlayerRankData.objects.order_by('-point')[from_index:to_index]

def get_rank_data_list_rkt(from_index, to_index):
	return EtheremonDB.EmaPlayerRankRKTData.objects.order_by('-point')[from_index:to_index]



def get_defenders_by_point_rkt(point, player_id, limit=10):
	greater_records = EtheremonDB.EmaPlayerRankRKTData.objects.filter(point__gte=point).filter(
		~Q(player_id=player_id)).order_by('point')[:limit]
	lower_records = EtheremonDB.EmaPlayerRankRKTData.objects.filter(point__lt=point).filter(
		~Q(player_id=player_id)).order_by('-point')[:limit]
	result_list = []
	for greater_record in greater_records:
		result_list.append(greater_record)
	for lower_record in lower_records:
		result_list.append(lower_record)
	random.shuffle(result_list)
	return result_list[:limit]


def get_defenders_by_point(point, player_id, limit=10):
	greater_records = EtheremonDB.EmaPlayerRankData.objects.filter(point__gte=point).filter(
		~Q(player_id=player_id)).order_by('point')[:limit]
	lower_records = EtheremonDB.EmaPlayerRankData.objects.filter(point__lt=point).filter(
		~Q(player_id=player_id)).order_by('-point')[:limit]
	result_list = []
	for greater_record in greater_records:
		result_list.append(greater_record)
	for lower_record in lower_records:
		result_list.append(lower_record)
	random.shuffle(result_list)
	return result_list[:limit]


def get_practice_castles_by_level(player_id, avg_level):
	greater_records = EtheremonDB.EmaPlayerRankData.objects.filter(avg_level__gte=avg_level).filter(
		~Q(player_id=player_id)).order_by('avg_bp')[:10]
	lower_records = EtheremonDB.EmaPlayerRankData.objects.filter(avg_level__lt=avg_level).filter(
		~Q(player_id=player_id)).order_by('-avg_bp')[:10]
	result_list = []
	for greater_record in greater_records:
		result_list.append(greater_record)
	for lower_record in lower_records:
		result_list.append(lower_record)
	random.shuffle(result_list)
	return result_list


def _get_battle_monster(monster_id):
	mon = ema_monster_manager.get_mon_info(monster_id)
	return mon["level"], mon["bp"]


def get_initial_elo_point(avg_bp):
	return 250


def calculate_avg_data(player_id):
	player_data = EtheremonDB.EmaPlayerRankData.objects.filter(player_id=player_id).first()
	if not player_data:
		return

	level0, bp0 = _get_battle_monster(player_data.a0)
	level1, bp1 = _get_battle_monster(player_data.a1)
	level2, bp2 = _get_battle_monster(player_data.a2)
	avg_level = (level0 + level1 + level2) / 3
	avg_bp = (bp0 + bp1 + bp2) / 3
	# only update avg bp and avg level
	EtheremonDB.EmaPlayerRankData.objects.filter(player_id=player_id).filter(a0=player_data.a0). \
		filter(a1=player_data.a1).filter(a2=player_data.a2).update(avg_bp=avg_bp, avg_level=avg_level)


def calculate_avg_data_by_address(trainer):
	player_data = EtheremonDB.EmaPlayerRankData.objects.filter(trainer=trainer).first()
	if not player_data:
		return

	level0, bp0 = _get_battle_monster(player_data.a0)
	level1, bp1 = _get_battle_monster(player_data.a1)
	level2, bp2 = _get_battle_monster(player_data.a2)
	avg_level = (level0 + level1 + level2) / 3
	avg_bp = (bp0 + bp1 + bp2) / 3
	# only update avg bp and avg level
	EtheremonDB.EmaPlayerRankData.objects.filter(trainer=trainer).filter(a0=player_data.a0). \
		filter(a1=player_data.a1).filter(a2=player_data.a2).update(avg_bp=avg_bp, avg_level=avg_level)


def try_disband_team(trainer_address):
	player_rank_data = get_player_rank_by_address(trainer_address)
	if player_rank_data:
		team = [etheremon_lib.ema_monster_manager.get_mon_info(mon_id) for mon_id in [player_rank_data.a0, player_rank_data.a1, player_rank_data.a2, player_rank_data.s0, player_rank_data.s1, player_rank_data.s2]]
		team_flag = False

		for i in range(6):
			flag = False
			if team[i] and team[i]["monster_id"] > 0 and team[i]["trainer"] != trainer_address:
				flag = True
			if any(team[i] and mon and team[i]["monster_id"] > 0 and mon["monster_id"] > 0 and team[i]["class_id"] == mon["class_id"] for mon in team[:i]):
				flag = True
			if flag:
				team[i] = etheremon_lib.ema_monster_manager.get_mon_info(-i - 1) if i < 3 else None
				team_flag = True

		if not team_flag:
			return player_rank_data

		player_rank_data.a0 = (team[0] or {}).get("monster_id", 0)
		player_rank_data.a1 = (team[1] or {}).get("monster_id", 0)
		player_rank_data.a2 = (team[2] or {}).get("monster_id", 0)
		player_rank_data.s0 = (team[3] or {}).get("monster_id", 0)
		player_rank_data.s1 = (team[4] or {}).get("monster_id", 0)
		player_rank_data.s2 = (team[5] or {}).get("monster_id", 0)
		player_rank_data.avg_level = (team[0]["total_level"] + team[1]["total_level"] + team[2]["total_level"]) / 3
		player_rank_data.avg_bp = (team[0]["total_bp"] + team[1]["total_bp"] + team[2]["total_bp"]) / 3
		player_rank_data.update_time = get_timestamp()
		player_rank_data.save()

	return player_rank_data
