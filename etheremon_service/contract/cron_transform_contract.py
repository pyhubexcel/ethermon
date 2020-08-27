import os
import sys
import time

from django.db import transaction
from django.db.models import Sum

from etheremon_lib.emont_bonus_manager import EmontBonusType
from etheremon_lib.transaction_manager import TxnTypes, TxnAmountTypes, TxnStatus

curr_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curr_dir)
sys.path.append(os.path.join(curr_dir, '../../'))

from common import context
from django.core.wsgi import get_wsgi_application

context.init_django('../', 'settings')
application = get_wsgi_application()

from common.logger import log
from common.utils import get_timestamp
from etheremon_lib.models import EtheremonDB
from etheremon_lib.config import *
from etheremon_lib import ema_settings_manager, transaction_manager, user_manager, emont_bonus_manager
from etheremon_lib.etherscan_client import get_txn_list, get_event_list
from etheremon_lib.infura_client import InfuraClient
from helper import _sync_player_dex

SMART_CONTRACT_METHOD_ID_LENGTH = 10
SMART_CONTRACT_BLOCK_STEP = 100000

INFURA_API_URL = INFURA_API_URLS["cron_task"]
ETHERSCAN_API_KEY = ETHERSCAN_API_KEYS["cron_2"]

TOPIC_LAYEGG = "0x3c3333d9f85107cb0696d2fe51b5060309ca58fa67419084a4159f1f0c76056c"



def update_transform_contract():
	infura_client = InfuraClient(INFURA_API_URL)
	current_block = infura_client.getCurrentBlock() - 2

	start_block = ema_settings_manager.get_setting_value(EmaSetting.SETTING_CONTRACT_TRANSFORM_BLOCK)
	end_block = start_block + SMART_CONTRACT_BLOCK_STEP

	start_time = time.time()


	transaction_list = get_txn_list(EtheremonTransformContract.ADDRESS, start_block, end_block, ETHERSCAN_API_KEY)
	
	
	
	if transaction_list is None:
		return

	log.data("start_update_transform_contract|current_block=%s,start_block=%s,end_block=%s,len_txn=%s", current_block, start_block, end_block, len(transaction_list))

	'''
	if len(transaction_list) > 50:
		log.data("update_transform|cut_down_txn|current_block=%s,start_block=%s,end_block=%s", current_block, start_block, end_block)
		transaction_list = transaction_list[:50]
	'''

	latest_load_block = start_block
	sender_set = set()
	for transaction in transaction_list:
		if len(transaction["input"]) < SMART_CONTRACT_METHOD_ID_LENGTH:
			log.warn("invalid_smart_contract_txn|transaction=%s", transaction)
			continue
		if int(transaction.get("isError", 1)) != 0:
			continue
		if int(transaction.get("txreceipt_status")) != 1:
			continue

		log.info("update_transform_contract|txn_hash=%s", transaction["hash"])
		latest_load_block = max(latest_load_block, int(transaction["blockNumber"]))
		if latest_load_block > current_block:
			return
		sender = str(transaction["from"]).lower()
		sender_set.add(sender)

	# update info by trainer
	count_new_egg = 0
	if sender_set:
		time.sleep(5)
		data_contract = infura_client.getDataContract()
		transform_contract = infura_client.getTransformContract()
		transform_data_contract = infura_client.getTransformDataContract()
		for player in sender_set:
			# update info
			result = _sync_player_dex(data_contract, player, transform_contract)
			if result is False:
				log.warn("sync_player_fail|player=%s", player)
				return

			# sync egg data
			egg_records = EtheremonDB.EmaEggDataTab.objects.filter(trainer=player).filter(new_obj_id=0).all()
			for egg_record in egg_records:
				(egg_id, mother_id, class_id, trainer_address, hatch_time, monster_id) = transform_data_contract.call().getEggDataById(egg_record.egg_id)
				if class_id == 0:
					log.warn("invalid_egg_data|egg_id=%s", egg_record.egg_id)
					return
				egg_record.mother_id = mother_id
				egg_record.class_id = class_id
				egg_record.trainer = str(trainer_address).lower()
				egg_record.hatch_time = int(hatch_time)
				egg_record.new_obj_id = monster_id
				egg_record.save()

		# sync new egg
		max_egg_record = EtheremonDB.EmaEggDataTab.objects.all().order_by("-egg_id").first()
		max_id = 0
		if max_egg_record:
			max_id = max_egg_record.egg_id
		current_total = transform_data_contract.call().totalEgg()
		index = max_id + 1
		while index <= current_total:
			(egg_id, mother_id, class_id, trainer_address, hatch_time, monster_id) = transform_data_contract.call().getEggDataById(index)
			if class_id == 0:
				log.warn("invalid_egg_data|egg_id=%s", index)
				return
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
			count_new_egg += 1

	record_block = latest_load_block
	if len(transaction_list) > 0:
		record_block += 1
		if record_block > current_block:
			record_block = current_block

	ema_settings_manager.set_setting(EmaSetting.SETTING_CONTRACT_TRANSFORM_BLOCK, record_block)
	elapsed = time.time() - start_time
	if elapsed < 5:
		time.sleep(5-elapsed)
	log.data("end_update_transform_contract|record_block=%s,total_txn=%s,total_player=%s,count_new_egg=%s,elapsed=%s",
		record_block, len(transaction_list), len(sender_set), count_new_egg, elapsed)





