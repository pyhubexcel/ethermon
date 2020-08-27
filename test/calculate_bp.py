import os
import sys
import random

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('../')

from etheremon_lib.monster_config import MONSTER_CLASS_STATS

LEVEL_REQUIREMENT = None

def gen_level_exp():
	global LEVEL_REQUIREMENT
	LEVEL_REQUIREMENT = {}
	level = 1
	requirement = 100
	sum = requirement
	while level <= 100:
		LEVEL_REQUIREMENT[level] = sum
		level += 1
		requirement = (requirement * 11) / 10 + 5
		sum += requirement

gen_level_exp()
def get_level(exp):
	if LEVEL_REQUIREMENT == None:
		gen_level_exp()

	min_index = 1
	max_index = 100
	current_index = 0

	while min_index < max_index:
		current_index = (min_index + max_index) / 2
		if exp < LEVEL_REQUIREMENT[current_index]:
			max_index = current_index
		else:
			min_index = current_index + 1
	return min_index


def cal_bp(class_id, exp, base_stats):
	class_info = MONSTER_CLASS_STATS[int(class_id)]
	level = get_level(int(exp))
	final_stat = []
	bp = 0
	for index in xrange(0, 6):
		final_stat.append(base_stats[index] + level * class_info['steps'][index] * 3)
		print final_stat[index]
		bp += final_stat[index]
	bp /= 6
	return bp

print get_level(26943)
print cal_bp(62, 26943, [93, 97, 98, 80, 98, 94])

