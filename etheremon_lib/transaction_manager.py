import json

from common.utils import get_timestamp
from etheremon_lib.models import EtheremonDB


class TxnTypes:
	CLAIM_QUEST = 1
	BURN_MON_REWARD = 2
	BURN_MON_REWARD_BONUS = 3

	GENERAL_REWARD = 10

	LUNAR_19_PAYMENT = 100
	LUNAR_19_REWARD = 101
	LUNAR_19_EMONT_REBATE = 102
	LUNAR_19_REWARD_MYSTERY_BOX = 103

	LUCKY_DRAW_PAYMENT = 110
	LUCKY_DRAW_REWARD = 111

	EVENT_KING_OF_HILL = 200


class TxnAmountTypes:
	UNDEFINED = 0

	ENERGY = 1
	IN_GAME_EMONT = 2
	WALLET_EMONT = 3
	IN_GAME_ETH = 4
	WALLET_ETH = 5

	MON = 40

	ADV_LEVEL_STONE_1 = 50
	ADV_LEVEL_STONE_2 = 51

	LUNAR_HONGBAO = 100
	LUNAR_MYSTERY_BOX = 101		# 5x level stone 1 + lunar Mon
	LUNAR_MON = 102				# Mon xx
	LUNAR_NO_PRIZE = 103

	LUCKY_DRAW_NO_PRIZE = 200


class TxnStatus:
	INIT = 0
	PENDING = 1
	FINISHED = 2
	FAILED = 3


def create_transaction(player_uid, player_address, txn_type, txn_info, amount_type, amount_value, status=TxnStatus.INIT, txn_hash=None, extra=None):
	txn = EtheremonDB.TransactionTab(
		player_uid=player_uid,
		player_address=player_address,
		txn_type=txn_type,
		txn_info=txn_info,
		txn_hash=txn_hash,
		status=status,
		amount_type=amount_type,
		amount_value=round(amount_value, 4),
		extra=extra if extra is None else json.dumps(extra),
		create_time=get_timestamp(),
		update_time=get_timestamp(),
	)

	txn.save()
	return txn


def get_player_transactions(player_uid, txn_type, amount_type=None, status=None):
	res = EtheremonDB.TransactionTab.objects.filter(player_uid=player_uid).filter(txn_type=txn_type)
	if amount_type is not None:
		res = res.filter(amount_type=amount_type)
	if status is not None:
		res = res.filter(status=status)
	return res


def get_transaction_by_id(txn_id):
	return EtheremonDB.TransactionTab.objects.filter(id=txn_id).first()
