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



def dcl_stats():
	with transaction.atomic():

		#TODO add a where condition for last_seen < 12 hours? because others are already done
		#used to determine how long it takes for a mon to gain 1000 energy
		UserActiveStatus = EtheremonDB.DCLUserActiveStatus.objects.select_for_update().filter().all()
		for rec in UserActiveStatus:
			monsters = EtheremonDB.DCLMonsterData.objects.select_for_update().filter(Q(address=rec.address)).all()
			for monster in monsters:
				if monster is None:
					continue
				#will always have last_saved 	
				if monster.last_saved :
					mon_last_saved_secs = get_timestamp() - monster.last_saved 


				#monster lost its privilege to stay full
				if  monster.hunger_current >= 1000 and monster.hunger_state_end_timer < get_timestamp() :
					monster.hunger_state = 1
					monster.hunger_state_end_timer = None
				# stil under timer	
				elif monster.hunger_current >= 1000 and monster.hunger_state_end_timer > get_timestamp() :
					monster.hunger_state	= 2
				elif monster.hunger_current >= 500 :	
					monster.hunger_state	= 1
				elif monster.hunger_current < 500 : 
					monster.hunger_state	= 0 

		
			
				# this is player online..not monster's status
				#set sleep_end_timer for alive..others are already set
				if rec.is_live == 1 :
					secs = get_timestamp() - rec.last_seen 
					#last seen 5 mins ago . put to sleep
					if (secs / 60) >= 5 :
						rec.is_live = 0
						rec.save()
			
					# if last_saved is null, this is the first time the user gets checked up - so don't addup exp on the first run..anyway he last_saved will be updated in 5 mins
					if (monster.last_saved) :
						#	wait for an hour
						if (mon_last_saved_secs / 60) >= 60 :
							#mon full..just add dxp
							if monster.hunger_state == 2 :
								monster.dxp += 50
							# mon half full..deplete hunger as well	
							elif monster.hunger_state == 1 :
								monster.dxp += 20
								monster.hunger_current -= 5
								#monster.current_energy += (get_timestamp() - LAST_SEEN) / sleep_energy_rate 
							# mon nearly empty..no dxp
							else :
								# TODO .current_energy += (time.now - LAST_SEEN) / sleep_energy_rate (increase if sleeping)
								monster.hunger_current -= 5
							monster.last_saved =  get_timestamp()
		
									
				elif rec.is_live == 0 :

					if (monster.last_saved) :
							#	wait for an hour
							if (mon_last_saved_secs / 60) >= 60 :
								#mon full..just add dxp
								if monster.hunger_state == 2 :
									monster.dxp += 50
								# mon half full..deplete hunger as well	
								elif monster.hunger_state == 1 :
									monster.dxp += 20
									monster.hunger_current -= 10
									# TODO .current_energy += (time.now - LAST_SEEN) / sleep_energy_rate (increase if sleeping)
								# mon nearly empty..no dxp
								else :
									# TODO .current_energy += (time.now - LAST_SEEN) / sleep_energy_rate (increase if sleeping)
									monster.hunger_current -= 10	
								monster.last_saved =  get_timestamp()

				#can't save negative -  unsigned				
				if monster.hunger_current >= 0 :

					if monster.hunger_current > 1000 : 
						monster.hunger_current = 1000
					monster.save()		






	#put player offline
	#how to put player offline
	#if player offline 
	
	


if __name__ == "__main__":
	dcl_stats()
