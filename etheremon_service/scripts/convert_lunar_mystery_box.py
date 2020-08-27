# After moving win reward to quest, some forgot to claim the old win reward.
# This script is to add this amount back to the emont balance.
from django.db import transaction

from etheremon_lib import transaction_manager
from etheremon_lib.models import EtheremonDB
from etheremon_lib.transaction_manager import TxnTypes, TxnAmountTypes, TxnStatus


def convert_mystery_box():
	mystery_rewards = EtheremonDB.TransactionTab.objects\
		.filter(txn_type=TxnTypes.LUNAR_19_REWARD)\
		.filter(amount_type=TxnAmountTypes.LUNAR_MYSTERY_BOX)\
		.filter(status=TxnStatus.INIT)

	with transaction.atomic():
		for reward in mystery_rewards:
			print("Converting", reward.id)
			for i in range(0, 5):
				transaction_manager.create_transaction(
					reward.player_uid,
					reward.player_address,
					TxnTypes.LUNAR_19_REWARD_MYSTERY_BOX,
					"unbox mystery - lvl",
					TxnAmountTypes.ADV_LEVEL_STONE_1,
					1,
					status=TxnStatus.INIT,
				)

			transaction_manager.create_transaction(
				reward.player_uid,
				reward.player_address,
				TxnTypes.LUNAR_19_REWARD_MYSTERY_BOX,
				"unbox mystery - mon",
				TxnAmountTypes.LUNAR_MON,
				1,
				status=TxnStatus.INIT,
			)

			reward.status = TxnStatus.FINISHED
			reward.save()
