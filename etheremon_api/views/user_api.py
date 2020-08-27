# coding=utf-8
import requests
from random import randint
import json
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from common.utils import parse_params, log_request, get_timestamp
from common.logger import log
from etheremon_lib.decorators.auth_decorators import sign_in_required
from etheremon_lib.transaction_manager import TxnStatus, TxnAmountTypes, TxnTypes
from etheremon_lib.utils import *
from etheremon_lib.form_schema import *
from etheremon_lib.preprocessor import pre_process_header
from etheremon_lib import user_manager, ladder_manager, crypt, emont_bonus_manager, ema_energy_manager, \
	transaction_manager
from etheremon_lib import ema_monster_manager, ema_egg_manager
from etheremon_lib import ema_market_manager, ema_battle_manager, ema_player_manager, ema_adventure_manager
from etheremon_lib.models import EtheremonDB
from etheremon_lib.infura_client import get_general_infura_client
from etheremon_api.views.helper import *
from etheremon_api.views.ema_helper import _verify_signature
import qrcode
from io import BytesIO
from etheremon_service.contract.helper import _sync_player_dex
from django.http import FileResponse
from django.utils.encoding import smart_str


SHOW_LETTERS = ['a', 'b', 'e', 'g', 'h', 't', 'n', 'r', 'y']

MARKET_PRICE_DIVISION = (10 ** 18) / (10 ** 6)

'''
@csrf_exempt
@log_request()
@parse_params(form=GetTrainerBalanceSchema, method='POST', data_format='JSON', error_handler=api_response_error_params)
def get_trainer_balance(request, data):
	# verify information
	if not Web3.isAddress(data["trainer_address"]):
		log.warn("send_to_address_invalid|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invald_send_to_address"})

	try:
		balance = ether_data_contract.call().getExpectedBalance(data['trainer_address'])
		return api_response_result(request, ResultCode.SUCCESS, {
			"balance": balance
		})
	except Exception as ex:
		logging.exception("get_trainer_balance_fail|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": ex.message})
'''


def update_and_get_claiming_emont(uid):
	infura_client = get_general_infura_client()
	refer_contract = infura_client.getReferContract()
	pending_claim = user_manager.get_pending_emont_claim(uid)
	if pending_claim:
		amount = refer_contract.call().getClaimIdInfo(pending_claim.id)
		if amount == pending_claim.amount:
			pending_claim.status = ReferClaimStatus.STATUS_COMPLETE
			pending_claim.update_time = get_timestamp()
			pending_claim.save()
	return pending_claim


QR = {
	"type": "object",
	"properties": {
		"address": {
			"type": "string",
		}
	},
	"required": ["address"]
}


@csrf_exempt
@parse_params(form=QR, method='GET', data_format='FORM', error_handler=api_response_error_params)
def qr_code(request, data):
	address = data['address']
	qr = qrcode.QRCode(version=1,
						error_correction=qrcode.constants.ERROR_CORRECT_L,
						box_size=15,
						border=2)
	qr.add_data(address)
	qr.make(fit=True)
	img = qr.make_image()
	response = HttpResponse(content_type="image/png")
	img.save(response,"PNG")
	return response




@csrf_exempt
@parse_params(form=UserSubscribeForm, method='POST', data_format='JSON', error_handler=api_response_error_params)
def subscribe(request, data):
	email_address = data['email_address']
	subscribe_type = data.get("type", SubscribeType.HOME_PAGE)

	try:
		octopus_config = config.OCTOPUS_EMAIL_CONFIG
		url = octopus_config["subscribe_url"]
		if subscribe_type == SubscribeType.ADVENTURE_PAGE:
			url = octopus_config["adventure_url"]
		r = requests.post(url,
			data = {
				"api_key": octopus_config["api_key"],
				"email_address": email_address,
				"subscribed": True
			})
	except:
		logging.exception("request_email_octopus_fail|email_address=%s", email_address)
		return api_response_result(request, ResultCode.ERROR_SERVER)

	if r.status_code == 200:
		log.data("subscribe|email=%s,response=%s", email_address, r.text)
		return api_response_result(request, ResultCode.SUCCESS)
	else:
		log.info("subscribe_fail|status_code=%s,message=%s", r.status_code, r.text)
		response_data = r.json()
		if response_data.get("error", {}).get("code") == "MEMBER_EXISTS_WITH_EMAIL_ADDRESS":
			log.info("re_subscribe|email=%s", email_address)
			return api_response_result(request, ResultCode.SUCCESS)
		else:
			return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": json.loads(r.text).get("error", {}).get("code")})


