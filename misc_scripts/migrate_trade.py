from web3 import Web3, HTTPProvider, IPCProvider
import json
from config import TRADE_ABI, TRADE_ADDRESS, TRANSFORM_ABI, TRANSFORM_ADDRESS
import time, datetime
from threading import Thread
from pymemcache.client.base import Client as MemcacheClient
from common.logger import log
from private_config import OWNER_ADDRESS, OWNER_PASSPHRASE, OWNER_PRIVATE_KEY
import traceback

memcache_client = None

TEST = True
GETH_HOST = 'localhost'
GETH_PORT = '8545'
if TEST:
    GETH_PORT = '8546' # Geth rinkeby

def migrate_trade():
    web3_client = Web3(HTTPProvider('http://' + GETH_PORT + ":" + GETH_PORT))

    sell_list = json.loads(memcache_client.get('sell_list'))
    borrow_list = json.loads(memcache_client.get('borrow_list'))
  
    try:
        web3_client.personal.importRawKey(OWNER_PRIVATE_KEY, OWNER_PASSPHRASE)
    except ValueError:
        pass

    web3_client.personal.unlockAccount(OWNER_ADDRESS, OWNER_PASSPHRASE)
    web3_client.eth.defaultAccount = OWNER_ADDRESS

    trade_class = web3_client.eth.contract(abi=TRADE_ABI)
    trade_contract = trade_class(TRADE_ADDRESS)

    for start in xrange(0, len(sell_list), 5):
        sell_set = []
        for i in xrange(0, 5):
            if start + i < len(sell_list):
                sell_set.append(sell_list[start + i])
            else:
                sell_set.append({
                    'monster_id': 0,
                    'selling_price': 0
                })
        trade_contract.transact().addSellItem(
            sell_set[0]['monster_id'], sell_set[0]['selling_price'],
            sell_set[1]['monster_id'], sell_set[1]['selling_price'],
            sell_set[2]['monster_id'], sell_set[2]['selling_price'],
            sell_set[3]['monster_id'], sell_set[3]['selling_price'],
            sell_set[4]['monster_id'], sell_set[4]['selling_price'],
        )
  

if __name__ == "__main__":
  if memcache_client is None:
    memcache_client = MemcacheClient(('localhost', 11211))
  migrate_trade()