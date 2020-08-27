import os
import sys
import time
import logging

curr_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curr_dir)
sys.path.append(os.path.join(curr_dir, '../../'))

from common import context
from django.core.wsgi import get_wsgi_application
from django.db.models import Q

context.init_django('../', 'settings')
application = get_wsgi_application()

from common.logger import log
from etheremon_lib.config import *
from etheremon_lib.infura_client import InfuraClient
from etheremon_service.contract.helper import _sync_monster_id
from etheremon_lib.models import EtheremonDB

SMART_CONTRACT_METHOD_ID_LENGTH = 10
SMART_CONTRACT_BLOCK_STEP = 100000

INFURA_API_URL = INFURA_API_URLS["general"]

def crawl_monster():
	infura_client = InfuraClient(INFURA_API_URL)
	data_contract = infura_client.getDataContract()

	start_time = time.time()
	update_count = 0
	add_count = 0
	total_monster = data_contract.call().totalMonster()
	current_block_number = infura_client.getCurrentBlock()
	log.data("start_crawl_monster|total=%s,block_number=%s", total_monster, current_block_number)

	monster_id = 1
	while monster_id <= total_monster:
		try:
			result, add_flag, update_flag = _sync_monster_id(data_contract, monster_id)
			if result is False:
				break
			add_count += add_flag
			update_count += update_flag
		except:
			logging.exception("update_ema_monster_fail|monster_id=%s", monster_id)
			break
		monster_id += 1

	elapsed = time.time() - start_time
	log.data("end_crawl_monster|elapsed=%s,total_monster=%s,ending_monster=%s,update_count=%s,adding_count=%s,start_at_block=%s",
		elapsed, total_monster, monster_id, update_count, add_count, current_block_number)

def fix_stats_monster():
	infura_client = InfuraClient(INFURA_API_URL)
	data_contract = infura_client.getDataContract()

	monster_records = EtheremonDB.EmaMonsterDataTab.objects.filter(Q(b0=0) | Q(b1=0) | Q(b2=0) | Q(b3=0) | Q(b4=0) | Q(b5=0)).all()
	for monster in monster_records:
		if monster.monster_id < 32599:
			continue
		base_stats = []
		for index in xrange(0, 6):
			stat_value = data_contract.call().getElementInArrayType(DataArrayType.STAT_BASE, monster.monster_id, index)
			base_stats.append(stat_value)
		if 0 in base_stats:
			log.error("fix_monster_invalid_stat|monster_id=%s,base_stats=%s", monster.monster_id, base_stats)
			continue
		monster.b0 = base_stats[0]
		monster.b1 = base_stats[1]
		monster.b2 = base_stats[2]
		monster.b3 = base_stats[3]
		monster.b4 = base_stats[4]
		monster.b5 = base_stats[5]
		monster.exp = 0
		monster.save()
		_sync_monster_id(data_contract, monster.monster_id)

		time.sleep(0.05)
		log.info("fix_monster_stats|monster_id=%s", monster.monster_id)
if __name__ == "__main__":
	crawl_monster()
	fix_stats_monster()
	