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

context.init_django('../', 'settings')
application = get_wsgi_application()

from common.logger import log
from etheremon_lib.models import EtheremonDB
from etheremon_lib.config import *

INFURA_API_URL = INFURA_API_URLS["general"]

def crawl_monster_bonus_egg():
	infura_client = InfuraClient(INFURA_API_URL)
	current_block_number = infura_client.getCurrentBlock()
	transform_contract = infura_client.getTransformDataContract()

	start_time = time.time()
	monster_records = list(EtheremonDB.EmaMonsterDataTab.objects.filter(class_id__lte=24).all())
	log.data("start_crawl_monster_bonus_egg|total_monster=%s,block=%s", len(monster_records), current_block_number)

	count = 0
	for monster_record in monster_records:
		count += 1
		egg_bonus = int(transform_contract.call().getBonusEgg(monster_record.monster_id))
		monster_record.egg_bonus = egg_bonus
		monster_record.save()
		log.info("ema_crawl_monster_egg|monster_id=%s,egg_bonus=%s", monster_record.monster_id, egg_bonus)

	log.data("end_crawl_monster_bonus_egg|count=%s,block=%s,elapsed=%s", count, current_block_number, time.time() - start_time)

def crawl_monster_egg_data():
	infura_client = InfuraClient(INFURA_API_URL)
	current_block_number = infura_client.getCurrentBlock()
	transform_data_contract = infura_client.getTransformDataContract()

	start_time = time.time()
	total_egg_no = transform_data_contract.call().totalEgg()
	log.data("start_crawl_egg_data|total_egg=%s,block=%s", total_egg_no, current_block_number)

	index = 1
	while index <= total_egg_no:
		try:
			(egg_id, mother_id, class_id, trainer_address, hatch_time, monster_id) = transform_data_contract.call().getEggDataById(index)
		except Exception as error:
			log.warn("query_borrow_data_error|index=%s,error=%s", index, error.message)
			time.sleep(5)
			infura_client = InfuraClient(INFURA_API_URL)
			transform_data_contract = infura_client.getTransformDataContract()
			continue

		egg_record = EtheremonDB.EmaEggDataTab.objects.filter(egg_id=index).first()
		if egg_record:
			egg_record.mother_id = mother_id
			egg_record.class_id = class_id
			egg_record.trainer = str(trainer_address).lower()
			egg_record.hatch_time = int(hatch_time)
			egg_record.new_obj_id = monster_id
			egg_record.create_time = start_time
		else:
			EtheremonDB.EmaEggDataTab.objects.create(
				egg_id=index,
				mother_id=mother_id,
				class_id=class_id,
				trainer=str(trainer_address).lower(),
				hatch_time=int(hatch_time),
				new_obj_id=monster_id,
				create_time=start_time
			)
		index += 1

	log.data("end_crawl_egg_data|total_egg=%s,block=%s,elapsed=%s", total_egg_no, current_block_number, time.time() - start_time)


def fix_bonus_egg():
	infura_client = InfuraClient(INFURA_API_URL)
	current_block_number = infura_client.getCurrentBlock()

	mother_egg_records = EtheremonDB.EmaEggDataTab.objects.filter(mother_id__gt=0).filter(class_id__lt=25).values('mother_id').distinct()
	mother_id = []
	for mother_egg_record in mother_egg_records:
		mother_id.append(mother_egg_record["mother_id"])

	# monster
	transform_contract = infura_client.getTransformContract()
	monster_records = list(EtheremonDB.EmaMonsterDataTab.objects.filter(monster_id__in=mother_id).filter(egg_bonus__gt=0).all())
	count = 0
	while count < len(monster_records):
		monster_record = monster_records[count]
		try:
			egg_bonus = transform_contract.call().getBonusEgg(monster_record.monster_id)
		except Exception as error:
			log.warn("get_egg_bonus_error|monster_id=%s,error=%s", monster_record.monster_id, error)
			time.sleep(4)
			continue
		if monster_record.egg_bonus != egg_bonus:
			log.info("fix_egg_bonus|monster_id=%s,before_bonus=%s,after_bonus=%s,block=%s", monster_record.monster_id, monster_record.egg_bonus, egg_bonus, current_block_number)
			EtheremonDB.EmaMonsterDataTab.objects.filter(monster_id=monster_record.monster_id).update(egg_bonus=egg_bonus)
		else:
			log.info("correct_egg_bonus|monster_id=%s", monster_record.monster_id)
		count += 1

def fix_egg_info():
	infura_client = InfuraClient(INFURA_API_URL)
	transform_data_contract = infura_client.getTransformDataContract()

	egg_records = list(EtheremonDB.EmaEggDataTab.objects.filter(class_id=0).all())
	index = 0
	while index < len(egg_records):
		egg_record = egg_records[index]
		(egg_id, mother_id, class_id, trainer_address, hatch_time, monster_id) = transform_data_contract.call().getEggDataById(egg_record.egg_id)
		if class_id is 0:
			log.warn("invalid_egg_data|egg_id=%s", index)
			continue
		egg_record.mother_id = mother_id
		egg_record.class_id = class_id
		egg_record.trainer = str(trainer_address).lower()
		egg_record.hatch_time = int(hatch_time)
		egg_record.new_obj_id = monster_id
		egg_record.save()
		index += 1

if __name__ == "__main__":
	#crawl_monster_bonus_egg()
	crawl_monster_egg_data()
	fix_bonus_egg()
	fix_egg_info()




