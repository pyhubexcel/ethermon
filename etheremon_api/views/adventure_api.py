from django.views.decorators.csrf import csrf_exempt
from web3 import Web3, KeepAliveRPCProvider
from common.utils import parse_params, log_request
from common.logger import log
from common.utils import get_timestamp
from etheremon_lib.infura_client import InfuraClient
from etheremon_lib.utils import *
from etheremon_lib.form_schema import *
from etheremon_lib.preprocessor import pre_process_header
from etheremon_lib.ema_adventure_manager import get_adventure_items, get_sites_by_trainer, get_pending_claim_sites, get_player_explores
from etheremon_lib.ema_adventure_manager import get_site_token_balance, count_explore_by_site, get_items_by_trainer, get_pending_explore
from etheremon_lib.ema_adventure_manager import set_adventure_vote, get_adventure_vote, count_adventure_item_by_class
from etheremon_lib.ema_monster_manager import get_monster_data
from etheremon_lib.config import INFURA_API_URLS
from etheremon_api.views.ema_helper import _verify_signature
from etheremon_api.views.locations import Location
from etheremon_api.views.items import ITEMS_ORIGIN

@csrf_exempt
@log_request()
@parse_params(form=AdventureGetItemDataSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_item_data(request, data):
	token_ids = data["token_ids"]
	response_data = {}

	token_records = get_adventure_items(token_ids)

	for record in token_records:
		if record.token_id <= 1080:
			name = get_adv_site_name(record.class_id, data["_client_language"])
			image = get_adv_site_image_url(record.class_id)
			desc = get_adv_site_description(record.class_id, data["_client_language"])
		else:
			name = get_adv_item_name(record.class_id, record.value, data["_client_language"])
			image = get_adv_item_image(record.class_id, record.value)
			desc = get_adv_item_desc(record.class_id, record.value, data["_client_language"])

		response_data[record.token_id] = {
			"token_id": record.token_id,
			"owner": record.owner,
			"item_class": record.class_id,
			"item_value": record.value,
			"name": name,
			"image": image,
			"desc": desc
		}

	return api_response_result(request, ResultCode.SUCCESS, response_data)



@csrf_exempt
@log_request()
@parse_params(form=AdventureGetItemDataSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_item_metadata(request, data):
	token_ids = data["token_ids"]
	response_data = {}

	token_records = get_adventure_items(token_ids)

	for record in token_records:
		if record.token_id <= 1080:
			name = get_adv_site_name(record.class_id, data["_client_language"])
			image = get_adv_site_image_url(record.class_id)
			desc = get_adv_site_description(record.class_id, data["_client_language"])
		else:
			name = get_adv_item_name(record.class_id, record.value, data["_client_language"])
			image = get_adv_item_image(record.class_id, record.value)
			desc = get_adv_item_desc(record.class_id, record.value, data["_client_language"])

		if int(record.token_id) <= 540:
			class_value = "Adventure Site"
		else:
			class_checking = record.class_id
			class_value = None
			if int(class_checking) == 200:
				class_value = "Level Stone"
			elif int(class_checking) == 201:
				class_value = "EXP Potion"
			elif int(class_checking) in range(310,312):
				class_value = "HP Shards"
			elif int(class_checking) in range(300,302):
				class_value = "PA Shards"
			elif int(class_checking) in range(320,322):
				class_value = "PD Shards"
			elif int(class_checking) in range(330,332):
				class_value = "SA Shards"
			elif int(class_checking) in range(340,342):
				class_value = "SD Shards"
			elif int(class_checking) in range(350,352):
				class_value = "SP Shards"

		traits = [{"trait_type": "Class", "value": class_value}]
		if int(record.token_id) <= 540:
			traits.append({"trait_type": "Location", "value": Location.get("location.name."+str(record.class_id))})
		if int(record.token_id) > 540:
			traits.append({"trait_type": "Item", "value": ITEMS_ORIGIN.get("item.name."+str(record.class_id))})

		"""
		response_data[record.token_id] = {
			"attributes":traits,
			"token_id": record.token_id,
			"item_value": record.value,
			"item_class": record.class_id,
			"owner": record.owner,
			"name": name,
			"image": image,
			"description": desc
		}
		"""
		response_data = {
			"attributes":traits,
			#"token_id": record.token_id,
			#"item_value": record.value,
			#"item_class": record.class_id,
			#"owner": record.owner,
			"name": name,
			"image": image,
			"description": desc
		}

	return api_response_result(request, ResultCode.SUCCESS, response_data)





@csrf_exempt
@log_request()
@parse_params(form=AdventureGetMySitesSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_my_sites(request, data):
	# verify information
	if not Web3.isAddress(data["trainer_address"]):
		log.warn("send_to_address_invalid|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invald_send_to_address"})
	trainer_address = data["trainer_address"].lower()

	response_data = {
		"total_balance": {
			"eth_amount": 0,
			"emont_amount": 0
		},
		"vote": {
			"explore_eth_fee": 0.01,
			"explore_emont_fee": 15,
			"challenge_eth_fee": 0.01,
			"challenge_emont_fee": 15
		},
		"sites": [],
		"claimable_sites": []
	}

	response_data["vote"] = get_adventure_vote(trainer_address)
	token_records = get_sites_by_trainer(trainer_address)
	for record in token_records:
		if record.token_id <= 1080:
			name = get_adv_site_name(record.class_id, data["_client_language"])
			image = get_adv_site_image_url(record.class_id)
			desc = get_adv_site_description(record.class_id, data["_client_language"])
		else:
			name = ""
			image = ""
			desc = ""
		eth_revenue, emont_revenue = get_site_token_balance(record.class_id, record.token_id)
		eth_revenue = round(eth_revenue, 6)
		emont_revenue = round(emont_revenue, 6)
		response_data["total_balance"]["eth_amount"] += eth_revenue
		response_data["total_balance"]["emont_amount"] += emont_revenue
		response_data["sites"].append({
			"token_id": record.token_id,
			"owner": record.owner,
			"item_class": record.class_id,
			"item_value": record.value,
			"image": image,
			"name": name,
			"desc": desc,
			"eth_amount": eth_revenue,
			"emont_amount": emont_revenue,
			"total_visit": count_explore_by_site(record.class_id)
		})

	claimable_records = get_pending_claim_sites(trainer_address)
	for claimable_record in claimable_records:
		bid_price = claimable_record.bid_amount
		if claimable_record.site_id < 53:
			bid_price = bid_price * 1.0 / (10 ** 18)
		else:
			bid_price = bid_price * 1.0 / (10 ** 8)
		response_data["claimable_sites"].append({
			"site_id": claimable_record.site_id,
			"site_index": claimable_record.site_index,
			"bid_price": bid_price
		})

	return api_response_result(request, ResultCode.SUCCESS, response_data)

@csrf_exempt
@log_request()
@parse_params(form=AdventureGetMyAdventureItemsSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_my_adventure_items(request, data):
	trainer_address = data["trainer_address"].lower()
	item_records = get_items_by_trainer(trainer_address)

	response_data = {}
	for item_record in item_records:
		response_data[item_record.token_id] = {
			"item_id": item_record.token_id,
			"item_class": item_record.class_id,
			"item_value": item_record.value
		}

	return api_response_result(request, ResultCode.SUCCESS, response_data)

@csrf_exempt
@log_request()
@parse_params(form=AdventureGetMyExploresSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_my_explores(request, data):
	trainer_address = data["trainer_address"].lower()
	response_data = {}

	explore_records = get_player_explores(trainer_address)
	for explore_record in explore_records:
		reward_monster_class = explore_record.reward_monster_class
		reward_item_class = explore_record.reward_item_class
		reward_item_value = explore_record.reward_item_value
		if reward_monster_class == 0 and reward_item_class == 0 and reward_item_value == '0':
			continue
		monster_class = 0
		if explore_record.monster_type == EmaAdventureMonsterType.ETHEREMON:
			monster_data = get_monster_data(explore_record.monster_id)
			monster_class = monster_data.class_id
			if monster_class == 21:
				continue
		reward_value = int(reward_item_value)
		if reward_value > 0 and reward_item_class == 0:
			reward_value = reward_value * 1.0 / 10 ** 8
		explore_item = {
			"monster_class": monster_class,
			"explore_id": explore_record.explore_id,
			"trainer": explore_record.sender,
			"monster_type": explore_record.monster_type,
			"monster_id": explore_record.monster_id,
			"site_class": explore_record.site_id,
			"block": explore_record.start_block,
			"reward_monster_class": reward_monster_class,
			"reward_item_class": reward_item_class,
			"reward_value": reward_value,
			"timestamp": explore_record.create_time,
		}
		response_data[explore_record.explore_id] = explore_item

	return api_response_result(request, ResultCode.SUCCESS, response_data)


@csrf_exempt
@log_request()
@parse_params(form=AdventureGetPendingExploreSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_adventure_pending_explore(request, data):
	trainer_address = data["trainer_address"].lower()
	response_data = {
		"explore_id": 0,
		"monster_type": 0,
		"monster_id": 0,
		"monster_class": 0,
		"site_id": 0,
		"start_block": 0,
		"end_block": 0,
		"current_block": 0,
		"estimated_time_back": 0,
		"can_fasten": False,
	}
	pending_explore = get_pending_explore(trainer_address)
	if pending_explore:
		if pending_explore.monster_type == EmaAdventureMonsterType.ETHEREMON:
			monster_data = get_monster_data(pending_explore.monster_id)
			if monster_data.class_id == 21:
				log.warn("sending_invalid_monster|explore_id=%s", pending_explore.explore_id)
				return api_response_result(request, ResultCode.SUCCESS, response_data)
			response_data["monster_class"] = monster_data.class_id

		response_data["explore_id"] = pending_explore.explore_id
		response_data["monster_type"] = pending_explore.monster_type
		response_data["monster_id"] = pending_explore.monster_id
		response_data["site_id"] = pending_explore.site_id
		response_data["start_block"] = pending_explore.start_block
		response_data["end_block"] = pending_explore.end_block

		infura_client = InfuraClient(INFURA_API_URLS["adventure_task"])
		response_data["current_block"] = infura_client.getCurrentBlock()
		if response_data["end_block"] > response_data["current_block"]:
			response_data["estimated_time_back"] = (response_data["end_block"] - response_data["current_block"]) * 15
		if response_data["current_block"] >= response_data["start_block"] + 2:
			response_data["can_fasten"] = True

	return api_response_result(request, ResultCode.SUCCESS, response_data)


@csrf_exempt
@log_request()
@parse_params(form=AdventureGetAdventureStatsSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_adventure_stats(request, data):
	trainer_address = data["trainer_address"].lower()
	user_explore_records = get_player_explores(trainer_address)
	response_data = {
		"total_explore": 0,
		"total_visited_sites": 0,
		"total_collected_monsters": 0,
		"total_collected_items": 0,
		"total_sent_monsters": 0
	}

	if user_explore_records:
		response_data["total_explore"] = len(user_explore_records)
		site_id_set = set()
		etheremon_monster_id_set = set()
		cryptokitties_monster_id_set = set()
		for explore_record in user_explore_records:
			site_id_set.add(explore_record.site_id)
			if explore_record.monster_type == EmaAdventureMonsterType.ETHEREMON:
				etheremon_monster_id_set.add(explore_record.monster_id)
			elif explore_record.monster_type == EmaAdventureMonsterType.CRYPTOKITTIES:
				cryptokitties_monster_id_set.add(explore_record.monster_id)
			if explore_record.reward_monster_class > 0:
				response_data["total_collected_monsters"] += 1
			if explore_record.reward_item_class > 0:
				response_data["total_collected_items"] += 1
		response_data["total_sent_monsters"] = len(etheremon_monster_id_set) + len(cryptokitties_monster_id_set)
		response_data["total_visited_sites"] = len(site_id_set)
	return api_response_result(request, ResultCode.SUCCESS, response_data)


@csrf_exempt
@log_request()
@parse_params(form=AdventureVoteSchema, method='POST', data_format='JSON', error_handler=api_response_error_params)
@pre_process_header()
def vote(request, data):
	trainer_address = data["trainer_address"].lower()
	signature = data["signature"].lower()
	vote_timestamp = data["vote_timestamp"]
	explore_eth = round(data["explore_eth"], 5)
	explore_emont = round(data["explore_emont"], 5)
	challenge_eth = round(data["challenge_eth"], 5)
	challenge_emont = round(data["challenge_emont"], 5)

	# verify information
	if not Web3.isAddress(data["trainer_address"]):
		log.warn("trainer_address_invalid|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invald_send_to_address"})

	current_ts = get_timestamp()
	if abs(current_ts - vote_timestamp) > 5 * 60:
		log.warn("old_vote_time|current_ts=%s,data=%s", current_ts, data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_timestamp"})

	# verify signature
	message = "vote-%s" % vote_timestamp
	if not _verify_signature(message, signature, trainer_address):
		log.warn("trainer_invalid_signature|trainer=%s,message=%s", trainer_address, message)
		return api_response_result(request, ResultCode.ERROR_SIGNATURE)

	set_adventure_vote(trainer_address, explore_eth, explore_emont, challenge_eth, challenge_emont, vote_timestamp)

	log.data("update_vote|trainer=%s,explore_eth=%s,explore_emont=%s,challenge_eth=%s,challenge_emont=%s",
		trainer_address, explore_eth, explore_emont, challenge_eth, challenge_emont)

	return api_response_result(request, ResultCode.SUCCESS)

@csrf_exempt
@log_request()
@parse_params(form=AdventureCountItemSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def count_item(request, data):
	item_classes = data["item_classes"]
	item_count = count_adventure_item_by_class(item_classes)
	return api_response_result(request, ResultCode.SUCCESS, {"count": item_count})