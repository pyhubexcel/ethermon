import json
from common.utils import get_timestamp
from django.db import transaction
from django.db.models import Q
from etheremon_api.views.helper import get_start_time_of_the_day, get_end_time_of_the_day
from etheremon_lib import quest_config, ema_energy_manager, emont_bonus_manager, transaction_manager, \
	user_balance_manager
from etheremon_lib.emont_bonus_manager import EmontBonusType
from etheremon_lib.models import EtheremonDB
from etheremon_lib.quest_config import QuestStatus, QuestTypes, RewardTypes
from etheremon_lib.constants import INFINITY_FUTURE
from etheremon_lib.transaction_manager import TxnTypes, TxnAmountTypes, TxnStatus
from etheremon_lib.user_balance_manager import BalanceTypes


def get_player_quest(player_uid, quest_id):
	return EtheremonDB.QuestTab.objects.filter(player_uid=player_uid).filter(quest_id=quest_id).first()


def get_player_to_claim_quests(player_uid):
	return EtheremonDB.QuestTab.objects.filter(player_uid=player_uid).filter(status=QuestStatus.TO_CLAIM).all()


def get_player_quests(player_uid, player_address, quest_type):
	current_ts = get_timestamp()

	with transaction.atomic():
		quests = EtheremonDB.QuestTab.objects\
			.filter(player_uid=player_uid)\

		if quest_type != QuestTypes.ALL_TYPES:
			quests = quests.filter(quest_type=quest_type)

		quest_map = {}
		for quest in quests:
			quest_info = quest_config.QUEST_LIST[quest.quest_id]
			is_daily_quest = quest_info['quest_type'] == QuestTypes.DAILY or quest_info.get('is_daily', False)
			is_active_daily_quest = is_daily_quest and quest_info.get("start_time", 0) < current_ts < quest_info.get("end_time", INFINITY_FUTURE)

			if is_active_daily_quest or quest.start_time <= current_ts <= quest.end_time:
				quest_map[quest.quest_id] = quest

		# Update quest
		for quest_id, quest_info in quest_config.QUEST_LIST.iteritems():
			if quest_type in [QuestTypes.ALL_TYPES, quest_info['quest_type']]\
					and quest_info.get("start_time", 0) < current_ts < quest_info.get("end_time", INFINITY_FUTURE):
				quest_map[quest_id] = create_or_update_quest(
					player_uid, player_address, quest_id,
					quest_map.get(quest_id, None)
				)

		return quest_map


def create_or_update_quest(player_uid, player_address, quest_id, quest):
	current_ts = get_timestamp()
	today_start_time = get_start_time_of_the_day(current_ts)
	today_end_time = get_end_time_of_the_day(current_ts)

	# Get quest info
	quest_info = quest_config.QUEST_LIST[quest_id]
	quest_start_time = quest_info.get("start_time", 0)
	quest_end_time = quest_info.get("end_time", INFINITY_FUTURE)
	is_daily_quest = quest_info['quest_type'] == QuestTypes.DAILY or quest_info.get('is_daily', False)

	# Case daily quest reset
	if quest and is_daily_quest:
		if current_ts > quest.end_time:
			quest.start_time = max(quest_start_time, today_start_time)
			quest.end_time = min(quest_end_time, today_end_time)
			quest.status = QuestStatus.TO_DO
			quest.quest_level = 0
			quest.quest_target = quest_info['quest_target'][0]
			quest.reward_type = quest_info['reward_type'][0]
			quest.reward_value = quest_info['reward_value'][0]

	# Case claimed / finished quest
	if quest and quest.status != QuestStatus.TO_DO:
		return quest

	# Case new quest
	if quest is None:
		quest = EtheremonDB.QuestTab(
			player_uid=player_uid,
			player_address=player_address,
			quest_id=quest_id,
			quest_type=quest_info['quest_type'],
			quest_level=0,
			quest_name=quest_info['quest_name'],
			quest_target=quest_info['quest_target'][0],
			quest_progress=0,
			reward_type=quest_info['reward_type'][0],
			reward_value=quest_info['reward_value'][0],
			status=QuestStatus.TO_DO,
			start_time=quest_start_time if not is_daily_quest else max(quest_start_time, today_start_time),
			end_time=quest_end_time if not is_daily_quest else min(quest_end_time, today_end_time),
			last_check=0,
			create_time=current_ts,
			extra="{}",
		)

	# Update progress
	temp = quest_info['update_progress_func'](quest, current_ts)
	quest_progress = temp if not isinstance(temp, tuple) else temp[0]
	quest.quest_progress = min(quest.quest_target, quest_progress)

	# Ready to claim
	if quest.quest_progress == quest.quest_target:
		quest.status = QuestStatus.TO_CLAIM

	quest_extra_data = None if not isinstance(temp, tuple) else temp[1]
	extra_data = json.loads(quest.extra or "{}")
	extra_data["info"] = quest_extra_data
	quest.extra = json.dumps(extra_data)

	quest.last_check = current_ts
	quest.update_time = current_ts
	quest.save()

	return quest


