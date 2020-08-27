from etheremon_api.views.helper import get_start_time_of_the_day, get_end_time_of_the_day
from etheremon_lib import user_manager, ema_battle_manager, ema_player_manager, \
	ema_adventure_manager, ema_egg_manager, ema_energy_manager
from etheremon_lib.constants import BattleResult, AdventureRewardItems, FREE_MONSTERS, INFINITY_FUTURE, \
	LUNAR_19_START_TIME, LUNAR_19_END_TIME
import datetime
import json
from random import randint


QUEST_SYSTEM_START_TIME = int((datetime.datetime.strptime('2018-12-01-T00:00', '%Y-%m-%d-T%H:%M') - datetime.datetime(1970, 1, 1)).total_seconds())


class QuestTypes:
	ALL_TYPES = 0
	TUTORIAL = 1
	DAILY = 2
	PROGRESS = 3
	EVENT = 4
	CIRCLE = 5
	TYPE_LIST = [ALL_TYPES, TUTORIAL, DAILY, PROGRESS, EVENT, CIRCLE]


class QuestStatus:
	TO_CLAIM = 1
	TO_DO = 2
	CLAIMED = 3
	CLOSED = 4


class RewardTypes:
	UNDEFINED = 0
	EMONT = 1
	ENERGY = 2
	RANDOM_EMONT = 3

	HONGBAO = 100


# Define all functions to update progress here
# def update_num_rank_team(quest, current_ts):
# 	player_rank_data = ema_player_manager.get_player_rank_by_id(quest.player_uid)
# 	return max(quest.quest_progress, 1 if player_rank_data else 0)


# def update_mon_caught(quest, current_ts):
# 	return ema_monster_manager.count_monster_data_by_trainer(quest.player_address)


# def update_gym_played(quest, current_ts):
	# from_time = 0
	# to_time = constants.INFINITY_FUTURE
	# if quest.quest_type == QuestTypes.DAILY or quest_info.get("is_daily", False):
	# 	from_time = get_start_time_of_the_day(current_ts)
	# 	to_time = get_end_time_of_the_day(current_ts)

	# return 0


def update_practice_played(quest, current_ts):
	quest_info = QUEST_LIST[quest.quest_id]

	if quest.quest_type == QuestTypes.DAILY or quest_info.get("is_daily", False):
		return ema_battle_manager.count_practice_battles_by_time(
			quest.player_address,
			get_start_time_of_the_day(current_ts),
			get_end_time_of_the_day(current_ts)
		)
	else:
		if len(quest_info["quest_target"]) >= 2:
			prev_res = ema_battle_manager.count_practice_battles_by_time(quest.player_address, 0, QUEST_SYSTEM_START_TIME)
			curr_res = ema_battle_manager.count_practice_battles_by_time(quest.player_address, QUEST_SYSTEM_START_TIME+1, current_ts)
			return min(prev_res, quest_info["quest_target"][0]+quest_info["quest_target"][1]) + curr_res
		else:
			return ema_battle_manager.count_practice_battles(quest.player_address)


def update_rank_played(quest, current_ts):
	player_bid = ema_player_manager.get_player_bid_by_address(quest.player_address)
	quest_info = QUEST_LIST[quest.quest_id]

	if quest.quest_type == QuestTypes.DAILY or quest_info.get("is_daily", False):
		return ema_battle_manager.count_rank_battles_by_time(
			player_bid,
			get_start_time_of_the_day(current_ts),
			get_end_time_of_the_day(current_ts)
		)
	else:
		if len(quest_info["quest_target"]) >= 2:
			prev_res = ema_battle_manager.count_rank_battles_by_time(player_bid, 0, QUEST_SYSTEM_START_TIME)
			curr_res = ema_battle_manager.count_rank_battles_by_time(player_bid, QUEST_SYSTEM_START_TIME + 1, current_ts)
			return min(prev_res, quest_info["quest_target"][0] + quest_info["quest_target"][1]) + curr_res
		else:
			return ema_battle_manager.count_rank_battles(player_bid)


def update_rank_practice_played(quest, current_ts):
	return update_rank_played(quest, current_ts) + update_practice_played(quest, current_ts)


