from etheremon_lib.models import *


def is_on_market(monster_id):
	return EtheremonDB.EmaMarketTab.objects.filter(monster_id=monster_id).first() is not None


def get_monster_market(monster_id):
	return EtheremonDB.EmaMarketTab.objects.filter(monster_id=monster_id).first()


def get_sold_monsters(trainer):
	return EtheremonDB.MarketHistoryTab.objects.filter(seller=trainer).all()


def get_trading_history(monster_id):
	return EtheremonDB.MarketHistoryTab.objects.filter(monster_id=monster_id).order_by("-id").all()
