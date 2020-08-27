# After moving win reward to quest, some forgot to claim the old win reward.
# This script is to add this amount back to the emont balance.
from django.db import transaction

from etheremon_lib import ema_energy_manager
from etheremon_lib.models import EtheremonDB
from etheremon_lib.user_balance_manager import BalanceTypes


def convert_hongbao_to_energy():
	with transaction.atomic():
		players = EtheremonDB.BalanceTab.objects\
			.filter(balance_type=BalanceTypes.HONGBAO)\
			.filter(balance_value__gt=0).all()

		print("Num Player with non-0 Hongbao balances", players.count())

		for player in players:
			print(player.player_address)
			# Add energy
			energy = ema_energy_manager.add_energy(player.player_address, player.balance_value)

			if energy is None:
				print("--->>> could not add energy")
			else:
				# Reset hongbao balance
				player.balance_value = 0
				player.save()