@csrf_exempt
@log_request()
@parse_params(form=UserGetMonsterDexSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_my_monster(request, data):
	# verify information
	# if not Web3.isAddress(data["trainer_address"]):
	# 	log.warn("send_to_address_invalid|data=%s", data)
	# 	return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invald_send_to_address"})

	try:
		data["trainer_address"] = data["trainer_address"].lower()
		metamask_flag = data.get("metamask_flag", MetamaskFlag.DISABLE)
		response_data = {
			"username": user_manager.get_user_name(data["trainer_address"]),
			"total_emont": 0,
			"total_eth": 0,
			"total_monster": 0,
			"total_monster_class": 0,
			"total_monster_sold": 0,
			"total_lending": 0,
			"total_renting": 0,
			"total_selling": 0,
			"total_adventure_item": ema_adventure_manager.count_adventure_items(data["trainer_address"]),
			"current_balance": 0,
			"hatching_egg": {},
			"monsters": {},
		}
		if metamask_flag == MetamaskFlag.DISABLE:
			infura_client = get_general_infura_client()
			emont_contract = infura_client.getEmontContract()
			world_contract = infura_client.getWorldContract()

			total_emont = emont_contract.call().balanceOf(data['trainer_address'])
			total_emont = (total_emont * 1.0) / 10**8
			response_data["total_emont"] = total_emont
			response_data["current_balance"] = world_contract.call().getTrainerBalance(data['trainer_address'])

			total_eth = infura_client.getCurrentEthBalance(data['trainer_address'])
			response_data["total_eth"] = (total_eth * 1.0) / 10**18

		# Egg
		hatching_egg = ema_egg_manager.get_hatching_egg(data['trainer_address'])
		if hatching_egg:
			response_data["hatching_egg"] = {
				"egg_id": hatching_egg.egg_id,
				"class_id": hatching_egg.class_id,
				"hatch_time": hatching_egg.hatch_time
			}

		on_chain_mons = list(ema_monster_manager.get_monster_data_by_trainer(data['trainer_address']))
		off_chain_mons = list(ema_monster_manager.get_offchain_mons(player_address=data['trainer_address']))
		monster_data_records = on_chain_mons + off_chain_mons
		response_data["total_monster"] = len(monster_data_records)
		monster_class_set = set()

		if response_data["total_monster"] > 0:
			for monster_record in monster_data_records:
				monster_id = -monster_record.id if not hasattr(monster_record, 'monster_id') else monster_record.monster_id
				name = monster_record.name
				class_id = monster_record.class_id
				monster_class_set.add(class_id)
				exp = monster_record.exp
				create_index = 0 if not hasattr(monster_record, 'create_index') else monster_record.create_index
				create_time = monster_record.create_time
				base_stats = [monster_record.b0, monster_record.b1, monster_record.b2, monster_record.b3, monster_record.b4, monster_record.b5]
				stats, bp, level = get_stats(class_id, exp, base_stats)

				monster_market = ema_market_manager.get_monster_market(monster_id)
				is_approvable = not monster_market

				monster_status = EmaMonsterStatus.Normal
				trading = {"lending_price": 0, "selling_price": 0, "release_time": 0}
				if monster_market:
					if monster_market.type == EmaMarketType.SELL:
						trading["selling_price"] = float(monster_market.price) * MARKET_PRICE_DIVISION / 10 ** 18
						monster_status = EmaMonsterStatus.Selling
						response_data["total_selling"] += 1
					else:
						trading["lending_price"] = float(monster_market.price) / MARKET_PRICE_DIVISION / 10 ** 18
						extra_data = json.loads(monster_market.extra_data)
						trading["release_time"] = extra_data.get("release_time", 0)
						if monster_market.status == EmaMarketStatus.LENT:
							monster_status = EmaMonsterStatus.Renting
							response_data["total_renting"] += 1
						else:
							monster_status = EmaMonsterStatus.Lending
							response_data["total_lending"] += 1

				pending_exp = ema_monster_manager.get_pending_exp(monster_id)
				if pending_exp is None:
					pending_exp = 0
				else:
					pending_exp = pending_exp.adding_exp

				total_stats, total_bp, total_level = get_stats(class_id, exp + pending_exp, base_stats)

				perfect_stats, perfect_rate = get_perfection(base_stats, class_id)

				monster_data = {
					"monster_id": monster_id,
					"class_id": class_id,
					"class_name": get_class_name(class_id, data["_client_language"]),
					"exp": exp,
					"pending_exp": pending_exp,
					"total_level": total_level,
					"level": level,
					"next_level_exp": get_next_level_exp(level),
					"bp": bp,
					"total_bp": total_bp,
					"battle_stats": stats,
					"total_battle_stats": total_stats,
					"create_index": create_index,
					"create_time": create_time,
					"user_defined_name": name,
					"status": monster_status,
					"egg_bonus": 0 if not hasattr(monster_record, 'egg_bonus') else monster_record.egg_bonus,
					"trading": trading,
					"approvable": is_approvable,
					"perfect_stats": perfect_stats,
					"perfect_rate": perfect_rate
				}

				response_data["monsters"][monster_id] = monster_data
			response_data["total_monster_class"] = len(monster_class_set)

		# Lunar Event
		# current_ts = get_timestamp()
		# if LUNAR_19_START_TIME <= current_ts <= LUNAR_19_END_TIME:
		# 	response_data["event_data"] = {
		# 		"bonus_eggs_left": max(0, 888 - EtheremonDB.EmaEggDataTab.objects.filter(mother_id=0).filter(
		# 			create_time__gte=LUNAR_19_START_TIME).filter(create_time__lte=LUNAR_19_END_TIME).count()),
		# 		"player_purchases": max(0, EtheremonDB.EmaEggDataTab.objects.filter(mother_id=0).filter(
		# 			trainer=data["trainer_address"]).filter(create_time__gte=LUNAR_19_START_TIME).filter(
		# 			create_time__lte=LUNAR_19_END_TIME).count())
		# 	}

		return api_response_result(request, ResultCode.SUCCESS, response_data)
	except Exception as ex:
		logging.exception("get_trainer_balance_fail|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": ex.message})


