import etheremon_lib.config as config
from common import cache, jsonutils
from common.logger import log

CACHE_KEY_SELLING_LIST = 'sell_list'
CACHE_KEY_BORROWING_LIST = 'borrow_list'
CACHE_KEY_GENERAL_STATS = 'general_stats'
CACHE_PRACTICE_LAST_ACTION = 'practice_last_action.%s'
CACHE_KEY_BEST_BUILDER_LIST = 'best_builder_list.%s.%s'
CACHE_KEY_BEST_CASTLE_LIST = 'best_castle_list.%s.%s'
CACHE_KEY_BEST_BATTLER_LIST = 'best_battler_list.%s.%s'
CACHE_KEY_BEST_MON_LIST = 'best_mon_list.%s.%s'
CACHE_KEY_BEST_COLLECTOR_LIST = 'best_collector_list.%s.%s'
CACHE_KEY_NEW_PLAYER_COUNT = 'new_player_count'
CACHE_KEY_MON_CLASS_INFO = 'mon_class_info.%s'
CACHE_KEY_ACTIVE_CASTLE = 'get_active_castle'
CACHE_KEY_EGG_LIST = 'egg_list'
CACHE_KEY_MARKET_BLOCK = 'market_history_block'
CACHE_KEY_MARKET_BLOCK_BACKUP = 'market_history_block_backup'
CACHE_KEY_WORLD_CRON_BLOCK = 'world_cron_block'
CACHE_KEY_SALES_HISTORY = 'sales_history.%s.%s.%s.%s'
CACHE_KEY_CRON_ID = 'cron_id.%s'
CACHE_KEY_EGG_NO = 'egg_no.%s'
CACHE_KEY_MARKET_HISTORY_COUNT = 'sales_history_count'
CACHE_KEY_PLAYER_QUESTS = 'player_quests.%s.%s'
CACHE_KEY_PLAYER_USERNAME = 'user_name.%s'

MON_CLASS_CACHE_TIME = 20 * 60		# 20 mins
LEADER_BOARD_CACHE_TIME = 15 * 60
GENERAL_STATS_CACHE_TIME = 60
SALES_HISTORY_CACHE_TIME = 10 * 60
SALES_HISTORY_COUNT_CACHE_TIME = 5 * 60
SELL_BORROW_LIST_EXPIRE_TIME = 60 * 60

ACTIVE_CASTLE_CACHE_TIME = 3 * 60
EGG_LIST_CACHE_TIME = 12 * 60 * 60

PLAYER_QUESTS_CACHE_TIME = 1 * 60		# 1 mins
PLAYER_USER_NAME = 2 * 60		# 2 mins

DEFAULT_EXPIRE = 0

if hasattr(config, 'CACHE_SERVERS'):
	cache.init_cache(config.CACHE_SERVERS)


def cache_get_json(key, client_id="default"):
	# No cache on TEST
	if not config.TEST:
		return jsonutils.from_json_safe(cache.get_cache(client_id).get(key))
	else:
		return None


def cache_set_json(key, dict_value, expiry_time=DEFAULT_EXPIRE, client_id="default"):
	# No cache on TEST
	if not config.TEST:
		cache.get_cache(client_id).set(key, jsonutils.to_json(dict_value), expiry_time)


def cache_delete_json(key, client_id="default"):
	cache.get_cache(client_id).delete(key)


def get_selling_list():
	return cache_get_json(CACHE_KEY_SELLING_LIST)


def set_selling_list(sell_list):
	return cache_set_json(CACHE_KEY_SELLING_LIST, sell_list, SELL_BORROW_LIST_EXPIRE_TIME)


def get_borrowing_list():
	return cache_get_json(CACHE_KEY_BORROWING_LIST)


def set_borrowing_list(borrow_list):
	return cache_set_json(CACHE_KEY_BORROWING_LIST, borrow_list, SELL_BORROW_LIST_EXPIRE_TIME)


def get_total_castle():
	return cache_get_json(CACHE_KEY_BORROWING_LIST)


def get_general_stats():
	return cache_get_json(CACHE_KEY_GENERAL_STATS)