def claim_quest(quest):
	current_ts = get_timestamp()
	if not(quest.status == quest_config.QuestStatus.TO_CLAIM and quest.start_time-120 <= current_ts <= quest.end_time+120):
		return None

	with transaction.atomic():
		quest_info = quest_config.QUEST_LIST[quest.quest_id]

		# Claim reward
		if quest.reward_type == RewardTypes.ENERGY:
			ema_energy_manager.add_energy(quest.player_address, quest.reward_value)
			txn_amount_type = TxnAmountTypes.ENERGY
		elif quest.reward_type == RewardTypes.EMONT:
			emont_bonus_manager.add_bonus(quest.player_uid, {
				EmontBonusType.QUEST: quest.reward_value
			})
			txn_amount_type = TxnAmountTypes.IN_GAME_EMONT
		elif quest.reward_type == RewardTypes.RANDOM_EMONT:
			quest.reward_value = quest_info['calc_reward_func'](quest, current_ts)
			emont_bonus_manager.add_bonus(quest.player_uid, {
				EmontBonusType.QUEST: quest.reward_value
			})
			txn_amount_type = TxnAmountTypes.IN_GAME_EMONT
		elif quest.reward_type == RewardTypes.HONGBAO:
			user_balance_manager.add_balance_value(quest.player_uid, BalanceTypes.HONGBAO, quest.reward_value)
			txn_amount_type = TxnAmountTypes.LUNAR_HONGBAO
		else:
			txn_amount_type = TxnAmountTypes.UNDEFINED

		transaction_manager.create_transaction(
			player_uid=quest.player_uid,
			player_address=quest.player_address,
			txn_type=TxnTypes.CLAIM_QUEST,
			txn_info=quest.quest_id,
			amount_type=txn_amount_type,
			amount_value=quest.reward_value,
			status=TxnStatus.FINISHED
		)

		quest.update_time = current_ts

		if quest.quest_level == len(quest_info["quest_target"]) - 1 and quest.quest_type != QuestTypes.CIRCLE:
			quest.status = QuestStatus.CLOSED
		else:
			if quest.quest_type == QuestTypes.CIRCLE and quest.quest_level == len(quest_info["quest_target"]) - 1:
				# Case CIRCLE QUEST, reset it to level 0
				new_level = 0
				extra_data = json.loads(quest.extra or "{}")
				extra_data["claimed_points"] = extra_data.get("claimed_points", 0) + quest.quest_target
				quest.extra = json.dumps(extra_data)
			else:
				new_level = quest.quest_level + 1

			quest.quest_level = new_level
			quest.quest_target = quest_info["quest_target"][quest.quest_level]
			quest.reward_type = quest_info["reward_type"][quest.quest_level]
			quest.reward_value = quest_info["reward_value"][quest.quest_level]

			temp = quest_info['update_progress_func'](quest, current_ts)

			quest_progress = temp if not isinstance(temp, tuple) else temp[0]
			quest.quest_progress = min(quest.quest_target, quest_progress)
			quest.status = QuestStatus.TO_DO if quest.quest_progress < quest.quest_target else QuestStatus.TO_CLAIM

			quest_extra_data = None if not isinstance(temp, tuple) else temp[1]
			extra_data = json.loads(quest.extra or "{}")
			extra_data["info"] = quest_extra_data
			quest.extra = json.dumps(extra_data)

		quest.save()

	return quest
