# coding=utf-8
import requests
from random import randint
import json
from django.db import transaction
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from common.utils import parse_params, log_request, get_timestamp
from common.logger import log
from etheremon_lib.decorators.auth_decorators import sign_in_required
from etheremon_lib.transaction_manager import TxnStatus, TxnAmountTypes
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

from etheremon_service.contract.helper import _sync_player_dex


@csrf_exempt
@log_request()
@parse_params(form=DexGetSpeciesSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_species(request, data):
	trainer_address = data.get("trainer_address", "null").lower()
	if not Web3.isAddress(trainer_address):
		trainer_address = None

	if trainer_address is not None:
		monster_data_records = list(ema_monster_manager.get_monster_data_by_trainer(trainer_address))
	else:
		monster_data_records = []

	owned_class_ids = {}
	for mon in monster_data_records:
		owned_class_ids[mon.class_id] = True

	response_data = []
	for class_id, info in MONSTER_CLASS_STATS.items():
		if class_id != 21:
			location_list = []
			if class_id in CATCHABLE_MONSTER_CLASS_IDS:
				location_list.append(0)
			if class_id in ADVENTURE_MONSTER_CLASS_IDS:
				location_list.append(1)

			response_data.append({
				"class_id": class_id,
				"types": info["types"],
				"is_gason": int(info["is_gason"]),
				"is_collected": int(owned_class_ids.get(class_id, False)),
				"location": location_list,
			})

	return api_response_result(request, ResultCode.SUCCESS, response_data)


@csrf_exempt
@log_request()
@parse_params(form=DevGetMonsterSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
def get_monsters(request, data):
	page_id = data["page_id"]
	page_size = data["page_size"]
	class_ids = data.get("class_ids", None)
	types = data.get("types", [])
	bp = data.get("bp", [])
	level = data.get("level", [])
	sort = data.get("sort", None)
	search = data.get("search", None)
	forms = data.get("forms", [])
	egg = data.get("egg", None)
	gen = data.get("gen", None)

	monsters = EtheremonDB.EmaMonsterDataTab.objects.filter(~Q(class_id=21) & ~Q(trainer="0x0000000000000000000000000000000000000000"))

	# Filter class ids
	c_ids = set(MONSTER_CLASS_STATS.keys())

	type_ids = set([])
	for typ in types:
		type_ids = type_ids.union(MONSTER_TYPES_TO_CLASSES[typ])
	if len(type_ids):
		c_ids = c_ids.intersection(type_ids)

	form_ids = set([])
	for form in forms:
		form_ids = form_ids.union(MONSTER_FORMS_TO_CLASSES[form])
	if len(form_ids):
		c_ids = c_ids.intersection(form_ids)

	if search is not None:
		search_ids = set([])
		for c_id in MONSTER_CLASS_STATS.keys():
			if search.lower() in get_class_name(c_id, data["_client_language"]).lower():
				search_ids.add(c_id)
		c_ids = c_ids.intersection(search_ids)

	if gen is not None:
		c_ids = c_ids.intersection(MONSTER_GENS_TO_CLASSES[gen])

	if len(c_ids) != len(MONSTER_CLASS_STATS):
		monsters = monsters.filter(class_id__in=c_ids)

	if egg is not None:
		monsters = monsters.filter(egg_bonus=egg)

	if len(bp) == 2:
		monsters = monsters.filter(Q(bp__gte=bp[0]) & Q(bp__lte=bp[1]))

	if len(level) == 2:
		monsters = monsters.filter(Q(exp__gte=get_exp_by_level(level[0]-1)+1) & Q(exp__lte=get_exp_by_level(level[1])))

	if sort is not None:
		if sort == "-bp":
			monsters = monsters.order_by("-bp")
		elif sort == " bp":
			monsters = monsters.order_by("bp")
		elif sort == "-level":
			monsters = monsters.order_by("-exp")
		elif sort == " level":
			monsters = monsters.order_by("exp")
		elif sort == "-idx":
			monsters = monsters.order_by("-id")
		elif sort == " idx":
			monsters = monsters.order_by("id")
		elif sort == " create_index":
			monsters = monsters.order_by("create_index")

	print(sort)

	response_data = {
		"total_mons": monsters.count(),
		"mons": [],
	}

	for mon in monsters[(page_id-1)*page_size:page_id*page_size]:
		pending_exp = ema_monster_manager.get_pending_exp(mon.monster_id)
		pending_exp = 0 if pending_exp is None else pending_exp.adding_exp
		base_stats = [mon.b0, mon.b1, mon.b2, mon.b3, mon.b4, mon.b5]
		stats, bp, level = get_stats(mon.class_id, mon.exp, base_stats)
		total_stats, total_bp, total_level = get_stats(mon.class_id, mon.exp + pending_exp, base_stats)
		# perfect_stats, perfect_rate = get_perfection(base_stats, mon.class_id)

		monster_data = {
			"monster_id": mon.monster_id,
			"class_id": mon.class_id,
			"exp": mon.exp,
			"level": level,
			"battle_stats": stats,
			"bp": bp,

			"total_exp": mon.exp + pending_exp,
			"total_level": total_level,
			"total_battle_stats": total_stats,
			"total_bp": total_bp,

			"next_level_exp": get_next_level_exp(total_level),

			"create_index": mon.create_index,
			"create_time": mon.create_time,

			"egg_bonus": mon.egg_bonus,
			"types": MONSTER_CLASS_STATS[mon.class_id]["types"],
			# "perfect_stats": perfect_stats,
			# "perfect_rate": perfect_rate
		}

		response_data["mons"].append(monster_data)

	return api_response_result(request, ResultCode.SUCCESS, response_data)
