import os
import sys
import json
import requests

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('../')

requests.packages.urllib3.disable_warnings()

DOMAIN = "https://www.etheremon.com"

API_GENERAL_GET_TYPE_METADATA = DOMAIN + "/api/general/get_type_metadata"
API_GENERAL_GET_CLASS_METADATA = DOMAIN + "/api/general/get_class_metadata"

API_USER_GET_MY_MONSTER = DOMAIN + "/api/user/get_my_monster"
API_USER_GET_SOLD_MONSTER = DOMAIN + "/api/user/get_sold_monster"
API_USER_UPDATE_INFO = DOMAIN + "/api/user/update_info"
API_USER_GET_INFO = DOMAIN + "/api/user/get_info"
API_USER_GET_LADDER_INFO = DOMAIN + "/api/user/get_ladder_info"
API_USER_SUBCRIBE = DOMAIN + "/api/user/subscribe"

API_MONSTER_GET_DATA = DOMAIN + "/api/monster/get_data"

API_BATTLE_GET_CASTLES = DOMAIN + "/api/battle/get_castles"
API_BATTLE_GET_BATTLE_LOG = DOMAIN + "/api/battle/get_battle_log"
API_BATTLE_GET_PRACTICE_PLAYERS = DOMAIN + "/api/battle/get_practice_players"
API_BATTLE_GET_PRACTICE_HISTORY = DOMAIN + "/api/battle/get_practice_history"

API_TRADING_GET_SELL_ORDER_LIST = DOMAIN + "/api/trading/get_sell_order_list"
API_TRADING_GET_BORROW_ORDER_LIST = DOMAIN + "/api/trading/get_borrow_order_list"

API_EMA_BATTLE_GET_USER_STATS = DOMAIN + "/api/ema_battle/get_user_stats"
API_EMA_BATTLE_GET_RANK_CASTLES = DOMAIN + "/api/ema_battle/get_rank_castles"
API_EMA_BATTLE_GET_RANK_HISTORY = DOMAIN + "/api/ema_battle/get_rank_history"
API_EMA_BATTLE_GET_PRACTICE_CASTLES = DOMAIN + "/api/ema_battle/get_practice_castles"
API_EMA_BATTLE_GET_PRACTICE_HISTORY = DOMAIN + "/api/ema_battle/get_practice_history"
API_EMA_BATTLE_GET_RANK_BATTLE = DOMAIN + "/api/ema_battle/get_rank_battle"

API_EMA_ADVENTURE_GET_ITEM_DATA = DOMAIN + "/api/adventure/get_item_data"
API_EMA_ADVENTURE_GET_MY_SITES = DOMAIN + "/api/adventure/get_my_sites"
API_EMA_ADVENTURE_GET_STATS = DOMAIN + "/api/adventure/get_stats"
API_EMA_ADVENTURE_GET_EXPLORES = DOMAIN + "/api/adventure/get_my_explores"
API_EMA_ADVENTURE_GET_ITEMS = DOMAIN + "/api/adventure/get_my_items"
API_EMA_ADVENTURE_GET_PENDING_EXPLORE = DOMAIN + "/api/adventure/get_pending_explore"
API_EMA_ADVENTURE_COUNT_ITEM = DOMAIN + "/api/adventure/count_item"

API_QUEST_GET_QUEST = DOMAIN + "/api/quest/get_quests"
API_QUEST_CLAIM_QUEST = DOMAIN + "/api/quest/claim_quest"
API_QUEST_CLAIM_ALL = DOMAIN + "/api/quest/claim_all"


def request_service_api(url, data, method="POST"):
	print "\n+ REQUEST:", url
	headers = {
		'X-Emon-App-Id': "1001",
		'X-Emon-Access-Token': '6e7dfb0a3322763931d8c46e203c16496c6797883959a1096670e8fc1962fc9a',
		'X-Emon-Api-Version': "1",
		'X-Emon-Client-Type': "1",
		'X-Emon-Client-Version': '0000',
		'X-Emon-Client-Id': '',
		'X-Emon-Client-Language': 'en'
	}
	if method == "POST":
		response = requests.post(url, data=json.dumps(data), verify=False, headers=headers)
	else:
		response = requests.get(url, params=data, verify=False, headers=headers)
	try:
		if response.status_code != 200:
			print "  REQUEST HTTP ERROR CODE: %s" % response.status_code
			return None, None
		result = response.json()
		result_code = result["result"]
		result_body = result.get("data")
		return result_code, result_body
	except Exception as error:
		print "  REQUEST EXCEPTION: %s" % error.message
	return None, None