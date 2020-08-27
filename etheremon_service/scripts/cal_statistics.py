import os
import sys
import time
import json
from datetime import datetime

from django.core.wsgi import get_wsgi_application

curr_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curr_dir)
sys.path.append(os.path.join(curr_dir, '../../'))

from common import context

context.init_django('../', 'settings')
application = get_wsgi_application()

from etheremon_lib.models import EtheremonDB
from etheremon_lib.monster_config import MONSTER_CLASS_STATS
from etheremon_lib.utils import get_new_monster_price
from etheremon_lib.contract_manager import EtheremonLadderPracticeContract, EtheremonTradeContract
from etheremon_lib.config import ETHERSCAN_API_KEYS
from etheremon_lib import ema_player_manager

from collections import OrderedDict, defaultdict

init_time = datetime(1970, 1, 1)


def get_key(year, month):
    return "%.4d-%.2d" % (year, month)


from_time = '2017-12'
to_time = '2019-03'
user_first_seen = defaultdict(lambda: '2100-01')
user_active = defaultdict(set)


def update_user_stats(user_address, time_key):
    user_address = user_address.lower()
    user_active[time_key].add(user_address)
    user_first_seen[user_address] = min(user_first_seen[user_address], time_key)


def print_stats_by_month(name, data):
    res = [name]
    for y in range(2017, 2020):
        for m in range(1, 13):
            k = get_key(y, m)
            if from_time <= k <= to_time:
                res.append(data.get(k, 0))

    print "|".join(map(str, res))


def scan_castle_mode():
    battle_count = {}

    for battle in EtheremonDB.BattleLogTab.objects.all().values("create_time", "attacker_address"):
        battle_time = datetime.fromtimestamp(battle["create_time"])
        key = get_key(battle_time.year, battle_time.month)

        battle_count[key] = battle_count.get(key, 0) + 1
        update_user_stats(battle["attacker_address"], key)

    print_stats_by_month('Battle-Castle Matches', battle_count)


def scan_ladder_mode():
    battle_count = {}

    for battle in EtheremonDB.BattleLadderTab.objects.values("monster_data", "create_time"):
        battle_time = datetime.fromtimestamp(battle["create_time"])
        key = get_key(battle_time.year, battle_time.month)

        battle_count[key] = battle_count.get(key, 0) + 1
        monster_data = json.loads(battle["monster_data"])
        trainer = monster_data["attacker_monsters"][0]["trainer"]
        update_user_stats(trainer, key)

    print_stats_by_month('Battle-Ladder-Rank Matches', battle_count)


def scan_practice_ladder_mode():
    battle_count = {}

    for battle in EtheremonDB.PracticeLadderTab.objects.values("trainee", "create_time"):
        battle_time = datetime.fromtimestamp(battle["create_time"])
        key = get_key(battle_time.year, battle_time.month)

        battle_count[key] = battle_count.get(key, 0) + 1
        update_user_stats(battle["trainee"], key)

    print_stats_by_month('Battle-Ladder-Practice Matches', battle_count)


def scan_offchain_rank_mode():
    battle_count = {}

    for battle in EtheremonDB.EmaRankBattleTab.objects.values("monster_data", "create_time"):
        battle_time = datetime.fromtimestamp(battle["create_time"])
        key = get_key(battle_time.year, battle_time.month)

        battle_count[key] = battle_count.get(key, 0) + 1
        monster_data = json.loads(battle["monster_data"])
        trainer = monster_data["attacker_monsters"][0]["trainer"]
        update_user_stats(trainer, key)

    print_stats_by_month('Offchain Rank Matches', battle_count)


def scan_offchain_practice_mode():
    battle_count = {}

    for battle in EtheremonDB.EmaPracticeBattleTab.objects.values("trainer", "create_time"):
        battle_time = datetime.fromtimestamp(battle["create_time"])
        key = get_key(battle_time.year, battle_time.month)

        battle_count[key] = battle_count.get(key, 0) + 1
        update_user_stats(battle["trainer"], key)

    print_stats_by_month('Offchain Practice Matches', battle_count)


def scan_adventure_explore_mode():
    battle_count = {}

    for battle in EtheremonDB.EmaAdventureExploreTab.objects.values("sender", "create_time"):
        battle_time = datetime.fromtimestamp(battle["create_time"])
        key = get_key(battle_time.year, battle_time.month)

        battle_count[key] = battle_count.get(key, 0) + 1
        update_user_stats(battle["sender"], key)

    print_stats_by_month('Adventure Explorations', battle_count)


def count_users():
    months = ["key"]
    for y in range(2017, 2020):
        for m in range(1, 13):
            k = get_key(y, m)
            if from_time <= k <= to_time:
                months.append(k)
    print "|".join(months)

    scan_castle_mode()
    scan_ladder_mode()
    scan_practice_ladder_mode()
    scan_offchain_rank_mode()
    scan_offchain_practice_mode()
    scan_adventure_explore_mode()

    user_active_count = {key: len(val) for key, val in user_active.items()}
    print_stats_by_month('Monthly Active Users (Estimated from all stats above)', user_active_count)

    new_users = {}
    for user, first_seen in user_first_seen.items():
        new_users[first_seen] = new_users.get(first_seen, 0) + 1
    print_stats_by_month('New Seen Users (Estimated from all stats above)', new_users)


if __name__ == "__main__":
    count_users()

