import os
import sys
import time
from random import randint

from etheremon_lib.burn_manager import BurnStatus, BurnRewardTypes
from etheremon_lib.emont_bonus_manager import EmontBonusType
from etheremon_lib.transaction_manager import TxnStatus, TxnTypes, TxnAmountTypes

curr_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curr_dir)
sys.path.append(os.path.join(curr_dir, '../../'))

from common import context
from django.core.wsgi import get_wsgi_application

context.init_django('../', 'settings')
application = get_wsgi_application()

from web3 import Web3
from common.logger import log
from etheremon_lib.config import *
from etheremon_lib import ema_settings_manager, transaction_manager, burn_manager, ema_energy_manager, \
	emont_bonus_manager, user_manager
from etheremon_lib.etherscan_client import get_txn_list
from etheremon_lib.infura_client import InfuraClient

SMART_CONTRACT_METHOD_ID_LENGTH = 10
SMART_CONTRACT_BLOCK_STEP = 100000

INFURA_API_URL = INFURA_API_URLS["cron_task"]
ETHERSCAN_API_KEY = ETHERSCAN_API_KEYS["cron_2"]

BURN_MON_METHOD = "0x4d8a369e"


def update_burn_mon_contract():
	infura_client = InfuraClient(INFURA_API_URL)
	current_block = infura_client.getCurrentBlock() - 5

	start_block = ema_settings_manager.get_setting_value(EmaSetting.SETTING_CONTRACT_BURN_MON)
	end_block = start_block + SMART_CONTRACT_BLOCK_STEP

	start_time = time.time()
	transaction_list = get_txn_list(EtheremonBurnMonContract.ADDRESS, start_block, end_block, ETHERSCAN_API_KEY)
	latest_load_block = None
	log.data("start_update_burn_mon_contract|current_block=%s,start_block=%s,end_block=%s,len_txn=%s", current_block, start_block, end_block, len(transaction_list))

	monster_id_set = set()

	for transaction in transaction_list:
		if len(transaction["input"]) < SMART_CONTRACT_METHOD_ID_LENGTH:
			log.warn("invalid_smart_contract_txn|transaction=%s", transaction)
			continue
		if int(transaction.get("isError", 1)) != 0:
			continue
		if int(transaction.get("txreceipt_status")) != 1:
			continue
		if int(transaction["blockNumber"]) > current_block:
			continue

		latest_load_block = int(transaction["blockNumber"]) if latest_load_block is None else max(latest_load_block, int(transaction["blockNumber"]))
		method_id = transaction["input"][0:SMART_CONTRACT_METHOD_ID_LENGTH]

		if method_id == BURN_MON_METHOD:
			contract_mon_id_hash = "0x" + transaction["input"][SMART_CONTRACT_METHOD_ID_LENGTH:SMART_CONTRACT_METHOD_ID_LENGTH + 64]
			contract_mon_id = Web3.toInt(hexstr=contract_mon_id_hash)
			contract_burn_id_hash = "0x" + transaction["input"][SMART_CONTRACT_METHOD_ID_LENGTH + 64:SMART_CONTRACT_METHOD_ID_LENGTH + 128]
			contract_burn_id = Web3.toInt(hexstr=contract_burn_id_hash)

			mon_id, burn_id = burn_manager.get_mon_id_from_contract_burn_id(contract_burn_id)
			burn_request = burn_manager.get_burn_request_by_id(burn_id)

			if not burn_request or burn_request.mon_id != contract_mon_id:
				logging.exception("burn_mon_failed|contract_burn_id=%s,txn_hash=%s", contract_burn_id, transaction["hash"])
				continue

			if burn_request.status in [BurnStatus.FINISHED, BurnStatus.FAILED]:
				logging.exception("burn_already_finished|contract_burn_id=%s,txn_hash=%s", contract_burn_id, transaction["hash"])
				continue

			try:
				with transaction.atomic():
					player_uid = user_manager.get_uid_by_address_default_0(burn_request.player_address)

					if burn_request.reward_value > 0:
						# Only if there is reward
						if burn_request.reward_type == BurnRewardTypes.ENERGY:
							ema_energy_manager.add_energy(burn_request.player_address, burn_request.reward_value)
						elif burn_request.reward_type == BurnRewardTypes.IN_GAME_EMONT:
							emont_bonus_manager.add_bonus(player_uid, {
								EmontBonusType.EVENT_BONUS: burn_request.reward_value
							})

						transaction_manager.create_transaction(
							player_uid=player_uid,
							player_address=burn_request.player_address,
							txn_type=TxnTypes.BURN_MON_REWARD,
							txn_info="mon %s" % burn_request.mon_id,
							amount_type=TxnAmountTypes.IN_GAME_EMONT if burn_request.reward_type == BurnRewardTypes.IN_GAME_EMONT else TxnAmountTypes.ENERGY,
							amount_value=burn_request.reward_value,
							status=TxnStatus.FINISHED,
							txn_hash=transaction["hash"]
						)

						# 300 EMONT BONUS
						# if burn_request.mon_level >= 30 and randint(1, 100) <= 3:
						if randint(1, 100) <= 3:
							additional_bonus = 500

							emont_bonus_manager.add_bonus(player_uid, {
								EmontBonusType.EVENT_BONUS: additional_bonus
							})

							transaction_manager.create_transaction(
								player_uid=player_uid,
								player_address=burn_request.player_address,
								txn_type=TxnTypes.BURN_MON_REWARD_BONUS,
								txn_info="mon %s" % burn_request.mon_id,
								amount_type=TxnAmountTypes.IN_GAME_EMONT,
								amount_value=additional_bonus,
								status=TxnStatus.FINISHED,
								txn_hash=transaction["hash"]
							)

					burn_request.status = BurnStatus.FINISHED
					burn_request.save()
			except:
				logging.exception("burn_mon_failed|contract_burn_id=%s,txn_hash=%s", contract_burn_id, transaction["hash"])
				continue

	record_block = latest_load_block + 1 if latest_load_block is not None else end_block + 1
	record_block = min(record_block, current_block)

	ema_settings_manager.set_or_create_setting(
		setting_id=EmaSetting.SETTING_CONTRACT_BURN_MON,
		name="burn mon contract",
		value=record_block
	)
	elapsed = time.time() - start_time
	if elapsed < 5:
		time.sleep(5-elapsed)
	log.data("end_update_burn_mon_contract|record_block=%s,total_txn=%s,total_monster=%s,elapsed=%s",
		record_block, len(transaction_list), len(monster_id_set), elapsed)


if __name__ == "__main__":
	update_burn_mon_contract()
