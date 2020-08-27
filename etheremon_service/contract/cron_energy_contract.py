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


SMART_CONTRACT_METHOD_ID_LENGTH = 10
SMART_CONTRACT_BLOCK_STEP = 100000

INFURA_API_URL = INFURA_API_URLS["cron_task"]
ETHERSCAN_API_KEY = ETHERSCAN_API_KEYS["cron_1"]

def update_energy_contract():
	infura_client = InfuraClient(INFURA_API_URL)
	current_block = infura_client.getCurrentBlock() - 2

	start_block = ema_settings_manager.get_setting_value(EmaSetting.SETTING_CONTRACT_ENERGY_BLOCK)
	end_block = start_block + SMART_CONTRACT_BLOCK_STEP

	start_time = time.time()
	transaction_list = get_txn_list(EtheremonEnergyContract.ADDRESS, start_block, end_block, ETHERSCAN_API_KEY)
	if transaction_list is None:
		return

	log.data("start_update_energy_contract|current_block=%s,start_block=%s,end_block=%s,len_txn=%s", current_block, start_block, end_block, len(transaction_list))

	'''
	if len(transaction_list) > 50:
		log.data("update_energy|cut_down_txn|current_block=%s,start_block=%s,end_block=%s", current_block, start_block, end_block)
		transaction_list = transaction_list[:50]
	'''

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
		log.info("update_energy_contract|txn_hash=%s,sender=%s", transaction["hash"], sender)

	if sender_set:
		time.sleep(5)
		log.info("update_energy_contract|len_sender=%s,latest_load_block=%s", len(sender_set), latest_load_block)
		energy_contract = infura_client.getEnergyContract()
		current_ts = get_timestamp()
		for sender in sender_set:
			(free_amount, paid_amount, last_claim) = energy_contract.call().getPlayerEnergy(sender)
			log.info("player_energy_update|sender=%s,current_block=%s,free_amount=%s,paid_amount=%s,last_claim=%s", sender, current_block, free_amount, paid_amount, last_claim)
			record = EtheremonDB.EmaPlayerEnergyTab.objects.filter(trainer=sender).first()
			if record:
				if free_amount > record.free_amount:
					latest_gap = free_amount - record.free_amount
					new_available_energy = record.init_amount + free_amount + record.paid_amount - record.consumed_amount - record.invalid_amount
					if new_available_energy > 50:
						deducted_amount = new_available_energy - 50
						if deducted_amount > latest_gap:
							record.invalid_amount += latest_gap
						else:
							record.invalid_amount += deducted_amount
				record.free_amount = free_amount
				record.paid_amount = paid_amount
				record.last_claim_time = last_claim
				record.update_time = current_ts
				record.save()
			else:
				EtheremonDB.EmaPlayerEnergyTab.objects.create(
					trainer=sender,
					init_amount=0,
					free_amount=free_amount,
					paid_amount=paid_amount,
					invalid_amount=0,
					consumed_amount=0,
					last_claim_time=last_claim,
					create_time=current_ts,
					update_time=current_ts
				)

	record_block = latest_load_block
	if len(transaction_list) > 0:
		record_block += 1
		if record_block > current_block:
			record_block = current_block

	ema_settings_manager.set_setting(EmaSetting.SETTING_CONTRACT_ENERGY_BLOCK, record_block)
	elapsed = time.time() - start_time
	if elapsed < 5:
		time.sleep(5-elapsed)
	log.data("end_update_energy_contract|record_block=%s,total_txn=%s,total_player=%s,elapsed=%s", record_block, len(transaction_list), len(sender_set), elapsed)


if __name__ == "__main__":
	update_energy_contract()






