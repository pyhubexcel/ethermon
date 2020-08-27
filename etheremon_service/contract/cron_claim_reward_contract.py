import os
import sys
import time

from etheremon_lib.transaction_manager import TxnStatus

curr_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curr_dir)
sys.path.append(os.path.join(curr_dir, '../../'))

from common import context
from django.core.wsgi import get_wsgi_application

context.init_django('../', 'settings')
application = get_wsgi_application()

from common.logger import log
from etheremon_lib.config import *
from etheremon_lib import ema_settings_manager, transaction_manager
from etheremon_lib.etherscan_client import get_txn_list
from etheremon_lib.infura_client import InfuraClient
from etheremon_lib.crypt import decode_claim_reward_token

SMART_CONTRACT_METHOD_ID_LENGTH = 10
SMART_CONTRACT_BLOCK_STEP = 100000

INFURA_API_URL = INFURA_API_URLS["cron_task"]
ETHERSCAN_API_KEY = ETHERSCAN_API_KEYS["cron_2"]

CLAIM_REWARD_METHOD = "0x47d30418"


def update_claim_reward_contract():
	infura_client = InfuraClient(INFURA_API_URL)
	current_block = infura_client.getCurrentBlock() - 5

	start_block = ema_settings_manager.get_setting_value(EmaSetting.SETTING_CONTRACT_CLAIM_REWARD_BLOCK)
	end_block = start_block + SMART_CONTRACT_BLOCK_STEP

	start_time = time.time()
	transaction_list = get_txn_list(EtheremonClaimRewardContract.ADDRESS, start_block, end_block, ETHERSCAN_API_KEY)
	latest_load_block = None
	log.data("start_update_claim_reward_contract|current_block=%s,start_block=%s,end_block=%s,len_txn=%s", current_block, start_block, end_block, len(transaction_list))

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

		if method_id == CLAIM_REWARD_METHOD:
			token_bytes = transaction["input"][SMART_CONTRACT_METHOD_ID_LENGTH:SMART_CONTRACT_METHOD_ID_LENGTH + 256]
			token = token_bytes.decode("hex")
			token_data = decode_claim_reward_token(token)

			reward_txn_id = token_data["reward_id"]

			try:
				txn = transaction_manager.get_transaction_by_id(reward_txn_id)
				txn.txn_hash = transaction["hash"]
				txn.status = TxnStatus.FINISHED
				txn.save()
			except:
				logging.exception("process_claim_reward_failed|reward_txn_id=%s,txn_hash=%s", reward_txn_id, transaction["hash"])
				continue

	record_block = latest_load_block + 1 if latest_load_block is not None else end_block + 1
	record_block = min(record_block, current_block)

	ema_settings_manager.set_or_create_setting(
		setting_id=EmaSetting.SETTING_CONTRACT_CLAIM_REWARD_BLOCK,
		name="claim reward contract",
		value=record_block
	)
	elapsed = time.time() - start_time
	if elapsed < 5:
		time.sleep(5-elapsed)
	log.data("end_update_claim_reward_contract|record_block=%s,total_txn=%s,total_monster=%s,elapsed=%s",
		record_block, len(transaction_list), len(monster_id_set), elapsed)


if __name__ == "__main__":
	update_claim_reward_contract()