def update_adventure_played(quest, current_ts):
	quest_info = QUEST_LIST[quest.quest_id]
	
	if quest.quest_type == QuestTypes.DAILY or quest_info.get("is_daily", False):
		return ema_adventure_manager.count_player_explores_by_time(
			quest.player_address,
			get_start_time_of_the_day(current_ts),
			get_end_time_of_the_day(current_ts)
		)
	else:
		if len(quest_info["quest_target"]) >= 2:
			prev_res = ema_adventure_manager.count_player_explores_by_time(quest.player_address, 0, QUEST_SYSTEM_START_TIME)
			curr_res = ema_adventure_manager.count_player_explores_by_time(quest.player_address, QUEST_SYSTEM_START_TIME + 1, current_ts)
			return min(prev_res, quest_info["quest_target"][0] + quest_info["quest_target"][1]) + curr_res
		else:
			return ema_adventure_manager.count_player_explores(quest.player_address)


def update_rank_won(quest, current_ts):
	player_bid = ema_player_manager.get_player_bid_by_address(quest.player_address)
	quest_info = QUEST_LIST[quest.quest_id]
	
	if quest.quest_type == QuestTypes.DAILY or quest_info.get("is_daily", False):
		return ema_battle_manager.count_rank_wins_by_time(
			player_bid,
			get_start_time_of_the_day(current_ts),
			get_end_time_of_the_day(current_ts)
		)
	else:
		if len(quest_info["quest_target"]) >= 2:
			prev_res = ema_battle_manager.count_rank_wins_by_time(player_bid, 0, QUEST_SYSTEM_START_TIME)
			curr_res = ema_battle_manager.count_rank_wins_by_time(player_bid, QUEST_SYSTEM_START_TIME + 1, current_ts)
			return min(prev_res, quest_info["quest_target"][0] + quest_info["quest_target"][1]) + curr_res
		else:
			return ema_battle_manager.count_rank_wins(player_bid)


def update_consecutive_rank_won(quest, current_ts):
	player_bid = ema_player_manager.get_player_bid_by_address(quest.player_address)
	quest_info = QUEST_LIST[quest.quest_id]

	if quest.quest_type == QuestTypes.DAILY or quest_info.get("is_daily", False):
		matches = ema_battle_manager.get_rank_attack_battles_by_time(
			player_bid,
			get_start_time_of_the_day(current_ts),
			get_end_time_of_the_day(current_ts)
		)
	else:
		matches = ema_battle_manager.get_rank_attack_battles(player_bid)

	win_streak = 0
	longest_streak = 0
	for match in matches:
		if match.result == BattleResult.ATTACKER_WIN:
			win_streak += 1
			longest_streak = max(longest_streak, win_streak)
		else:
			win_streak = 0

	return longest_streak if longest_streak >= quest.quest_target else win_streak


def update_daily_login(quest, current_ts):
	return 1


def update_daily_energy_claim(quest, current_ts):
	energy_record = ema_energy_manager.get_energy_by_trainer(quest.player_address)
	if not energy_record:
		return 0
	return int(energy_record and get_start_time_of_the_day(current_ts) <= energy_record.last_claim_time <= get_end_time_of_the_day(current_ts))


# No Daily
def update_adventure_mon_caught(quest, current_ts):
	quest_info = QUEST_LIST[quest.quest_id]
	if len(quest_info["quest_target"]) >= 2:
		prev_res = ema_adventure_manager.count_adventure_mon_caught_by_time(quest.player_address, 0, QUEST_SYSTEM_START_TIME)
		curr_res = ema_adventure_manager.count_adventure_mon_caught_by_time(quest.player_address, QUEST_SYSTEM_START_TIME + 1, current_ts)
		return min(prev_res, quest_info["quest_target"][0] + quest_info["quest_target"][1]) + curr_res
	else:
		return ema_adventure_manager.count_adventure_mon_caught(quest.player_address)


