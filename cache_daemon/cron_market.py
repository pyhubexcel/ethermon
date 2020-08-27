from web3 import Web3, HTTPProvider, IPCProvider
from web3.exceptions import BadFunctionCallOutput
import json
from config import TRADE_ABI, TRADE_ADDRESS, TRANSFORM_ABI, TRANSFORM_ADDRESS
import time, datetime
from threading import Thread
from pymemcache.client.base import Client as MemcacheClient
from common.logger import log
import traceback

memcache_client = None

THREAD_NO = 10
def cache_market():
  web3 = Web3(HTTPProvider('http://localhost:8545'))

  eth_block_no = web3.eth.blockNumber

  trade_class = web3.eth.contract(abi=TRADE_ABI)
  trade_contract = trade_class(TRADE_ADDRESS)

  transform_class = web3.eth.contract(abi=TRANSFORM_ABI)
  transform_contract = transform_class(TRANSFORM_ADDRESS)

  total = trade_contract.call().getTotalSellingItem()
  start_time = time.time()

  monList = [{} for i in xrange(0, total)]
  threads = []

  def getMonsterEgg(memcache_client, obj_id):
    egg_no = memcache_client.get('egg_no.%s' % str(obj_id))
    if (egg_no is None) or (egg_no > 0):
      egg_no = transform_contract.call().getBonusEgg(obj_id)
      if (egg_no == 0):
        memcache_client.set('egg_no.%s' % str(obj_id), egg_no)
    return egg_no

  def addSell(indexList):
    try:
      memcache_client_thread = MemcacheClient(('localhost', 11211))
      for index in indexList:
        (obj_id, class_id, exp, bp, trainer, create_index, price) = trade_contract.call().getSellingItem(index)
        egg_no = getMonsterEgg(memcache_client_thread, obj_id)
        monList[index] = {
          'index': index,
          'monster_id': obj_id,
          'class_id': class_id,
          'exp': exp,
          'bp': bp,
          'trainer': trainer,
          'create_index': create_index,
          'selling_price': price,
          'bonus_egg': egg_no
        } 
        # print "done: ", index
    except Exception as e:
      log.error('cron_sell|error=%s,traceback=%s', e, traceback.format_exc())
  step = total / THREAD_NO
  for i in xrange(0, total, step):
    attemptList = [i+j for j in xrange(0, min(step, total - i))]
    thread = Thread(target=addSell, args=(attemptList,))
    thread.start()
    threads.append(thread)
  for thread in threads:
    thread.join()
  #print monList

  threads = []
  total_borrow = trade_contract.call().getTotalBorrowingItem()
  log.info('cron_borrow|total=%s', total_borrow)
  borrowList = [{} for i in xrange(0, total_borrow)]
  def addBorrow(indexList):
    try:
      memcache_client_thread = MemcacheClient(('localhost', 11211))
      for index in indexList:
        try:
          (obj_id, owner, borrower, price, lent, release_time, class_id, exp, create_index, bp) = trade_contract.call().getBorrowingItem(index)
          egg_no = getMonsterEgg(memcache_client_thread, obj_id)
          borrowList[index] = {
              'index': index,
              'monster_id': obj_id,
              'class_id': class_id,
              'exp': exp,
              'bp': bp,
              'owner': owner,
              'borrower': borrower,
              'lent': lent,
              'release_time': release_time,
              'create_index': create_index,
              'lending_price': price,
              'bonus_egg': egg_no
          }
        except BadFunctionCallOutput as e:
          log.error('cron_borrow_failed|index=%s, error=%s,traceback=%s', index, e, traceback.format_exc())
        # print "done: ", index
    except Exception as e:
        log.error('cron_borrow|error=%s,traceback=%s', e, traceback.format_exc())
  
  step = total / THREAD_NO
  for i in xrange(0, total_borrow, step):
    attemptList = [i+j for j in xrange(0, min(step, total_borrow - i))]
    thread = Thread(target=addBorrow, args=(attemptList, ))
    thread.start()
    threads.append(thread)
  for thread in threads:
    thread.join()
  memcache_client.set('sell_list', json.dumps(monList))
  memcache_client.set('borrow_list', json.dumps(borrowList))

  with open('cron_market.log', 'a') as f:
    f.write("\n")
    f.write("Last update time: " + str(datetime.datetime.fromtimestamp(int(time.time())).strftime('%Y-%m-%d %H:%M:%S')) + "\n")
    f.write("Block no: " + str(eth_block_no) + "\n")
    f.write("Total_sell: " + str(total) + "\n")
    f.write("Total_borrow: " + str(total_borrow) + "\n")
    f.write("Elasped: " + str(time.time() - start_time) + "\n")

if __name__ == "__main__":
  if memcache_client is None:
    memcache_client = MemcacheClient(('localhost', 11211))
  def main():
    while True:
      cache_market()
  from common.daemon import Daemon
  Daemon(main, 'cron_market.pid', './cron_daemon_output.log').main()
  # main() 