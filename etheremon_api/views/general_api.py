from django.views.decorators.csrf import csrf_exempt
from common.utils import parse_params, log_request
from etheremon_lib.contract_manager import *
from etheremon_lib.form_schema import *
from etheremon_lib.preprocessor import pre_process_header
from etheremon_lib.monster_config import MONSTER_CLASS_STATS, MONSTER_AGAINST_CONFIG
from etheremon_lib.infura_client import get_general_infura_client
from etheremon_lib.utils import *




def get_class_data(class_id, language="en"):
	class_setting = MONSTER_CLASS_STATS.get(class_id)
	if not class_setting:
		return None
	laying_setting = class_setting.get("lvl_lay", [0, 0])
	return {
		"class_id": class_id,
		"type_ids": class_setting["types"],
		"name": get_class_name(class_id, language),
		"description": get_class_desc(class_id, language),
		"image": get_class_image_url(class_id),
		"3d_model": get_gltf(class_id),
		"ancestor_class_ids": class_setting.get("ancestors", []),
		"generation": class_setting.get("generation", 0),
		"is_gason": class_setting.get("is_gason", False),
		"price": class_setting.get("price", 0),
		"level_steps": class_setting.get("steps", []),
		"transform_level": class_setting.get("lvl_transform", 0),
		"form_class_ids": class_setting.get("next_forms", []),
		"laying_level": laying_setting[0],
		"laying_deduction": laying_setting[1],
		"stat_range": [[stat, stat + 31] for stat in class_setting["stats"]]
	}


@csrf_exempt
@log_request(max_response_length=50)
@pre_process_header()
def get_type_metadata(request, data):
	response_data = {}
	for type_id, against_type_id in MONSTER_AGAINST_CONFIG.iteritems():
		response_data[type_id] = {
			"type_id": type_id,
			"against_type_id": against_type_id,
			"name": get_type_name(type_id, data["_client_language"])
		}
	return api_response_result(request, ResultCode.SUCCESS, response_data)


@csrf_exempt
@log_request(max_response_length=50)
@parse_params(form=GeneralGetClassMetadataSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_class_metadata(request, data):
	infura_client = get_general_infura_client()
	data_client = infura_client.getDataContract()
	try:
		class_ids = data["class_ids"]
		response_data = {}
		for class_id in class_ids:
			class_info = data_client.call().getMonsterClass(class_id)
			if class_id != class_info[0]:
				log.warn("invalid_return_class|class_id=%s,class_info=%s", class_id, class_info)
				continue
			class_data = get_class_data(class_id, data["_client_language"])
			if not class_data:
				log.warn("invalid_class_setting|class_id=%s", class_id)
				continue
			#price = web3_client.fromWei(class_info[1], 'ether')
			class_data["total"] = class_info[3]
			class_data["catchable"] = class_info[4]
			response_data[class_id] = class_data
		return api_response_result(request, ResultCode.SUCCESS, response_data)
	except Exception as ex:
		logging.exception("get_trainer_balance_fail|request=%s", request.body)
		return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": ex.message})



@csrf_exempt
@log_request()
@pre_process_header()
def get_ip_info(request, data):
	response_data = {"country_ip": data["_country_by_ip"], "ip": data["_ip"]}
	return api_response_result(request, ResultCode.SUCCESS, response_data)