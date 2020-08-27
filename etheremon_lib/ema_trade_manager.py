from etheremon_lib.models import *
from etheremon_lib.constants import EmaMarketStatus, EmaMarketType

def get_items_by_type(type):
	return EtheremonDB.EmaMarketTab.objects.filter(type=type).all()

def get_lending_items(trainer):
	return EtheremonDB.EmaMarketTab.objects.filter(player=trainer).filter(type=EmaMarketType.BORROW).filter(status=EmaMarketStatus.LENT).all()