def update_internal_transform_contract():
	infura_client = InfuraClient(INFURA_API_URL)
	current_block = infura_client.getCurrentBlock() - 2

	start_block = ema_settings_manager.get_setting_value(EmaSetting.SETTING_CONTRACT_TRANSFORM_BLOCK)
	end_block = start_block + SMART_CONTRACT_BLOCK_STEP

	start_time = time.time()


	
	
	event_list = get_event_list(EtheremonTransformContract.ADDRESS, start_block, end_block, ETHERSCAN_API_KEY, TOPIC_LAYEGG)


	
	
	if event_list is None:
		return

	log.data("events_start_update_transform_contract|current_block=%s,start_block=%s,end_block=%s,len_txn=%s", current_block, start_block, end_block, len(event_list))


	latest_load_block = start_block
	sender_set = set()
	for transaction in transaction_list:
		if len(transaction["input"]) < SMART_CONTRACT_METHOD_ID_LENGTH:
			log.warn("invalid_smart_contract_txn|transaction=%s", transaction)
			continue
		if int(transaction.get("isError", 1)) != 0:
			continue
		if int(transaction.get("txreceipt_status")) != 1:
			continue

		log.info("event_update_transform_contract|txn_hash=%s", transaction["hash"])
		latest_load_block = max(latest_load_block, int(transaction["blockNumber"]))
		if latest_load_block > current_block:
			return
		sender = str(transaction["from"]).lower()
		sender_set.add(sender)

	# update info by trainer
	count_new_egg = 0
	if sender_set:
		time.sleep(5)
		data_contract = infura_client.getDataContract()
		transform_contract = infura_client.getTransformContract()
		transform_data_contract = infura_client.getTransformDataContract()
		for player in sender_set:
			# update info
			result = _sync_player_dex(data_contract, player, transform_contract)
			if result is False:
				log.warn("sync_player_fail|player=%s", player)
				return

			# sync egg data
			egg_records = EtheremonDB.EmaEggDataTab.objects.filter(trainer=player).filter(new_obj_id=0).all()
			for egg_record in egg_records:
				(egg_id, mother_id, class_id, trainer_address, hatch_time, monster_id) = transform_data_contract.call().getEggDataById(egg_record.egg_id)
				if class_id == 0:
					log.warn("invalid_egg_data|egg_id=%s", egg_record.egg_id)
					return
				egg_record.mother_id = mother_id
				egg_record.class_id = class_id
				egg_record.trainer = str(trainer_address).lower()
				egg_record.hatch_time = int(hatch_time)
				egg_record.new_obj_id = monster_id
				egg_record.save()

		# sync new egg
		max_egg_record = EtheremonDB.EmaEggDataTab.objects.all().order_by("-egg_id").first()
		max_id = 0
		if max_egg_record:
			max_id = max_egg_record.egg_id
		current_total = transform_data_contract.call().totalEgg()
		index = max_id + 1
		while index <= current_total:
			(egg_id, mother_id, class_id, trainer_address, hatch_time, monster_id) = transform_data_contract.call().getEggDataById(index)
			if class_id == 0:
				log.warn("invalid_egg_data|egg_id=%s", index)
				return
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
			count_new_egg += 1

	record_block = latest_load_block
	if len(transaction_list) > 0:
		record_block += 1
		if record_block > current_block:
			record_block = current_block

	ema_settings_manager.set_setting(EmaSetting.SETTING_CONTRACT_TRANSFORM_BLOCK, record_block)
	elapsed = time.time() - start_time
	if elapsed < 5:
		time.sleep(5-elapsed)
	log.data("end_event_update_transform_contract|record_block=%s,total_txn=%s,total_player=%s,count_new_egg=%s,elapsed=%s",
		record_block, len(transaction_list), len(sender_set), count_new_egg, elapsed)





def update_lunar_egg_rebate():
	if get_timestamp() > LUNAR_19_END_TIME + 60:
		return

	bonus_eggs = EtheremonDB.EmaEggDataTab.objects.filter(mother_id=0).filter(create_time__gte=LUNAR_19_START_TIME).filter(create_time__lte=LUNAR_19_END_TIME).order_by("egg_id")[:888]

	egg_purchases = {}
	for data in bonus_eggs:
		egg_purchases[data.trainer] = egg_purchases.get(data.trainer, 0) + 1

	for address in egg_purchases:
		player_uid = user_manager.get_uid_by_address_default_0(address)
		if player_uid == 0:
			continue

		cc = min(8, egg_purchases[address]) * 88
		collected = transaction_manager.get_transactions(player_uid, TxnTypes.LUNAR_19_EMONT_REBATE).aggregate(sum=Sum('amount_value'))['sum']
		to_collect = max(0, round(cc - (collected or 0), 2))

		if to_collect > 0:
			with transaction.atomic():
				emont_bonus_manager.add_bonus(
					uid=player_uid,
					bonus_dict={
						EmontBonusType.EVENT_BONUS: to_collect
					}
				)
				transaction_manager.create_transaction(
					player_uid=player_uid,
					player_address=address,
					txn_type=TxnTypes.LUNAR_19_EMONT_REBATE,
					txn_info='{"past_collected": %s}' % collected,
					amount_type=TxnAmountTypes.IN_GAME_EMONT,
					amount_value=to_collect,
					status=TxnStatus.FINISHED
				)
				log.data("lunar_bonus|player=%s,collected=%s,collected=%s,to_collect=%s", address, player_uid, collected, to_collect)


if __name__ == "__main__":
	update_transform_contract()
	update_internal_transform_contract()
	# update_lunar_egg_rebate()
