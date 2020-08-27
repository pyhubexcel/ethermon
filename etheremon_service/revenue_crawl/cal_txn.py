import os
import sys
import time
import json
import datetime

curr_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curr_dir)
sys.path.append(os.path.join(curr_dir, '../../'))

from common import context
from django.db.models import Max
from common.utils import get_timestamp
from django.core.wsgi import get_wsgi_application
from etheremon_lib.infura_client import InfuraClient
from etheremon_lib.etherscan_client import get_txn_list
from revenue_constants import *

context.init_django('../', 'settings')
application = get_wsgi_application()

from common.logger import log
from etheremon_lib.models import EtheremonDB
from etheremon_lib.config import *

SMART_CONTRACT_METHOD_ID_LENGTH = 10
#START_BLOCK = 4745164
SMART_CONTRACT_BLOCK_STEP = 1000000


START_BLOCK = {"0xcaef67f72114b4d2b4f43e7407455285b7de8de5": 4745164, "0x6c8dce6d842e0d9d109dc4c69f35cf8904fc4cbf": 4745164, "0x57964e649ea3735757d6898ca56f135f4437e554": 8900082, "0x16ecc82b4e3e5ff5a4db8510ed191282a37639b0": 4745164, "0xcdf7cfc9f7c129a0d7aec376bc205ab87fc878e1": 4745164, }

ACTIVE_SMART_CONTRACTS = [
	#"0x4ba72f0f8dad13709ee28a992869e79d0fe47030",  # trade
	#"0xa6ff73743b2fd8dedfacea4067a51ef86d249491",  # transform
	"0xcaef67f72114b4d2b4f43e7407455285b7de8de5",  # gym
	"0x6c8dce6d842e0d9d109dc4c69f35cf8904fc4cbf",  #energy
	"0x57964e649ea3735757d6898ca56f135f4437e554", # new trade
	"0x16ecc82b4e3e5ff5a4db8510ed191282a37639b0", # transform 2
	"0xcdf7cfc9f7c129a0d7aec376bc205ab87fc878e1", # adventure
]

def _getDate(ts):
	return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')

def _getDateInInteger(ts):
	return int(datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d'))

def cal_txn(contract_address, default_block=START_BLOCK):
	total_count = 0

	start_block = EtheremonDB.RevenueTxnTab.objects.filter(contract_address=contract_address).all().aggregate(Max('block_number'))
	if not start_block["block_number__max"]:
		start_block = default_block[contract_address]
	else:
		start_block = start_block["block_number__max"]


	print start_block
	while True:
		end_block = start_block + SMART_CONTRACT_BLOCK_STEP

		time.sleep(3)
		transaction_list = get_txn_list(contract_address, start_block, end_block, ETHERSCAN_API_KEYS["cron_3"])
		if transaction_list is None:
			break

		if len(transaction_list) == 0:
			break


		new_row = 0
		for transaction in transaction_list:
			if len(transaction["input"]) < SMART_CONTRACT_METHOD_ID_LENGTH:
				log.warn("invalid_smart_contract_txn|transaction=%s", transaction)
				continue
			if int(transaction.get("isError", 1)) != 0:
				continue
			if int(transaction.get("txreceipt_status")) != 1:
				continue

			block_number = int(transaction["blockNumber"])
			start_block = max(start_block, block_number)

			eth_amount = long(transaction["value"])
			if eth_amount == 0:
				continue

			txn_time = int(transaction["timeStamp"])
			catch_date_str = _getDate(txn_time)
			catch_date_int = _getDateInInteger(txn_time)

			eth_amount = float(eth_amount*1.0 / (10**18))
			if catch_date_str not in ETH_PRICE_DICT:
				#print "--- missing ETH price:", catch_date_str
				#break
				usd_amount = 0
			else :
				usd_amount = float(eth_amount * ETH_PRICE_DICT[catch_date_str])

			method_id = str(transaction["input"][0:SMART_CONTRACT_METHOD_ID_LENGTH]).lower()
			sender = str(transaction["from"]).lower()
			txn_hash = str(transaction["hash"]).lower()

			current_record = EtheremonDB.RevenueTxnTab.objects.filter(txn_hash=txn_hash).first()
			if not current_record:
				EtheremonDB.RevenueTxnTab(
					contract_address=contract_address,
					method_id=method_id,
					txn_hash=txn_hash,
					sender=sender,
					eth_amount=eth_amount,
					usd_amount=usd_amount,
					block_number=block_number,
					create_date=catch_date_int,
					timestamp=txn_time
				).save()
				new_row += 1
				total_count += 1
		if new_row == 0:
			break

	print "query:contract=%s,total_added=%s,block=%s" % (contract_address, total_count, start_block)



def call() :
	for active_contract in ACTIVE_SMART_CONTRACTS:
		cal_txn(active_contract)

if __name__ == "__main__":
	contract_address = sys.argv[1]
	default_block = None
	if len(sys.argv) > 2:
		default_block = int(sys.argv[2])
	if contract_address == "all":
		for active_contract in ACTIVE_SMART_CONTRACTS:
			cal_txn(active_contract, default_block)
	else:
		cal_txn(contract_address, default_block)