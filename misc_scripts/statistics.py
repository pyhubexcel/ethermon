import os
import sys
import time
import json
from datetime import datetime

from django.core.wsgi import get_wsgi_application

curr_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curr_dir)
sys.path.append(os.path.join(curr_dir, '../'))

from common import context

context.init_django('../etheremon_api', 'settings')
application = get_wsgi_application()

from etheremon_lib.models import EtheremonDB
from etheremon_lib.monster_config import MONSTER_CLASS_STATS
from etheremon_lib.utils import get_new_monster_price
from etheremon_lib.contract_manager import EtheremonLadderPracticeContract, EtheremonTradeContract
from etheremon_lib.config import ETHERSCAN_API_KEYS

from collections import OrderedDict

init_time = datetime(1970, 1, 1)

months = OrderedDict([
    ('before', {
        'start': 0,
        'end':  int((datetime(2018, 1, 1) - init_time).total_seconds())
    }),
    ('jan18', {
        'start': int((datetime(2018, 1, 1) - init_time).total_seconds()),
        'end': int((datetime(2018, 2, 1) - init_time).total_seconds())
    }),
    ('feb18', {
        'start': int((datetime(2018, 2, 1) - init_time).total_seconds()),
        'end': int((datetime(2018, 3, 1) - init_time).total_seconds())
    }),
    ('mar18', {
        'start': int((datetime(2018, 3, 1) - init_time).total_seconds()),
        'end': int((datetime(2018, 4, 1) - init_time).total_seconds())
    }),
    ('apr18', {
        'start': int((datetime(2018, 4, 1) - init_time).total_seconds()),
        'end': int((datetime(2018, 5, 1) - init_time).total_seconds()),
    }),
    ('may18', {
        'start': int((datetime(2018, 5, 1) - init_time).total_seconds()),
        'end': int((datetime(2018, 6, 1) - init_time).total_seconds()),
    }),
    ('jun18', {
        'start': int((datetime(2018, 6, 1) - init_time).total_seconds()),
        'end': int((datetime(2018, 7, 1) - init_time).total_seconds()),
    }),
    ('jul18', {
        'start': int((datetime(2018, 7, 1) - init_time).total_seconds()),
        'end': int((datetime(2018, 8, 1) - init_time).total_seconds()),
    }),
    ('aug18', {
        'start': int((datetime(2018, 8, 1) - init_time).total_seconds()),
        'end': int((datetime(2018, 9, 1) - init_time).total_seconds()),
    }),
    ('sep18', {
        'start': int((datetime(2018, 9, 1) - init_time).total_seconds()),
        'end': int((datetime(2018, 10, 1) - init_time).total_seconds()),
    }),
    ('oct18', {
        'start': int((datetime(2018, 10, 1) - init_time).total_seconds()),
        'end': int((datetime(2018, 11, 1) - init_time).total_seconds()),
    }),
    ('nov18', {
        'start': int((datetime(2018, 11, 1) - init_time).total_seconds()),
        'end': int((datetime(2018, 12, 1) - init_time).total_seconds()),
    }),
    ('dec18', {
        'start': int((datetime(2018, 12, 1) - init_time).total_seconds()),
        'end': int((datetime(2019, 1, 1) - init_time).total_seconds()),
    }),
    ('jan19', {
        'start': int((datetime(2019, 1, 1) - init_time).total_seconds()),
        'end': int((datetime(2019, 2, 1) - init_time).total_seconds()),
    }),

    ('feb19', {
        'start': int((datetime(2019, 2, 1) - init_time).total_seconds()),
        'end': int((datetime(2019, 3, 1) - init_time).total_seconds()),
    }),
    ('mar19', {
        'start': int((datetime(2019, 3, 1) - init_time).total_seconds()),
        'end': int((datetime(2019, 4, 1) - init_time).total_seconds()),
    })
])


