import os
import sys
import time

curr_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curr_dir)
sys.path.append(os.path.join(curr_dir, '../../'))

from common import context
from django.core.wsgi import get_wsgi_application

context.init_django('../', 'settings')
application = get_wsgi_application()

from common.logger import log
from common.utils import get_timestamp
from etheremon_lib.config import *
from etheremon_lib import ema_settings_manager
from etheremon_lib.etherscan_client import get_txn_list
from etheremon_lib.infura_client import InfuraClient
from etheremon_lib.models import EtheremonDB
from etheremon_lib.crypt import decode_claim_exp_token, decode_claim_win_token, decode_claim_top_token
from etheremon_lib.ema_claim_manager import proceed_pending_exp_claim, proceed_pending_win_claim, proceed_pending_top_claim
from helper import _sync_monster_id

SMART_CONTRACT_METHOD_ID_LENGTH = 10
SMART_CONTRACT_BLOCK_STEP = 100000

INFURA_API_URL = INFURA_API_URLS["cron_task"]
ETHERSCAN_API_KEY = ETHERSCAN_API_KEYS["cron_2"]

CLAIM_MONSTER_EXP_METHOD = "0x42cc5d74"
CLAIM_WIN_RANK_METHOD = "0x95199b24"
CLAIM_TOP_RANK_METHOD = "0x18a75b18"

def update_claim_contract():
	infura_client = InfuraClient(INFURA_API_URL)
	current_block = infura_client.getCurrentBlock() - 5

	start_block = ema_settings_manager.get_setting_value(EmaSetting.SETTING_CONTRACT_CLAIM_BLOCK)
	end_block = start_block + SMART_CONTRACT_BLOCK_STEP

	start_time = time.time()
	transaction_list = get_txn_list(EtheremonClaimContract.ADDRESS, start_block, end_block, ETHERSCAN_API_KEY)
	if transaction_list is None:
		return

	log.data("start_update_claim_contract|current_block=%s,start_block=%s,end_block=%s,len_txn=%s", current_block, start_block, end_block, len(transaction_list))

	latest_load_block = start_block
	monster_id_set = set()
	for transaction in transaction_list:
		if len(transaction["input"]) < SMART_CONTRACT_METHOD_ID_LENGTH:
			log.warn("invalid_smart_contract_txn|transaction=%s", transaction)
			continue
		if int(transaction.get("isError", 1)) != 0:
			continue
		if int(transaction.get("txreceipt_status")) != 1:
			continue

		latest_load_block = max(latest_load_block, int(transaction["blockNumber"]))
		if latest_load_block > current_block:
			return

		method_id = transaction["input"][0:SMART_CONTRACT_METHOD_ID_LENGTH]

		if method_id == CLAIM_MONSTER_EXP_METHOD:
			token_bytes = transaction["input"][SMART_CONTRACT_METHOD_ID_LENGTH:SMART_CONTRACT_METHOD_ID_LENGTH + 64]
			token = token_bytes.decode("hex")
			token_data = decode_claim_exp_token(token)
			request_id = token_data["request_id"]
			monster_id = token_data["monster_id"]

			result = proceed_pending_exp_claim(request_id)
			monster_id_set.add(monster_id)
			log.info("process_exp_claim|request_id=%s,result=%s,txn_hash=%s,monster_id=%s", request_id, result, transaction["hash"], monster_id)
		elif method_id == CLAIM_WIN_RANK_METHOD:
			token_bytes = transaction["input"][SMART_CONTRACT_METHOD_ID_LENGTH:SMART_CONTRACT_METHOD_ID_LENGTH + 64]
			token = token_bytes.decode("hex")
			token_data = decode_claim_win_token(token)
			request_id = token_data["request_id"]
			try:
				result = proceed_pending_win_claim(request_id)
			except:
				logging.exception("process_win_claim_invalid|request_id=%s,txn_hash=%s", request_id, transaction["hash"])
				continue
			log.info("process_win_claim|request_id=%s,result=%s,txn_hash=%s", request_id, result, transaction["hash"])
		elif method_id == CLAIM_TOP_RANK_METHOD:
			token_bytes = transaction["input"][SMART_CONTRACT_METHOD_ID_LENGTH:SMART_CONTRACT_METHOD_ID_LENGTH + 64]
			token = token_bytes.decode("hex")
			token_data = decode_claim_top_token(token)
			request_id = token_data["request_id"]

			result = proceed_pending_top_claim(request_id)
			log.info("process_top_claim|request_id=%s,result=%s,txn_hash=%s", request_id, result, transaction["hash"])

	# update monster id
	if monster_id_set:
		log.info("update_claim_contract|monster_len=%s,latest_load_block=%s,current_block=%s", len(monster_id_set), latest_load_block, current_block)
		data_contract = infura_client.getDataContract()
		for monster_id in monster_id_set:
			result, add_flag, update_flag = _sync_monster_id(data_contract, monster_id)
			if result is False:
				return

	record_block = latest_load_block
	if len(transaction_list) > 0:
		record_block += 1
		if record_block > current_block:
			record_block = current_block

	ema_settings_manager.set_setting(EmaSetting.SETTING_CONTRACT_CLAIM_BLOCK, record_block)
	elapsed = time.time() - start_time
	if elapsed < 5:
		time.sleep(5-elapsed)
	log.data("end_update_claim_contract|record_block=%s,total_txn=%s,total_monster=%s,elapsed=%s",
		record_block, len(transaction_list), len(monster_id_set), elapsed)


if __name__ == "__main__":
	update_claim_contract()