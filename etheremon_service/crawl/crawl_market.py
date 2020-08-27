import os
import sys
import time
import json

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

SMART_CONTRACT_METHOD_ID_LENGTH = 10
SMART_CONTRACT_BLOCK_STEP = 100000

MARKET_PRICE_DIVISION = (10 ** 18) / (10 ** 6)

INFURA_API_URL = INFURA_API_URLS["general"] #'http://localhost:8545'

def crawl_market():
	infura_client = InfuraClient(INFURA_API_URL)
	trade_contract = infura_client.getTradeContract()

	total_sell = trade_contract.call().getTotalSellingMonsters()
	total_borrow = trade_contract.call().getTotalBorrowingMonsters()
	current_block_number = infura_client.getCurrentBlock()
	log.data("start_crawl_market|total_sell=%s,total_borrow=%s,block_number=%s", total_sell, total_borrow, current_block_number)

	# clear all table
	EtheremonDB.EmaMarketTab.objects.filter(id__gte=0).delete()

	# clone sell
	current_ts = get_timestamp()
	index = 0
	while index < total_sell:
		try:
			(obj_id, class_id, exp, bp, trainer, create_index, price, create_time) = trade_contract.call().getSellingItem(index)
		except Exception as error:
			log.warn("query_sell_data_error|index=%s,error=%s", index, error.message)
			time.sleep(5)
			infura_client = InfuraClient(INFURA_API_URL)
			trade_contract = infura_client.getTradeContract()
			continue

		price = price/MARKET_PRICE_DIVISION
		extra_data = {}

		EtheremonDB.EmaMarketTab.objects.create(
			type=EmaMarketType.SELL,
			player=trainer,
			monster_id=obj_id,
			price=price,
			status=EmaMarketStatus.NONE,
			extra_data=json.dumps(extra_data),
			create_time=create_time
		)
		index += 1

	# clone borrow
	index = 0
	while index < total_borrow:
		try:
			(obj_id, owner, borrower, price, lent, create_time, release_time) = trade_contract.call().getBorrowingItem(index)
		except Exception as error:
			log.warn("query_borrow_data_error|index=%s,error=%s", index, error.message)
			time.sleep(5)
			infura_client = InfuraClient(INFURA_API_URL)
			trade_contract = infura_client.getTradeContract()
			continue

		owner = owner.lower()
		price = price/MARKET_PRICE_DIVISION
		extra_data = {
			"borrower": borrower,
			"create_time": create_time,
			"release_time": release_time
		}
		status = EmaMarketStatus.NONE
		if lent:
			status = EmaMarketStatus.LENT

		EtheremonDB.EmaMarketTab.objects.create(
			type=EmaMarketType.BORROW,
			player=owner,
			monster_id=obj_id,
			price=price,
			status=status,
			extra_data=json.dumps(extra_data),
			create_time=create_time
		)
		index += 1

	log.data("end_crawl_market|block=%s,elapsed=%s", current_block_number, time.time() - current_ts)



def fix_borrow_problem():

	infura_client = InfuraClient(INFURA_API_URL)
	trade_contract = infura_client.getTradeContract()

	borrow_records = EtheremonDB.EmaMarketTab.objects.filter(type=EmaMarketType.BORROW).all()
	for borrow_record in borrow_records:
		extra_data = json.loads(borrow_record.extra_data)
		release_time = extra_data.get("release_time", 0)
		if release_time > 2061775712:
			(sell_price, lending_price, lent, release_time) = trade_contract.call().getTradingInfo(borrow_record.monster_id)
			extra_data["release_time"] = int(release_time)
			borrow_record.extra_data = json.dumps(extra_data)
			borrow_record.save()
			log.info("fix_borrow|monster_id=%s", borrow_record.monster_id)


if __name__ == "__main__":
	crawl_market()
	fix_borrow_problem()