def get_all_stats():
    all_mons = EtheremonDB.EmaMonsterDataTab.objects.all()

    user_first_catch = {}
    user_first_buy = {}

    revenue_mon = OrderedDict()
    for month_id in months:
        revenue_mon[month_id] = 0.0

    free_count = 0

    for mon in all_mons:
        catch_time = mon.create_time
        owner = mon.trainer
        class_id = mon.class_id
        user_first_catch[owner] = min(user_first_catch.get(owner, catch_time), catch_time)
        is_free = class_id in [25, 26, 27]
        is_from_egg = class_id in [101, 102, 103, 104]
        is_transformed = MONSTER_CLASS_STATS[class_id].get('transformed', False)
        price = 0
        if is_free:
            free_count += 1
        if not is_free and not is_transformed and 'price' in MONSTER_CLASS_STATS[class_id]:
            price = get_new_monster_price(MONSTER_CLASS_STATS[class_id]['price'], mon.create_index)
        for month_id, month_time in months.iteritems():
            if month_time['start'] <= catch_time <= month_time['end']:
                user_dict[month_id].add(mon.trainer)
                revenue_mon[month_id] += price
        if not is_free and not is_transformed and not is_from_egg:
            user_first_buy[owner] = min(user_first_buy.get(owner, catch_time), catch_time)

    count_all_player = OrderedDict()
    count_nonfree_player = OrderedDict()

    for month_id, month_time in months.iteritems():
        count_all_player[month_id] = 0
        count_nonfree_player[month_id] = 0
        for user, catch_time in user_first_catch.iteritems():
            if month_time['start'] <= catch_time <= month_time['end']:
                count_all_player[month_id] += 1
        for user, catch_time in user_first_buy.iteritems():
            if month_time['start'] <= catch_time <= month_time['end']:
                count_nonfree_player[month_id] += 1

    print "free count: ", free_count
    print "count all: ", count_all_player
    print "count non free: ", count_nonfree_player
    print "revenue mon: ", revenue_mon

    # revenue_market = OrderedDict()
    # mon_sold = OrderedDict()
    # mon_sold_total = OrderedDict()
    # for month_id in months:
    #     revenue_market[month_id] = 0.0
    #     mon_sold[month_id] = 0.0
    #     mon_sold_total[month_id] = 0
    #
    # all_market_items = EtheremonDB.MarketHistoryTab.objects.filter(is_sold=True).all()
    # for market_item in all_market_items:
    #     for month_id, month_time in months.iteritems():
    #         if month_time['start'] <= market_item.buy_time <= month_time['end']:
    #             revenue_market[month_id] += market_item.price/1000.0/100.0
    #             mon_sold[month_id] += market_item.price/1000.0
    #             mon_sold_total[month_id] += 1
    #
    # print "revenue market: ", revenue_market
    # print "mon sold: ", mon_sold
    # print "mon sold total: ", mon_sold_total


ETHER_SCAN_API = "http://api.etherscan.io/api?module=account&action=txlist&address=%s&startblock=%s&endblock=%s&sort=asc&apikey=%s"
NO_OF_BLOCK = 10000
MAX_BLOCK = 5537517
import requests
import time

user_dict = OrderedDict()
for month_id in months:
    user_dict[month_id] = set()


def contract_count_battle(START_BLOCK, address):
    battle_played = OrderedDict()
    for month_id in months:
        battle_played[month_id] = 0
    start_block = START_BLOCK
    while start_block <= MAX_BLOCK:
        end_block = start_block + NO_OF_BLOCK
        result = requests.get(ETHER_SCAN_API % (
            address,
            start_block,
            end_block,
            ETHERSCAN_API_KEYS["stats"]
        )).json()

        if int(result["status"]) != 1:
            print "GET CONTRACT ERROR: ", result
            if result["message"] == "Query Timeout occurred. Please select a smaller result dataset":
                continue
            start_block = end_block + 1
            continue

        transaction_list = result["result"]
        transaction_list = sorted(transaction_list, key=lambda transaction_item: int(transaction_item["timeStamp"]))

        for transaction in transaction_list:
            if int(transaction.get("isError", 1)) != 0:  # transaction is not successful
                # print "transaction failed"
                continue
            print "time: ", transaction["timeStamp"]
            for month_id, month_time in months.iteritems():
                if month_time['start'] <= int(transaction["timeStamp"]) <= month_time['end']:
                    battle_played[month_id] += 1
                    user_dict[month_id].add(transaction["from"])

        print "block: ", start_block
        print "battle_played: ", battle_played

        time.sleep(0.1)

        start_block = end_block + 1


def battle_count_old_1():
    contract_count_battle(4864977, "0xc43eae20ae38d1e11bab5b57178777096908dbd6")


def battle_count_old_2():
    contract_count_battle(4866989, "0x65ca30af89af5a048cc8b715101171fbca6452b5")


def battle_count_old_3():
    contract_count_battle(4946531, "0xe171783da2c451186b4256727481fa30203fef86")


def battle_count_old_4():
    contract_count_battle(4979964, "0x0c28bf52d0d4d9447e86d7e7f0e317f273d3c9a3")


