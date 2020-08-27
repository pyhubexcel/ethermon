import os
import sys
import json
import requests
import pytz
import time
from datetime import datetime

ETHER_SCAN_KEY = "8GGCGF6S9YG1SC6XG76MW5HI8K1PP4VAHP"
ETHER_SCAN_API = "http://api.etherscan.io/api"

BATTLE_SMART_CONTRACTS = [
	"0xc43eae20ae38d1e11bab5b57178777096908dbd6",
	"0x65ca30af89af5a048cc8b715101171fbca6452b5",
	"0xe171783da2c451186b4256727481fa30203fef86",
	"0x0fa8051dbdbbcc32d602803d5f1de1e6f92a0bbd",
	"0x0c28bf52d0d4d9447e86d7e7f0e317f273d3c9a3",
	"0xdf6164efd12678bf6a7d5a1ddf73c831493f6574"
]
GYM_SMART_CONTRACTS = ["0xcaef67f72114b4d2b4f43e7407455285b7de8de5"]
TRANSFORM_SMART_CONTRACTS = ["0x57f854ba5baf019ec3a77f81c2966fd0d8905a38", "0xf3a8f103574bc64358e372ed68e95db0b2bb0936", "0xa6ff73743b2fd8dedfacea4067a51ef86d249491"]
PRACTICE_SMART_CONTRACTS = ["0xb902e19f24950c43ae69cfee20876283fa842b03"]
TRADING_SMART_CONTRACTS = ["0x4ba72f0f8dad13709ee28a992869e79d0fe47030"]

MAX_RECORD_RETURN = 5000

SingaporeTimezone = pytz.timezone('Singapore')

def get_txn_data(address, page=1, offset=MAX_RECORD_RETURN, from_block=0, to_block=999999999):
	data = {
		"module": "account",
		"action": "txlist",
		"address": address,
		"startblock": from_block,
		"endblock": to_block,
		"sort": "asc",
		"apikey": ETHER_SCAN_KEY,
		"page": page,
		"offset": offset
	}
	response = requests.get(ETHER_SCAN_API, params=data)
	# {"status": xx, "message": xx, "result":[]}
	try:
		if response.status_code != 200:
			print "  REQUEST HTTP ERROR CODE: %s" % response.status_code
			return None, None
		result = response.json()
		status = result["status"]
		message = result["message"]
		result_data = result.get("result")
		return status, result_data
	except Exception as error:
		print "  REQUEST EXCEPTION: %s" % error.message
	return None, None

'''
{
	"blockNumber": "5349217",
	"timeStamp": "1522417866",
	"hash": "0x7f1a98b7c5d98830018ea71d14cdcdea983272e77f820506487671afdad58a9b",
	"nonce": "532",
	"blockHash": "0x665ccc9091aad99d15b1f2f934ed6457f4cdba9221b74f226353d7e964d6cbd6",
	"transactionIndex": "63",
	"from": "0xa77005f4e2eaa00a02cd96bb553e89c004f9da31",
	"to": "0x4ba72f0f8dad13709ee28a992869e79d0fe47030",
	"value": "0",
	"gas": "500000",
	"gasPrice": "1110000000",
	"isError": "0",
	"txreceipt_status": "1",
	"input": "0x4eb4fe800000000000000000000000000000000000000000000000000000000000006425",
	"contractAddress": "",
	"cumulativeGasUsed": "6557197",
	"gasUsed": "105820",
	"confirmations": "195"
}
'''
def get_revenue(txn_data):
	revenue = {}
	for txn in txn_data:
		if txn["txreceipt_status"] != "1":
			continue
		dt = datetime.fromtimestamp(int(txn["timeStamp"]), SingaporeTimezone)
		dt_string = dt.strftime("%Y-%m-%d")
		value = float(txn["value"]) / 10 ** 18
		if value > 0:
			if dt_string in revenue:
				revenue[dt_string] += value
			else:
				revenue[dt_string] = value
	keylist = revenue.keys()
	keylist.sort()
	for key in keylist:
		print key, revenue[key]

def print_revenue(contract, from_block, to_block):
	page = 1
	final_result = []
	result, txn_data = get_txn_data(contract, page, MAX_RECORD_RETURN, from_block, to_block)
	while len(txn_data) == MAX_RECORD_RETURN:
		final_result += txn_data
		page += 1
		time.sleep(1)
		result, txn_data = get_txn_data(contract, page, MAX_RECORD_RETURN, from_block, to_block)
	if txn_data:
		final_result += txn_data
	if final_result:
		print "contract:", contract
		print get_revenue(final_result)

if __name__ == "__main__":
	param_len = len(sys.argv[1:])
	if param_len == 2:
		from_block = sys.argv[1:][0]
		to_block = sys.argv[1:][1]
	else:
		from_block = 0
		to_block = 999999999
	print "from_block:", from_block, "to_block:", to_block
	print "Battle contract"
	for contract in BATTLE_SMART_CONTRACTS:
		print_revenue(contract, from_block, to_block)

	time.sleep(1)
	print "Gym contract"
	for contract in GYM_SMART_CONTRACTS:
		print_revenue(contract, from_block, to_block)

	time.sleep(1)
	print "Transform contract"
	for contract in TRANSFORM_SMART_CONTRACTS:
		print_revenue(contract, from_block, to_block)

	time.sleep(1)
	print "Trading contract"
	for contract in TRADING_SMART_CONTRACTS:
		print_revenue(contract, from_block, to_block)

	time.sleep(1)
	print "practice contract"
	for contract in PRACTICE_SMART_CONTRACTS:
		print_revenue(contract, from_block, to_block)

