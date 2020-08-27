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

context.init_django('../', 'settings')
application = get_wsgi_application()

from common.logger import log
from etheremon_lib.models import EtheremonDB
from etheremon_lib.config import *
from revenue_constants import *

START_MONSTER_ID = 20254
FREE_MONSTER_ID_LIST = [25, 26, 27]

# in ETH
MONSTER_PRICE_DICT = {
	28: 0.09,
	29: 0.09,
	30: 0.15,
	31: 0.04,
	32: 0.09,
	33: 0.09,
	34: 0.03,
	35: 0.03,
	36: 0.03,
	37: 0.09,
	72: 0.03,
	73: 0.03,
	74: 0.03,
	75: 0.03,
	76: 0.03,
	77: 0.15,
	78: 0.09,
	79: 0.05,
	80: 0.09,
	81: 0.07,
	90: 0.5,
	93: 0.5,
	96: 0.03,
	97: 0.09,
	99: 0.12,
	105: 0.03,
	106: 0.13,
	109: 0.03,
	110: 0.03,
	111: 0.03,
	112: 0.03,
	113: 0.03,
	114: 0.03,
	115: 0.03,
	156: 0.2,
	159: 0.3
}

def _getDate(ts):
	return datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')

def _getDateInInteger(ts):
	return int(datetime.datetime.fromtimestamp(ts).strftime('%Y%m%d'))

def _getTime(ts):
	return datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')

def cal_monster():
	max_claimed_monster_id = EtheremonDB.RevenueMonsterTab.objects.all().aggregate(Max('monster_id'))
	if not max_claimed_monster_id['monster_id__max']:
		max_claimed_monster_id = START_MONSTER_ID
	else:
		max_claimed_monster_id = max_claimed_monster_id['monster_id__max']

	egg_monster_id_list = EtheremonDB.EmaEggDataTab.objects.filter(new_obj_id__gt=max_claimed_monster_id).values_list('new_obj_id', flat=True)
	egg_monster_id_set = set(egg_monster_id_list)

	while True:
		monster_records = EtheremonDB.EmaMonsterDataTab.objects.filter(monster_id__gt=max_claimed_monster_id).order_by('monster_id')[:5000]
		if not monster_records:
			break
		monster_records = list(monster_records)
		for monster_record in monster_records:
			if monster_record.class_id not in MONSTER_PRICE_DICT:
				continue
			if monster_record.monster_id in egg_monster_id_set:
				continue

			# calculate pay amount
			if monster_record.create_index == 1 or monster_record.create_index == 2:
				pay_amount = MONSTER_PRICE_DICT[monster_record.class_id]
			else:
				pay_amount = MONSTER_PRICE_DICT[monster_record.class_id] + (monster_record.create_index - 2) * MONSTER_PRICE_DICT[monster_record.class_id]/1000

			catch_date_str = _getDate(monster_record.create_time)
			catch_date_int = _getDateInInteger(monster_record.create_time)
			revenue_monster_record = EtheremonDB.RevenueMonsterTab(
				monster_id=monster_record.monster_id,
				trainer=monster_record.trainer,
				class_id=monster_record.class_id,
				eth_amount=pay_amount,
				usd_amount=pay_amount * ETH_PRICE_DICT[catch_date_str],
				catch_date=catch_date_int,
				timestamp=monster_record.create_time
			)
			revenue_monster_record.save()

		time.sleep(2)
		max_claimed_monster_id = monster_records[-1].monster_id
		log.info("cal_monster_revenue|latest_monster_id=%s", max_claimed_monster_id)

if __name__ == "__main__":
	cal_monster()