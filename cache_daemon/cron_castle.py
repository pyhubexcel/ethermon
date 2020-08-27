from web3 import Web3, HTTPProvider, IPCProvider
from pymemcache.client.base import Client as MemcacheClient
from django.db import IntegrityError
from common.daemon import Daemon
from common.logger import log
from common import dbmodel
from etheremon_lib import config as etheremon_config
from etheremon_lib.config import DATABASES

from common import config as common_config
from common import context
common_config.init_config(etheremon_config)
context.init_django('../', 'etheremon_lib.config')
from etheremon_lib.models import EtheremonDB
from config import CASTLE_ABI, CASTLE_ADDRESS

import time
import json
import traceback

web3 = None
memcache = None

ID_LOG_FILE = 'cron_castle.log'
DEBUG = False

def update_castle():
    castle_class = web3.eth.contract(abi=CASTLE_ABI)
    castle_contract = castle_class(CASTLE_ADDRESS)

    castle_length = castle_contract.call().totalCastle()
    if DEBUG: print "castle_length: ", castle_length
    log.info('update_castle_length|castle_length=%s', castle_length)

    castle_id = 1
    with open(ID_LOG_FILE, 'r') as f:
        castle_id = int(f.read())

    if DEBUG: print "castle id start:", castle_id
    log.info('update_castle_start|castle_start_id=%s', castle_id)

    while castle_id <= castle_length:
        (name, owner, brick_number, total_win, total_lose, create_time) = castle_contract.call().getCastleStats(castle_id)
        (monster_id_1, monster_id_2, monster_id_3, support_id_1, support_id_2, support_id_3) = castle_contract.call().getCastleObjInfo(castle_id)
        if DEBUG: print "castle id %s %s %s" % (castle_id, type(name), name.encode('utf-8'))
        log.info('update_castle|caslte_id=%s', castle_id)
        try:
            EtheremonDB.CastleTab.objects.create(
                castle_id=castle_id,
                name=name,
                owner_address=owner,
                brick_number=brick_number,
                castle_create_time=create_time,
                monster_id_1=monster_id_1,
                monster_id_2=monster_id_2,
                monster_id_3=monster_id_3,
                supporter_id_1=support_id_1,
                supporter_id_2=support_id_2,
                supporter_id_3=support_id_3,
                total_win=total_win,
                total_lose=total_lose,
                extra_data=json.dumps({})
            )
        except IntegrityError:
            log.warn('update_castle|re_update_id=%s', castle_id)
        castle_id += 1

    with open(ID_LOG_FILE, 'w') as f:
        f.write(str(castle_id))


if __name__=="__main__":

    if web3 is None:
        web3 = Web3(HTTPProvider('http://localhost:8545'))
    if memcache is None:
        memcache = MemcacheClient(('localhost', 11211))

    def main():
        while True:
            try:
                update_castle()
            except Exception as e:
                log.error('cron_castle_error|error=%s,traceback=%s', e, traceback.format_exc())
            time.sleep(5)

    if not DEBUG:
        Daemon(main, 'cron_castle.pid', './cron_daemon_output.log').main()
    else:
        main()