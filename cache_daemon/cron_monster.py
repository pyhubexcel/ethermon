from web3 import Web3, HTTPProvider, IPCProvider
from pymemcache.client.base import Client as MemcacheClient
from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from common.daemon import Daemon
from common.logger import log
from common import dbmodel
from etheremon_lib import config as etheremon_config
from etheremon_lib.config import DATABASES, EtheremonDataContract
from etheremon_lib.constants import DataArrayType

from common import config as common_config
from common import context
common_config.init_config(etheremon_config)
context.init_django('../', 'etheremon_lib.config')
import django
django.setup()
from etheremon_lib.models import EtheremonDB

import time
import json
import traceback

web3 = None
memcache = None

ID_LOG_FILE = 'cron_monster.log'
DEBUG = False

def update_monster():
    data_class = web3.eth.contract(abi=EtheremonDataContract.ABI)
    data_contract = data_class(EtheremonDataContract.ADDRESS)

    total_monster = data_contract.call().totalMonster()
    if DEBUG: print "total monster: ", total_monster
    log.info('update_monster|total_monster=%s', total_monster)

    monster_id = 1

    if DEBUG: print "Start id: ", monster_id
    log.info('update_monster|start|monster_id=%s', monster_id)

    while monster_id <= total_monster:        
        (monster_return_id, class_id, owner_address, exp, create_index, last_claim_index, monster_create_time) = data_contract.call().getMonsterObj(monster_id)
        if DEBUG: print monster_id, " ", owner_address
        name = data_contract.call().getMonsterName(monster_id)
        name =(name[:100] + '..') if len(name) > 100 else name
        name = name.encode('utf8')
        monster_stat = []            
        for index in xrange(0, 6):
            monster_stat.append(data_contract.call().getElementInArrayType(DataArrayType.STAT_BASE, monster_id, index))
        try:
            monster = EtheremonDB.MonsterTab.objects.get(monster_id=monster_id)
            monster.name = name
            monster.exp = int(exp)
            monster.owner_address = owner_address
            monster.last_claim_index = last_claim_index
            monster.save()
            if DEBUG: print "update", ": ", monster_id    
            log.info('update_monster|updated|monster_id=%s', monster_id)            
        except EtheremonDB.MonsterTab.DoesNotExist:
            EtheremonDB.MonsterTab.objects.create(
                monster_id=monster_id,
                class_id=class_id,
                name=name,
                owner_address=owner_address,
                exp=int(exp),
                create_index=create_index,
                last_claim_index=last_claim_index,
                monster_create_time=monster_create_time,
                base_stat_1 = monster_stat[0],
                base_stat_2 = monster_stat[1],
                base_stat_3 = monster_stat[2],
                base_stat_4 = monster_stat[3],
                base_stat_5 = monster_stat[4],
                base_stat_6 = monster_stat[5],
                extra_data=json.dumps({})
            )
            if DEBUG: print "create", ": ", monster_id
            log.info('update_monster|created|monster_id=%s', monster_id)
        monster_id += 1


if __name__=="__main__":

    if web3 is None:
        web3 = Web3(HTTPProvider('http://localhost:8545'))
    if memcache is None:
        memcache = MemcacheClient(('localhost', 11211))

    def main():
        while True:
            try:
                start = time.time()
                update_monster()
                if DEBUG: print "Elapsed: ", time.time() - start
            except Exception as e:
                if DEBUG: traceback.print_exc()
                log.error('cron_monster_error|error=%s,traceback=%s', e, traceback.format_exc())
            time.sleep(5)

    if DEBUG:
        main()
    else:
        Daemon(main, 'cron_monster.pid', './cron_daemon_output.log').main()