# No Daily
def update_adventure_level_stone_1_collected(quest, current_ts):
	quest_info = QUEST_LIST[quest.quest_id]
	if len(quest_info["quest_target"]) >= 2:
		prev_res = ema_adventure_manager.count_adventure_item_found_by_time(quest.player_address, AdventureRewardItems.LEVEL_STONE, 1, 0, QUEST_SYSTEM_START_TIME)
		curr_res = ema_adventure_manager.count_adventure_item_found_by_time(quest.player_address, AdventureRewardItems.LEVEL_STONE, 1, QUEST_SYSTEM_START_TIME + 1, current_ts)
		return min(prev_res, quest_info["quest_target"][0] + quest_info["quest_target"][1]) + curr_res
	else:
		return ema_adventure_manager.count_adventure_item_found(quest.player_address, AdventureRewardItems.LEVEL_STONE, 1)


# No Daily
def update_adventure_level_stone_2_collected(quest, current_ts):
	quest_info = QUEST_LIST[quest.quest_id]
	if len(quest_info["quest_target"]) >= 2:
		prev_res = ema_adventure_manager.count_adventure_item_found_by_time(quest.player_address, AdventureRewardItems.LEVEL_STONE, 2, 0, QUEST_SYSTEM_START_TIME)
		curr_res = ema_adventure_manager.count_adventure_item_found_by_time(quest.player_address, AdventureRewardItems.LEVEL_STONE, 2, QUEST_SYSTEM_START_TIME + 1, current_ts)
		return min(prev_res, quest_info["quest_target"][0] + quest_info["quest_target"][1]) + curr_res
	else:
		return ema_adventure_manager.count_adventure_item_found(quest.player_address, AdventureRewardItems.LEVEL_STONE, 2)


# No Daily
def update_adventure_shard_collected(quest, current_ts):
	quest_info = QUEST_LIST[quest.quest_id]
	if len(quest_info["quest_target"]) >= 2:
		prev_res = ema_adventure_manager.count_adventure_shard_found_by_time(quest.player_address, 0, QUEST_SYSTEM_START_TIME)
		curr_res = ema_adventure_manager.count_adventure_shard_found_by_time(quest.player_address, QUEST_SYSTEM_START_TIME + 1, current_ts)
		return min(prev_res, quest_info["quest_target"][0] + quest_info["quest_target"][1]) + curr_res
	else:
		return ema_adventure_manager.count_adventure_shard_found(quest.player_address)


# No Daily
def update_non_free_store_mons_caught(quest, current_ts):
	player_data = user_manager.get_world_trainer(quest.player_address)
	if not player_data:
		return 0
	purchased_store_mons = json.loads(player_data.extra_data)

	quest_info = QUEST_LIST[quest.quest_id]
	if len(quest_info["quest_target"]) >= 2:
		prev_res = 0
		curr_res = 0
		for m in purchased_store_mons:
			if m[0] not in FREE_MONSTERS and m[1] <= QUEST_SYSTEM_START_TIME:
				prev_res += 1
			if m[0] not in FREE_MONSTERS and m[1] > QUEST_SYSTEM_START_TIME:
				curr_res += 1
		return min(prev_res, quest_info["quest_target"][0] + quest_info["quest_target"][1]) + curr_res
	else:
		return sum([1 if m[0] not in FREE_MONSTERS else 0 for m in purchased_store_mons])


# No Daily
def update_eggs_laid(quest, current_ts):
	quest_info = QUEST_LIST[quest.quest_id]
	if len(quest_info["quest_target"]) >= 2:
		prev_res = ema_egg_manager.count_hatched_eggs_by_time(quest.player_address, 0, QUEST_SYSTEM_START_TIME)
		curr_res = ema_egg_manager.count_hatched_eggs_by_time(quest.player_address, QUEST_SYSTEM_START_TIME + 1, current_ts)
		return min(prev_res, quest_info["quest_target"][0] + quest_info["quest_target"][1]) + curr_res
	else:
		return ema_egg_manager.count_hatched_eggs(quest.player_address)


