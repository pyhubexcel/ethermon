from common.logger import log
from etheremon_lib.models import *
from common.utils import get_timestamp
from django.db import transaction
from django.db.models import Q
from common.utils import parse_params, log_request
import re
from django.db import connection
import random



def dcl_update_transferred_mon(mon_id, owner):
	user_mon_record = EtheremonDB.DCLMonsterData.objects.filter(Q(Mon_ID=mon_id) ).first()
	if user_mon_record :
		user_mon_record.address =  owner
		user_mon_record.save()	




def add_purchase(data):

	pur_record = EtheremonDB.DCLMetazoePurchase(
		action = data["action"],
		meta_id = data["meta_id"],
		host_id = data["host_id"],
		plot_unique = data["plot_unique"],
		txn_token = data["txn_token"],
		eth_from = data["eth_from"],
		dcl_name = data["dcl_name"],
		sku = data["sku"],
		create_date = data["create_date"])
	pur_record.save()


	#sku will come as beet1 or beet3 - get the suffix
	temp = re.compile("([a-zA-Z]+)([0-9]+)") 
	sku_split = temp.match(data["sku"]).groups() 
	config_record = EtheremonDB.DCLItemClassConfig.objects.filter(Q(metazone_sku=sku_split[0])).first()

	if config_record is None:
		return 'NO_RELEVANT_DCL_ITEM_CLASS_CONFIG_FOUND_FOR_SKU '+sku_split[0]
	

	

	qty = sku_split[1]
	


	fungible_record = EtheremonDB.DCLUserFungible.objects.filter(Q(address=data["eth_from"]) & Q(ItemClass=config_record.ItemClass) & Q(ItemVariety=config_record.ItemVariety)).first()

	if fungible_record is None:
		new_record = EtheremonDB.DCLUserFungible.objects.update_or_create(
					address = data["eth_from"],
					ItemClass = config_record.ItemClass,
					ItemVariety = config_record.ItemVariety,
					craft_hierachy = 1,
					qty =  qty,
					create_time = get_timestamp()
					)
		new_record.save()
	else :
		fungible_record.qty +=  int(qty)
		create_time = get_timestamp()
		fungible_record.save()


	return 'SAVED'	
	


'''
LOGIC
==========
INIT / SET NEW Default Ethermon (if First time Mon in DCL )
dcl_user_active.a0 = DEFAULT (Set Mon Default Cobrus/Kyari)
dcl_monster_data.sleep_end_time = time.now - 1 (awake)
dcl_monster_data.(energy,hunger,mood) = 999/1000 (not full)
dcl_user_active_stats.last_seen = time.now - 1 (New Mon ONLY)
dcl_user_active_stats.is_live = 1 (New Mon ONLY)
seed (dcl_item_wip) with free food 98% complete
'''

def dcl_user_login(data):
	address = data["address"]
	with transaction.atomic():
		
		user_active_record = EtheremonDB.DCLUserActiveStatus.objects.filter(Q(address=data["address"]) ).first()

		if user_active_record is None:
			EtheremonDB.DCLUserActiveStatus.objects.create(
				address =  data["address"],
				is_live = 1,
				last_seen = get_timestamp() - 1
			)

		

		#user without a mon..
		if data.get('a0', None) is None:
			pass
		else :

			# user has mon..create it
			user_mon_record = EtheremonDB.DCLMonsterData.objects.filter(Q(Mon_ID=data["a0"]) ).first()

			if user_mon_record is None:
				EtheremonDB.DCLMonsterData.objects.create(
					Mon_ID =  data["a0"],
					address =  data["address"],
					dxp = 0,
					HP_current = 1000,
					energy_current = 1000,
					hunger_current = 800,
					mood_current = 0,
					HP_max = 1000,
					Energy_max = 1000,
					Hunger_max = 1000,
					Mood_max = 1000,
					hunger_state = 1,
					sleep_end_timer = get_timestamp(),
					last_saved =  get_timestamp()
					#last_saved has to be null - so dxp won't be accumulated just on the first run
				)
			else :
			#	from pprint import pprint
			#	pprint (vars(user_mon_record))
				user_mon_record.address =  data["address"]
				user_mon_record.save()	




		


		#anyway if user already exists
		if user_active_record :	
			user_active_record.is_live = 1
			user_active_record.last_seen = get_timestamp() - 1
			user_active_record.save()
		


		#if the new user doesn't have fungibles seed them
		userFungible = EtheremonDB.DCLUserFungible.objects.filter(address=address).first()
		if userFungible :
			#found
			pass
		else :
			config_records = EtheremonDB.DCLItemClassConfig.objects.filter().all()
			for rec in config_records:
				#seeding.append( { 'ItemClass': rec.ItemClass, 'ItemVariety' :  rec.ItemVariety, 'craft_hierachy' : 1, 'qty' :  rec.user_default_qty})
				fungible_record = EtheremonDB.DCLUserFungible(
					address = address,
					ItemClass = rec.ItemClass,
					ItemVariety = rec.ItemVariety,
					craft_hierachy = 1,
					qty	=  rec.user_default_qty,
					create_time = get_timestamp())
				fungible_record.save()	 

		
		#update monster lifelines
	