def gym_count():
    contract_count_battle(4902187, "0xcaef67f72114b4d2b4f43e7407455285b7de8de5")


def ladder_practice_count():
    contract_count_battle(5426064, EtheremonLadderPracticeContract.ADDRESS)


def contract_count_money(START_BLOCK, address):
    total_money = OrderedDict()
    for month_id in months:
        total_money[month_id] = 0
    start_block = START_BLOCK
    while start_block <= MAX_BLOCK:
        end_block = start_block + NO_OF_BLOCK
        result = requests.get(ETHER_SCAN_API % (
            address,
            start_block,
            end_block,
            ETHERSCAN_API_KEYS["stats"]
        )).json()

        if int(result["status"]) != 1:
            print "GET CONTRACT ERROR: ", result
            start_block = end_block + 1
            continue

        transaction_list = result["result"]
        transaction_list = sorted(transaction_list, key=lambda transaction_item: int(transaction_item["timeStamp"]))

        for transaction in transaction_list:
            if int(transaction.get("isError", 1)) != 0:  # transaction is not successful
                # print "transaction failed"
                continue
            print "time: ", transaction["timeStamp"]
            for month_id, month_time in months.iteritems():
                if month_time['start'] <= int(transaction["timeStamp"]) <= month_time['end']:
                    total_money[month_id] += int(transaction["value"]) / 1000000000000000000.0
                    user_dict[month_id].add(transaction["from"])

        print "block: ", start_block
        print "total eth: ", total_money

        time.sleep(0.1)

        start_block = end_block + 1


def ladder_practice_money():
    contract_count_money(5426064, EtheremonLadderPracticeContract.ADDRESS)


def gym_money():
    contract_count_money(4902187, "0xcaef67f72114b4d2b4f43e7407455285b7de8de5")


def transform_money():
    contract_count_money(5320024, "0xa6ff73743b2fd8dedfacea4067a51ef86d249491")


def transform_money_old():
    contract_count_money(5000125, "0xf3a8f103574bc64358e372ed68e95db0b2bb0936")


def trade_money():
    contract_count_money(4946456, EtheremonTradeContract.ADDRESS)


def battle_money_old_1():
    contract_count_money(4864977, "0xc43eae20ae38d1e11bab5b57178777096908dbd6")


def battle_money_old_2():
    contract_count_money(4866989, "0x65ca30af89af5a048cc8b715101171fbca6452b5")


def battle_money_old_3():
    contract_count_money(4946531, "0xe171783da2c451186b4256727481fa30203fef86")


def battle_money_old_4():
    contract_count_money(4979964, "0x0c28bf52d0d4d9447e86d7e7f0e317f273d3c9a3")


def lend_money():
    total_money = OrderedDict()
    for month_id in months:
        total_money[month_id] = 0

    count_lended = OrderedDict()
    for month_id in months:
        count_lended[month_id] = 0

    start_block = 4946456
    while start_block <= MAX_BLOCK:
        end_block = start_block + NO_OF_BLOCK
        result = requests.get(ETHER_SCAN_API % (
            EtheremonTradeContract.ADDRESS,
            start_block,
            end_block,
            ETHERSCAN_API_KEYS["stats"]
        )).json()

        if int(result["status"]) != 1:
            print "GET CONTRACT ERROR: ", result
            start_block = end_block + 1
            continue

        transaction_list = result["result"]
        transaction_list = sorted(transaction_list, key=lambda transaction_item: int(transaction_item["timeStamp"]))

        for transaction in transaction_list:
            if int(transaction.get("isError", 1)) != 0:  # transaction is not successful
                # print "transaction failed"
                continue
            method_id = transaction["input"][0:10]
            if method_id == "0xe9b6d671":
                print "time: ", transaction["timeStamp"]
                for month_id, month_time in months.iteritems():
                    if month_time['start'] <= int(transaction["timeStamp"]) <= month_time['end']:
                        total_money[month_id] += int(transaction["value"]) / 1000000000000000000.0
                        count_lended[month_id] += 1
                        user_dict[month_id].add(transaction["from"])

        print "block: ", start_block
        print "total eth: ", total_money
        print "total mon: ", count_lended

        time.sleep(0.1)

        start_block = end_block + 1


def count_users():
    get_all_stats()
    battle_count_old_1()
    gym_count()
    ladder_practice_count()
    transform_money()
    transform_money_old()
    trade_money()
    for month_id in months:
        print "month ", month_id, ": ", len(user_dict[month_id])


if __name__ == "__main__":
    count_users()
