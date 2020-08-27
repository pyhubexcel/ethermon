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
from django.db.models import Q, Count, F


from common.logger import log



def free_energy():
	print "sdsdsd"
	with transaction.atomic():
		#3 non free mons		
		free_mons = [25,26,27]

		non_free = EtheremonDB.EmaMonsterDataTab.objects.values('trainer').annotate(cnt=Count('trainer')).filter(Q(cnt__gte=3)).exclude(class_id__in=free_mons).all()
		non_free_trainers = []	
		for rec in non_free:
			print rec['trainer']
			non_free_trainers.append(str(rec['trainer']))

		#get mon less than 20 energy for the non free mon holders and recharge them 20
		non_free_players_energy = EtheremonDB.EmaPlayerEnergyTab.objects.select_for_update().annotate(variance=F('init_amount')+F('free_amount') + F('paid_amount') - F('invalid_amount') - F('consumed_amount')).filter(Q(trainer__in=non_free_trainers) & Q(variance__lt=20)).all()

		print "energy"
		for nfp in non_free_players_energy:
			energy_to_add = 20 - nfp.variance #max 20
			nfp.init_amount += energy_to_add
			nfp.update_time = get_timestamp()
			nfp.save()


		#exclude trainers who own paid mons..because they were already recharged above or already having sufficient energy
		other_mon_holders = EtheremonDB.EmaMonsterDataTab.objects.values('trainer').annotate(cnt=Count('trainer')).filter(Q(cnt__gte=3)).exclude(trainer__in=non_free_trainers).all()

		print "other mon holders"
		other_mon_trainers = []
		for om in other_mon_holders:
			print om['trainer']
			other_mon_trainers.append(str(om['trainer']))
			
		#get mon less than 10 energy for the other mon holders and recharge them 10
		other_mon_holders_energy = EtheremonDB.EmaPlayerEnergyTab.objects.select_for_update().annotate(variance=F('init_amount')+F('free_amount') + F('paid_amount') - F('invalid_amount') - F('consumed_amount')).filter(Q(trainer__in=other_mon_trainers) & Q(variance__lt=10)).all()

		print "other energy"
		for ome in other_mon_holders_energy:
			energy_to_add = 10 - ome.variance #max 10
			ome.init_amount += energy_to_add
			ome.update_time = get_timestamp()
			ome.save()




	

