import os
import sys

curr_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curr_dir)
sys.path.append(os.path.join(curr_dir, '../'))

from common import context
from django.core.wsgi import get_wsgi_application

context.init_django('.', 'settings')
application = get_wsgi_application()

from etheremon_lib.models import EtheremonDB

import datetime


def update_market_info():

    market_items = EtheremonDB.MarketHistoryTab.objects.all()
    count = 0
    for market_item in market_items:
        monster_id = market_item.monster_id
        try:
            monster = EtheremonDB.EmaMonsterDataTab.objects.get(monster_id=monster_id)
            market_item.class_id = monster.class_id
            market_item.base_bp = (monster.b0 + monster.b1 + monster.b2 + monster.b3 + monster.b4 + monster.b5) / 6
            market_item.create_index = monster.create_index
            market_item.save()
            print "market_item: ", market_item.class_id, ""
            count += 1
            print "updated: ", count, " - ", monster_id
        except EtheremonDB.EmaMonsterDataTab.DoesNotExist:
            print "MONSTER DOES NOT EXIST!!!!!"
            pass


def get_market_info():
    monsters = EtheremonDB.MarketHistoryTab.objects.filter(is_sold=True, buy_time__gte=1521738203).all()
    for monster in monsters:
        print str(monster.class_id) + "," + str(1.0 * monster.price / 1000) + "," + str(datetime.datetime.fromtimestamp(int(monster.buy_time)).strftime('%Y-%m-%d %H:%M:%S'))


if __name__=="__main__":
    update_market_info()