#plant food
def use_user_fungible(data) :


	dcl_fungible_id = data['dcl_fungible_id']
	host_id = data['host_id']
	meta_id = data['meta_id']
	qty = data['qty']


	

	with transaction.atomic():
		
		record = EtheremonDB.DCLUserFungible.objects.select_for_update().filter(Q(dcl_fungible_id=dcl_fungible_id)).first()

		
		if not record :
			return 'USER_FUNGIBLE_MATCHING_THE_ID_NOT_FOUND'
			
		exists = EtheremonDB.DCLItemWip.objects.filter(Q(host_id=host_id) & Q(meta_id=meta_id) & Q(growth_state=0) & Q(address=record.address)).first()
		
		if exists :
			return 'META_AND_HOST_AND_ADDRESS_ALREADY_EXISTS_IN_GROWING_STATE'
	
		#proceed only if requested qty is available
		if 	record.qty >= qty :
			record.qty -= qty
			record.save()

			#fetch time to grow from config	
			secs_to_grow = 60*60
			config_record = EtheremonDB.DCLItemClassConfig.objects.filter(Q(ItemClass=record.ItemClass) & Q(ItemVariety=record.ItemVariety)).first()
			
			if config_record:
				secs_to_grow = config_record.craft_timer
			#create new wip
			EtheremonDB.DCLItemWip.objects.create(
				ItemClass = record.ItemClass,
				ItemVariety= record.ItemVariety,
				wild= 'no',
				wild_count= 0,
				address= record.address,
				growth_state= 0,
				host_id= host_id,
				meta_id= meta_id,
				start_timer= get_timestamp(),
				end_timer= get_timestamp() + secs_to_grow
			)

			return 'SAVED'
		else :
			return 'NOT_ENOUGH_QTY'


#eat food
'''
dcl_item_wip.growth_state = 1 (set crop as eaten)
dcl_monster_data.hunger_current += hunger_bonus from eating
(after eaten)
if .hunger >= 1000, dcl_monster_data.hunger_state = 2 (full)
.hunger_state_timer = now.time + 12 hour
elseif .hunger_state == 2, add hunger_state_time_bonus
elseif .hunger >= 500 dcl_monster_data.hunger_state = 1
else dcl_monster_data.hunger_state = 0
'''
def use_item_wip(data) :

	dcl_item_id = data['dcl_item_id']
	Mon_ID = data['Mon_ID']
	with transaction.atomic():

		wiprecord = EtheremonDB.DCLItemWip.objects.select_for_update().filter(Q(dcl_item_id=dcl_item_id)).first()

		if not wiprecord :
			return 'ITEM_NOT_FOUND_IN_WIP'
		
		config_record = EtheremonDB.DCLItemClassConfig.objects.select_for_update().filter(Q(ItemClass=wiprecord.ItemClass) & Q(ItemVariety=wiprecord.ItemVariety)).first()
		
		if config_record is None:
			return 'NO_RELEVANT_DCL_ITEM_CLASS_CONFIG_FOUND'
		
		hunger_bonus = config_record.hunger_bonus
		dxp_bonus = config_record.dxp_bonus
		if wiprecord.end_timer >= get_timestamp() :
			return 'NOT_FULLY_GROWN'
		elif wiprecord.growth_state != 0 :	
			return 'ALREADY_EATEN_OR_PICKED'
		#if it is fully grown
		elif  wiprecord.end_timer <= get_timestamp() and wiprecord.growth_state == 0 :
			monrecord = EtheremonDB.DCLMonsterData.objects.select_for_update().filter(Q(Mon_ID=Mon_ID)).first()
			if monrecord is None:
				return 'MON_NOT_FOUND'
			monrecord.hunger_current +=  hunger_bonus
			monrecord.dxp += dxp_bonus

			if monrecord.hunger_current >= 1000 :
				monrecord.hunger_state	= 2 #full
				monrecord.hunger_state_end_timer = get_timestamp() + (3600 * 12) + config_record.hunger_state_time_bonus   #12 hours + bonus time
			elif monrecord.hunger_current >= 500 :	
				monrecord.hunger_state	= 1 #not that much hungry
			else : # less than 500
				monrecord.hunger_state	= 0 # hungry
			wiprecord.growth_state = 1


				#one final check before save
				#if food carries hunger_state_time_bonus then make it full
				#> 1000 is already handled above
			if (config_record.hunger_state_time_bonus > 0 and monrecord.hunger_current < 1000) :
				monrecord.hunger_state	= 2
				monrecord.hunger_current = 1000
				monrecord.hunger_state_end_timer = get_timestamp() + config_record.hunger_state_time_bonus  

			monrecord.save()	
			wiprecord.save()

			return 'SAVED'
				

def put_mon_to_sleep(data):
	with transaction.atomic():
		Mon_ID = data['Mon_ID']
		ts = get_timestamp()
		monrecord = EtheremonDB.DCLMonsterData.objects.select_for_update().filter(Q(Mon_ID=Mon_ID)).first()
		monrecord.last_saved = ts
		#SET sleep_end_timer to time require to 1000 Energy
		#So 1.388 energy per minute or 83,3 per hour or 1000 per 12 hours
		sleep_end_timer = get_timestamp() + (monrecord.Energy_max-monster.energy_current)*43.2
		monrecord.sleep_end_timer = sleep_end_timer
		monrecord.save()

	
		return "SAVED"



def get_user_active_stats(data):

		address = data['address']
		Mon_ID = data['Mon_ID']
		response_data = {}

		
		
		UserActiveStatus = EtheremonDB.DCLUserActiveStatus.objects.filter(Q(address=address)).first()

		if UserActiveStatus is None:
			return {"status" : "UserActiveStatus not found"}

		monrecord = EtheremonDB.DCLMonsterData.objects.filter(Q(Mon_ID=Mon_ID)).first()

		if monrecord.sleep_end_timer <= get_timestamp():
			return {"status" : "SUCCESS", 'awake' : 1, "sleep_end_timer" : monrecord.sleep_end_timer}

		if monrecord.sleep_end_timer > get_timestamp():
			return {"status" : "SUCCESS", 'awake' : 0, "sleep_end_timer" : monrecord.sleep_end_timer}


