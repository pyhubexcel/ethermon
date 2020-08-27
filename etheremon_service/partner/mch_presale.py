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

context.init_django('../', 'settings')
application = get_wsgi_application()

from common.logger import log
from etheremon_lib.models import EtheremonDB
from etheremon_lib.config import *

SMART_CONTRACT_METHOD_ID_LENGTH = 10
START_BLOCK = 6367418
SMART_CONTRACT_BLOCK_STEP = 1000000

SMART_CONTRACT_ADDRESS = "0x946048a75af11c300a274344887ec39452218b3d"

class MCHFlag:
	FLAG_NONE = 0
	FLAG_ETHEREMON_PLAYER = 1
	FLAG_FAKE = 2
	FLAG_CRYPTOKITTIES = 3

def crawl_txn():

	start_block = EtheremonDB.PartnerMchPresaleTab.objects.all().aggregate(Max('latest_block_number'))
	if not start_block["latest_block_number__max"]:
		start_block = START_BLOCK
	else:
		start_block = start_block["latest_block_number__max"]

	old_block = 0
	while True:
		end_block = start_block + SMART_CONTRACT_BLOCK_STEP

		time.sleep(3)
		transaction_list = get_txn_list(SMART_CONTRACT_ADDRESS, start_block, end_block, ETHERSCAN_API_KEYS["cron_3"])
		if transaction_list is None:
			break

		if len(transaction_list) == 0:
			break

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
			eth_amount = float(eth_amount*1.0 / (10**18))
			sender = str(transaction["from"]).lower()
			txn_hash = str(transaction["hash"]).lower()

			current_record = EtheremonDB.PartnerMchPresaleTab.objects.filter(player=sender).first()
			if not current_record:
				# check etheremon player
				mch_flag = MCHFlag.FLAG_NONE
				country = ""
				etheremon_user = EtheremonDB.UserTab.objects.filter(address=sender).first()
				if etheremon_user:
					mch_flag = MCHFlag.FLAG_ETHEREMON_PLAYER
					country = etheremon_user.country
				else:
					if EtheremonDB.EmaMonsterDataTab.objects.filter(trainer=sender).count() > 0:
						mch_flag = MCHFlag.FLAG_ETHEREMON_PLAYER

				EtheremonDB.PartnerMchPresaleTab(
					player=sender,
					amount=eth_amount,
					flag=mch_flag,
					country=country,
					txn_count=1,
					latest_block_number=block_number
				).save()
			else:
				if current_record.latest_block_number >= block_number:
					continue
				current_record.amount += eth_amount
				current_record.txn_count += 1
				current_record.latest_block_number = block_number
				current_record.save()

		if start_block == old_block:
			break
		old_block = start_block

if __name__ == "__main__":
	crawl_txn()