# Xmas 2018 event
def update_xmas_event(quest, current_ts):
	player_bid = ema_player_manager.get_player_bid_by_address(quest.player_address)

	ranked_played = ema_battle_manager.count_rank_battles_by_time(player_bid, quest.start_time, quest.end_time)
	adventure_played = ema_adventure_manager.count_player_explores_by_time(quest.player_address, quest.start_time, quest.end_time)

	matches = ema_battle_manager.get_rank_attack_battles_by_time(player_bid, quest.start_time, quest.end_time)
	win_streak = 0
	longest_streak = 0
	for match in matches:
		if match.result == BattleResult.ATTACKER_WIN:
			win_streak += 1
			longest_streak = max(longest_streak, win_streak)
		else:
			win_streak = 0

	return (ranked_played >= 150) + (longest_streak >= 10) + (adventure_played >= 50), {
		"ranked_played": [min(ranked_played, 150), 150],
		"adventure_played": [min(adventure_played, 50), 50],
		"win_streak": [10 if longest_streak >= 10 else win_streak, 10],
	}


def cal_reward_xmas_event(quest, current_ts):
	if randint(0, 9) <= 1:
		return 1000
	return randint(0, 350) + 150


def update_referral_points(quest, current_ts):
	friends = user_manager.get_referred_addresses(quest.player_uid, quest.start_time, quest.end_time)
	converted_friends = 0
	for friend in friends:
		if user_manager.count_store_non_free_mons_caught(friend, quest.start_time, quest.end_time) > 0:
			converted_friends += 1

	user_info = user_manager.get_user_info(quest.player_address)
	refer_bonus = user_info and user_info.refer_uid > 0 \
				  and quest.start_time <= user_info.create_time <= quest.end_time \
				  and user_manager.count_store_non_free_mons_caught(quest.player_address, quest.start_time, quest.end_time) > 0

	extra_data = json.loads(quest.extra or "{}")
	current_points = max(0, (converted_friends + refer_bonus) * 5 - extra_data.get("claimed_points", 0))

	return current_points, {
		"current_points": current_points,
		"total_referred": converted_friends,
		"refer_bonus": int(refer_bonus),
	}