@csrf_exempt
@log_request()
@parse_params(form=UserGetSoldMonsterSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_sold_monster(request, data):
	# verify information
	if not Web3.isAddress(data["trainer_address"]):
		log.warn("send_to_address_invalid|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_send_to_address"})

	trainer_address = data["trainer_address"].lower()
	response_data = []
	sold_monsters = ema_market_manager.get_sold_monsters(trainer_address)
	sold_monster_ids = [record.monster_id for record in sold_monsters]
	monster_data_records = ema_monster_manager.get_monster_by_ids(sold_monster_ids)
	monster_data_dict = {}
	for monster_data in monster_data_records:
		monster_data_dict[monster_data.monster_id] = monster_data
	for sold_monster in sold_monsters:
		monster_data = monster_data_dict[sold_monster.monster_id]
		exp = 1
		if sold_monster.exp > 0:
			exp = sold_monster.exp
		base_stats = [monster_data.b0, monster_data.b1, monster_data.b2, monster_data.b3, monster_data.b4, monster_data.b5]
		final_stats, bp, level = get_stats(monster_data.class_id, exp, base_stats)
		next_level_exp = get_next_level_exp(level)
		sold_price = sold_monster.price * 1.0 / 1000000
		item = {
			"monster_id": sold_monster.monster_id,
			"class_id": sold_monster.class_id,
			"exp": exp,
			"level": level,
			"next_level_exp": next_level_exp,
			"bp": bp,
			"current_owner": sold_monster.buyer,
			"create_index": monster_data.create_index,
			"sold_price": sold_price,
			"sold_time": sold_monster.buy_time,
			"bonus_egg": monster_data.egg_bonus
		}
		response_data.append(item)

	response_data.sort(key=lambda x: x["sold_time"], reverse=True)

	return api_response_result(request, ResultCode.SUCCESS, response_data)


