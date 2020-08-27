import requests
from common.logger import log
import logging

ETHER_SCAN_DOMAIN = "http://api.etherscan.io/api"

def get_txn_list(address, start_block, end_block, apikey):
	try:
		params = {
			"module": "account",
			"action": "txlist",
			"sort": "asc",
			"apikey": apikey,
			"address": address,
			"startblock": start_block,
			"endblock": end_block
		}
		response = requests.get(ETHER_SCAN_DOMAIN, params=params)
		if response.status_code != 200:
			logging.error("get_txn_fail|address=%s,start_block=%s,end_block=%s,api_key=%s,response_code=%s", address, start_block, end_block, apikey, response.status_code)
			return None
		response_data = response.json()
		if int(response_data["status"]) != 1:
			logging.info("get_txn_status_empty|address=%s,start_block=%s,end_block=%s,api_key=%s,response_data=%s", address, start_block, end_block, apikey, response_data)
			return []
		return response_data["result"]
	except Exception as error:
		logging.error("get_txn_exception|address=%s,start_block=%s,end_block=%s,api_key=%s,msg=%s", address, start_block, end_block, apikey, error.message)
		return None

# only 1000 records
def get_event_list(address, start_block, end_block, apikey, topic):
	try:
		params = {
			"module": "logs",
			"action": "getLogs",
			"apikey": apikey,
			"address": address,
			"fromBlock": start_block,
			"toBlock": end_block,
			"topic0": topic
		}
		response = requests.get(ETHER_SCAN_DOMAIN, params=params)
		if response.status_code != 200:
			logging.error("get_event_log_fail|address=%s,start_block=%s,end_block=%s,api_key=%s,topic=%s,response_code=%s", address, start_block, end_block, apikey, topic, response.status_code)
			return None
		response_data = response.json()
		if int(response_data["status"]) != 1:
			logging.info("get_event_status_empty|address=%s,start_block=%s,end_block=%s,api_key=%s,topic=%s,response_data=%s", address, start_block, end_block, apikey, topic, response_data)
			return []
		return response_data["result"]
	except Exception as error:
		logging.error("get_event_exception|address=%s,start_block=%s,end_block=%s,api_key=%s,topic=%s,msg=%s", address, start_block, end_block, apikey, topic, error.message)
		return None