# coding=utf-8
from django.views.decorators.csrf import csrf_exempt
from common.utils import parse_params, log_request
from etheremon_lib.form_schema import *
from etheremon_lib.preprocessor import pre_process_header
from etheremon_lib import cache_manager
from etheremon_lib.infura_client import get_general_infura_client
from etheremon_api.views.helper import *


@csrf_exempt
@log_request()
@parse_params(form=StoreGetClassesSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_classes(request, data):
	infura_client = get_general_infura_client()
	data_client = infura_client.getDataContract()

	try:
		class_ids = data.get("class_ids", MONSTER_CLASS_STATS.keys())
		response_data = {}

		for class_id in class_ids:
			if class_id in FORBIDDEN_MONS:
				continue

			# Case in cache
			data = cache_manager.get_monster_class_info(class_id)
			if data and class_id not in NEW_MONS:
				response_data[class_id] = data
				continue

			class_info = data_client.call().getMonsterClass(class_id)

			c_class_id = class_info[0]
			c_price = 1.0 * class_info[1] / ETH_UNIT
			c_return_price = 1.0 * class_info[2] / ETH_UNIT
			c_total = class_info[3]
			c_catchable = class_info[4]
			price_increase = 0

			if c_return_price == 0 and c_total > 0:
				price_increase = c_price / 1000
				c_price += price_increase * (c_total - 1)

			if class_id != c_class_id:
				log.warn("invalid_return_class|class_id=%s,class_info=%s", class_id, class_info)
				continue

			location_list = []
			if class_id in CATCHABLE_MONSTER_CLASS_IDS:
				location_list.append(MonLocations.STORE)
			if class_id in ADVENTURE_MONSTER_CLASS_IDS:
				location_list.append(MonLocations.ADVENTURE)
			if class_id in EGG_CLASS_IDS:
				location_list.append(MonLocations.EGG)

			data = {
				"class_id": c_class_id,
				"price": round(c_price, 6),
				"price_next": round(c_price + price_increase, 6),
				"price_safe": round(c_price + price_increase * 5, 6),
				"price_increase": round(price_increase, 6),
				"total": c_total,
				"catchable": c_catchable,
				"location": location_list
			}

			response_data[class_id] = data
			cache_manager.set_monster_class_info(class_id, data)

		return api_response_result(request, ResultCode.SUCCESS, response_data)
	except Exception as ex:
		logging.exception("get_trainer_balance_fail|request=%s", request.body)
		return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": ex.message})


