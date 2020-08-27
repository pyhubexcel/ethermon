import json

from common.utils import get_timestamp
from etheremon_lib.constants import FREE_MONSTERS
from etheremon_lib.models import EtheremonDB


class BurnRewardTypes:
	UNDEFINED = 0

	ENERGY = 1
	IN_GAME_EMONT = 2


class BurnStatus:
	INIT = 0
	PENDING = 1
	FINISHED = 2
	FAILED = 3


BURN_MON_REWARDS = {
	0: {'type': BurnRewardTypes.ENERGY, 'value': 0},
	1: {'type': BurnRewardTypes.ENERGY, 'value': 1},
	2: {'type': BurnRewardTypes.ENERGY, 'value': 1},
	3: {'type': BurnRewardTypes.ENERGY, 'value': 1},
	4: {'type': BurnRewardTypes.ENERGY, 'value': 1},
	5: {'type': BurnRewardTypes.ENERGY, 'value': 2},
	6: {'type': BurnRewardTypes.ENERGY, 'value': 2},
	7: {'type': BurnRewardTypes.ENERGY, 'value': 3},
	8: {'type': BurnRewardTypes.ENERGY, 'value': 3},
	9: {'type': BurnRewardTypes.ENERGY, 'value': 4},
	10: {'type': BurnRewardTypes.ENERGY, 'value': 5},
	11: {'type': BurnRewardTypes.ENERGY, 'value': 5},
	12: {'type': BurnRewardTypes.ENERGY, 'value': 6},
	13: {'type': BurnRewardTypes.ENERGY, 'value': 7},
	14: {'type': BurnRewardTypes.ENERGY, 'value': 8},
	15: {'type': BurnRewardTypes.ENERGY, 'value': 9},
	16: {'type': BurnRewardTypes.ENERGY, 'value': 10},
	17: {'type': BurnRewardTypes.ENERGY, 'value': 11},
	18: {'type': BurnRewardTypes.ENERGY, 'value': 12},
	19: {'type': BurnRewardTypes.ENERGY, 'value': 13},
	20: {'type': BurnRewardTypes.ENERGY, 'value': 14},
	21: {'type': BurnRewardTypes.ENERGY, 'value': 15},
	22: {'type': BurnRewardTypes.ENERGY, 'value': 16},
	23: {'type': BurnRewardTypes.ENERGY, 'value': 17},
	24: {'type': BurnRewardTypes.ENERGY, 'value': 19},
	25: {'type': BurnRewardTypes.ENERGY, 'value': 20},
	26: {'type': BurnRewardTypes.ENERGY, 'value': 22},
	27: {'type': BurnRewardTypes.ENERGY, 'value': 23},
	28: {'type': BurnRewardTypes.ENERGY, 'value': 25},
	29: {'type': BurnRewardTypes.ENERGY, 'value': 27},
	30: {'type': BurnRewardTypes.ENERGY, 'value': 28},
	31: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 32},
	32: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 34},
	33: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 36},
	34: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 38},
	35: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 40},
	36: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 43},
	37: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 46},
	38: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 48},
	39: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 51},
	40: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 54},
	41: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 57},
	42: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 60},
	43: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 64},
	44: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 67},
	45: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 71},
	46: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 75},
	47: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 79},
	48: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 84},
	49: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 88},
	50: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 93},
	51: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 98},
	52: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 103},
	53: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 108},
	54: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 114},
	55: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 120},
	56: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 126},
	57: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 133},
	58: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 140},
	59: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 147},
	60: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 154},
	61: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 162},
	62: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 170},
	63: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 179},
	64: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 188},
	65: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 198},
	66: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 207},
	67: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 218},
	68: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 229},
	69: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 240},
	70: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 252},
	71: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 265},
	72: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 278},
	73: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 291},
	74: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 306},
	75: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 321},
	76: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 337},
	77: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 353},
	78: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 370},
	79: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 388},
	80: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 407},
	81: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 427},
	82: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 448},
	83: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 470},
	84: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 493},
	85: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 517},
	86: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 542},
	87: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 568},
	88: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 595},
	89: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 624},
	90: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 654},
	91: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 686},
	92: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 719},
	93: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 754},
	94: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 790},
	95: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 828},
	96: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 868},
	97: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 910},
	98: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 954},
	99: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 999},
	100: {'type': BurnRewardTypes.IN_GAME_EMONT, 'value': 1048},
}


def get_reward_from_level(level, monster_class_id):
	if monster_class_id in FREE_MONSTERS and level < 30:
		return BURN_MON_REWARDS[0]
	else:
		return BURN_MON_REWARDS[level]


def get_or_create_burn_request(player_address, mon_id, mon_level=1, mon_exp=1, amount_type=BurnRewardTypes.UNDEFINED, amount_value=0, status=BurnStatus.INIT):
	burn_request = get_burn_request_by_mon(player_address, mon_id)\
		.filter(status__in=[BurnStatus.INIT, BurnStatus.PENDING])\
		.first()

	if burn_request:
		if burn_request.mon_level != mon_level or burn_request.mon_exp != mon_exp:
			burn_request.mon_level = mon_level
			burn_request.mon_exp = mon_exp
			burn_request.save()
		return burn_request

	burn_request = EtheremonDB.BurnMonTab(
		player_address=player_address,
		mon_id=mon_id,
		mon_level=mon_level,
		mon_exp=mon_exp,
		amount_type=amount_type,
		amount_value=amount_value,
		status=status,
		create_time=get_timestamp(),
		update_time=get_timestamp(),
	)
	burn_request.save()
	return burn_request


def get_burn_request_by_mon(player_address, mon_id):
	return EtheremonDB.BurnMonTab.objects.filter(player_address=player_address).filter(mon_id=mon_id)


def get_burn_request_by_id(burn_id):
	return EtheremonDB.BurnMonTab.objects.filter(id=burn_id).first()


def get_contract_burn_id(mon_id, burn_id):
	return 1000000 * mon_id + burn_id


def get_mon_id_from_contract_burn_id(contract_burn_id):
	"""
	:param contract_burn_id:
	:return: mon_id, burn_id
	"""
	return contract_burn_id / 1000000, contract_burn_id % 1000000