@csrf_exempt
@log_request()
@parse_params(form=UserUpdateInfoSchema, method='POST', data_format='JSON', error_handler=api_response_error_params)
@pre_process_header()
@sign_in_required()
def update_info(request, data):
	trainer_address = data["trainer_address"].lower()
	email = data["email"]
	username = data["username"]

	# verify information
	if not Web3.isAddress(trainer_address):
		log.warn("send_to_address_invalid|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_send_to_address"})

	if not is_valid_email(email):
		log.warn("invalid_email|email=%s", email)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_email"})

	user = user_manager.get_user_info(trainer_address)
	try:
		refer_uid = crypt.decrypt_refer_code(data.get("refer_code", ""))
	except Exception as error:
		logging.exception("invalid_refer_code|refer_code=%s", data.get("refer_code", ""))
		refer_uid = 0
	if user:
		user.email = email
		user.username = username
		user.ip = data["_ip"]
		user.country = data["_country_by_ip"]
		user.update_time = get_timestamp()
		user.save()
	else:
		# Case new user, create user & initialize energy
		user = user_manager.create_new_user(trainer_address, email, username, data["_ip"], data["_country_by_ip"], refer_uid)
		ema_energy_manager.initialize_energy_if_not_exist(trainer_address, 20)

	return api_response_result(request, ResultCode.SUCCESS, {
		"uid": user.uid,
		"username": user.username,
		"email": ''.join(letter if letter in SHOW_LETTERS else '*' for letter in user.email),
	})


@csrf_exempt
@log_request()
@parse_params(form=UserGetInfoSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_info(request, data):
	print ("good takkeur$%$%$%")
	#print (user)
	# verify information
	if not Web3.isAddress(data["trainer_address"]):
		log.warn("send_to_address_invalid|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invald_send_to_address"})
	trainer_address = data["trainer_address"].lower()

	user = user_manager.get_user_info(trainer_address)
	

	response_data = {
		"address": trainer_address,
		"username": "",
		"email": "",
		"user_type": UserType.NORMAL,
		"emont_claimed": 0,
		"emont_pending": 0,
		"emont_in_game_balance": 0,
		"refer_code": "",
	}

	if user:
		response_data["username"] = user.username
		response_data["email"] = ''.join(letter if letter in SHOW_LETTERS else '*' for letter in user.email)
		response_data["user_type"] = user_manager.get_user_type(trainer_address)
		response_data["emont_claimed"] = 1.0 * user_manager.get_claimed_emont_bonus(user.uid) / EMONT_UNIT
		response_data["refer_code"] = crypt.encrypt_refer_code(user.uid, trainer_address)

		emont_total_bonus = emont_bonus_manager.get_total_emont_bonus(user.uid)
		pending_claim = update_and_get_claiming_emont(user.uid)
		if pending_claim:
			pending_amount = 1.0 * pending_claim.amount / EMONT_UNIT
			if pending_claim.status == ReferClaimStatus.STATUS_PENDING:
				response_data["emont_pending"] = pending_amount
			else:
				response_data["emont_claimed"] += pending_amount

		response_data["emont_in_game_balance"] = emont_total_bonus - response_data["emont_claimed"] - response_data["emont_pending"]

	return api_response_result(request, ResultCode.SUCCESS, response_data)


