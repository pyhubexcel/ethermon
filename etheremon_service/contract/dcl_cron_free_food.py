import os
import sys
import time

curr_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curr_dir)
sys.path.append(os.path.join(curr_dir, '../../'))

from common import context
from django.core.wsgi import get_wsgi_application
from web3 import Web3, HTTPProvider

context.init_django('../', 'settings')
application = get_wsgi_application()

from common.utils import get_timestamp
from etheremon_lib.models import EtheremonDB
from etheremon_lib.config import *
from etheremon_lib import ema_settings_manager
from helper import _sync_player_dex
from django.db import transaction
from django.db import connection

from django.db.models import Q
from django.db.models import QuerySet
from common.logger import log

import random

def update_free_food() :

		free_food_config = EtheremonDB.DCLItemClassConfig.objects.filter(ItemVariety='beet').first()
		
		if free_food_config is None:
			print 'NO_RELEVANT_DCL_ITEM_CLASS_CONFIG_FOUND'
			return false

		## delete already planted food which are not eaten / plucked yet

		EtheremonDB.DCLItemWip.objects.filter(growth_state=0).filter(ItemVariety=free_food_config.ItemVariety).delete()


		# plant a free food -  50% chance for each users who are all logged in two weeks
	
		
		two_weeks = get_timestamp() - (14*24*3600) #2 weeks

		users = EtheremonDB.DCLUserActiveStatus.objects.filter(last_seen__gt=two_weeks ).all()


		cursor = connection.cursor()
		cursor.execute('SELECT DISTINCT host_id from dcl_item_wip')
		cur_gar = cursor.fetchall()
		all_gardens = []
		for g in cur_gar:
			all_gardens.append(g[0])
			

		#every user will plant on all host_id..50% chance
		for user in users:
			#seed on all gardens
			for garden in all_gardens:
				#50% chance
				if random.choice([True, False]):
					with transaction.atomic():
						exists = EtheremonDB.DCLItemWip.objects.filter(Q(host_id=garden) & Q(meta_id=86) & Q(growth_state=0) & Q(address=user.address)).first()
		
						if exists :
							print 'META_AND_HOST_AND_ADDRESS_ALREADY_EXISTS_IN_GROWING_STATE'
							continue

						secs_to_grow = 0
						
						if free_food_config:
							secs_to_grow = free_food_config.craft_timer

						#create new wip
						EtheremonDB.DCLItemWip.objects.create(
							ItemClass = free_food_config.ItemClass,
							ItemVariety= free_food_config.ItemVariety,
							wild= 'no',
							wild_count= 0,
							address= user.address,
							growth_state= 0,
							host_id= garden,
							meta_id= 86,
							start_timer= get_timestamp(),
							end_timer= get_timestamp() + secs_to_grow
						)
					


if __name__ == "__main__":
	update_free_food()
