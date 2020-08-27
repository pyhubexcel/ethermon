from common.utils import get_timestamp
from etheremon_lib import user_manager
from etheremon_lib.models import EtheremonDB


class BalanceTypes:
	UNDEFINED = 0

	HONGBAO = 100
	HONGBAO_ADVENTURE = 101


class BalanceStatus:
	ACTIVE = 0
	SUSPENDED = 1


def create_balance_obj(player_uid, player_address, balance_type, init_value, status=BalanceStatus.ACTIVE, extra=None):
	return EtheremonDB.BalanceTab.objects.create(
		player_uid=player_uid,
		player_address=player_address,
		balance_type=balance_type,
		balance_value=init_value,
		status=status,
		extra=extra,
		create_time=get_timestamp(),
		update_time=get_timestamp()
	)


def get_balance(player_uid, balance_type):
	obj = EtheremonDB.BalanceTab.objects\
		.filter(player_uid=player_uid)\
		.filter(balance_type=balance_type).first()
	return 0 if not obj else round(obj.balance_value, 2)


def get_balance_obj(player_uid, balance_type):
	return EtheremonDB.BalanceTab.objects\
		.filter(player_uid=player_uid)\
		.filter(balance_type=balance_type).first()


def set_balance_value(player_uid, balance_type, balance_value):
	balance_obj = get_balance_obj(player_uid, balance_type)
	if balance_obj.status != BalanceStatus.ACTIVE:
		raise Exception("balance_inactive")
	if balance_value < 0:
		raise Exception("balance_invalid_amount")

	balance_obj.balance_value = round(balance_value, 2)
	balance_obj.save()
	return balance_obj


def add_balance_value(player_uid, balance_type, balance_value):
	balance_obj = get_balance_obj(player_uid, balance_type)

	if not balance_obj:
		balance_obj = create_balance_obj(player_uid, user_manager.get_address_by_uid(player_uid), balance_type, init_value=0)

	if balance_obj.status != BalanceStatus.ACTIVE:
		raise Exception("balance_inactive")

	balance_obj.balance_value = round(balance_obj.balance_value + balance_value, 2)
	balance_obj.save()
	return balance_obj


def deduct_balance_value(player_uid, balance_type, balance_value):
	balance_obj = get_balance_obj(player_uid, balance_type)
	if not balance_obj or balance_obj.status != BalanceStatus.ACTIVE:
		raise Exception("balance_inactive")
	if balance_obj.balance_value < balance_value:
		raise Exception("balance_insufficient")

	balance_obj.balance_value = round(balance_obj.balance_value - balance_value, 2)
	balance_obj.save()
	return balance_obj