# Dict's key is quest's id
QUEST_LIST = {
	# 1001: {
	# 	'quest_type': QuestTypes.TUTORIAL,
	# 	'quest_name': 'catch 1st store mon',
	# 	'quest_target': [1],
	# 	'reward_type': [RewardTypes.ENERGY],
	# 	'reward_value': [2],
	# 	'update_progress_func': update_mon_caught,
	# },
	# 1002: {
	# 	'quest_type': QuestTypes.TUTORIAL,
	# 	'quest_name': 'first gym',
	# 	'quest_target': [1],
	# 	'reward_type': [RewardTypes.ENERGY],
	# 	'reward_value': [2],
	# 	'update_progress_func': update_gym_played,
	# },
	# 1003: {
	# 	'quest_type': QuestTypes.TUTORIAL,
	# 	'quest_name': 'first practice',
	# 	'quest_target': [1],
	# 	'reward_type': [RewardTypes.ENERGY],
	# 	'reward_value': [2],
	# 	'update_progress_func': update_practice_played,
	# },
	# 1004: {
	# 	'quest_type': QuestTypes.TUTORIAL,
	# 	'quest_name': 'first rank team',
	# 	'quest_target': [1],
	# 	'reward_type': [RewardTypes.ENERGY],
	# 	'reward_value': [2],
	# 	'update_progress_func': update_num_rank_team,
	# },
	# 1005: {
	# 	'quest_type': QuestTypes.TUTORIAL,
	# 	'quest_name': 'first adventure',
	# 	'quest_target': [1],
	# 	'reward_type': [RewardTypes.ENERGY],
	# 	'reward_value': [6],
	# 	'update_progress_func': update_adventure_played,
	# },

	# 2001: {
	# 	'quest_type': QuestTypes.DAILY,
	# 	'quest_name': 'daily_gym',
	# 	'quest_target': [1],
	# 	'reward_type': [RewardTypes.ENERGY],
	# 	'reward_value': [2],
	# 	'update_progress_func': update_gym_played,
	# },
	2002: {
		'quest_type': QuestTypes.DAILY,
		'quest_name': 'daily_battle',
		'quest_target': [7],
		'reward_type': [RewardTypes.ENERGY],
		'reward_value': [4],
		'update_progress_func': update_rank_practice_played,
	},
	2003: {
		'quest_type': QuestTypes.DAILY,
		'quest_name': 'daily_rank_win',
		'quest_target': [1],
		'reward_type': [RewardTypes.ENERGY],
		'reward_value': [2],
		'update_progress_func': update_rank_won,
	},
	2004: {
		'quest_type': QuestTypes.DAILY,
		'quest_name': 'daily_consecutive_rank_win',
		'quest_target': [3],
		'reward_type': [RewardTypes.ENERGY],
		'reward_value': [4],
		'update_progress_func': update_consecutive_rank_won,
	},
	2005: {
		'quest_type': QuestTypes.DAILY,
		'quest_name': 'daily_adventure',
		'quest_target': [1],
		'reward_type': [RewardTypes.EMONT],
		'reward_value': [2],
		'update_progress_func': update_adventure_played,
	},
	2006: {
		'quest_type': QuestTypes.DAILY,
		'quest_name': 'daily_win_challenge',
		'quest_target': [5, 10, 15, 20, 50, 100],
		'reward_type': [RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT],
		'reward_value': [1, 1, 1.2, 1.4, 9, 16],
		# 'reward_value': [1, 1, 1, 1, 9, 16],
		'update_progress_func': update_rank_won,
	},


	# 3001: {
	# 	'quest_type': QuestTypes.PROGRESS,
	# 	'quest_name': 'progress_gym',
	# 	'quest_target': [5, 15, 50, 200, 1000],
	# 	'reward_type': [RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT],
	# 	'reward_value': [1, 2, 6, 25, 144],
	# 	'update_progress_func': update_gym_played,
	# },
	# 3002: {
	# 	'quest_type': QuestTypes.PROGRESS,
	# 	'quest_name': 'progress_practice',
	# 	'quest_target': [10, 50, 200, 1000, 5000],
	# 	'reward_type': [RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT],
	# 	'reward_value': [3, 10, 40, 200, 1000],
	# 	'update_progress_func': update_practice_played,
	# },
	3003: {
		'quest_type': QuestTypes.PROGRESS,
		'quest_name': 'progress_rank',
		'quest_target': [20, 100, 400, 2000, 10000],
		'reward_type': [RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT],
		'reward_value': [1, 6, 25, 150, 750],
		'update_progress_func': update_rank_played,
	},
	3004: {
		'quest_type': QuestTypes.PROGRESS,
		'quest_name': 'progress_rank_win',
		'quest_target': [20, 100, 400, 2000, 10000],
		'reward_type': [RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT],
		'reward_value': [2, 12, 50, 270, 1400],
		'update_progress_func': update_rank_won,
	},
	3005: {
		'quest_type': QuestTypes.PROGRESS,
		'quest_name': 'progress_adventure',
		'quest_target': [5, 25, 100, 250, 1000],
		'reward_type': [RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT],
		'reward_value': [5, 20, 70, 160, 850],
		'update_progress_func': update_adventure_played,
	},
	3006: {
		'quest_type': QuestTypes.PROGRESS,
		'quest_name': 'progress_adventure_mon',
		'quest_target': [1, 3, 10, 25, 50],
		'reward_type': [RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT],
		'reward_value': [10, 50, 200, 500, 1100],
		'update_progress_func': update_adventure_mon_caught,
	},
	3007: {
		'quest_type': QuestTypes.PROGRESS,
		'quest_name': 'progress_adventure_stone_1',
		'quest_target': [1, 5, 20, 40, 80],
		'reward_type': [RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT],
		'reward_value': [20, 110, 440, 650, 1350],
		'update_progress_func': update_adventure_level_stone_1_collected,
	},
	3008: {
		'quest_type': QuestTypes.PROGRESS,
		'quest_name': 'progress_adventure_stone_2',
		'quest_target': [1, 2, 5, 10, 20],
		'reward_type': [RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT],
		'reward_value': [50, 120, 290, 500, 1700],
		'update_progress_func': update_adventure_level_stone_2_collected,
	},
	3009: {
		'quest_type': QuestTypes.PROGRESS,
		'quest_name': 'progress_shard',
		'quest_target': [10, 20, 50, 100, 200],
		'reward_type': [RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT],
		'reward_value': [20, 50, 110, 200, 420],
		'update_progress_func': update_adventure_shard_collected,
	},
	3010: {
		'quest_type': QuestTypes.PROGRESS,
		'quest_name': 'progress_non_store_mons',
		'quest_target': [1, 3, 10],
		'reward_type': [RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT],
		'reward_value': [3, 10, 40],
		'update_progress_func': update_non_free_store_mons_caught,
	},
	# 3011: {
	# 	'quest_type': QuestTypes.PROGRESS,
	# 	'quest_name': 'evolve mon xx times',
	# 	'quest_target': [1, 3, 7, 16, 40],
	# 	'reward_type': [RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT],
	# 	'reward_value': [91, 98, 102, 305, 874],
	# 	'update_progress_func': ,
	# },
	3012: {
		'quest_type': QuestTypes.PROGRESS,
		'quest_name': 'progress_eggs_laid',
		'quest_target': [1, 3, 7, 16, 40],
		'reward_type': [RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT],
		'reward_value': [20, 60, 100, 240, 670],
		'update_progress_func': update_eggs_laid,
	},

	4001: {
		'quest_type': QuestTypes.EVENT,
		'quest_name': 'xmas_event',
		'quest_target': [3],
		'reward_type': [RewardTypes.RANDOM_EMONT],
		'reward_value': [0],
		'start_time': 1545465600,		# 12/22/2018 @ 8:00am (UTC)
		'end_time': 1546300799,			# 12/31/2018 @ 11:59pm (UTC)
		'calc_reward_func': cal_reward_xmas_event,
		'update_progress_func': update_xmas_event,
	},

	# Lunar 19
	4002: {
		'is_daily': True,
		'quest_type': QuestTypes.EVENT,
		'quest_name': 'lunar_19_fresh_energy',
		'quest_target': [1],
		'reward_type': [RewardTypes.HONGBAO],
		'reward_value': [1],
		'start_time': LUNAR_19_START_TIME,		# 01/28/2019 @ 1:00pm (UTC)
		'end_time': LUNAR_19_END_TIME,			# 02/11/2019 @ 1:00pm (UTC)
		'update_progress_func': update_daily_energy_claim,
	},
	4003: {
		'is_daily': True,
		'quest_type': QuestTypes.EVENT,
		'quest_name': 'lunar_19_rank_played',
		'quest_target': [5],
		'reward_type': [RewardTypes.HONGBAO],
		'reward_value': [1],
		'start_time': LUNAR_19_START_TIME,		# 01/28/2019 @ 1:00pm (UTC)
		'end_time': LUNAR_19_END_TIME,			# 02/11/2019 @ 1:00pm (UTC)
		'update_progress_func': update_rank_played,
	},
	4004: {
		'is_daily': True,
		'quest_type': QuestTypes.EVENT,
		'quest_name': 'lunar_19_adventure',
		'quest_target': [1],
		'reward_type': [RewardTypes.HONGBAO],
		'reward_value': [2],
		'start_time': LUNAR_19_START_TIME,		# 01/28/2019 @ 1:00pm (UTC)
		'end_time': LUNAR_19_END_TIME,			# 02/11/2019 @ 1:00pm (UTC)
		'update_progress_func': update_adventure_played,
	},
	4005: {
		'is_daily': True,
		'quest_type': QuestTypes.EVENT,
		'quest_name': 'lunar_19_adventure_2',
		'quest_target': [2],
		'reward_type': [RewardTypes.HONGBAO],
		'reward_value': [3],
		'start_time': LUNAR_19_START_TIME,		# 01/28/2019 @ 1:00pm (UTC)
		'end_time': LUNAR_19_END_TIME,			# 02/11/2019 @ 1:00pm (UTC)
		'update_progress_func': update_adventure_played,
	},

	5001: {
		'quest_type': QuestTypes.CIRCLE,
		'quest_name': 'circle_referral',
		'quest_target': [5, 10, 15, 20, 30],
		'reward_type': [RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT, RewardTypes.EMONT],
		'reward_value': [10, 20, 30, 45, 90],
		'start_time': 1547193600,		# 01/11/2019 @ 08:00am (UTC)
		'end_time': INFINITY_FUTURE,
		'update_progress_func': update_referral_points,
	},
}