@csrf_exempt
@log_request()
@parse_params(form=ClaimReferRewardSchema, method='POST', data_format='JSON', error_handler=api_response_error_params)
@pre_process_header()
def cash_out_in_game_emont(request, data):
	# verify information
	if not Web3.isAddress(data["trainer_address"]):
		log.warn("send_to_address_invalid|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_send_to_address"})

	trainer_address = data["trainer_address"].lower()
	claim_timestamp = data["claim_timestamp"]
	signature = data["signature"]

	# verify signature
	message = "%s-%s" % ("claim_refer", claim_timestamp)
	if not _verify_signature(message, signature, trainer_address):
		log.warn("claim_refer_invalid_signature|trainer=%s,message=%s", trainer_address, message)
		return api_response_result(request, ResultCode.ERROR_SIGNATURE)

	user = user_manager.get_user_info(trainer_address)
	if not user:
		log.warn("user_not_exist|trainer_address=%s", trainer_address)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_user"})

	pending_claim = update_and_get_claiming_emont(user.uid)

	if pending_claim and pending_claim.status == ReferClaimStatus.STATUS_PENDING:
		to_claim_id = pending_claim.id
		to_claim_amount = pending_claim.amount
	else:
		total_emont_bonus = emont_bonus_manager.get_total_emont_bonus(user.uid) * EMONT_UNIT
		claimed_emont = user_manager.get_claimed_emont_bonus(user.uid)
		to_claim_amount = max(0, total_emont_bonus - claimed_emont)

		if to_claim_amount > 0:
			pending_claim = user_manager.create_emont_claim(user.uid, to_claim_amount)
			to_claim_id = pending_claim.id

	if to_claim_amount == 0:
		log.warn("invalid_claim_amount|trainer_address=%s,uid=%s", trainer_address, user.uid)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_claim_amount"})

	to_claim_amount = int(to_claim_amount)
	current_ts = get_timestamp()
	random_nonce = randint(0, 429496729)
	refer_token = crypt.create_refer_reward_token(to_claim_id, user.uid, to_claim_amount, current_ts, random_nonce, random_nonce)
	r, s, v = sign_refer_claim(refer_token, trainer_address)

	response_data = {"token": "0x" + refer_token, "r": r, "s": s, "v": v}

	log.data("claim_refer|trainer_address=%s,uid=%s,token=0x%s", trainer_address, user.uid, refer_token)

	return api_response_result(request, ResultCode.SUCCESS, response_data)


@csrf_exempt
@log_request()
@parse_params(form=ClaimRewardSchema, method='POST', data_format='JSON', error_handler=api_response_error_params)
@pre_process_header()
@sign_in_required()
def claim_reward(request, data):
	trainer_address = data["trainer_address"].lower()
	reward_txn_id = data["reward_id"]

	# verify information
	if not Web3.isAddress(trainer_address):
		log.warn("send_to_address_invalid|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_send_to_address"})

	txn_info = transaction_manager.get_transaction_by_id(reward_txn_id)
	if not txn_info or txn_info.player_address != trainer_address:
		log.warn("invalid_reward|trainer_address=%s", trainer_address)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_reward"})

	if txn_info.status not in [TxnStatus.INIT, TxnStatus.PENDING]:
		log.warn("reward_already_claimed|trainer_address=%s", trainer_address)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_reward"})

	txn_info.status = TxnStatus.PENDING
	txn_info.save()

	# Map to contract's reward types
	if txn_info.amount_type == TxnAmountTypes.ADV_LEVEL_STONE_1:
		reward_type = EtheremonClaimRewardContract.REWARD_TYPES["level_stone"]
		reward_value = 1
	elif txn_info.amount_type == TxnAmountTypes.ADV_LEVEL_STONE_2:
		reward_type = EtheremonClaimRewardContract.REWARD_TYPES["level_stone"]
		reward_value = 2
	elif txn_info.amount_type == TxnAmountTypes.MON:
		reward_type = EtheremonClaimRewardContract.REWARD_TYPES["mon"]
		reward_value = txn_info.amount_value
	else:
		log.warn("reward_not_supported|trainer_address=%s", trainer_address)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_reward"})

	current_ts = get_timestamp()
	claim_reward_token = crypt.create_claim_reward_token(txn_info.id, reward_type, reward_value, current_ts)

	r, s, v = sign_claim_reward(claim_reward_token, trainer_address)

	response_data = {"token": "0x" + claim_reward_token, "r": r, "s": s, "v": v}
	log.data("claim_reward|trainer_address=%s,token=0x%s", trainer_address, claim_reward_token)

	return api_response_result(request, ResultCode.SUCCESS, response_data)


