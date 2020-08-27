from django.views.decorators.csrf import csrf_exempt
from common.utils import parse_params, log_request
from etheremon_lib.burn_manager import BURN_MON_REWARDS, BurnStatus
from etheremon_lib.decorators.auth_decorators import sign_in_required
from etheremon_lib.form_schema import *
from etheremon_lib import ema_monster_manager, user_manager, burn_manager
from etheremon_lib.preprocessor import pre_process_header
from etheremon_lib.ema_claim_manager import get_pending_exp_claim
from etheremon_lib import ema_market_manager
from etheremon_api.views.helper import *
from etheremon_api.views.description import Description
from etheremon_api.views.credit import credit_data
from etheremon_lib.monster_config import _MONSTER_CLASS_STATS
from etheremon_lib.i18n import en

MARKET_PRICE_DIVISION = (10 ** 18) / (10 ** 6)

@csrf_exempt
@log_request()
@parse_params(form=MonsterGetDataSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_data(request, data):

	monster_ids = data["monster_ids"]
	response_data = {}

	for monster_id in monster_ids:
		if monster_id > 0:
			monster_data = ema_monster_manager.get_monster_data(monster_id)
		else:
			monster_data = ema_monster_manager.get_offchain_mon_by_id(-monster_id)

		if not monster_data:
			continue

		pending_exp = ema_monster_manager.get_pending_exp(monster_id)
		pending_exp = 0 if pending_exp is None else pending_exp.adding_exp

		pending_exp_record = get_pending_exp_claim(monster_id)
		pending_exp_txn = 0 if pending_exp_record is None else pending_exp_record.exp

		base_stats = [monster_data.b0, monster_data.b1, monster_data.b2, monster_data.b3, monster_data.b4, monster_data.b5]

		# On-chain stats
		stats, bp, level = get_stats(
			monster_data.class_id,
			monster_data.exp,
			base_stats,
		)

		# On-chain + Off-chain stats
		total_stats, total_bp, total_level = get_stats(
			monster_data.class_id,
			monster_data.exp + pending_exp,
			base_stats,
		)

		# Perfect Stats
		perfect_stats, perfect_rate = get_perfection(base_stats, monster_data.class_id)

		owner = monster_data.trainer

		# Market data
		monster_market = ema_market_manager.get_monster_market(monster_id)
		is_approvable = not monster_market

		monster_status = EmaMonsterStatus.Normal
		trading = {"lending_price": 0, "selling_price": 0, "release_time": 0, "borrower": "", "borrower_name": ""}
		if monster_market:
			if monster_market.type == EmaMarketType.SELL:
				trading["selling_price"] = round(float(monster_market.price) * MARKET_PRICE_DIVISION / ETH_UNIT, 6)
				monster_status = EmaMonsterStatus.Selling
			else:
				owner = monster_market.player
				trading["lending_price"] = round(float(monster_market.price) * MARKET_PRICE_DIVISION / ETH_UNIT, 6)
				extra_data = json.loads(monster_market.extra_data)
				trading["release_time"] = extra_data.get("release_time", 0)
				trading["borrower"] = extra_data.get("borrower", "")
				trading["borrower_name"] = user_manager.get_user_name(trading["borrower"])

				if monster_market.status == EmaMarketStatus.LENT:
					monster_status = EmaMonsterStatus.Renting
				else:
					monster_status = EmaMonsterStatus.Lending

		mon_history = ema_market_manager.get_trading_history(monster_id)
		trading_history = []
		for e in mon_history:
			if e.is_sold == 1:
				trading_history.append({
					"class_id": e.class_id,
					"seller": e.seller,
					"seller_name": user_manager.get_user_name(e.seller),
					"buyer": e.buyer,
					"buyer_name": user_manager.get_user_name(e.buyer),
					"price": round(float(e.price) * MARKET_PRICE_DIVISION / ETH_UNIT, 8),
					"timestamp": e.buy_time,
					"txn": e.txn_hash
				})
		type_data = _MONSTER_CLASS_STATS.get(monster_data.class_id).get("types") if _MONSTER_CLASS_STATS.get(monster_data.class_id) is not None else 0
		types = []
		monster_dat = en.i18n.I18N['en']
		for ty_data in type_data:
			types.append(monster_dat.get("monster.type."+str(ty_data)))
			
		response_data[monster_id] = {
			"monster_id": monster_id,
			"class_id": monster_data.class_id,
			"name": monster_data.name,
			"owner": owner,
			"owner_name": user_manager.get_user_name(owner),
			"exp": monster_data.exp,
			"pending_exp": pending_exp,
			"pending_exp_txn": pending_exp_txn,
			"description": Description.get("monster.desc."+str(monster_data.class_id)),
			"types":types,
			"trading_history": trading_history,
			"level": level,
			"total_level": total_level,
			"next_level_exp": get_next_level_exp(level),
			"bp": bp,
			"total_bp": total_bp,
			"battle_stats": stats,
			"total_battle_stats": total_stats,

			"status": monster_status,
			"trading": trading,

			"egg_bonus": 0 if not hasattr(monster_data, 'egg_bonus') else monster_data.egg_bonus,
			"create_index": 0 if not hasattr(monster_data, 'create_index') else monster_data.create_index,
			"create_time": monster_data.create_time,

			"perfect_stats": perfect_stats,
			"perfect_rate": perfect_rate,

			"burn_reward": burn_manager.get_reward_from_level(level, monster_data.class_id),

			# public api
			"class_name": get_class_name(monster_data.class_id, data["_client_language"]),
			"user_defined_name": monster_data.name,
			"image": get_class_image_url(monster_data.class_id),
			"3d_model": get_gltf(monster_data.class_id),
			"approvable": is_approvable
		}
	return api_response_result(request, ResultCode.SUCCESS, response_data)



@csrf_exempt
@log_request()
@parse_params(form=MonsterGetDataSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_metadata(request, data):

	monster_ids = data["monster_ids"]
	response_data = {}

	for monster_id in monster_ids:
		if monster_id > 0:
			monster_data = ema_monster_manager.get_monster_data(monster_id)
		else:
			monster_data = ema_monster_manager.get_offchain_mon_by_id(-monster_id)

		if monster_id > 0:
			monster_dcl_data = ema_monster_manager.get_monster_dcl_data(monster_id)

		if not monster_data:
			continue

		pending_exp = ema_monster_manager.get_pending_exp(monster_id)
		pending_exp = 0 if pending_exp is None else pending_exp.adding_exp

		pending_exp_record = get_pending_exp_claim(monster_id)
		pending_exp_txn = 0 if pending_exp_record is None else pending_exp_record.exp

		base_stats = [monster_data.b0, monster_data.b1, monster_data.b2, monster_data.b3, monster_data.b4, monster_data.b5]

		# On-chain stats
		stats, bp, level = get_stats(
			monster_data.class_id,
			monster_data.exp,
			base_stats,
		)
		if monster_dcl_data is not None:
			dcl_level = get_level(monster_dcl_data.dxp)
		else:
			dcl_level = 0
		# On-chain + Off-chain stats
		total_stats, total_bp, total_level = get_stats(
			monster_data.class_id,
			monster_data.exp + pending_exp,
			base_stats,
		)

		# Perfect Stats
		perfect_stats, perfect_rate = get_perfection(base_stats, monster_data.class_id)

		owner = monster_data.trainer

		# Market data
		monster_market = ema_market_manager.get_monster_market(monster_id)
		is_approvable = not monster_market

		monster_status = EmaMonsterStatus.Normal
		trading = {"lending_price": 0, "selling_price": 0, "release_time": 0, "borrower": "", "borrower_name": ""}
		if monster_market:
			if monster_market.type == EmaMarketType.SELL:
				trading["selling_price"] = round(float(monster_market.price) * MARKET_PRICE_DIVISION / ETH_UNIT, 6)
				monster_status = EmaMonsterStatus.Selling
			else:
				owner = monster_market.player
				trading["lending_price"] = round(float(monster_market.price) * MARKET_PRICE_DIVISION / ETH_UNIT, 6)
				extra_data = json.loads(monster_market.extra_data)
				trading["release_time"] = extra_data.get("release_time", 0)
				trading["borrower"] = extra_data.get("borrower", "")
				trading["borrower_name"] = user_manager.get_user_name(trading["borrower"])

				if monster_market.status == EmaMarketStatus.LENT:
					monster_status = EmaMonsterStatus.Renting
				else:
					monster_status = EmaMonsterStatus.Lending

		mon_history = ema_market_manager.get_trading_history(monster_id)
		trading_history = []
		for e in mon_history:
			if e.is_sold == 1:
				trading_history.append({
					"class_id": e.class_id,
					"seller": e.seller,
					"seller_name": user_manager.get_user_name(e.seller),
					"buyer": e.buyer,
					"buyer_name": user_manager.get_user_name(e.buyer),
					"price": round(float(e.price) * MARKET_PRICE_DIVISION / ETH_UNIT, 8),
					"timestamp": e.buy_time,
					"txn": e.txn_hash
				})
		create_index = 0 if not hasattr(monster_data, 'create_index') else monster_data.create_index
		if int(create_index) == 1:
			create_index_value = "Gold"
		elif int(create_index) == 2:
			create_index_value = "Silver"
		elif int(create_index) == 3:
			create_index_value = "Bronze"
		else:
			create_index_value = "-"
		traits = [
				{"trait_type": "Class Name", "value": get_class_name(monster_data.class_id, data["_client_language"])},
				{"trait_type": "Badge", "value": create_index_value},
				{"trait_type": "Mon_Artist", "value": credit_data.get(monster_data.class_id).get("credit") if credit_data.get(monster_data.class_id) is not None else None},
				{"trait_type": "OnChain_EXP", "value": monster_data.exp},
				{"trait_type": "Offchain_EXP", "value": pending_exp},
				{"trait_type": "OnChain_Level", "value": level},
				{"trait_type": "OffChain_Level", "value": total_level},
				{"trait_type": "OffChain_BP", "value": total_bp},
				{"trait_type": "OnChain_BP", "value": bp},
				{"trait_type": "Hit Point HP", "value": total_stats[0]},
				{"trait_type": "Primary ATK", "value": total_stats[1]},
				{"trait_type": "Primary DEF", "value": total_stats[2]},
				{"trait_type": "Secondary ATK", "value": total_stats[3]},
				{"trait_type": "Secondary DEF", "value": total_stats[4]},
				{"trait_type": "Speed SPD", "value": total_stats[5]},
				{"trait_type": "DCL level", "value": dcl_level},
				{"trait_type": "DXP", "value": monster_dcl_data.dxp if monster_dcl_data is not None else 0},
				{"display_type": "number", "trait_type": "Catch_Number", "value": 0 if not hasattr(monster_data, 'create_index') else monster_data.create_index},
    			{"display_type": "boost_number", "trait_type": "Egg_Bonus", "value": 0 if not hasattr(monster_data, 'egg_bonus') else monster_data.egg_bonus},
				{"display_type": "boost_percentage", "trait_type": "Perfection", "value": perfect_rate}
		]

		response_data = {
			"name": monster_data.name,
			"image": get_class_image_url(monster_data.class_id),
			"external_url": "https://ethermon.io/mons-info/"+str(monster_id),
			"description": Description.get("monster.desc."+str(monster_data.class_id)),
			"attributes": traits,

			#"monster_id": monster_id,
			#"class_id": monster_data.class_id,
			#"owner": owner,
			#"owner_name": user_manager.get_user_name(owner),
			#"create_time": monster_data.create_time,
			#"user_defined_name": monster_data.name,
			#"approvable": is_approvable
			#"exp": monster_data.exp,
			#"pending_exp": pending_exp,
			#notused"pending_exp_txn": pending_exp_txn,

			#notused"trading_history": trading_history,

			#"level": level,
			#"total_level": total_level,
			#notused"next_level_exp": get_next_level_exp(level),
			#"bp": bp,
			#"total_bp": total_bp,
			#notused"battle_stats": stats,
			#"total_battle_stats": total_stats,

			#notused"status": monster_status,
			#notused"trading": trading,

			#"egg_bonus": 0 if not hasattr(monster_data, 'egg_bonus') else monster_data.egg_bonus,
			#"create_index": 0 if not hasattr(monster_data, 'create_index') else monster_data.create_index,
			

			#notused"perfect_stats": perfect_stats,
			#"perfect_rate": perfect_rate,

			#notused"burn_reward": burn_manager.get_reward_from_level(level, monster_data.class_id),

			# public api
			#"class_name": get_class_name(monster_data.class_id, data["_client_language"]),
			#"user_defined_name": monster_data.name,
			#notused"3d_model": get_gltf(monster_data.class_id),
			#"approvable": is_approvable
		}
	return api_response_result(request,ResultCode.SUCCESS,response_data)



@csrf_exempt
@log_request()
@parse_params(form=RequestAddExpMonSchema, method='POST', data_format='JSON', error_handler=api_response_error_params)
@pre_process_header()
def add_exp_to_mon(request, data):
	exp_gain = data["exp"]
	monster_id = data["monster_id"]

	#ema_monster_manager.add_exp(monster_id, exp_gain)

	return api_response_result(request, ResultCode.SUCCESS, {
		'result': 'success',		
	})





@csrf_exempt
@log_request()
@parse_params(form=RequestBurnMonSchema, method='POST', data_format='JSON', error_handler=api_response_error_params)
@pre_process_header()
@sign_in_required()
def request_burn_mon(request, data):
	trainer_address = data["trainer_address"].lower()
	monster_id = data["monster_id"]

	# verify information
	if not Web3.isAddress(trainer_address):
		log.warn("send_to_address_invalid|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_send_to_address"})

	mon = ema_monster_manager.get_monster_data(monster_id)
	if not mon or mon.trainer != trainer_address:
		log.warn("burn_invalid_mon|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_FORBIDDEN, {"error_message": "invalid_mon_id"})

	mon_level = get_level(mon.exp)
	reward = burn_manager.get_reward_from_level(mon_level, mon.class_id)

	burn_request = burn_manager.get_or_create_burn_request(
		player_address=trainer_address,
		mon_id=mon.monster_id,
		mon_level=mon_level,
		mon_exp=mon.exp,
		amount_type=reward['type'],
		amount_value=reward['value'],
		status=BurnStatus.INIT
	)

	log.data("burn_mon_request|trainer_address=%s,data=%s", trainer_address, data)
	return api_response_result(request, ResultCode.SUCCESS, {
		'mon_id': burn_request.mon_id,
		'mon_level': burn_request.mon_level,
		'mon_exp': burn_request.mon_exp,
		'reward_type': burn_request.amount_type,
		'reward_value': burn_request.amount_value,
		'burn_identifier': burn_manager.get_contract_burn_id(burn_request.mon_id, burn_request.id),
	})


@csrf_exempt
@log_request()
@parse_params(form=ClaimOffchainMonsSchema, method='POST', data_format='JSON', error_handler=api_response_error_params)
@pre_process_header()
# @sign_in_required()
def claim_offchain_mons(request, data):
	trainer_address = data["trainer_address"].lower()

	# verify information
	if not Web3.isAddress(trainer_address):
		log.warn("send_to_address_invalid|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_send_to_address"})

	ema_monster_manager.create_offchain_mons(player_address=trainer_address)

	return api_response_result(request, ResultCode.SUCCESS, {
		'offchain_mons': [{
			'id': - mon.id,
			'name': mon.name,
			'class_id': mon.class_id,
		} for mon in ema_monster_manager.get_offchain_mons(player_address=trainer_address)]
	})

