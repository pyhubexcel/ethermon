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

INFURA_API_URL = INFURA_API_URLS["adventure_task"]
ETHERSCAN_API_KEY = ETHERSCAN_API_KEYS["cron_4"]

EXPLORE_MIN_BLOCK_GAP = 240

def crawl_explore_info(explore_id):
	infura_client = InfuraClient(INFURA_API_URL)
	adventure_explore_contract = infura_client.getAdventureExploreContract()
	explore_data = adventure_explore_contract.call().getExploreItem(explore_id)
	if explore_data[2] == 0:
		log.warn("explore_data_invalid|explore_id=%s", explore_id)
		return
	explore_ending_block = explore_data[4] + EXPLORE_MIN_BLOCK_GAP + explore_data[4] % EXPLORE_MIN_BLOCK_GAP
	current_record = EtheremonDB.EmaAdventureExploreTab.objects.filter(explore_id=explore_id).first()
	sm_sender = explore_data[0].lower()
	if not current_record:
		current_ts = get_timestamp()
		EtheremonDB.EmaAdventureExploreTab.objects.create(
			explore_id=explore_id,
			fee_type=EmaAdventureExploreFee.NONE,
			sender=sm_sender,
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
		log.info("add_explore_info|explore_id=%s", explore_id)
	else:
		if current_record.sender != sm_sender or current_record.start_block != explore_data[4] or current_record.monster_id != explore_data[2]:
			log.warn("mismatch_db_explore|explore_id=%s,sender=%s,sm_sender=%s,start_block=%s,sm_start_block=%s,monster_id=%s,sm_monster_id=%s",
				explore_id, current_record.sender, sm_sender, current_record.start_block, explore_data[4], current_record.monster_id, explore_data[2])
			current_record.sender = sm_sender
			current_record.monster_type = explore_data[1]
			current_record.monster_id = explore_data[2]
			current_record.site_id = explore_data[3]
			current_record.reward_monster_class = explore_data[5]
			current_record.reward_item_class = explore_data[6]
			current_record.reward_item_value = str(explore_data[7])
			current_record.start_block = explore_data[4]
			current_record.save()

def crawl_site_revenue(site_id):
	infura_client = InfuraClient(INFURA_API_URL)
	adventure_data_contract = infura_client.getAdventureDataContract()
	site_revenue = adventure_data_contract.call().getLandRevenue(site_id)
	current_ts = get_timestamp()
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

def crawl_token_claim(token_id):
	infura_client = InfuraClient(INFURA_API_URL)
	adventure_data_contract = infura_client.getAdventureDataContract()
	current_ts = get_timestamp()
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

def cron_run_setting():
	explore_ids = range(6289, 7000)
	site_ids = []
	token_ids = []
	if explore_ids:
		for explore_id in explore_ids:
			print "checking explore id", explore_id
			crawl_explore_info(explore_id)
			time.sleep(1)
	if site_ids:
		for site_id in site_ids:
			print "checking site id", site_id
			crawl_site_revenue(site_id)
			time.sleep(1)
	if token_ids:
		for token_id in token_ids:
			print "checking token id", token_id
			crawl_token_claim(token_id)
			time.sleep(1)

if __name__ == "__main__":
	explore_ids = range(6289, 7000)
	site_ids = []
	token_ids = []
	if explore_ids:
		for explore_id in explore_ids:
			print "checking explore id", explore_id
			crawl_explore_info(explore_id)
			time.sleep(1)
	if site_ids:
		for site_id in site_ids:
			print "checking site id", site_id
			crawl_site_revenue(site_id)
			time.sleep(1)
	if token_ids:
		for token_id in token_ids:
			print "checking token id", token_id
			crawl_token_claim(token_id)
			time.sleep(1)