@csrf_exempt
@log_request()
@parse_params(form=GetRewardSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_rewards(request, data):
	trainer_address = data["trainer_address"].lower()

	response_data = [{
		"id": r.id,
		"amount_type": r.amount_type,
		"amount_value": r.amount_value,
		"detail": r.txn_info,
		"status": r.status,
		"timestamp": r.create_time
	} for r in EtheremonDB.TransactionTab.objects
		.filter(player_address=trainer_address).filter(txn_type=TxnTypes.GENERAL_REWARD)
		.order_by("status").order_by("id")
	]

	return api_response_result(request, ResultCode.SUCCESS, response_data)


@csrf_exempt
@log_request()
@parse_params(form=UserSyncDatachema, method='POST', data_format='JSON', error_handler=api_response_error_params)
@pre_process_header()
def sync_data(request, data):
	# verify information
	if not Web3.isAddress(data["trainer_address"]):
		log.warn("send_to_address_invalid|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_send_to_address"})
	trainer_address = data["trainer_address"].lower()

	current_ts = get_timestamp()

	# update rank
	infura_client = get_general_infura_client()

	# sync player index
	data_contract = infura_client.getDataContract()
	transform_contract = infura_client.getTransformContract()
	_sync_player_dex(data_contract, trainer_address, transform_contract, True)

	# update energy
	energy_contract = infura_client.getEnergyContract()
	(free_amount, paid_amount, last_claim) = energy_contract.call().getPlayerEnergy(trainer_address)
	if free_amount + paid_amount > 0:
		record = EtheremonDB.EmaPlayerEnergyTab.objects.filter(trainer=trainer_address).first()
		if record:
			if free_amount > record.free_amount:
				latest_gap = free_amount - record.free_amount
				new_available_energy = record.init_amount + free_amount + record.paid_amount - record.consumed_amount - record.invalid_amount
				if new_available_energy > 50:
					deducted_amount = new_available_energy - 50
					if deducted_amount > latest_gap:
						record.invalid_amount += latest_gap
					else:
						record.invalid_amount += deducted_amount
			record.free_amount = free_amount
			record.paid_amount = paid_amount
			record.last_claim_time = last_claim
			record.update_time = current_ts
			record.save()
		else:
			EtheremonDB.EmaPlayerEnergyTab.objects.create(
				trainer=trainer_address,
				init_amount=0,
				free_amount=free_amount,
				paid_amount=paid_amount,
				invalid_amount=0,
				consumed_amount=0,
				last_claim_time=last_claim,
				create_time=current_ts,
				update_time=current_ts
			)

	# sync explore
	pending_explore = EtheremonDB.EmaAdventureExploreTab.objects.filter(sender=trainer_address).filter(reward_monster_class=0).filter(reward_item_class=0).filter(reward_item_value='0').first()
	if pending_explore:
		adventure_explore_contract = infura_client.getAdventureExploreContract()
		explore_data = adventure_explore_contract.call().getExploreItem(pending_explore.explore_id)
		pending_explore.reward_monster_class = explore_data[5]
		pending_explore.reward_item_class = explore_data[6]
		pending_explore.reward_item_value = str(explore_data[7])
		pending_explore.save()

	# sync site revenue
	if data.get("site_id"):
		site_id = data.get('site_id')
		adventure_data_contract = infura_client.getAdventureDataContract()
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

	if data.get("token_id"):
		token_id = data.get("token_id")
		adventure_data_contract = infura_client.getAdventureDataContract()
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

	return api_response_result(request, ResultCode.SUCCESS)
