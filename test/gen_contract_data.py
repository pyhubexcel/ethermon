import os
import sys
import random

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('../')

from etheremon_lib import monster_config
from etheremon_lib import site_config

# 50, 250, 150, 300, 250
# 10, 240, 150, 350, 250

NORMAL_DROP_RATE_DATA = {
	"monster_rate": 25,
	"shard_rate": 350,
	"level_rate": 50,
	"exp_rate": 350,
	"emont_rate": 225
}

LEGENDARY_DROP_RATE_DATA = {
	"monster_rate": 5,
	"shard_rate": 350,
	"level_rate": 50,
	"exp_rate": 350,
	"emont_rate": 245
}

def gen_monster_stats():
	site_set_collection = []
	monster_site_map = {}
	for monster_id, monster in monster_config.MONSTER_CLASS_STATS.items():
		site_list = set()
		for site_id, site in site_config.SITE_CLASS_STATS.items():
			if monster["types"][0] in site["types"]:
				site_list.add(site_id)
		site_index = 0
		while site_index < len(site_set_collection):
			if site_list == site_set_collection[site_index]:
				monster_site_map[monster_id] = site_index
				break
			site_index += 1
		if site_index == len(site_set_collection):
			site_set_collection.append(site_list)
			monster_site_map[monster_id] = site_index
	'''
	site_index = 1
	for site_set in site_set_collection:
		print "siteSet[%s] = [%s];" % (site_index, ', '.join(str(v) for v in site_set))
		site_index += 1
	'''
	'''
	for monster_id, site_index in monster_site_map.items():
		print "monsterClassSiteSet[%s] = %s;" % (monster_id, site_index+1)
	'''
	print "MONSTER_EXPLORE_SITES = {"
	for monster_id, site_index in monster_site_map.items():
		site_info = site_set_collection[site_index]
		print "%s: [%s]," % (monster_id, ', '.join(str(v) for v in site_info))
	print "};"


def gen_drop_stats():
	for site_id, site in site_config.SITE_CLASS_STATS.items():
		if site_id == 49 or site_id == 50 or site_id == 51:
			stats = [
				LEGENDARY_DROP_RATE_DATA["monster_rate"],
				site["monster_id"],
				LEGENDARY_DROP_RATE_DATA["shard_rate"],
				site["shard_id"],
				LEGENDARY_DROP_RATE_DATA["level_rate"],
				LEGENDARY_DROP_RATE_DATA["exp_rate"],
				LEGENDARY_DROP_RATE_DATA["emont_rate"]
			]
		else:
			stats = [
				NORMAL_DROP_RATE_DATA["monster_rate"],
				site["monster_id"],
				NORMAL_DROP_RATE_DATA["shard_rate"],
				site["shard_id"],
				NORMAL_DROP_RATE_DATA["level_rate"],
				NORMAL_DROP_RATE_DATA["exp_rate"],
				NORMAL_DROP_RATE_DATA["emont_rate"]
			]
		print "siteRewards[%s] = RewardData(%s);" % (site_id, ', '.join(str(v) for v in stats))
		#print "setting.setSiteRewards(%s, %s);" % (site_id, ', '.join(str(v) for v in stats))

gen_drop_stats()