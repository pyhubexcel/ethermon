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
from helper import _sync_monster_id

SMART_CONTRACT_METHOD_ID_LENGTH = 10
SMART_CONTRACT_BLOCK_STEP = 100000

INFURA_API_URL = INFURA_API_URLS["cron_task"]
ETHERSCAN_API_KEY = ETHERSCAN_API_KEYS["cron_2"]


MARKET_PRICE_DIVISION = (10 ** 18) / (10 ** 6)
#HISTORY_PRICE_DIVISION = 1000000000000000

TRADING_CONTRACT_PLACE_SELL_METHOD = "0xa4406bcd"
TRADING_CONTRACT_REMOVE_SELL_METHOD = "0x0559c114"
TRADING_CONTRACT_BUY_METHOD = "0xe7fb74c7"

TRADING_CONTRACT_OFFER_BORROW_METHOD = "0x27e90a7e"
TRADING_CONTRACT_REMOVE_OFFER_BORROW_METHOD = "0x2f6dc6b3"
TRADING_CONTRACT_BORROW_METHOD = "0xee422f13"
TRADING_CONTRACT_GET_BACK_LENDING_METHOD = "0x4eb4fe80"

# 1. update market
# 2. update market history
# 3. update monster info
def update_trade_contract():
	infura_client = InfuraClient(INFURA_API_URL)
	current_block = infura_client.getCurrentBlock() - 2

	start_block = ema_settings_manager.get_setting_value(EmaSetting.SETTING_CONTRACT_TRADE_BLOCK)
	end_block = start_block + SMART_CONTRACT_BLOCK_STEP

	start_time = time.time()
	transaction_list = get_txn_list(EtheremonTradeContract.ADDRESS, start_block, end_block, ETHERSCAN_API_KEY)
	if transaction_list is None:
		return

	log.data("start_update_trade_contract|current_block=%s,start_block=%s,end_block=%s,len_txn=%s", current_block, start_block, end_block, len(transaction_list))

	latest_load_block = start_block
	current_ts = get_timestamp()
	monster_id_set = set()
	for transaction in transaction_list:
		if len(transaction["input"]) < SMART_CONTRACT_METHOD_ID_LENGTH:
			log.warn("invalid_smart_contract_txn|transaction=%s", transaction)
			continue
		if int(transaction.get("isError", 1)) != 0:
			continue
		if int(transaction.get("txreceipt_status")) != 1:
			continue

		log.info("update_trade_contract|txn_hash=%s", transaction["hash"])
		latest_load_block = max(latest_load_block, int(transaction["blockNumber"]))
		if latest_load_block > current_block:
			return
		method_id = transaction["input"][0:SMART_CONTRACT_METHOD_ID_LENGTH]
		sender = str(transaction["from"]).lower()

		if method_id == TRADING_CONTRACT_PLACE_SELL_METHOD:
			monster_id_hash = "0x" + transaction["input"][SMART_CONTRACT_METHOD_ID_LENGTH:SMART_CONTRACT_METHOD_ID_LENGTH + 64]
			monster_id = Web3.toInt(hexstr=monster_id_hash)

			price_hash = "0x" + transaction["input"][SMART_CONTRACT_METHOD_ID_LENGTH + 64:SMART_CONTRACT_METHOD_ID_LENGTH + 128]
			original_price = Web3.toInt(hexstr=price_hash)
			price = original_price/MARKET_PRICE_DIVISION

			if price > 1000000000:
				log.warn("price_too_high|txn_hash=%s,origin_price=%s,price=%s", transaction["hash"], original_price, price)
				continue


			current_record = EtheremonDB.EmaMarketTab.objects.filter(type=EmaMarketType.SELL).filter(monster_id=monster_id).first()
			if current_record:
				extra_data = json.loads(current_record.extra_data)
				if current_record.price == price and extra_data.get("txn_hash") == transaction["hash"]:
					continue
				extra_data["txn_hash"] = transaction["hash"]
				current_record.player = sender
				current_record.extra_data = json.dumps(extra_data)
				current_record.price = price
				current_record.save()
			else:
				extra_data = {"txn_hash": transaction["hash"]}
				EtheremonDB.EmaMarketTab.objects.create(
					type=EmaMarketType.SELL,
					player=sender,
					monster_id=monster_id,
					price=price,
					status=EmaMarketStatus.NONE,
					extra_data=json.dumps(extra_data),
					create_time=int(transaction["timeStamp"])
				)

			# update market history
			'''
			price = original_price/HISTORY_PRICE_DIVISION
			monster_record = EtheremonDB.EmaMonsterDataTab.objects.filter(monster_id=monster_id).first()
			if monster_record is None:
				log.warn("monster_id_not_exist|monster_id=%s,trade_hash=%s", monster_id, transaction["hash"])
				return
			market_history_item = EtheremonDB.MarketHistoryTab.objects.filter(monster_id=monster_id, sell_time=int(transaction["timeStamp"])).first()
			if market_history_item:
				continue
			base_bp = (monster_record.b0 + monster_record.b1 + monster_record.b2 + monster_record.b3 + monster_record.b4 + monster_record.b5) / 6
			EtheremonDB.MarketHistoryTab.objects.create(
				monster_id=monster_id,
				price=price,
				is_sold=False,
				block_number=int(transaction["blockNumber"]),
				sell_time=int(transaction["timeStamp"]),
				buy_time=0,
				class_id=monster_record.class_id,
				base_bp=base_bp,
				create_index=monster_record.create_index,
				extra_data=json.dumps({}),
				exp=monster_record.exp
			)
			'''
			log.info("mark_list_monster_for_sell|monster_id=%s,sell_time=%s", monster_id, int(transaction["timeStamp"]))

		elif method_id == TRADING_CONTRACT_REMOVE_SELL_METHOD:
			monster_id_hash = "0x" + transaction["input"][SMART_CONTRACT_METHOD_ID_LENGTH:SMART_CONTRACT_METHOD_ID_LENGTH + 64]
			monster_id = Web3.toInt(hexstr=monster_id_hash)
			EtheremonDB.EmaMarketTab.objects.filter(type=EmaMarketType.SELL).filter(monster_id=monster_id).delete()
			log.info("remove_sell|monster_id=%s,txn_hash=%s", monster_id, transaction["hash"])

		elif method_id == TRADING_CONTRACT_BUY_METHOD:
			monster_id_hash = "0x" + transaction["input"][SMART_CONTRACT_METHOD_ID_LENGTH:SMART_CONTRACT_METHOD_ID_LENGTH + 64]
			monster_id = Web3.toInt(hexstr=monster_id_hash)

			# update monster info
			monster_id_set.add(monster_id)

			monster_record = EtheremonDB.EmaMonsterDataTab.objects.filter(monster_id=monster_id).first()
			if monster_record is None:
				log.warn("monster_id_not_exist|monster_id=%s,trade_hash=%s", monster_id, transaction["hash"])
				return

			txn_hash = transaction["hash"].lower()
			market_record = EtheremonDB.EmaMarketTab.objects.filter(type=EmaMarketType.SELL).filter(monster_id=monster_id).first()
			if not market_record:
				log.warn("market_record_not_exist|txn_hash=%s,monster_id=%s", txn_hash, monster_id)
				continue

			market_history_item = EtheremonDB.MarketHistoryTab.objects.filter(txn_hash=txn_hash).first()
			base_bp = (monster_record.b0 + monster_record.b1 + monster_record.b2 + monster_record.b3 + monster_record.b4 + monster_record.b5) / 6
			if not market_history_item:
				EtheremonDB.MarketHistoryTab.objects.create(
					monster_id=monster_id,
					txn_hash=txn_hash,
					seller=market_record.player,
					buyer=sender,
					price=market_record.price,
					is_sold=True,
					block_number=int(transaction["blockNumber"]),
					sell_time=market_record.create_time,
					buy_time=int(transaction["timeStamp"]),
					class_id=monster_record.class_id,
					base_bp=base_bp,
					create_index=monster_record.create_index,
					extra_data=json.dumps({}),
					exp=monster_record.exp
				)
			market_record.delete()

			log.info("buy_item|monster_id=%s,txn_hash=%s", monster_id, transaction["hash"])

			# update market history
			'''
			if market_history_item is None:
				log.warn("item_sold_not_found|monster_id=%s,hash=%s", monster_id, transaction["hash"])
				continue
			if market_history_item.is_sold:
				continue
			if EtheremonDB.MarketHistoryTab.objects.filter(monster_id=monster_id, buy_time=int(transaction["timeStamp"])).first() is not None:
				log.warn("item_duplicate_buy|monster_id=%s,hash=%s", monster_id, transaction["hash"])
				continue
			monster_record = EtheremonDB.EmaMonsterDataTab.objects.filter(monster_id=monster_id).first()
			if monster_record is None:
				log.warn("monster_id_not_exist|monster_id=%s,trade_hash=%s", monster_id, transaction["hash"])
				return
			base_bp = (monster_record.b0 + monster_record.b1 + monster_record.b2 + monster_record.b3 + monster_record.b4 + monster_record.b5) / 6
			market_history_item.is_sold = True
			market_history_item.buy_time = int(transaction["timeStamp"])
			market_history_item.class_id = monster_record.class_id
			market_history_item.base_bp = base_bp
			market_history_item.create_index = monster_record.create_index
			market_history_item.exp = monster_record.exp
			market_history_item.save()
			log.info("mark_buy_monster|monster_id=%s,buy_time=%s", monster_id, int(transaction["timeStamp"]))
			'''

		elif method_id == TRADING_CONTRACT_OFFER_BORROW_METHOD:
			monster_id_hash = "0x" + transaction["input"][SMART_CONTRACT_METHOD_ID_LENGTH:SMART_CONTRACT_METHOD_ID_LENGTH + 64]
			monster_id = Web3.toInt(hexstr=monster_id_hash)

			price_hash = "0x" + transaction["input"][SMART_CONTRACT_METHOD_ID_LENGTH + 64:SMART_CONTRACT_METHOD_ID_LENGTH + 128]
			price = Web3.toInt(hexstr=price_hash)
			price = price/MARKET_PRICE_DIVISION

			release_time_hash = "0x" + transaction["input"][SMART_CONTRACT_METHOD_ID_LENGTH + 128:SMART_CONTRACT_METHOD_ID_LENGTH + 192]
			release_time = Web3.toInt(hexstr=release_time_hash)

			current_record = EtheremonDB.EmaMarketTab.objects.filter(type=EmaMarketType.BORROW).filter(monster_id=monster_id).first()
			if current_record:
				extra_data = json.loads(current_record.extra_data)
				if current_record.price == price and current_record.status == EmaMarketStatus.NONE and extra_data["release_time"] == release_time and extra_data.get("txn_hash") == transaction["hash"]:
					continue
				extra_data["txn_hash"] = transaction["hash"].lower()
				extra_data["release_time"] = release_time
				extra_data["borrower"] = ""
				current_record.player=sender
				current_record.status = EmaMarketStatus.NONE
				current_record.price = price
				current_record.extra_data = json.dumps(extra_data)
				current_record.save()
			else:
				extra_data = {
					"txn_hash": transaction["hash"].lower(),
					"borrower": "",
					"release_time": release_time
				}
				EtheremonDB.EmaMarketTab.objects.create(
					type=EmaMarketType.BORROW,
					player=sender,
					monster_id=monster_id,
					price=price,
					status=EmaMarketStatus.NONE,
					extra_data=json.dumps(extra_data),
					create_time=current_ts
				)
		elif method_id == TRADING_CONTRACT_REMOVE_OFFER_BORROW_METHOD:
			monster_id_hash = "0x" + transaction["input"][SMART_CONTRACT_METHOD_ID_LENGTH:SMART_CONTRACT_METHOD_ID_LENGTH + 64]
			monster_id = Web3.toInt(hexstr=monster_id_hash)
			EtheremonDB.EmaMarketTab.objects.filter(type=EmaMarketType.BORROW).filter(monster_id=monster_id).delete()
			log.info("remove_borrow|monster_id=%s,txn_hash=%s", monster_id, transaction["hash"])

		elif method_id == TRADING_CONTRACT_BORROW_METHOD:
			monster_id_hash = "0x" + transaction["input"][SMART_CONTRACT_METHOD_ID_LENGTH:SMART_CONTRACT_METHOD_ID_LENGTH + 64]
			monster_id = Web3.toInt(hexstr=monster_id_hash)

			# update monster info
			monster_id_set.add(monster_id)

			current_record = EtheremonDB.EmaMarketTab.objects.filter(type=EmaMarketType.BORROW).filter(monster_id=monster_id).first()
			if not current_record:
				log.error("no_monster_borrow_record|monster_id=%s,txn_hash=%s", monster_id, transaction["hash"])
				break

			extra_data = json.loads(current_record.extra_data)
			extra_data["borrower"] = str(transaction["from"]).lower()
			if extra_data["release_time"] < 10000000:
				extra_data["release_time"] += int(transaction["timeStamp"])
			current_record.status = EmaMarketStatus.LENT
			current_record.extra_data = json.dumps(extra_data)
			current_record.save()

		elif method_id == TRADING_CONTRACT_GET_BACK_LENDING_METHOD:
			monster_id_hash = "0x" + transaction["input"][SMART_CONTRACT_METHOD_ID_LENGTH:SMART_CONTRACT_METHOD_ID_LENGTH + 64]
			monster_id = Web3.toInt(hexstr=monster_id_hash)
			monster_id_set.add(monster_id)

			EtheremonDB.EmaMarketTab.objects.filter(type=EmaMarketType.BORROW).filter(monster_id=monster_id).delete()
			log.info("remove_borrow|monster_id=%s,txn_hash=%s", monster_id, transaction["hash"])

	if len(monster_id_set) > 0:
		log.info("update_trade_contract|monster_len=%s,latest_load_block=%s", len(monster_id_set), latest_load_block)
		data_contract = infura_client.getDataContract()
		for monster_id in monster_id_set:
			_sync_monster_id(data_contract, monster_id)
			log.info("trade_contract|update_monster|monster_id=%s", monster_id)

	record_block = latest_load_block
	if len(transaction_list) > 0:
		record_block += 1
		if record_block > current_block:
			record_block = current_block

	ema_settings_manager.set_setting(EmaSetting.SETTING_CONTRACT_TRADE_BLOCK, record_block)
	elapsed = time.time() - start_time
	if elapsed < 5:
		time.sleep(5-elapsed)
	log.data("end_update_trade_contract|record_block=%s,total_txn=%s,total_monster=%s,elapsed=%s",
		record_block, len(transaction_list), len(monster_id_set), elapsed)

if __name__ == "__main__":
	update_trade_contract()