def set_general_stats(stats_dict):
	cache_set_json(CACHE_KEY_GENERAL_STATS, stats_dict, GENERAL_STATS_CACHE_TIME)


def get_practice_last_action(trainer_address, client_id="default"):
	return cache.get_cache(client_id).get(CACHE_PRACTICE_LAST_ACTION % trainer_address)


def set_practice_last_action(trainer_address, value, expiry_time=0, client_id="default"):
	cache.get_cache(client_id).set(CACHE_PRACTICE_LAST_ACTION % trainer_address, value, expiry_time)


def get_best_builder_list(page_id, page_size):
	return cache_get_json(CACHE_KEY_BEST_BUILDER_LIST % (page_id, page_size))


def set_best_builder_list(page_id, page_size, builder_list):
	cache_set_json(CACHE_KEY_BEST_BUILDER_LIST % (page_id, page_size), builder_list, LEADER_BOARD_CACHE_TIME)


def get_best_castle_list(page_id, page_size):
	return cache_get_json(CACHE_KEY_BEST_CASTLE_LIST % (page_id, page_size))


def set_best_castle_list(page_id, page_size, castle_list):
	cache_set_json(CACHE_KEY_BEST_CASTLE_LIST % (page_id, page_size), castle_list, LEADER_BOARD_CACHE_TIME)


def get_best_battler_list(page_id, page_size):
	return cache_get_json(CACHE_KEY_BEST_BATTLER_LIST % (page_id, page_size))


def set_best_battler_list(page_id, page_size, battler_list):
	cache_set_json(CACHE_KEY_BEST_BATTLER_LIST % (page_id, page_size), battler_list, LEADER_BOARD_CACHE_TIME)


def get_best_mon_list(page_id, page_size):
	return cache_get_json(CACHE_KEY_BEST_MON_LIST % (page_id, page_size))


def set_best_mon_list(page_id, page_size, mon_list):
	cache_set_json(CACHE_KEY_BEST_MON_LIST % (page_id, page_size), mon_list, LEADER_BOARD_CACHE_TIME)


def get_monster_class_info(class_id):
	return cache_get_json(CACHE_KEY_MON_CLASS_INFO % str(class_id))


def set_monster_class_info(class_id, class_info):
	cache_set_json(CACHE_KEY_MON_CLASS_INFO % str(class_id), class_info, MON_CLASS_CACHE_TIME)


def get_best_collector_list(page_id, page_size):
	return cache_get_json(CACHE_KEY_BEST_COLLECTOR_LIST % (page_id, page_size))


def set_best_collector_list(page_id, page_size, collector_list):
	cache_set_json(CACHE_KEY_BEST_COLLECTOR_LIST % (page_id, page_size), collector_list, LEADER_BOARD_CACHE_TIME)


def get_new_player_count():
	return cache_get_json(CACHE_KEY_NEW_PLAYER_COUNT)


def set_new_player_count(info):
	cache_set_json(CACHE_KEY_NEW_PLAYER_COUNT, info, LEADER_BOARD_CACHE_TIME)


def get_active_castle():
	return cache_get_json(CACHE_KEY_ACTIVE_CASTLE)


def set_active_castle(info):
	cache_set_json(CACHE_KEY_ACTIVE_CASTLE, info, ACTIVE_CASTLE_CACHE_TIME)


def get_egg_list():
	return cache_get_json(CACHE_KEY_EGG_LIST)


def set_egg_list(info):
	cache_set_json(CACHE_KEY_EGG_LIST, info, EGG_LIST_CACHE_TIME)


def get_last_market_block():
	return cache_get_json(CACHE_KEY_MARKET_BLOCK)


def set_last_market_block(block_number):
	cache_set_json(CACHE_KEY_MARKET_BLOCK, block_number, 0)  # never expire


def get_last_market_block_backup():
	return cache_get_json(CACHE_KEY_MARKET_BLOCK_BACKUP)


def set_last_market_block_backup(block_number):
	cache_set_json(CACHE_KEY_MARKET_BLOCK_BACKUP, block_number, 0)  # never expire


