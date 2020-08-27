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
from etheremon_lib.etherscan_client import get_event_list
from etheremon_lib.infura_client import InfuraClient
from etheremon_lib.models import EtheremonDB
from web3 import Web3, HTTPProvider
from helper import _sync_player_dex

SMART_CONTRACT_METHOD_ID_LENGTH = 10
SMART_CONTRACT_BLOCK_STEP = 100000

INFURA_API_URL = INFURA_API_URLS["cron_task"]
ETHERSCAN_API_KEY = ETHERSCAN_API_KEYS["cron_1"]

TOPIC_TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

def update_adventure_nft_contract():
	infura_client = InfuraClient(INFURA_API_URL)
	current_block = infura_client.getCurrentBlock() - 2

	start_block = ema_settings_manager.get_setting_value(EmaSetting.SETTING_CONTRACT_ADVENTURE_ITEM)
	end_block = start_block + SMART_CONTRACT_BLOCK_STEP

	start_time = time.time()
	event_list = get_event_list(EtheremonAdventureItemContract.ADDRESS, start_block, end_block, ETHERSCAN_API_KEY, TOPIC_TRANSFER)
	if event_list is None:
		return

	log.data("start_update_adventure_nft_contract|current_block=%s,start_block=%s,end_block=%s,len_event=%s", current_block, start_block, end_block, len(event_list))

	latest_load_block = start_block
	token_id_set = set()
	token_id_address_dict = {}
	from_address_set = set()
	for event in event_list:
		latest_load_block = max(latest_load_block, int(event["blockNumber"], 16))
		if latest_load_block > current_block:
			return
		token_id_hash = event["topics"][3]
		token_id = Web3.toInt(hexstr=token_id_hash)
		token_id_set.add(token_id)
		from_address = '0x' + event["topics"][1][26:].lower()
		token_address = '0x' + event["topics"][2][26:].lower()
		from_address_set.add(from_address)
		if token_id in token_id_address_dict:
			token_id_address_dict[token_id].add(token_address)
		else:
			token_id_address_dict[token_id] = set([token_address])
		log.info("scan_adventure_event|txn_hash=%s,token_id=%s,target_address=%s,from_address=%s", event["transactionHash"], token_id, token_address, from_address)

	current_ts = get_timestamp()
	if token_id_set:
		adventure_item_contract = infura_client.getAdventureItemContract()
		for token_id in token_id_set:
			try:
				owner = adventure_item_contract.call().ownerOf(token_id)
			except Exception as error:
				log.info("error_owner_token|token_id=%s", token_id)
				owner = EMPTY_ADDRESS
			owner = owner.lower()
			if owner not in token_id_address_dict[token_id]:
				# Case current owner is different from the old transaction => ignore
				log.warn("adventure_item_owner_invalid|token_id=%s,owner=%s,owner_set=%s", token_id, owner, token_id_address_dict[token_id])
				continue
			(item_class, item_value) = adventure_item_contract.call().getItemInfo(token_id)
			if item_class == 0:
				log.warn("adventure_item_class_invalid|token_id=%s,item_class=%s,item_value=%s", token_id, item_class, item_value)
				return
			token_record = EtheremonDB.EmaAdventureItemTab.objects.filter(token_id=token_id).first()
			if token_record:
				token_record.owner = owner
				token_record.class_id = item_class
				token_record.value = item_value
				token_record.update_time = current_ts
			else:
				token_record = EtheremonDB.EmaAdventureItemTab(
					token_id=token_id,
					owner=owner,
					class_id=item_class,
					value=item_value,
					update_time=current_ts
				)
			token_record.save()

			# update claim
			if token_id < 1081:
				if token_id % 10 == 0:
					site_id = token_id / 10
					site_index = 9
				else:
					site_id = token_id / 10 + 1
					site_index = token_id % 10 - 1
				EtheremonDB.EmaAdventurePresaleTab.objects.filter(site_id=site_id).filter(site_index=site_index).update(token_id=token_id)

	# sync player data
	if from_address_set:
		log.info("update_adventure_nft_contract|sender_len=%s,latest_load_block=%s", len(from_address_set), latest_load_block)
		data_contract = infura_client.getDataContract()
		for player in from_address_set:
			result = _sync_player_dex(data_contract, player, None, True)
			if result is False:
				log.warn("sync_player_fail|player=%s", player)
				return
			log.info("contract_adventure_nft_sync_player|sync_player=%s,block=%s", player, current_block)

	record_block = latest_load_block
	if len(token_id_set) > 0:
		record_block += 1
		if record_block > current_block:
			record_block = current_block

	ema_settings_manager.set_setting(EmaSetting.SETTING_CONTRACT_ADVENTURE_ITEM, record_block)
	elapsed = time.time() - start_time
	if elapsed < 5:
		time.sleep(5-elapsed)
	log.data("end_update_adventure_item_contract|record_block=%s,total_txn=%s,total_token=%s,elapsed=%s", record_block, len(event_list), len(token_id_set), elapsed)

if __name__ == "__main__":
	update_adventure_nft_contract()

