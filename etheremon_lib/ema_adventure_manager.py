from django.db.models import Q
from etheremon_lib.constants import MAX_ADVENTURE_SITE_ID, AdventureRewardItems
from etheremon_lib.models import *

def get_adventure_items(token_ids):
	return EtheremonDB.EmaAdventureItemTab.objects.filter(token_id__in=token_ids).all()

def count_adventure_item_by_class(item_classes):
	return EtheremonDB.EmaAdventureItemTab.objects.filter(class_id__in=item_classes).count()

def get_sites_by_trainer(trainer):
	return EtheremonDB.EmaAdventureItemTab.objects.filter(owner=trainer).filter(token_id__lte=MAX_ADVENTURE_SITE_ID).all()

def get_items_by_trainer(trainer):
	return EtheremonDB.EmaAdventureItemTab.objects.filter(owner=trainer).filter(token_id__gt=MAX_ADVENTURE_SITE_ID).all()

def get_pending_claim_sites(trainer):
	return EtheremonDB.EmaAdventurePresaleTab.objects.filter(bidder=trainer).filter(token_id=0).all()

def count_adventure_items(trainer):
	return EtheremonDB.EmaAdventureItemTab.objects.filter(owner=trainer).filter(token_id__gt=MAX_ADVENTURE_SITE_ID).count()

def get_player_explores(trainer):
	return EtheremonDB.EmaAdventureExploreTab.objects.filter(sender=trainer).all()

def count_player_explores(trainer):
	return EtheremonDB.EmaAdventureExploreTab.objects.filter(sender=trainer).count()

def count_player_explores_by_time(trainer, from_time, to_time):
	return EtheremonDB.EmaAdventureExploreTab.objects\
		.filter(sender=trainer)\
		.filter(create_time__gte=from_time) \
		.filter(create_time__lte=to_time).count()

def get_pending_explore(trainer):
	return EtheremonDB.EmaAdventureExploreTab.objects.filter(sender=trainer).filter(reward_monster_class=0).filter(reward_item_class=0).filter(reward_item_value='0').first()

def count_explore_by_site(site_id):
	return EtheremonDB.EmaAdventureExploreTab.objects.filter(site_id=site_id).count()

def get_site_token_balance(site_id, token_id):
	site_revenue = EtheremonDB.EmaAdventureRevenueSiteTab.objects.filter(site_id=site_id).first()
	if not site_revenue:
		return 0, 0
	token_claim = EtheremonDB.EmaAdventureClaimTokenTab.objects.filter(token_id=token_id).first()
	if not token_claim:
		return site_revenue.eth_amount*9/100, site_revenue.emont_amount*9/100
	return (site_revenue.eth_amount*9/100 - token_claim.claimed_eth_amount), (site_revenue.emont_amount*9/100 - token_claim.claimed_emont_amount)

def set_adventure_vote(trainer, explore_eth, explore_emont, challenge_eth, challenge_emont, vote_time):
	obj, created = EtheremonDB.EmaAdventureVoteTab.objects.update_or_create(
		owner=trainer,
		defaults={
			"explore_eth_fee": explore_eth,
			"explore_emont_fee": explore_emont,
			"challenge_eth_fee": challenge_eth,
			"challenge_emont_fee": challenge_emont,
			"update_time": vote_time})
	return obj

def get_adventure_vote(trainer):
	record = EtheremonDB.EmaAdventureVoteTab.objects.filter(owner=trainer).first()
	result = {
		"explore_eth_fee": 0.01,
		"explore_emont_fee": 15,
		"challenge_eth_fee": 0.01,
		"challenge_emont_fee": 15
	}
	if record:
		result["explore_eth_fee"] = record.explore_eth_fee
		result["explore_emont_fee"] = record.explore_emont_fee
		result["challenge_eth_fee"] = record.challenge_eth_fee
		result["challenge_emont_fee"] = record.challenge_emont_fee
	return result


def count_adventure_mon_caught(trainer):
	return EtheremonDB.EmaAdventureExploreTab.objects\
		.filter(sender=trainer)\
		.filter(reward_monster_class__gt=0).count()


def count_adventure_mon_caught_by_time(trainer, from_time, to_time):
	return EtheremonDB.EmaAdventureExploreTab.objects\
		.filter(sender=trainer)\
		.filter(reward_monster_class__gt=0) \
		.filter(create_time__gte=from_time) \
		.filter(create_time__lte=to_time).count()


def count_adventure_item_found(trainer, item_class, item_value):
	return EtheremonDB.EmaAdventureExploreTab.objects \
		.filter(sender=trainer) \
		.filter(reward_item_class=item_class)\
		.filter(reward_item_value=item_value).count()


def count_adventure_item_found_by_time(trainer, item_class, item_value, from_time, to_time):
	return EtheremonDB.EmaAdventureExploreTab.objects \
		.filter(sender=trainer) \
		.filter(reward_item_class=item_class) \
		.filter(reward_item_value=item_value) \
		.filter(create_time__gte=from_time) \
		.filter(create_time__lte=to_time).count()


def count_adventure_shard_found(trainer):
	return EtheremonDB.EmaAdventureExploreTab.objects \
		.filter(sender=trainer) \
		.filter(reward_item_class__gte=AdventureRewardItems.SHARD_MIN) \
		.filter(reward_item_class__lte=AdventureRewardItems.SHARD_MAX).count()


def count_adventure_shard_found_by_time(trainer, from_time, to_time):
	return EtheremonDB.EmaAdventureExploreTab.objects \
		.filter(sender=trainer) \
		.filter(reward_item_class__gte=AdventureRewardItems.SHARD_MIN) \
		.filter(reward_item_class__lte=AdventureRewardItems.SHARD_MAX) \
		.filter(create_time__gte=from_time) \
		.filter(create_time__lte=to_time).count()
