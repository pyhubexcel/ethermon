import os
import sys
import time

curr_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curr_dir)
sys.path.append(os.path.join(curr_dir, '../../'))

from common import context
from django.core.wsgi import get_wsgi_application
from web3 import Web3, HTTPProvider

context.init_django('../', 'settings')
application = get_wsgi_application()

from common.logger import log
from common.utils import get_timestamp
from etheremon_lib.models import EtheremonDB
from etheremon_lib.config import *
from etheremon_lib import ema_settings_manager
from etheremon_lib.etherscan_client import get_txn_list
from etheremon_lib.infura_client import InfuraClient
from helper import _sync_player_dex

SMART_CONTRACT_METHOD_ID_LENGTH = 10
SMART_CONTRACT_BLOCK_STEP = 100000
FREE_MONSTER_CLASS_IDS = [25, 26, 27]

INFURA_API_URL = INFURA_API_URLS["adventure_task"]
ETHERSCAN_API_KEY = ETHERSCAN_API_KEYS["cron_4"]

ADVENTURE_CLAIM_EARNING_METHOD = "0xcc1ace9a"

def update_adventure_revenue_contract():
	infura_client = InfuraClient(INFURA_API_URL)
	current_block = infura_client.getCurrentBlock() - 2

	start_block = ema_settings_manager.get_setting_value(EmaSetting.SETTING_CONTRACT_ADVENTURE_REVENUE_BLOCK)
	end_block = start_block + SMART_CONTRACT_BLOCK_STEP

	start_time = time.time()
	transaction_list = get_txn_list(EtheremonAdventureRevenueContract.ADDRESS, start_block, end_block, ETHERSCAN_API_KEY)
	if transaction_list is None:
		return

	log.data("start_update_adventure_revenue_contract|current_block=%s,start_block=%s,end_block=%s,len_txn=%s", current_block, start_block, end_block, len(transaction_list))

	latest_load_block = start_block
	current_ts = get_timestamp()
	adventure_data_contract = infura_client.getAdventureDataContract()
	token_id_set = set()
	for transaction in transaction_list:
		if len(transaction["input"]) < SMART_CONTRACT_METHOD_ID_LENGTH:
			log.warn("invalid_smart_contract_txn|transaction=%s", transaction)
			continue
		if int(transaction.get("isError", 1)) != 0:
			continue
		if int(transaction.get("txreceipt_status")) != 1:
			continue

		log.info("update_adventure_revenue_contract|txn_hash=%s", transaction["hash"])

		latest_load_block = max(latest_load_block, int(transaction["blockNumber"]))
		if latest_load_block > current_block:
			return
		method_id = transaction["input"][0:SMART_CONTRACT_METHOD_ID_LENGTH]

		sender = str(transaction["from"]).lower()

		if method_id == ADVENTURE_CLAIM_EARNING_METHOD:
			token_id_hash = "0x" + transaction["input"][SMART_CONTRACT_METHOD_ID_LENGTH:SMART_CONTRACT_METHOD_ID_LENGTH + 64]
			token_id = Web3.toInt(hexstr=token_id_hash)
			token_id_set.add(token_id)
			log.info("claim_earning|sender=%s,token_id=%s,txn_hash=%s", sender, token_id, transaction["hash"])

	if token_id_set:
		for token_id in token_id_set:
			claim_data = adventure_data_contract.call().getTokenClaim(token_id)
			eth_amount = 1.0 * claim_data[1] / 10 ** 18
			emont_amount = 1.0 * claim_data[0] / 10 ** 8
			claim_record = EtheremonDB.EmaAdventureClaimTokenTab.objects.filter(token_id=token_id).first()
			if not claim_record:
				EtheremonDB.EmaAdventureClaimTokenTab.objects.create(
					token_id=token_id,
					claimed_eth_amount=eth_amount,
					claimed_emont_amount=emont_amount,
					update_time=current_ts
				)
			else:
				if claim_record.claimed_eth_amount < eth_amount:
					claim_record.claimed_eth_amount = eth_amount
				if claim_record.claimed_emont_amount < emont_amount:
					claim_record.claimed_emont_amount = emont_amount
				claim_record.update_time = current_ts
				claim_record.save()

	record_block = latest_load_block
	if len(transaction_list) > 0:
		record_block += 1
		if record_block > current_block:
			record_block = current_block

	ema_settings_manager.set_setting(EmaSetting.SETTING_CONTRACT_ADVENTURE_REVENUE_BLOCK, record_block)
	elapsed = time.time() - start_time
	if elapsed < 5:
		time.sleep(5-elapsed)
	log.data("end_update_adventure_contract|record_block=%s,total_txn=%s,elapsed=%s",
		record_block, len(transaction_list), elapsed)


if __name__ == "__main__":
	update_adventure_revenue_contract()

