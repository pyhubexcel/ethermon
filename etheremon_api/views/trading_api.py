from django.views.decorators.csrf import csrf_exempt
from common.utils import parse_params, log_request
from etheremon_lib.form_schema import *
from etheremon_lib.contract_manager import *
from etheremon_lib import ema_trade_manager, ema_monster_manager
from etheremon_lib.preprocessor import pre_process_header
from etheremon_lib.utils import *

MARKET_PRICE_DIVISION = (10 ** 18) / (10 ** 6)


@csrf_exempt
@log_request(max_response_length=50)
def get_sell_order_list(request):
	selling_items = ema_trade_manager.get_items_by_type(EmaMarketType.SELL)
	selling_monster_ids = [record.monster_id for record in selling_items]
	monster_data_records = ema_monster_manager.get_monster_by_ids(selling_monster_ids)
	monster_data_dict = {}
	for monster_data in monster_data_records:
		monster_data_dict[monster_data.monster_id] = monster_data

	result_list = []
	index = 0
	for selling_item in selling_items:
		monster_id = selling_item.monster_id

		if monster_id not in monster_data_dict:
			continue

		monster_data = monster_data_dict[monster_id]
		is_catchable = monster_data.class_id in CATCHABLE_MONSTER_CLASS_IDS
		item = {
			"index": index,
			"monster_id": monster_id,
			"class_id": monster_data.class_id,
			"exp": monster_data.exp,
			"bp": monster_data.bp,
			"trainer": monster_data.trainer,
			"create_index": monster_data.create_index,
			"selling_price": selling_item.price * MARKET_PRICE_DIVISION,
			"bonus_egg": monster_data.egg_bonus,
			"class_catchable": is_catchable,
			"sell_time": selling_item.create_time
		}
		result_list.append(item)
		index += 1

	return api_response_result(request, ResultCode.SUCCESS, result_list)


@csrf_exempt
@log_request(max_response_length=50)
def get_borrow_order_list(request):
	borrow_items = ema_trade_manager.get_items_by_type(EmaMarketType.BORROW)
	borrow_monster_ids = [record.monster_id for record in borrow_items]
	monster_data_records = ema_monster_manager.get_monster_by_ids(borrow_monster_ids)
	monster_data_dict = {}
	for monster_data in monster_data_records:
		monster_data_dict[monster_data.monster_id] = monster_data

	result_list = []
	index = 0
	for borrow_item in borrow_items:
		monster_id = borrow_item.monster_id

		if monster_id not in monster_data_dict:
			continue

		monster_data = monster_data_dict[monster_id]
		extra_data = json.loads(borrow_item.extra_data)
		lent = borrow_item.status == EmaMarketStatus.LENT
		is_catchable = monster_data.class_id in CATCHABLE_MONSTER_CLASS_IDS
		item = {
			"index": index,
			"monster_id": monster_id,
			"class_id": monster_data.class_id,
			"exp": monster_data.exp,
			"bp": monster_data.bp,
			"owner": monster_data.trainer,
			"borrower": extra_data["borrower"].lower(),
			"lent": lent,
			"release_time": extra_data["release_time"],
			"create_index": monster_data.create_index,
			"lending_price": borrow_item.price * MARKET_PRICE_DIVISION,
			"bonus_egg": monster_data.egg_bonus,
			"class_catchable": is_catchable
		}
		result_list.append(item)
		index += 1
	return api_response_result(request, ResultCode.SUCCESS, result_list)


@csrf_exempt
@log_request()
@parse_params(form=TradingGetLendingListSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_lending_list(request, data):
	player = data["trainer_address"]
	lending_items = ema_trade_manager.get_lending_items(player)

	lending_monster_ids = [record.monster_id for record in lending_items]
	monster_data_records = ema_monster_manager.get_monster_by_ids(lending_monster_ids)
	monster_data_dict = {}
	for monster_data in monster_data_records:
		monster_data_dict[monster_data.monster_id] = monster_data

	result_list = []
	for lending_item in lending_items:
		extra_data = json.loads(lending_item.extra_data)
		monster_data = monster_data_dict[lending_item.monster_id]
		result_item = {
			"monster_id": lending_item.monster_id,
			"owner": lending_item.player,
			"borrower": extra_data.get("borrower"),
			"lending_price": lending_item.price * MARKET_PRICE_DIVISION,
			"lent": True,
			"getback_time": extra_data.get("release_time"),
			"class_id": monster_data.class_id,
			"exp": monster_data.exp,
			"bp": monster_data.bp,
			"create_index": monster_data.create_index,
			"bonus_egg": monster_data.egg_bonus,
		}
		result_list.append(result_item)

	return api_response_result(request, ResultCode.SUCCESS, result_list)
