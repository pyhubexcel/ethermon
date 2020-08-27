import os
import sys
import time
import json
import logging

curr_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curr_dir)
sys.path.append(os.path.join(curr_dir, '../../'))

from common import context
from common.utils import get_timestamp
from django.core.wsgi import get_wsgi_application
from etheremon_lib.infura_client import InfuraClient

context.init_django('../', 'settings')
application = get_wsgi_application()

from common.logger import log
from etheremon_lib.models import EtheremonDB
from etheremon_lib.config import *

INFURA_API_URL = INFURA_API_URLS["general"]
ADVENTURE_SITE_ID_MAX = 54
ADVENTURE_SITE_ITEM_MAX = 10

def crawl_adventure_presale():
	infura_client = InfuraClient(INFURA_API_URL)
	adventure_presale_contract = infura_client.getAdventurePresaleContract()

	current_ts = get_timestamp()
	site_id_index = 1
	while site_id_index <= 54:
		site_item_index = 0
		while site_item_index < 10:
			try:
				(bidder, bid_id, site_id, amount, bid_time) = adventure_presale_contract.call().getBidBySiteIndex(site_id_index, site_item_index)
				if bid_id == 0:
					log.warn("query_adventure_presale_invalid|site_id=%s,site_index=%s", site_id_index, site_item_index)
					time.sleep(3)
					continue
			except Exception as error:
				logging.exception("query_adventure_presale_exception|site_id=%s,site_index=%s", site_id_index, site_item_index)
				time.sleep(3)
				continue

			bidder = bidder.lower()
			record = EtheremonDB.EmaAdventurePresaleTab.objects.filter(bid_id=bid_id).first()
			if record:
				record.site_id = site_id
				record.bid_id = bid_id
				record.site_index = site_item_index
				record.bidder = bidder
				record.bid_amount = amount
				record.bid_time = bid_time

			else:
				record = EtheremonDB.EmaAdventurePresaleTab(
					site_id=site_id,
					site_index=site_item_index,
					bid_id=bid_id,
					bidder=bidder,
					bid_amount=amount,
					bid_time=bid_time,
					token_id=0,
					update_time=current_ts
				)
			log.data("adventure_presale_query|site_id=%s,site_index=%s,bid_id=%s", site_id_index, site_item_index, bid_id)
			record.save()

			site_item_index += 1

		site_id_index += 1

if __name__ == "__main__":
	crawl_adventure_presale()

