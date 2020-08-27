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
from etheremon_lib.config import *
from etheremon_lib import ema_settings_manager
from etheremon_lib.etherscan_client import get_txn_list
from etheremon_lib.infura_client import InfuraClient
from helper import _sync_player_dex

SMART_CONTRACT_METHOD_ID_LENGTH = 10
SMART_CONTRACT_BLOCK_STEP = 100000

INFURA_API_URL = INFURA_API_URLS["cron_task"]
ETHERSCAN_API_KEY = ETHERSCAN_API_KEYS["cron_1"]

def update_erc721_contract():
	infura_client = InfuraClient(INFURA_API_URL)
	current_block = infura_client.getCurrentBlock() - 2

	start_block = ema_settings_manager.get_setting_value(EmaSetting.SETTING_CONTRACT_ERC721_BLOCK)
	end_block = start_block + SMART_CONTRACT_BLOCK_STEP

	start_time = time.time()
	transaction_list = get_txn_list(EtheremonERC721Contract.ADDRESS, start_block, end_block, ETHERSCAN_API_KEY)
	if transaction_list is None:
		return

	log.data("start_update_erc721_contract|current_block=%s,start_block=%s,end_block=%s,len_txn=%s", current_block, start_block, end_block, len(transaction_list))

	latest_load_block = start_block
	sender_set = set()
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
		sender = str(transaction["from"]).lower()
		sender_set.add(sender)
		log.info("update_erc721|txn_hash=%s,sender=%s", transaction["hash"], sender)


	if sender_set:
		log.info("update_erc721|len_sender=%s,latest_load_block=%s", len(sender_set), latest_load_block)
		data_contract = infura_client.getDataContract()
		for player in sender_set:
			result = _sync_player_dex(data_contract, player)
			if result is False:
				log.warn("sync_player_fail|player=%s", player)
				return

	record_block = latest_load_block
	if len(transaction_list) > 0:
		record_block += 1
		if record_block > current_block:
			record_block = current_block

	ema_settings_manager.set_setting(EmaSetting.SETTING_CONTRACT_ERC721_BLOCK, record_block)
	elapsed = time.time() - start_time
	if elapsed < 5:
		time.sleep(5-elapsed)
	log.data("end_update_erc721_contract|record_block=%s,total_txn=%s,total_player=%s,elapsed=%s",
		record_block, len(transaction_list), len(sender_set), elapsed)


if __name__ == "__main__":
	update_erc721_contract()