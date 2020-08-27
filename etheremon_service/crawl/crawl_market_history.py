import os
import sys
import time
import json
import math
import requests

curr_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curr_dir)
sys.path.append(os.path.join(curr_dir, '../../'))

from common import context
from common.utils import get_timestamp
from django.core.wsgi import get_wsgi_application
from etheremon_lib.infura_client import InfuraClient
from etheremon_lib.etherscan_client import get_txn_list

context.init_django('../', 'settings')
application = get_wsgi_application()

from common.logger import log
from etheremon_lib.models import EtheremonDB
from etheremon_lib.config import *
from web3 import Web3, HTTPProvider

SMART_CONTRACT_METHOD_ID_LENGTH = 10

INFURA_API_URL = "https://mainnet.infura.io/h2s5XPxRh0XcbzUvI53"
CONTRACT_ADDRESS = "0x4ba72f0f8dad13709ee28a992869e79d0fe47030"#"0x4ba72f0f8dad13709ee28a992869e79d0fe47030"
BUY_METHOD_ID = "0xd6f551e4"

ETHERSCAN_API_KEY = ETHERSCAN_API_KEYS["cron_4"]

def get_internal_txn(apikey, txn_hash):
	try:
		params = {
			"module": "account",
			"action": "txlistinternal",
			"apikey": apikey,
			"txhash": txn_hash
		}
		response = requests.get("https://api.etherscan.io/api", params=params)
		if response.status_code != 200:
			print "ERROR|ETHERSCAN|http_status_code=%s" % response.status_code
			return None
		response_data = response.json()
		if int(response_data["status"]) != 1:
			print "ERROR|ETHERSCAN|data_status=%s" % response_data["status"]
			return []
		return response_data["result"]
	except Exception as error:
		print "ERROR|ETHERSCAN|Exception=%s" % error.message
		return None

def crawl_trade_txn(from_id):
	trade_buy_records = EtheremonDB.RevenueTxnTab.objects.filter(contract_address=CONTRACT_ADDRESS).filter(method_id=BUY_METHOD_ID).filter(id__gt=from_id).order_by("id").all()
	infura_client = InfuraClient(INFURA_API_URL)

	for trade_buy_record in trade_buy_records:
		txn_hash = trade_buy_record.txn_hash.lower()
		if EtheremonDB.MarketHistoryTab.objects.filter(txn_hash=txn_hash).exists():
			continue

		txn_data = infura_client.web3_client.eth.getTransaction(txn_hash)
		input_data = txn_data.input

		method_id = input_data[0:SMART_CONTRACT_METHOD_ID_LENGTH]
		monster_id_hash = "0x" + input_data[SMART_CONTRACT_METHOD_ID_LENGTH:SMART_CONTRACT_METHOD_ID_LENGTH + 64]
		monster_id = Web3.toInt(hexstr=monster_id_hash)

		market_history_price = int(trade_buy_record.eth_amount * (10 ** 6))
		market_history_records = list(EtheremonDB.MarketHistoryTab.objects.filter(monster_id=monster_id).filter(txn_hash="").order_by("id").all())
		if len(market_history_records) > 0:
			first_record = market_history_records[0]
			if abs(first_record.price - market_history_price) > 1000:
				print "ERROR|price_mismatch|txn_hash=%s,monster_id=%s,record_price=%s,revenue_price=%s" % (txn_hash, monster_id, first_record.price, market_history_price)
				return
			first_record.price = market_history_price
			first_record.txn_hash = txn_hash
			first_record.buyer = trade_buy_record.sender
			first_record.save()
			print "MAP|txn_hash=%s,history_id=%s,revenue_id=%s" %(txn_hash, first_record.id, trade_buy_record.id)
		else:
			print "ERROR|not_match|txn_hash=%s,monster_id=%s,price=%s,record_len=%s" % (txn_hash, monster_id, market_history_price, len(market_history_records))
			break

def craw_market_seller():
	empty_seller_records = EtheremonDB.MarketHistoryTab.objects.order_by('id').all()
	for empty_seller_record in empty_seller_records:
		if empty_seller_record.txn_hash == "":
			print "ERROR|no_txn_hash|id=%s" % empty_seller_record.id
			return
		internal_txn_data = get_internal_txn(ETHERSCAN_API_KEY, empty_seller_record.txn_hash)
		if not internal_txn_data:
			print "ERROR|record_id=%s" % empty_seller_record.id
		seller = internal_txn_data[0]["to"].lower()
		empty_seller_record.seller = seller
		empty_seller_record.save()
		print "UPDATE_SELLER|id=%s,txn_hash=%s,seller=%s" % (empty_seller_record.id, empty_seller_record.txn_hash, seller)
		time.sleep(0.1)

if __name__ == "__main__":
	craw_market_seller()
