from django.views.decorators.csrf import csrf_exempt
from common.utils import parse_params, log_request
from etheremon_lib.decorators.auth_decorators import sign_in_required
from etheremon_lib.dcl_schema import *
from etheremon_lib.preprocessor import pre_process_header
from etheremon_api.views.helper import *
from django.db.models import Q
from etheremon_lib.models import EtheremonDB
from etheremon_lib import dcl_manager
from django.db import transaction

from django.http.response import JsonResponse



@csrf_exempt
@log_request()
@parse_params(form=ItemClassConfigGetDataSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_item_class_config(request, data):
	id = 0
	if 'id' in data:
		id = data['id']

	try:
		if id > 0 :
			icc = EtheremonDB.DCLItemClassConfig.objects.filter(dcl_item_class_ID=id).first()
			return api_response_result(request, ResultCode.SUCCESS, {
			"dcl_item_class_ID": icc.dcl_item_class_ID,
			"ItemClass": icc.ItemClass,
			"ItemVariety": icc.ItemVariety,
			"craft_timer": icc.craft_timer,
			"cost": icc.cost,
			"craft_formula": icc.craft_formula,
			"dxp_bonus": icc.dxp_bonus,
			"hunger_bonus": icc.hunger_bonus,
			"energy_bonus": icc.energy_bonus,
			"hp_bonus": icc.hp_bonus,
			"mood_bonus": icc.mood_bonus,
			"alignment_status": icc.alignment_status,
			"buff_status": icc.buff_status,
			"hunger_state_time_bonus": icc.hunger_state_time_bonus,
			"mon_lv_req": icc.mon_lv_req,
			"create_time": icc.create_time,
			})
		else:
			records = EtheremonDB.DCLItemClassConfig.objects.all()
			response_data = []
			for icc in records:
				print (icc.dcl_item_class_ID)
				response_data.append( {
					"dcl_item_class_ID": icc.dcl_item_class_ID,
					"ItemClass": icc.ItemClass,
					"ItemVariety": icc.ItemVariety,
					"craft_timer": icc.craft_timer,
					"cost": icc.cost,
					"craft_formula": icc.craft_formula,
					"dxp_bonus": icc.dxp_bonus,
					"hunger_bonus": icc.hunger_bonus,
					"energy_bonus": icc.energy_bonus,
					"hp_bonus": icc.hp_bonus,
					"mood_bonus": icc.mood_bonus,
					"alignment_status": icc.alignment_status,
					"buff_status": icc.buff_status,
					"hunger_state_time_bonus": icc.hunger_state_time_bonus,
					"mon_lv_req": icc.mon_lv_req,
					"create_time": icc.create_time
				})
			return api_response_result(request, ResultCode.SUCCESS, response_data)

	except Exception as ex:
			print (ex)
			return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": "record not found"})



@csrf_exempt
@log_request()
@parse_params(form=ItemWipGetDataSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_item_wip(request, data):

	try:
		address = data['address']

		records = EtheremonDB.DCLItemWip.objects.filter(address=address).all()

		response_data = []
		for ItemWip in records:
			response_data.append( {
				"dcl_item_id": ItemWip.dcl_item_id,
				"ItemClass": ItemWip.ItemClass,
				"ItemVariety": ItemWip.ItemVariety,
				"wild": ItemWip.wild,
				"wild_count": ItemWip.wild_count,
				"address": ItemWip.address,
				"growth_state": ItemWip.growth_state,
				"host_id": ItemWip.host_id,
				"meta_id": ItemWip.meta_id,
				"start_timer": ItemWip.start_timer,
				"end_timer": ItemWip.end_timer
			})
			return api_response_result(request, ResultCode.SUCCESS, response_data)

		
	except Exception as ex:
			return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": "record not found"})			

@csrf_exempt
@log_request()
@parse_params(form=EthermonWildGetDataSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_ethermon_wild(request, data):

	try:
		mon_class = data['mon_class']

		records =  EtheremonDB.DCLEthermonWild.objects.filter(mon_class=mon_class).all()

		response_data = []
		for EthermonWild in records:
			response_data.append( {
			"mon_class": EthermonWild.mon_class,
			"wild": EthermonWild.wild,
			"wild_count": EthermonWild.wild_count,
			"address": EthermonWild.address,
			"spawn_start": EthermonWild.spawn_start,
			"spawn_end": EthermonWild.spawn_end,
			"host_id": EthermonWild.host_id,
			"meta_id": EthermonWild.meta_id,
			"create_time": EthermonWild.create_time,
			})
		return api_response_result(request, ResultCode.SUCCESS, response_data)
		
	except Exception as ex:
			return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": "record not found"})		


@csrf_exempt
@log_request()
@parse_params(form=UserFungibleGetDataSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_user_fungible(request, data):

	try:
		address = data['address']

		records = EtheremonDB.DCLUserFungible.objects.filter(address=address).all()
		print (records)
		response_data = []
		for UserFungible in records:
			response_data.append( {
			"dcl_fungible_id": UserFungible.dcl_fungible_id,
			"craft_hierachy": UserFungible.craft_hierachy,
			"address": UserFungible.address,
			"ItemClass": UserFungible.ItemClass,
			"ItemVariety": UserFungible.ItemVariety,
			"qty": UserFungible.qty,
			"create_time": UserFungible.create_time,
			})
		return api_response_result(request, ResultCode.SUCCESS, response_data)



		
	except Exception as ex:
			print (ex)
			return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": "record not found"})			


@csrf_exempt
@log_request()
@parse_params(form=UserFungibleUpdateQtySchema, method='POST', data_format='JSON', error_handler=api_response_error_params)
@pre_process_header()
def use_dcl_user_fungible(request, data):
	try:
		status = dcl_manager.use_user_fungible(data)
		if  status == 'SAVED':
			return api_response_result(request, ResultCode.SUCCESS, {"data": "success"})
		else :
			return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": status})

	except Exception as ex:
		print (ex)
		return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": ex})	


@csrf_exempt
@log_request()
@parse_params(form=MonIDSchema, method='POST', data_format='JSON', error_handler=api_response_error_params)
@pre_process_header()
def put_mon_to_sleep(request, data):
	try:
		status = dcl_manager.put_mon_to_sleep(data)
		if  status == 'SAVED':
			return api_response_result(request, ResultCode.SUCCESS, {"data": "success"})
		else :
			return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": status})

	except Exception as ex:
		print (ex)
		return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": ex})	


@csrf_exempt
@log_request()
@parse_params(form=ItemWIPUpdateSchema, method='POST', data_format='JSON', error_handler=api_response_error_params)
@pre_process_header()
#eat food
def use_item_wip(request, data):
	try:
		status = dcl_manager.use_item_wip(data)
		if status == 'SAVED':
			return api_response_result(request, ResultCode.SUCCESS, {"data": "success"})
		else :
			return JsonResponse({'error_message':status}, status=500)
			#return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": status})		
	except Exception as ex:
		print (ex)
		return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": ex})			

	
@csrf_exempt
@log_request()
@parse_params(form=MonsterDataGetDataSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_monster_data(request, data):

	try:
		id = data['id']

		response_data = {}

		MonsterData = EtheremonDB.DCLMonsterData.objects.filter(Mon_ID=id).first()

		return api_response_result(request, ResultCode.SUCCESS, {
			"Mon_ID": MonsterData.Mon_ID,
			"dxp": MonsterData.dxp,
			"last_saved": MonsterData.last_saved,
			"HP_current": MonsterData.HP_current,
			"energy_current": MonsterData.energy_current,
			"hunger_current": MonsterData.hunger_current,
			"mood_current": MonsterData.mood_current,
			"HP_max": MonsterData.HP_max,
			"Energy_max": MonsterData.Energy_max,
			"Hunger_max": MonsterData.Hunger_max,
			"Mood_max": MonsterData.Mood_max,
			"hunger_state": MonsterData.hunger_state,
			"hunger_state_end_timer": MonsterData.hunger_state_end_timer,
			"sleep_end_timer": MonsterData.sleep_end_timer,
		
		})
	except Exception as ex:
			print (ex)
			return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": "record not found"})			

@csrf_exempt
@log_request()
@parse_params(form=UserActiveStatusGetDataSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_user_active_stats(request, data):

	try:
		ret = dcl_manager.get_user_active_stats(data)
		if ret["status"] == 'SUCCESS':
			return api_response_result(request, ResultCode.SUCCESS, ret)
		else :
			return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": ret["status"]})		
	except Exception as ex:
		return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": ex})	


@csrf_exempt
@log_request()
@parse_params(form=PurchaseCallbackSchema, method='POST', data_format='JSON', error_handler=api_response_error_params)
@pre_process_header()
def purchase_callback(request, data):
	try:
		status = dcl_manager.add_purchase(data)
		if status == 'SAVED':
			return api_response_result(request, ResultCode.SUCCESS, {"data": "success"})
		else :
			return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": status})		
	except Exception as ex:
		return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": ex})	



@csrf_exempt
@log_request()
@parse_params(form=DCLUserLoginSchema, method='POST', data_format='JSON', error_handler=api_response_error_params)
@pre_process_header()
def user_login(request, data):
	try:
		dcl_manager.dcl_user_login(data)
		return api_response_result(request, ResultCode.SUCCESS, {
			'result': 'success',		
		})
	except Exception as ex:
		return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": ex})	