def get_last_world_cron_block():
	return cache_get_json(CACHE_KEY_WORLD_CRON_BLOCK)


def set_last_world_cron_block(block_number):
	cache_set_json(CACHE_KEY_WORLD_CRON_BLOCK, block_number, 0)  # never expire


def get_cron_id(cron_name):
	return cache_get_json(CACHE_KEY_CRON_ID % cron_name)


def set_cron_id(cron_name, cron_id):
	cache_set_json(CACHE_KEY_CRON_ID % cron_name, cron_id, 0)  # never expire


def get_market_sales_history(page_id, page_size, class_id, sort_by):
	return cache_get_json(CACHE_KEY_SALES_HISTORY % (page_id, page_size, class_id, sort_by))


def set_market_sales_history(page_id, page_size, class_id, sort_by, sales_dict):
	cache_set_json(CACHE_KEY_SALES_HISTORY % (page_id, page_size, class_id, sort_by), sales_dict,
				   SALES_HISTORY_CACHE_TIME)


def get_market_history_count():
	return cache_get_json(CACHE_KEY_MARKET_HISTORY_COUNT)


def set_market_history_count(market_history_count):
	return cache_set_json(CACHE_KEY_MARKET_HISTORY_COUNT, market_history_count, SALES_HISTORY_COUNT_CACHE_TIME)


def get_object_egg(obj_id):
	return cache_get_json(CACHE_KEY_EGG_NO % obj_id)


def set_object_egg(obj_id, egg_no):
	cache_set_json(CACHE_KEY_EGG_NO % obj_id, egg_no, 0)  # never expire


def get_player_quests(player_id, quest_type):
	return cache_get_json(CACHE_KEY_PLAYER_QUESTS % (player_id, quest_type))


def set_player_quests(player_id, quest_type, quest_list):
	cache_set_json(CACHE_KEY_PLAYER_QUESTS % (player_id, quest_type), quest_list, PLAYER_QUESTS_CACHE_TIME)


def delete_player_quests(player_id, quest_type):
	cache_delete_json(CACHE_KEY_PLAYER_QUESTS % (player_id, quest_type))


def get_player_username(address):
	return cache_get_json(CACHE_KEY_PLAYER_USERNAME % address)


def set_player_username(address, username):
	cache_set_json(CACHE_KEY_PLAYER_USERNAME % address, username, PLAYER_USER_NAME)


# some simple decorators to cache data
def simple_cache_data(cache_key_converter, cache_prefix, expiry_time=60, cache_name="default"):
	def _cache_data(func):
		def _func(*args, **kwargs):
			cache_key = cache_key_converter(cache_prefix, *args)
			data = cache.get_cache(cache_name).get(cache_key)
			force_query = kwargs.get("force_query", False)
			if force_query or data is None:
				data = func(*args)
				cache.get_cache(cache_name).set(cache_key, data, expiry_time)
			else:
				log.info("cache_hit|cache_key=%s", cache_key)
			return data

		return _func

	return _cache_data


# input: must be a list
# output: must be a dict
def key_cache_data(cache_prefix, expiry_time=60, cache_name="default"):
	def _cache_data(func):
		def _func(keys, **kwargs):
			if not keys:
				return {}
			keys = list(keys)
			force_query = kwargs.get("force_query", False)
			result_data = {}
			if not force_query:
				cache_key_map = {cache_prefix % key: key for key in keys}
				cached_data_dict = cache.get_cache(cache_name).get_many(cache_key_map.keys())
				for cached_key, cached_data in cached_data_dict.iteritems():
					key = cache_key_map[cached_key]
					result_data[key] = cached_data
					keys.remove(key)
				log.info("key_cache_hit|cached_key=%s", ','.join(cached_data_dict.keys()))
			if keys:
				response_data = func(keys)
				if response_data:
					data_to_cache = {cache_prefix % key: data for key, data in response_data.iteritems()}
					cache.get_cache(cache_name).set_many(data_to_cache, expiry_time)
				return dict(result_data.items() + response_data.items())
			else:
				return result_data

		return _func

	return _cache_data
