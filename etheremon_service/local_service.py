import os
import sys
import time
import json
from django.core.wsgi import get_wsgi_application

curr_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curr_dir)
sys.path.append(os.path.join(curr_dir, '../'))

import settings
from common import context
from common import crontask

context.init_django('.', 'settings')
application = get_wsgi_application()


from contract import dcl_cron
from contract import free_energy_boost_cron
from contract import dcl_cron_free_food

from etheremon_lib.dcl_manager import dcl_update_transferred_mon
from etheremon_lib import dcl_manager

from etheremon_service.revenue_crawl import cal_txn



UPDATE_DCL_STATS = "0 */1 * * * *"
PLAYER_ENERGY_BOOST = "0 0 */12 * * *"

FREE_FOOD_FOR_GARDENS = "0 0 */24 * * *"

cal_txn.call()

#dcl_manager.dcl_update_transferred_mon(49711, '0x888802AAbaDe809bB7154b17192401a3e9006017')

#dcl_cron_free_food.update_free_food()

#free_energy_boost_cron.free_energy()
#dcl_cron.dcl_stats()

#crontask.register_task(FREE_FOOD_FOR_GARDENS, task=dcl_cron_free_food.update_free_food)
#crontask.run()



# if __name__ == "__main__":
#     def main():
   
#         crontask.register_task(PLAYER_ENERGY_BOOST, task=free_energy_boost_cron.free_energy)
#         crontask.register_task(FREE_FOOD_FOR_GARDENS, task=dcl_cron_free_food.update_free_food)
#         crontask.register_task(UPDATE_DCL_STATS, task=dcl_cron.dcl_stats)
#         crontask.run()
 
#     from common.daemon import Daemon
#     Daemon(main, os.path.abspath(__file__).replace(".py", ".pid"), "./log/service_daemon.log").main()


	

