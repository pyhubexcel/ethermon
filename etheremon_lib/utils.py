import json
import re
import os
from django.http import HttpResponse

from common.i18n import _
from constants import *
from common.geo_utils import *
import config
from etheremon_lib.monster_config import *

LEVEL_REQUIREMENT = None
MAX_LEVEL = 100

REGEX_EMAIL = re.compile(r'^[\w\-+.%]+@[\w\-.]+\.\w+$')

if hasattr(config, 'GEOIP_PATH'):
	if os.path.isfile(config.GEOIP_PATH):
		init_geo(config.GEOIP_PATH, GeoLibType.IP2LOCATION)
	else:
		print("geoip_file_not_found|file=%s", config.GEOIP_PATH)


def is_valid_email(email):
	return re.match(REGEX_EMAIL, email)


def api_response(request, data):
	response = HttpResponse(json.dumps(data), content_type='application/json; charset=utf-8')
	return response


def api_response_result(request, result_code, data=None):
	if data is not None:
		return api_response(request, {'result': result_code, 'data': data})
	else:
		return api_response(request, {'result': result_code})


def api_response_error_params(request):
	return api_response_result(request, ResultCode.ERROR_PARAMS)


def api_response_plain_text(request):
	response = HttpResponse('v=0', content_type='text/plain')
	return response


def get_class_image_url(class_id):
	return config.CLASS_IMG_URL % class_id


def get_gltf(class_id):
	return config.CLASS_GLTF_URL % class_id


def get_type_name(type_id, language):
	return _('monster.type.%s' % type_id, language)


def get_class_name(class_id, language):
	return _('monster.name.%s' % class_id, language)


def get_class_desc(class_id, language):
	return _('monster.desc.%s' % class_id, language)


def get_adv_site_image_url(site_id):
	return config.ADV_SITE_IMG_URL % site_id


def get_adv_site_name(site_id, language):
	return _('location.name.%s' % site_id, 'en')


def get_adv_site_description(site_id, language):
	return _('location.desc.%s' % site_id, 'en')


def get_adv_item_image(class_id, class_value):
	if class_id == 200 or class_id == 201:
		return config.ADV_ITEM_IMG_URL % (class_id, '_' + str(class_value))
	return config.ADV_ITEM_IMG_URL % (class_id, '')


def get_adv_item_name(class_id, value, language):
	if class_id == 200 or class_id == 201:
		return _('item.name.%s' % class_id, 'en') % value
	return _('item.name.%s' % class_id, 'en')


def get_adv_item_desc(class_id, value, language):
	if class_id == 200 or class_id == 201:
		return _('item.desc.%s' % class_id, 'en') % value
	return _('item.desc.%s' % class_id, 'en')


def gen_level_exp():
	global LEVEL_REQUIREMENT
	LEVEL_REQUIREMENT = {}
	level = 1
	requirement = 100
	sum = requirement
	while level <= MAX_LEVEL:
		LEVEL_REQUIREMENT[level] = sum
		level += 1
		requirement = (requirement * 11) / 10 + 5
		sum += requirement


gen_level_exp()


def get_level(exp):
	if LEVEL_REQUIREMENT is None:
		gen_level_exp()

	min_index = 1
	max_index = 100
	current_index = 0

	while min_index < max_index:
		current_index = (min_index + max_index) / 2
		if exp < LEVEL_REQUIREMENT[current_index]:
			max_index = current_index
		else:
			min_index = current_index + 1
	return min_index


def get_exp_by_level(level):
	if level == 0:
		return 0
	return LEVEL_REQUIREMENT[level] - 1


def get_gain_exp_gap(level):
	if level > 90:
		return 9
	if level > 70:
		return 8
	if level > 50:
		return 7
	if level > 30:
		return 6
	if level > 20:
		return 5
	if level > 10:
		return 4
	return 3


def get_gain_exp(level2, level1, win, is_new):
	if is_new:
		LEVEL_GAP = get_gain_exp_gap(level2)
	else:
		LEVEL_GAP = 3
	if level1 > level2 + LEVEL_GAP:
		half_level1 = (level2 + LEVEL_GAP) / 2
	else:
		half_level1 = level1 / 2
	rate = (21 ** half_level1) * 1000 / (20 ** half_level1)
	rate = rate * rate
	if (level1 > level2 + LEVEL_GAP and level2 + LEVEL_GAP > 2 * half_level1) or (
			level1 <= level2 + LEVEL_GAP and level1 > 2 * half_level1):
		rate = rate * 21 / 20
	if win:
		gain_exp = 30 * rate / 1000000
	else:
		gain_exp = 10 * rate / 1000000
	if level2 >= level1 + LEVEL_GAP:
		gain_exp = gain_exp / (2 ** ((level2 - level1) / LEVEL_GAP))
	return gain_exp


def get_new_monster_price(price, index):
	return price + price * (index - 1) / 1000


def get_stats(class_id, exp, base_stats):
	class_info = MONSTER_CLASS_STATS[int(class_id)]
	level = get_level(int(exp))
	bp = 0
	final_stat = []
	for index in xrange(0, 6):
		final_stat.append(base_stats[index] + level * class_info['steps'][index] * 3)
		bp += final_stat[index]
	bp /= 6
	return final_stat, bp, level


def get_next_level_exp(level):
	if level >= 100:
		return LEVEL_REQUIREMENT[99]
	else:
		return LEVEL_REQUIREMENT[level]


def get_perfection(base_stats, class_id):
	class_setting = MONSTER_CLASS_STATS.get(class_id)
	perfect_stats = [
		(base_stats[0], class_setting["stats"][0] + 31),
		(base_stats[1], class_setting["stats"][1] + 31),
		(base_stats[2], class_setting["stats"][2] + 31),
		(base_stats[3], class_setting["stats"][3] + 31),
		(base_stats[4], class_setting["stats"][4] + 31),
		(base_stats[5], class_setting["stats"][5] + 31),
	]
	total = base_stats[0] + base_stats[1] + base_stats[2] + base_stats[3] + base_stats[4] + base_stats[5]
	total_basic = class_setting["stats"][0] + class_setting["stats"][1] + class_setting["stats"][2] + \
				  class_setting["stats"][3] + class_setting["stats"][4] + class_setting["stats"][5]

	rate = round(100.0 * (total - total_basic) / (6 * 31), 3)
	return perfect_stats, rate


