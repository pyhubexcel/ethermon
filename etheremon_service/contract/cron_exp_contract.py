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
from etheremon_lib.config import *
from etheremon_lib import ema_settings_manager
from etheremon_lib.crypt import decode_practice_pt, decode_ladder_token1, decode_ladder_token2
from etheremon_lib.infura_client import InfuraClient
from etheremon_lib.etherscan_client import get_txn_list
from helper import _sync_monster_id

SMART_CONTRACT_METHOD_ID_LENGTH = 10
SMART_CONTRACT_BLOCK_STEP = 100000

GYM_CONTRACT_START_TRAINING_METHOD = "0xbfcece9f"
PRACTICE_CONTRACT_PRACTICE_METHOD = "0x315058ae"

INFURA_API_URL = INFURA_API_URLS["cron_task"]

def _update_exp_contract(setting_type, app_key):
	infura_client = InfuraClient(INFURA_API_URL)
	current_block = infura_client.getCurrentBlock() - 2

	start_block = ema_settings_manager.get_setting_value(setting_type)
	end_block = start_block + SMART_CONTRACT_BLOCK_STEP

	start_time = time.time()
	contract_address = None
	if setting_type == EmaSetting.SETTING_EXP_GYM_BLOCK:
		contract_address = EtheremonGymContract.ADDRESS

	transaction_list = get_txn_list(contract_address, start_block, end_block, app_key)
	if transaction_list is None:
		return

	log.data("start_update_exp_contract|setting=%s,start_block=%s,end_block=%s,len_txn=%s", setting_type, start_block, end_block, len(transaction_list))


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

		if setting_type == EmaSetting.SETTING_EXP_GYM_BLOCK:
			if method_id == GYM_CONTRACT_START_TRAINING_METHOD:
				monster_id_hash = "0x" + transaction["input"][SMART_CONTRACT_METHOD_ID_LENGTH:SMART_CONTRACT_METHOD_ID_LENGTH + 64]
				monster_id = Web3.toInt(hexstr=monster_id_hash)
				monster_id_set.add(monster_id)
				log.info("update_gym_contract|monster_id=%s,hash=%s", monster_id, transaction["hash"])

	total_add = 0
	total_update = 0
	if monster_id_set:
		log.info("update_exp_contract|setting=%s,len_monster=%s,latest_load_block=%s", setting_type, len(monster_id_set), latest_load_block)
		data_contract = infura_client.getDataContract()
		for monster_id in monster_id_set:
			result, add_flag, update_flag = _sync_monster_id(data_contract, monster_id)
			if result is False:
				return
			total_add += add_flag
			total_update += update_flag

	block_value = latest_load_block
	if current_block < block_value:
		block_value = current_block

	ema_settings_manager.set_setting(setting_type, block_value)
	elapsed = time.time() - start_time
	if elapsed < 5:
		time.sleep(5-elapsed)
	log.data("end_update_exp_contract|setting=%s,total_add=%s,total_update=%s,start_block=%s,end_block=%s,block_sync=%s,elapsed=%s",
		setting_type, total_add, total_update, start_block, end_block, block_value, elapsed)

def update_exp():
	_update_exp_contract(EmaSetting.SETTING_EXP_GYM_BLOCK, ETHERSCAN_API_KEYS["cron_1"])

if __name__ == "__main__":
	_update_exp_contract(EmaSetting.SETTING_EXP_GYM_BLOCK, ETHERSCAN_API_KEYS["cron_1"])





