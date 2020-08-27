import json

from etheremon_lib import cache_manager, ema_monster_manager
from etheremon_lib.models import *
from django.db.models import Sum, Q
from common.utils import get_timestamp
from etheremon_lib.constants import WorldTrainerFlag, ReferClaimStatus, UserType, INFINITY_FUTURE, FREE_MONSTERS


def get_user_info(address):
	return EtheremonDB.UserTab.objects.filter(address=address).first()


def get_user_name(address):
	record = EtheremonDB.UserTab.objects.filter(address=address).first()
	return record.username if record else ""


def get_user_name_with_cache(address):
	username = cache_manager.get_player_username(address)
	if username:
		return username
	else:
		return get_user_name(address)


def create_new_user(address, email, username, ip, country, refer_uid=0):
	current_ts = get_timestamp()
	user = EtheremonDB.UserTab(address=address, email=email, username=username, status=0, flag=0, ip=ip, country=country, refer_uid=refer_uid, create_time=current_ts, update_time=current_ts)
	ema_monster_manager.create_offchain_mons(address)
	user.save()
	return user


def count_referred_friends(uid, from_time=0, to_time=INFINITY_FUTURE):
	res = EtheremonDB.UserTab.objects.filter(refer_uid=uid)
	if from_time > 0:
		res = res.filter(create_time__gte=from_time)
	if to_time < INFINITY_FUTURE:
		res = res.filter(create_time__lte=to_time)
	return res.count()


def get_referred_addresses(uid, from_time=0, to_time=INFINITY_FUTURE):
	res = EtheremonDB.UserTab.objects.filter(refer_uid=uid)
	if from_time > 0:
		res = res.filter(create_time__gte=from_time)
	if to_time < INFINITY_FUTURE:
		res = res.filter(create_time__lte=to_time)
	return res.values('address').distinct()


def get_address_by_uid(uid):
	player_record = EtheremonDB.UserTab.objects.filter(uid=uid).first()
	if not player_record:
		return ""
	return player_record.address


def get_uid_by_address(address):
	player_record = EtheremonDB.UserTab.objects.filter(address=address.lower()).first()
	if not player_record:
		return ""
	return player_record.uid


def get_uid_by_address_default_0(address):
	player_record = EtheremonDB.UserTab.objects.filter(address=address.lower()).first()
	return player_record.uid if player_record else 0


def get_pending_emont_claim(uid):
	return EtheremonDB.ClaimReferTab.objects.filter(uid=uid).filter(status=ReferClaimStatus.STATUS_PENDING).first()


def get_claimed_emont_bonus(uid):
	amount = EtheremonDB.ClaimReferTab.objects.filter(uid=uid).filter(status=ReferClaimStatus.STATUS_COMPLETE).aggregate(Sum('amount'))['amount__sum']
	return amount or 0


def get_claimed_or_pending_emont(uid):
	amount = EtheremonDB.ClaimReferTab.objects.filter(uid=uid).filter(Q(status=ReferClaimStatus.STATUS_COMPLETE) | Q(status=ReferClaimStatus.STATUS_PENDING)).aggregate(Sum('amount'))['amount__sum']
	return amount or 0


def create_emont_claim(uid, amount):
	current_ts = get_timestamp()
	record = EtheremonDB.ClaimReferTab(uid=uid, amount=amount, status=ReferClaimStatus.STATUS_PENDING, create_time=current_ts, update_time=current_ts)
	record.save()
	return record

	
def get_bonus_info(uid):
	return EtheremonDB.EmontBonusTab.objects.filter(uid=uid).first()


def get_world_trainer(address):
	return EtheremonDB.WorldTrainerTab.objects.filter(trainer=address).first()


def count_store_non_free_mons_caught(address, from_time=0, to_time=INFINITY_FUTURE):
	player_data = get_world_trainer(address)
	if not player_data:
		return 0

	purchased_store_mons = json.loads(player_data.extra_data)
	res = 0

	for m in purchased_store_mons:
		if m[0] not in FREE_MONSTERS and from_time <= m[1] <= to_time:
			res += 1

	return res


def create_bonus_info(uid, bonus_data, create_time):
	record = EtheremonDB.EmontBonusTab(uid=uid, bonus_data=bonus_data, create_time=create_time, update_time=create_time)
	record.save()
	return record


def get_user_type(address):
	player_data = EtheremonDB.EmaPlayerRankData.objects.filter(trainer=address).first()
	world_trainer = EtheremonDB.WorldTrainerTab.objects.filter(trainer=address).first()
	user_type = UserType.NORMAL
	if player_data:
		user_type = UserType.VERIFIED
	if world_trainer and world_trainer.flag == WorldTrainerFlag.SPEND_ETH:
		user_type = UserType.PAID_USER
	return user_type


def count_paid_address(address_list):
	return EtheremonDB.WorldTrainerTab.objects.filter(trainer__in=address_list).filter(flag=WorldTrainerFlag.SPEND_ETH).count()


def count_verified_user(address_list):
	return EtheremonDB.EmaPlayerRankData.objects.filter(trainer__in=address_list).count()


def get_paid_addresses(address_list):
	return EtheremonDB.WorldTrainerTab.objects.filter(trainer__in=address_list).filter(flag=WorldTrainerFlag.SPEND_ETH).values('trainer').distinct()


def get_user_general_info(uid=None, address=None):
	if uid is None and address is None:
		return None
	if uid is None:
		uid = get_uid_by_address_default_0(address)
	if address is None:
		address = get_address_by_uid(uid)

	user = EtheremonDB.UserGeneralInfoTab.objects.filter(address=address).first()
	if not user:
		user = EtheremonDB.UserGeneralInfoTab(
			uid=uid,
			address=address,
			tournament_win=0,
			tournament_loss=0,
			create_time=get_timestamp(),
			update_time=get_timestamp(),
		)
		user.save()

	return user
