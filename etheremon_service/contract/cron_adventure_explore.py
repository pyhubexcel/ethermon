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

EXPLORE_MIN_BLOCK_GAP = 240

ADVENTURE_EXPLORE_START_METHOD = "0x1a5f9bed"
ADVENTURE_EXPLORE_CLAIM_METHOD = "0xfbf7ba65"

def update_adventure_contract():
	infura_client = InfuraClient(INFURA_API_URL)
	current_block = infura_client.getCurrentBlock() - 2

	start_block = ema_settings_manager.get_setting_value(EmaSetting.SETTING_CONTRACT_ADVENTURE_EXPLORE_BLOCK)
	end_block = start_block + SMART_CONTRACT_BLOCK_STEP

	start_time = time.time()
	transaction_list = get_txn_list(EtheremonAdventureExploreContract.ADDRESS, start_block, end_block, ETHERSCAN_API_KEY)
	if transaction_list is None:
		return

	log.data("start_update_adventure_contract|current_block=%s,start_block=%s,end_block=%s,len_txn=%s", current_block, start_block, end_block, len(transaction_list))
	if len(transaction_list) > 20:
		log.data("update_adventure|cut_down_txn|current_block=%s,start_block=%s,end_block=%s", current_block, start_block, end_block)
		transaction_list = transaction_list[:20]

	latest_load_block = start_block
	current_ts = get_timestamp()
	adventure_explore_contract = infura_client.getAdventureExploreContract()
	adventure_data_contract = infura_client.getAdventureDataContract()
	site_id_set = set()
	sender_set = set()

	# check new explore id
	total_explore = adventure_data_contract.call().exploreCount()
	max_explore_record = EtheremonDB.EmaAdventureExploreTab.objects.all().order_by("-explore_id").first()
	max_explore_record_id = 0
	if max_explore_record:
		max_explore_record_id = max_explore_record.explore_id
	if max_explore_record_id < total_explore:
		explore_id_index = max_explore_record_id + 1
		while explore_id_index <= total_explore:
			explore_data = adventure_explore_contract.call().getExploreItem(explore_id_index)
			if explore_data[2] == 0:
				log.warn("explore_data_invalid|explore_id=%s", explore_id_index)
				return
			explore_ending_block = explore_data[4] + EXPLORE_MIN_BLOCK_GAP + explore_data[4] % EXPLORE_MIN_BLOCK_GAP
			if explore_data[4] > current_block - 4:
				time.sleep(30)
				log.info("skip_too_near_explore|explore_id=%s,sender=%s,start_block=%s,current_block=%s", explore_id_index, explore_data[0].lower(), explore_data[4], current_block)
				return
			EtheremonDB.EmaAdventureExploreTab.objects.create(
				explore_id=explore_id_index,
				fee_type=EmaAdventureExploreFee.NONE,
				sender=explore_data[0].lower(),
				monster_type=explore_data[1],
				monster_id=explore_data[2],
				site_id=explore_data[3],
				reward_monster_class=explore_data[5],
				reward_item_class=explore_data[6],
				reward_item_value=str(explore_data[7]),
				start_block=explore_data[4],
				end_block=explore_ending_block,
				claim_txn_hash='',
				create_time=current_ts
			)
			log.info("adding_new_explore|explore_id=%s,max_record_id=%s,sender=%s,start_block=%s,current_block=%s", explore_id_index, max_explore_record_id, explore_data[0].lower(), explore_data[4], current_block)
			site_id_set.add(explore_data[3])
			explore_id_index += 1

	for transaction in transaction_list:
		if len(transaction["input"]) < SMART_CONTRACT_METHOD_ID_LENGTH:
			log.warn("invalid_smart_contract_txn|transaction=%s", transaction)
			continue
		if int(transaction.get("isError", 1)) != 0:
			continue
		if int(transaction.get("txreceipt_status")) != 1:
			continue

		log.info("update_adventure_contract|txn_hash=%s", transaction["hash"])

		latest_load_block = max(latest_load_block, int(transaction["blockNumber"]))
		if latest_load_block > current_block:
			return
		method_id = transaction["input"][0:SMART_CONTRACT_METHOD_ID_LENGTH]

		sender = str(transaction["from"]).lower()

		if method_id == ADVENTURE_EXPLORE_START_METHOD:
			# check current pending
			pending_explore_data = adventure_explore_contract.call().getPendingExploreItem(sender)
			explore_id = pending_explore_data[0]
			if explore_id == 0:
				log.info("no_pending_txn|sender=%s", sender)
				continue
			current_record = EtheremonDB.EmaAdventureExploreTab.objects.filter(explore_id=explore_id).first()
			if not current_record:
				'''
				EtheremonDB.EmaAdventureExploreTab.objects.create(
					explore_id=explore_id,
					fee_type=EmaAdventureExploreFee.ETH,
					sender=sender,
					monster_type=pending_explore_data[1],
					monster_id=pending_explore_data[2],
					site_id=pending_explore_data[3],
					reward_monster_class=0,
					reward_item_class=0,
					reward_item_value='0',
					start_block=pending_explore_data[4],
					end_block=pending_explore_data[5],
					claim_txn_hash='',
					create_time=current_ts
				)
				log.info("adding_new_explore|explore_id=%s,sender=%s,txn_hash=%s", explore_id, sender, transaction["hash"])
				'''
				log.warn("explore_record_not_found|explore_id=%s,txn_hash=%s", explore_id, transaction["hash"])
				return
			else:
				if current_record.fee_type == 0:
					current_record.fee_type = EmaAdventureExploreFee.ETH
					current_record.save()
			site_id_set.add(pending_explore_data[3])
		elif method_id == ADVENTURE_EXPLORE_CLAIM_METHOD:
			explore_id_hash = "0x" + transaction["input"][SMART_CONTRACT_METHOD_ID_LENGTH:SMART_CONTRACT_METHOD_ID_LENGTH + 64]
			explore_id = Web3.toInt(hexstr=explore_id_hash)
			current_record = EtheremonDB.EmaAdventureExploreTab.objects.filter(explore_id=explore_id).first()
			explore_data = adventure_explore_contract.call().getExploreItem(explore_id)
			if explore_data[5] == 0 and explore_data[6] == 0 and explore_data[7] == 0:
				log.warn("invalid_explore_data_claim|explore_id=%s,explore_data=%s,txn_hash=%s", explore_id, explore_data, transaction["hash"])
				return
			if not current_record:
				'''
				log.warn("unable_to_find_explore|explore_id=%s,txn_hash=%s", explore_id, transaction["hash"])
				explore_ending_block = explore_data[4] + EXPLORE_MIN_BLOCK_GAP + explore_data[4] % EXPLORE_MIN_BLOCK_GAP
				EtheremonDB.EmaAdventureExploreTab.objects.create(
					explore_id=explore_id,
					fee_type=EmaAdventureExploreFee.ETH,
					sender=explore_data[0].lower(),
					monster_type=explore_data[1],
					monster_id=explore_data[2],
					site_id=explore_data[3],
					reward_monster_class=explore_data[5],
					reward_item_class=explore_data[6],
					reward_item_value=str(explore_data[7]),
					start_block=explore_data[4],
					end_block=explore_ending_block,
					claim_txn_hash=transaction["hash"].lower(),
					create_time=current_ts
				)
				site_id_set.add(explore_data[3])
				'''
				log.warn("explore_record_not_found|explore_id=%s,txn_hash=%s", explore_id, transaction["hash"])
				return
			else:
				current_record.claim_txn_hash = transaction["hash"].lower()
				current_record.reward_monster_class = explore_data[5]
				current_record.reward_item_class = explore_data[6]
				current_record.reward_item_value = str(explore_data[7])
				current_record.save()
				site_id_set.add(current_record.site_id)

			if explore_data[5] > 0:
				sender_set.add(current_record.sender)

	if site_id_set:
		for site_id in site_id_set:
			site_revenue = adventure_data_contract.call().getLandRevenue(site_id)
			log.info("update_site_revenue|site_id=%s,revenue=%s", site_id, site_revenue)
			if site_revenue[0] > 0 or site_revenue[1] > 0:
				emont_amount = (1.0 * site_revenue[0]) / 10**8
				eth_amount = (1.0 * site_revenue[1]) / 10**18
				site_revenue_record = EtheremonDB.EmaAdventureRevenueSiteTab.objects.filter(site_id=site_id).first()
				if not site_revenue_record:
					EtheremonDB.EmaAdventureRevenueSiteTab.objects.create(
						site_id=site_id,
						eth_amount=eth_amount,
						emont_amount=emont_amount,
						update_time=current_ts
					)
				else:
					if site_revenue_record.eth_amount < eth_amount:
						site_revenue_record.eth_amount = eth_amount
					if site_revenue_record.emont_amount < emont_amount:
						site_revenue_record.emont_amount = emont_amount
					site_revenue_record.update_time = current_ts
					site_revenue_record.save()

	# reload sender
	if sender_set:
		log.info("update_deck_explore|len_sender=%s,latest_load_block=%s", len(sender_set), latest_load_block)
		data_contract = infura_client.getDataContract()
		for player in sender_set:
			result = _sync_player_dex(data_contract, player)
			if result is False:
				log.warn("sync_player_fail|player=%s", player)

	record_block = latest_load_block
	if len(transaction_list) > 0:
		record_block += 1
		if record_block > current_block:
			record_block = current_block

	ema_settings_manager.set_setting(EmaSetting.SETTING_CONTRACT_ADVENTURE_EXPLORE_BLOCK, record_block)
	elapsed = time.time() - start_time
	if elapsed < 5:
		time.sleep(5-elapsed)
	log.data("end_update_adventure_contract|record_block=%s,total_txn=%s,site_set=%s,elapsed=%s",
		record_block, len(transaction_list), len(site_id_set), elapsed)


if __name__ == "__main__":
	update_adventure_contract()
