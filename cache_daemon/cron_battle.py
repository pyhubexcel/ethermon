from web3 import Web3, HTTPProvider, IPCProvider
from config import CASTLE_ABI, CASTLE_ADDRESS
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

import time
import json
import traceback

web3 = None
memcache = None

def update_battle():
    castle_class = web3.eth.contract(abi=CASTLE_ABI)
    castle_contract = castle_class(CASTLE_ADDRESS)

    total_battle = castle_contract.call().totalBattle()
    # print "total_battle: ", total_battle
    log.info('update_battle|total_battle=%s', total_battle)

    battle_id = 1
    with open('cron_battle.log', 'r') as f:
        battle_id = int(f.read())

    # print "battle id start:", battle_id
    log.info('update_battle|battle_id_start=%s', battle_id)

    while battle_id <= total_battle:
        (castle_id, attacker_address, result, 
            random_0, random_1, random_2, 
            castle_monster_exp_1, castle_monster_exp_2, castle_monster_exp_3) = castle_contract.call().getBattleDataLog(battle_id)
        (attacker_monster_id_1, attacker_monster_id_2, attacker_monster_id_3, 
            attacker_supporter_id_1, attacker_supporter_id_2, attacker_supporter_id_3,
            attacker_monster_exp_1, attacker_monster_exp_2, attacker_monster_exp_3) = castle_contract.call().getBattleAttackerLog(battle_id)
        if not castle_id or not attacker_monster_id_1:
            log.error('update_battle_error|battle_id=%s', battle_id)
            break
        # print "battle id update: ", battle_id
        log.info('update_battle|battle_id=%s', battle_id)
        try:
            EtheremonDB.BattleLogTab.objects.create(
                battle_id=battle_id,
                castle_id=castle_id,
                attacker_address=attacker_address,
                attacker_monster_id_1=attacker_monster_id_1,
                attacker_monster_id_2=attacker_monster_id_2,
                attacker_monster_id_3=attacker_monster_id_3,
                attacker_supporter_id_1=attacker_supporter_id_1,
                attacker_supporter_id_2=attacker_supporter_id_2,
                attacker_supporter_id_3=attacker_supporter_id_3,
                result=result,
                extra_data=json.dumps({
                    'castle_monster_exp_1': castle_monster_exp_1,
                    'castle_monster_exp_2': castle_monster_exp_2,
                    'castle_monster_exp_3': castle_monster_exp_3,
                    'attacker_monster_exp_1': attacker_monster_exp_1,
                    'attacker_monster_exp_2': attacker_monster_exp_2,
                    'attacker_monster_exp_3': attacker_monster_exp_3,
                })
            )
        except IntegrityError:
            log.warn('update_battle|re_update_id=%s', battle_id)
        battle_id += 1

    with open('cron_battle.log', 'w') as f:
        f.write(str(battle_id))


if __name__=="__main__":

    if web3 is None:
        web3 = Web3(HTTPProvider('http://localhost:8545'))
    if memcache is None:
        memcache = MemcacheClient(('localhost', 11211))

    def main():
        while True:
            try:
                update_battle()
            except Exception as e:
                log.error('cron_battle_error|error=%s,traceback=%s', e, traceback.format_exc())
            time.sleep(5)

    Daemon(main, 'cron_battle.pid', './cron_daemon_output.log').main()
    # main()