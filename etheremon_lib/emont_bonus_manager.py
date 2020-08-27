from etheremon_lib import user_manager
from etheremon_lib.constants import EMONT_UNIT
from etheremon_lib.models import *
import json
from common.utils import get_timestamp


class EmontBonusType:
	ADVENTURE_PRESALE_BONUS = "adventure_presale_bonus"
	FACEBOOK = "facebook"
	TWITTER = "twitter"
	QUEST = "quest"
	OLD_WIN_REWARD = "old_win_reward"

	EVENT_BONUS = "event_bonus"

	SPENT = "spent"


def get_bonus_info(uid):
	return EtheremonDB.EmontBonusTab.objects.filter(uid=uid).first()


def get_total_emont_bonus(uid):
	e = get_bonus_info(uid)
	if e:
		bonus_obj = json.loads(e.bonus_data)
		return bonus_obj.get(EmontBonusType.QUEST, 0) \
			+ bonus_obj.get(EmontBonusType.OLD_WIN_REWARD, 0) \
			+ bonus_obj.get(EmontBonusType.EVENT_BONUS, 0) \
			- bonus_obj.get(EmontBonusType.SPENT, 0)
	else:
		return 0


def get_emont_balance(uid):
	return round(get_total_emont_bonus(uid) - 1.0 * user_manager.get_claimed_or_pending_emont(uid) / EMONT_UNIT, 2)


# bonus_dict: {bonus_key: added_in_bonus_value}
def add_bonus(uid, bonus_dict):
	current_ts = get_timestamp()
	bonus_info = get_bonus_info(uid)

	# Case 1st time user
	if not bonus_info:
		bonus_info = EtheremonDB.EmontBonusTab(
			uid=uid,
			bonus_data="{}",
			create_time=current_ts,
		)

	# Update bonus
	bonus_obj = json.loads(bonus_info.bonus_data)
	for bonus_key, bonus_value in bonus_dict.iteritems():
		bonus_obj[bonus_key] = round(bonus_obj.get(bonus_key, 0) + bonus_value, 2)

	bonus_info.bonus_data = json.dumps(bonus_obj)
	bonus_info.update_time = current_ts
	bonus_info.save()

	return bonus_info


def deduct_emont_in_game_balance(uid, spend_value):
	balance = get_emont_balance(uid)
	if not balance or balance < spend_value:
		raise Exception("balance_insufficient")

	bonus_info = get_bonus_info(uid)
	bonus_obj = json.loads(bonus_info.bonus_data)
	bonus_obj[EmontBonusType.SPENT] = round(bonus_obj.get(EmontBonusType.SPENT, 0) + spend_value, 2)
	bonus_info.bonus_data = json.dumps(bonus_obj)
	bonus_info.update_time = get_timestamp()
	bonus_info.save()
	return bonus_info
