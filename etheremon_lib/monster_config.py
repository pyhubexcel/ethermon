MONSTER_AGAINST_CONFIG = {
	1: 14,
	2: 16,
	3: 8,
	4: 9,
	5: 2,
	6: 11,
	7: 3,
	8: 5,
	9: 15,
	11: 18,
	12: 7,
	13: 6,
	14: 17,
	15: 13,
	16: 12,
	17: 1,
	18: 4
}

CATCHABLE_MONSTER_CLASS_IDS = {25, 26, 27, 29, 31, 32, 33, 34, 35, 36, 37, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 96, 97, 99, 105, 106, 109, 110, 111, 112, 113, 114, 115}
ADVENTURE_MONSTER_CLASS_IDS = {128, 166, 134, 136, 138, 173, 177, 168, 144, 170, 116, 119, 148, 122, 125, 197} #catchable form 1 only (remove replaced adventure mons?)
# Q1 2020 Update
# 131 Iquander replace by 166 Spoulder
# 142 Clothom replace by 168 Foxeez
# 146 Kikapole replace by 170 Roichirp
# 151 Greipawn repalce by 173 Batflare
# 140 Dusprite replace by 177 Watuber

EGG_CLASS_IDS = {32, 97, 80, 73, 79, 80, 101, 103, 105}

_MONSTER_CLASS_STATS = {
	1: {
		"types": [14, 16],
		"stats": [45, 49, 49, 65, 65, 45],
		"steps": [2, 1, 1, 1, 2, 2],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [1, 38, 64],
		"lvl_transform": 20,
		"generation": 0
	},
	2: {
		"types": [4],
		"stats": [39, 52, 43, 60, 60, 65],
		"steps": [2, 2, 1, 2, 1, 1],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [2, 39, 65],
		"lvl_transform": 20,
		"generation": 0
	},
	3: {
		"types": [18],
		"stats": [44, 48, 65, 50, 64, 43],
		"steps": [1, 1, 2, 2, 2, 1],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [3, 40],
		"lvl_transform": 26,
		"generation": 0
	},
	4: {
		"types": [5, 16],
		"stats": [30, 35, 30, 100, 35, 80],
		"steps": [1, 1, 1, 1, 3, 2],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [4, 41, 66],
		"lvl_transform": 20,
		"generation": 0
	},
	5: {
		"types": [16],
		"stats": [35, 60, 44, 40, 54, 55],
		"steps": [1, 2, 1, 1, 2, 2],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [5, 42, 67],
		"lvl_transform": 20,
		"generation": 0
	},
	6: {
		"types": [11],
		"stats": [35, 55, 30, 50, 40, 90],
		"steps": [1, 2, 1, 2, 1, 3],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [6, 43],
		"lvl_transform": 25,
		"generation": 0
	},
	7: {
		"types": [3],
		"stats": [70, 45, 48, 60, 65, 35],
		"steps": [2, 1, 1, 2, 2, 1],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [7, 44],
		"lvl_transform": 28,
		"generation": 0
	},
	8: {
		"types": [7, 3],
		"stats": [115, 45, 20, 45, 25, 20],
		"steps": [2, 1, 2, 1, 2, 1],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [8, 45],
		"lvl_transform": 25,
		"generation": 0
	},
	9: {
		"types": [7],
		"stats": [40, 45, 35, 40, 40, 90],
		"steps": [1, 2, 1, 1, 2, 2],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [9, 46],
		"lvl_transform": 27,
		"generation": 0
	},
	10: {
		"types": [4],
		"stats": [55, 70, 45, 70, 50, 60],
		"steps": [1, 2, 1, 2, 1, 2],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [10, 47],
		"lvl_transform": 29,
		"generation": 0
	},
	11: {
		"types": [8],
		"stats": [25, 20, 15, 105, 55, 90],
		"steps": [1, 1, 1, 3, 1, 2],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [11, 48],
		"lvl_transform": 25,
		"generation": 0
	},
	12: {
		"types": [12],
		"stats": [70, 80, 50, 35, 35, 35],
		"steps": [2, 2, 2, 1, 1, 1],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [12, 49],
		"lvl_transform": 26,
		"generation": 0
	},
	13: {
		"types": [17, 6],
		"stats": [40, 80, 100, 30, 20, 20],
		"steps": [1, 2, 3, 1, 1, 1],
		"is_gason": False,
		"ancestors": [],
		"generation": 0
	},
	14: {
		"types": [6],
		"stats": [50, 50, 95, 40, 50, 35],
		"steps": [1, 2, 2, 1, 2, 1],
		"is_gason": False,
		"ancestors": [],
		"generation": 0
	},
	15: {
		"types": [18],
		"stats": [30, 40, 70, 70, 25, 60],
		"steps": [1, 1, 2, 2, 1, 2],
		"is_gason": False,
		"ancestors": [],
		"generation": 0
	},
	16: {
		"types": [1, 13],
		"stats": [70, 110, 80, 55, 80, 105],
		"steps": [1, 1, 2, 1, 1, 2],
		"is_gason": False,
		"ancestors": [],
		"generation": 0
	},
	17: {
		"types": [18, 13],
		"stats": [95, 125, 79, 60, 100, 81],
		"steps": [2, 1, 2, 1, 1, 1],
		"is_gason": False,
		"ancestors": [],
		"generation": 0
	},
	18: {
		"types": [7],
		"stats": [48, 48, 48, 48, 48, 48],
		"steps": [1, 1, 1, 1, 1, 1],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [18, 50],
		"lvl_transform": 28,
		"generation": 0
	},
	19: {
		"types": [7],
		"stats": [160, 110, 65, 65, 110, 30],
		"steps": [1, 2, 1, 1, 2, 1],
		"is_gason": False,
		"ancestors": [],
		"generation": 0
	},
	20: {
		"types": [2],
		"stats": [41, 64, 45, 50, 50, 50],
		"steps": [2, 1, 1, 1, 1, 1],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [20, 51, 68],
		"lvl_transform": 20,
		"generation": 0
	},
	21: {
		"types": [1],
		"stats": [0, 0, 0, 0, 0, 0],
		"steps": [0, 0, 0, 0, 0, 0],
		"is_gason": False,
		"ancestors": [],
		"generation": 0
	},
	22: {
		"types": [5],
		"stats": [55, 3, 87, 5, 89, 60],
		"steps": [1, 1, 2, 1, 2, 2],
		"is_gason": True,
		"ancestors": [],
		"generation": 0
	},
	23: {
		"types": [8],
		"stats": [70, 88, 80, 92, 81, 80],
		"steps": [2, 1, 1, 1, 1, 2],
		"is_gason": False,
		"ancestors": [],
		"generation": 0
	},
	24: {
		"types": [14, 7],
		"stats": [145, 150, 70, 77, 95, 50],
		"steps": [1, 1, 2, 1, 2, 1],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [24, 89, 158],
		"lvl_transform": 39,
		"generation": 0
	},
	25: {
		"types": [14, 15],
		"stats": [48, 53, 49, 52, 55, 54],
		"steps": [2, 2, 1, 1, 1, 2],
		"is_gason": False,
		"ancestors": [23, 8, 24],
		"next_forms": [25, 52, 69],
		"lvl_transform": 20,
		"generation": 1,
		"price": 0,
	},
	26: {
		"types": [18, 3],
		"stats": [58, 40, 61, 42, 63, 47],
		"steps": [2, 1, 2, 1, 2, 1],
		"is_gason": False,
		"ancestors": [5, 17, 7],
		"next_forms": [26, 53, 70],
		"lvl_transform": 21,
		"generation": 1,
		"price": 0,
	},
	27: {
		"types": [4, 8],
		"stats": [41, 59, 48, 60, 45, 58],
		"steps": [1, 2, 1, 2, 1, 2],
		"is_gason": False,
		"ancestors": [2, 19, 4],
		"next_forms": [27, 54],
		"lvl_transform": 28,
		"generation": 1,
		"price": 0,
	},
	28: {
		"types": [11, 16],
		"stats": [52, 47, 53, 65, 51, 58],
		"steps": [2, 1, 2, 2, 1, 1],
		"is_gason": False,
		"ancestors": [5, 6, 13],
		"next_forms": [28, 55],
		"lvl_transform": 28,
		"lvl_lay": [-1, -1],
		"price": 0.09,
		"generation": 1
	},
	29: {
		"types": [5, 9],
		"stats": [55, 57, 60, 53, 52, 51],
		"steps": [1, 2, 2, 1, 1, 2],
		"is_gason": False,
		"ancestors": [8, 1, 12],
		"next_forms": [29, 56],
		"lvl_transform": 27,
		"lvl_lay": [61, 50],
		"price": 0.09,
		"generation": 1
	},
	30: {
		"types": [2],
		"stats": [78, 65, 57, 57, 62, 65],
		"steps": [2, 2, 2, 1, 2, 1],
		"is_gason": False,
		"ancestors": [10, 16, 9],
		"next_forms": [30, 57],
		"lvl_transform": 28,
		"lvl_lay": [-1, -1],
		"price": 0.15,
		"generation": 1
	},
	31: {
		"types": [12],
		"stats": [55, 62, 51, 45, 50, 52],
		"steps": [2, 2, 1, 1, 1, 2],
		"is_gason": False,
		"ancestors": [14, 12, 55],
		"next_forms": [31, 58],
		"lvl_transform": 27,
		"lvl_lay": [51, 15],
		"price": 0.04,
		"generation": 2
	},
	32: {
		"types": [14],
		"stats": [56, 56, 54, 48, 54, 58],
		"steps": [2, 2, 2, 1, 1, 1],
		"is_gason": False,
		"ancestors": [18, 7, 1],
		"next_forms": [32, 59],
		"lvl_transform": 27,
		"lvl_lay": [61, 50],
		"price": 0.09,
		"generation": 1
	},
	33: {
		"types": [15, 7],
		"stats": [60, 51, 57, 58, 59, 50],
		"steps": [2, 1, 1, 2, 2, 1],
		"is_gason": False,
		"ancestors": [17, 3, 11],
		"next_forms": [33, 60],
		"lvl_transform": 28,
		"lvl_lay": [61, 50],
		"price": 0.09,
		"generation": 1
	},
	34: {
		"types": [18, 8],
		"stats": [52, 48, 47, 57, 46, 34],
		"steps": [2, 1, 1, 2, 2, 1],
		"is_gason": False,
		"ancestors": [15, 4, 29],
		"next_forms": [34, 61, 71],
		"lvl_transform": 21,
		"lvl_lay": [51, 15],
		"price": 0.03,
		"generation": 2
	},
	35: {
		"types": [18],
		"stats": [50, 20, 60, 20, 60, 50],
		"steps": [1, 1, 2, 1, 2, 2],
		"is_gason": True,
		"ancestors": [],
		"price": 0.03,
		"generation": 0
	},
	36: {
		"types": [4],
		"stats": [50, 20, 60, 20, 60, 50],
		"steps": [1, 1, 2, 1, 2, 2],
		"is_gason": True,
		"ancestors": [],
		"price": 0.03,
		"generation": 0
	},
	37: {
		"types": [7],
		"stats": [56, 57, 52, 45, 59, 58],
		"steps": [1, 2, 1, 1, 2, 2],
		"is_gason": False,
		"ancestors": [9, 18, 30],
		"next_forms": [37, 62, 63],
		"lvl_transform": 26,
		"lvl_lay": [61, 50],
		"price": 0.09,
		"generation": 2
	},
	38: {
		"types": [14, 16],
		"stats": [56, 61, 61, 81, 81, 56],
		"steps": [2, 1, 1, 2, 2, 2],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [1, 38, 64],
		"lvl_transform": 40,
		"generation": 0,
		"transformed": True
	},
	39: {
		"types": [4],
		"stats": [48, 65, 53, 75, 75, 81],
		"steps": [2, 2, 1, 2, 2, 1],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [2, 39, 65],
		"lvl_transform": 40,
		"generation": 0,
		"transformed": True
	},
	40: {
		"types": [18],
		"stats": [59, 64, 87, 67, 86, 58],
		"steps": [2, 1, 3, 2, 2, 2],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [3, 40],
		"generation": 0,
		"transformed": True
	},
	41: {
		"types": [5, 16],
		"stats": [57, 43, 60, 103, 49, 80],
		"steps": [2, 1, 1, 2, 2, 2],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [4, 41, 66],
		"lvl_transform": 39,
		"generation": 0,
		"transformed": True
	},
	42: {
		"types": [16],
		"stats": [52, 75, 55, 50, 67, 68],
		"steps": [2, 2, 1, 1, 2, 2],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [5, 42, 67],
		"lvl_transform": 42,
		"generation": 0,
		"transformed": True
	},
	43: {
		"types": [11],
		"stats": [68, 74, 40, 67, 54, 100],
		"steps": [1, 3, 2, 2, 2, 2],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [6, 43],
		"generation": 0,
		"transformed": True
	},
	44: {
		"types": [3],
		"stats": [94, 60, 64, 81, 87, 47],
		"steps": [2, 1, 2, 3, 2, 2],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [7, 44],
		"generation": 0,
		"transformed": True
	},
	45: {
		"types": [7, 3],
		"stats": [100, 60, 50, 80, 53, 50],
		"steps": [2, 1, 3, 2, 2, 2],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [8, 45],
		"generation": 0,
		"transformed": True
	},
	46: {
		"types": [7, 12],
		"stats": [64, 80, 57, 54, 64, 100],
		"steps": [2, 3, 2, 1, 2, 2],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [9, 46],
		"generation": 0,
		"transformed": True
	},
	47: {
		"types": [4],
		"stats": [74, 94, 60, 94, 67, 81],
		"steps": [1, 3, 2, 3, 2, 1],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [10, 47],
		"generation": 0,
		"transformed": True
	},
	48: {
		"types": [8],
		"stats": [74, 27, 40, 100, 74, 100],
		"steps": [2, 1, 2, 2, 2, 3],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [11, 48],
		"generation": 0,
		"transformed": True
	},
	49: {
		"types": [12],
		"stats": [94, 108, 67, 47, 47, 57],
		"steps": [2, 2, 2, 1, 2, 3],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [12, 49],
		"generation": 0,
		"transformed": True
	},
	50: {
		"types": [7],
		"stats": [74, 74, 74, 74, 74, 74],
		"steps": [2, 2, 2, 2, 2, 2],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [18, 50],
		"generation": 0,
		"transformed": True
	},
	51: {
		"types": [2, 17],
		"stats": [51, 80, 56, 62, 62, 62],
		"steps": [2, 2, 1, 1, 2, 2],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [20, 51, 68],
		"lvl_transform": 37,
		"generation": 0,
		"transformed": True
	},
	52: {
		"types": [14, 15],
		"stats": [60, 66, 61, 65, 68, 67],
		"steps": [2, 2, 1, 1, 2, 2],
		"is_gason": False,
		"ancestors": [23, 8, 24],
		"next_forms": [25, 52, 69],
		"lvl_transform": 39,
		"lvl_lay": [-1, -1],
		"generation": 1,
		"transformed": True
	},
	53: {
		"types": [18, 3],
		"stats": [72, 50, 76, 52, 78, 58],
		"steps": [2, 1, 2, 2, 2, 1],
		"is_gason": False,
		"ancestors": [5, 17, 7],
		"next_forms": [26, 53, 70],
		"lvl_transform": 38,
		"lvl_lay": [-1, -1],
		"generation": 1,
		"transformed": True
	},
	54: {
		"types": [4, 8],
		"stats": [69, 73, 66, 75, 67, 80],
		"steps": [2, 2, 2, 2, 2, 2],
		"is_gason": False,
		"ancestors": [2, 19, 4],
		"next_forms": [27, 54],
		"lvl_lay": [-1, -1],
		"generation": 1,
		"transformed": True
	},
	55: {
		"types": [11, 16],
		"stats": [74, 63, 71, 87, 68, 78],
		"steps": [2, 1, 2, 3, 2, 2],
		"is_gason": False,
		"ancestors": [5, 6, 13],
		"next_forms": [28, 55],
		"lvl_lay": [-1, -1],
		"generation": 1,
		"transformed": True
	},
	56: {
		"types": [5, 9],
		"stats": [74, 76, 81, 71, 70, 68],
		"steps": [2, 2, 3, 1, 3, 1],
		"is_gason": False,
		"ancestors": [8, 1, 12],
		"next_forms": [29, 56],
		"lvl_lay": [-1, -1],
		"generation": 1,
		"transformed": True
	},
	57: {
		"types": [2],
		"stats": [97, 87, 76, 76, 83, 87],
		"steps": [2, 2, 2, 2, 2, 2],
		"is_gason": False,
		"ancestors": [10, 16, 9],
		"next_forms": [30, 57],
		"lvl_lay": [-1, -1],
		"generation": 1,
		"transformed": True
	},
	58: {
		"types": [12],
		"stats": [74, 94, 68, 60, 67, 70],
		"steps": [2, 3, 1, 2, 2, 2],
		"is_gason": False,
		"ancestors": [14, 12, 55],
		"next_forms": [31, 58],
		"lvl_lay": [-1, -1],
		"generation": 2,
		"transformed": True
	},
	59: {
		"types": [14, 9],
		"stats": [75, 75, 72, 64, 72, 78],
		"steps": [2, 2, 2, 2, 2, 2],
		"is_gason": False,
		"ancestors": [18, 7, 1],
		"next_forms": [32, 59],
		"lvl_lay": [-1, -1],
		"generation": 1,
		"transformed": True
	},
	60: {
		"types": [15, 7],
		"stats": [81, 68, 76, 78, 79, 67],
		"steps": [2, 3, 2, 2, 2, 1],
		"is_gason": False,
		"ancestors": [17, 3, 11],
		"next_forms": [33, 60],
		"lvl_lay": [-1, -1],
		"generation": 1,
		"transformed": True
	},
	61: {
		"types": [18, 8],
		"stats": [65, 60, 58, 75, 57, 64],
		"steps": [2, 1, 2, 2, 2, 1],
		"is_gason": False,
		"ancestors": [15, 4, 29],
		"next_forms": [34, 61, 71],
		"lvl_transform": 39,
		"lvl_lay": [-1, -1],
		"generation": 2,
		"transformed": True
	},
	62: {
		"types": [7, 6],
		"stats": [78, 76, 75, 56, 73, 72],
		"steps": [2, 2, 2, 1, 2, 3],
		"is_gason": False,
		"ancestors": [9, 18, 30],
		"next_forms": [37, 62, 63],
		"lvl_transform": 5,
		"lvl_lay": [-1, -1],
		"generation": 2,
		"transformed": True
	},
	63: {
		"types": [7, 13],
		"stats": [78, 57, 65, 83, 65, 82],
		"steps": [2, 1, 2, 2, 2, 3],
		"is_gason": False,
		"ancestors": [9, 18, 30],
		"next_forms": [37, 62, 63],
		"lvl_lay": [-1, -1],
		"generation": 2,
		"transformed": True
	},
	64: {
		"types": [14, 16],
		"stats": [70, 76, 76, 101, 101, 70],
		"steps": [2, 1, 2, 3, 3, 2],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [1, 38, 64],
		"generation": 0,
		"transformed": True
	},
	65: {
		"types": [4],
		"stats": [60, 81, 66, 93, 93, 101],
		"steps": [2, 2, 2, 2, 2, 3],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [2, 39, 65],
		"generation": 0,
		"transformed": True
	},
	66: {
		"types": [5, 16],
		"stats": [71, 53, 75, 128, 61, 100],
		"steps": [2, 2, 2, 2, 3, 2],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [4, 41, 66],
		"generation": 0,
		"transformed": True
	},
	67: {
		"types": [16],
		"stats": [65, 93, 68, 62, 83, 84],
		"steps": [2, 3, 3, 1, 2, 2],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [5, 42, 67],
		"generation": 0,
		"transformed": True
	},
	68: {
		"types": [2, 17],
		"stats": [63, 100, 70, 77, 77, 77],
		"steps": [2, 3, 2, 2, 2, 2],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [20, 51, 68],
		"generation": 0,
		"transformed": True
	},
	69: {
		"types": [14, 15],
		"stats": [75, 82, 76, 81, 85, 83],
		"steps": [2, 2, 2, 2, 3, 2],  # old data [2, 3, 2, 2, 2, 2]
		"is_gason": False,
		"ancestors": [23, 8, 24],
		"next_forms": [25, 52, 69],
		"lvl_lay": [-1, -1],
		"generation": 1,
		"transformed": True
	},
	70: {
		"types": [18, 3],
		"stats": [90, 62, 95, 65, 97, 72],
		"steps": [2, 2, 3, 2, 2, 2],  # old data [2, 1, 3, 2, 3, 2]
		"is_gason": False,
		"ancestors": [5, 17, 7],
		"next_forms": [26, 53, 70],
		"lvl_lay": [-1, -1],
		"generation": 1,
		"transformed": True
	},
	71: {
		"types": [18, 8],
		"stats": [81, 75, 79, 93, 79, 80],
		"steps": [2, 2, 2, 3, 2, 2],
		"is_gason": False,
		"ancestors": [15, 4, 29],
		"next_forms": [34, 61, 71],
		"lvl_lay": [-1, -1],
		"generation": 2,
		"transformed": True
	},
	72: {
		"types": [9],
		"stats": [50, 20, 60, 20, 60, 50],
		"steps": [1, 1, 2, 1, 2, 2],
		"is_gason": True,
		"ancestors": [],
		"price": 0.03,
		"generation": 0
	},
	73: {
		"types": [13],
		"stats": [50, 20, 60, 20, 60, 50],
		"steps": [1, 1, 2, 1, 2, 2],
		"is_gason": True,
		"ancestors": [],
		"price": 0.03,
		"generation": 0
	},
	74: {
		"types": [16],
		"stats": [50, 20, 60, 20, 60, 50],
		"steps": [1, 1, 2, 1, 2, 2],
		"is_gason": True,
		"ancestors": [],
		"price": 0.03,
		"generation": 0
	},
	75: {
		"types": [3],
		"stats": [50, 20, 60, 20, 60, 50],
		"steps": [1, 1, 2, 1, 2, 2],
		"is_gason": True,
		"ancestors": [],
		"price": 0.03,
		"generation": 0
	},
	76: {
		"types": [14],
		"stats": [50, 20, 60, 20, 60, 50],
		"steps": [1, 1, 2, 1, 2, 2],
		"is_gason": True,
		"ancestors": [],
		"price": 0.03,
		"generation": 0
	},
	77: {
		"types": [13, 8],
		"stats": [62, 54, 58, 67, 65, 67],
		"steps": [2, 1, 1, 2, 2, 1],
		"is_gason": False,
		"ancestors": [14, 16, 11],
		"next_forms": [77, 82],
		"lvl_transform": 32,
		"lvl_lay": [81, 20],
		"price": 0.15,
		"generation": 1
	},
	78: {
		"types": [12, 5],
		"stats": [59, 63, 62, 45, 58, 62],
		"steps": [1, 2, 2, 1, 1, 2],
		"is_gason": False,
		"ancestors": [19, 9, 28],
		"next_forms": [78, 83],
		"lvl_transform": 30,
		"lvl_lay": [61, 50],
		"price": 0.09,
		"generation": 2
	},
	79: {
		"types": [14, 17],
		"stats": [53, 57, 57, 46, 51, 43],
		"steps": [2, 2, 2, 1, 1, 1],
		"is_gason": False,
		"ancestors": [24, 13, 32],
		"next_forms": [79, 84, 87],
		"lvl_transform": 23,
		"lvl_lay": [51, 50],
		"price": 0.05,
		"generation": 2
	},
	80: {
		"types": [1, 9],
		"stats": [50, 58, 67, 59, 55, 63],
		"steps": [1, 2, 1, 2, 1, 2],
		"is_gason": False,
		"ancestors": [29, 18, 16],
		"next_forms": [80, 85],
		"lvl_transform": 29,
		"lvl_lay": [61, 50],
		"price": 0.09,
		"generation": 2
	},
	81: {
		"types": [5, 6],
		"stats": [55, 53, 48, 62, 48, 59],
		"steps": [2, 1, 1, 2, 1, 2],
		"is_gason": False,
		"ancestors": [14, 4, 27],
		"next_forms": [81, 86, 88],
		"lvl_transform": 24,
		"lvl_lay": [61, 50],
		"price": 0.07,
		"generation": 2
	},
	82: {
		"types": [13, 8],
		"stats": [83, 72, 78, 90, 87, 90],
		"steps": [2, 1, 2, 3, 2, 2],
		"is_gason": False,
		"ancestors": [14, 11, 16],
		"next_forms": [77, 82],
		"lvl_lay": [-1, -1],
		"generation": 1,
		"transformed": True
	},
	83: {
		"types": [12, 5],
		"stats": [79, 85, 83, 60, 78, 83],
		"steps": [2, 2, 3, 1, 2, 2],
		"is_gason": False,
		"ancestors": [19, 9, 28],
		"next_forms": [78, 83],
		"lvl_lay": [-1, -1],
		"generation": 2,
		"transformed": True
	},
	84: {
		"types": [14, 17],
		"stats": [66, 71, 71, 57, 63, 53],
		"steps": [2, 2, 2, 1, 2, 1],
		"is_gason": False,
		"ancestors": [24, 32, 13],
		"next_forms": [79, 84, 87],
		"lvl_transform": 38,
		"lvl_lay": [-1, -1],
		"generation": 2,
		"transformed": True
	},
	85: {
		"types": [1, 9],
		"stats": [67, 78, 90, 79, 74, 85],
		"steps": [2, 2, 3, 1, 2, 2],
		"is_gason": False,
		"ancestors": [18, 29, 16],
		"next_forms": [80, 85],
		"lvl_lay": [-1, -1],
		"generation": 2,
		"transformed": True
	},
	86: {
		"types": [5, 6],
		"stats": [68, 66, 60, 77, 60, 73],
		"steps": [2, 2, 1, 2, 1, 2],
		"is_gason": False,
		"ancestors": [14, 27, 4],
		"next_forms": [81, 86, 88],
		"lvl_transform": 41,
		"lvl_lay": [-1, -1],
		"generation": 2,
		"transformed": True
	},
	87: {
		"types": [14, 17],
		"stats": [82, 88, 88, 71, 78, 66],
		"steps": [2, 3, 2, 2, 2, 2],
		"is_gason": False,
		"ancestors": [24, 32, 13],
		"next_forms": [79, 84, 87],
		"lvl_lay": [-1, -1],
		"generation": 2,
		"transformed": True
	},
	88: {
		"types": [5, 6],
		"stats": [85, 82, 75, 96, 75, 91],
		"steps": [2, 2, 2, 3, 2, 2],
		"is_gason": False,
		"ancestors": [14, 27, 4],
		"next_forms": [81, 86, 88],
		"lvl_lay": [-1, -1],
		"generation": 2,
		"transformed": True
	},
	89: {
		"types": [14, 7],
		"stats": [150, 162, 94, 89, 95, 67],
		"steps": [1, 1, 2, 2, 2, 2],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [24, 89, 158],
		"generation": 0,
		"lvl_transform": 42,
		"transformed": True
	},
	90: {
		"types": [4, 12],
		"stats": [58, 68, 58, 58, 58, 68],
		"steps": [1, 2, 2, 1, 2, 1],
		"is_gason": False,
		"ancestors": [25, 26, 54],
		"next_forms": [90, 91, 92],
		"lvl_transform": 28,
		"price": 0.5,
		"generation": 2
	},
	91: {
		"types": [4, 12],
		"stats": [72, 85, 72, 72, 72, 72],
		"steps": [2, 2, 2, 1, 2, 1],
		"is_gason": False,
		"ancestors": [25, 26, 54],
		"next_forms": [90, 91, 92],
		"lvl_transform": 38,
		"lvl_lay": [-1, -1],
		"generation": 2,
		"transformed": True
	},
	92: {
		"types": [4, 12],
		"stats": [90, 106, 90, 90, 90, 90],
		"steps": [2, 3, 3, 1, 2, 2],
		"is_gason": False,
		"ancestors": [25, 26, 54],
		"next_forms": [90, 91, 92],
		"lvl_lay": [-1, -1],
		"generation": 2,
		"transformed": True
	},
	93: {
		"types": [15, 7],
		"stats": [58, 58, 58, 68, 58, 68],
		"steps": [1, 1, 2, 2, 2, 1],
		"is_gason": False,
		"ancestors": [26, 27, 52],
		"next_forms": [93, 94, 95],
		"lvl_transform": 28,
		"price": 0.5,
		"generation": 2
	},
	94: {
		"types": [15, 7],
		"stats": [72, 72, 72, 85, 72, 72],
		"steps": [2, 1, 2, 2, 2, 1],
		"is_gason": False,
		"ancestors": [26, 27, 52],
		"next_forms": [93, 94, 95],
		"lvl_transform": 38,
		"lvl_lay": [-1, -1],
		"generation": 2,
		"transformed": True
	},
	95: {
		"types": [15, 7],
		"stats": [90, 90, 90, 106, 90, 90],
		"steps": [2, 1, 2, 3, 3, 2],
		"is_gason": False,
		"ancestors": [26, 27, 52],
		"next_forms": [93, 94, 95],
		"lvl_lay": [-1, -1],
		"generation": 2,
		"transformed": True
	},
	96: {
		"types": [6],
		"stats": [50, 20, 60, 20, 60, 50],
		"steps": [1, 1, 2, 1, 2, 2],
		"is_gason": True,
		"ancestors": [],
		"price": 0.03,
		"generation": 0
	},
	97: {
		"types": [6],
		"stats": [61, 70, 67, 47, 68, 45],
		"steps": [1, 2, 2, 1, 2, 1],
		"is_gason": False,
		"ancestors": [32, 81, 37],
		"next_forms": [97, 98],
		"lvl_transform": 32,
		"lvl_lay": [61, 50],
		"price": 0.09,
		"generation": 3
	},
	98: {
		"types": [6, 9],
		"stats": [83, 95, 91, 64, 91, 61],
		"steps": [2, 3, 2, 1, 2, 2],
		"is_gason": False,
		"ancestors": [32, 81, 37],
		"next_forms": [97, 98],
		"lvl_lay": [-1, -1],
		"generation": 3,
		"transformed": True
	},
	99: {
		"types": [16, 12],
		"stats": [50, 46, 66, 73, 66, 66],
		"steps": [1, 1, 1, 2, 2, 2],
		"is_gason": False,
		"ancestors": [31, 28, 78],
		"next_forms": [99, 100],
		"lvl_transform": 30,
		"lvl_lay": [71, 25],
		"price": 0.12,
		"generation": 3
	},
	100: {
		"types": [16, 12],
		"stats": [67, 62, 89, 99, 89, 99],
		"steps": [2, 1, 2, 3, 2, 2],
		"is_gason": False,
		"ancestors": [31, 28, 78],
		"next_forms": [99, 100],
		"lvl_lay": [-1, -1],
		"generation": 3,
		"transformed": True
	},
	101: {
		"types": [7, 13],
		"stats": [57, 63, 52, 55, 65, 70],
		"steps": [1, 2, 1, 1, 2, 2],
		"is_gason": False,
		"ancestors": [77, 93, 32],
		"next_forms": [101, 102],
		"lvl_transform": 31,
		"lvl_lay": [-1, -1],
		"generation": 3
	},
	102: {
		"types": [7, 13],
		"stats": [77, 85, 70, 74, 87, 94],
		"steps": [2, 2, 1, 1, 3, 3],
		"is_gason": False,
		"ancestors": [77, 93, 32],
		"next_forms": [101, 102],
		"lvl_lay": [-1, -1],
		"generation": 3
	},
	103: {
		"types": [4, 6],
		"stats": [66, 64, 56, 65, 57, 66],
		"steps": [2, 2, 1, 2, 1, 1],
		"is_gason": False,
		"ancestors": [90, 81, 79],
		"next_forms": [103, 104],
		"lvl_transform": 30,
		"lvl_lay": [-1, -1],
		"generation": 3
	},
	104: {
		"types": [4, 6],
		"stats": [89, 83, 75, 87, 76, 89],
		"steps": [2, 3, 1, 3, 1, 2],
		"is_gason": False,
		"ancestors": [90, 81, 79],
		"next_forms": [103, 104],
		"lvl_lay": [-1, -1],
		"generation": 3
	},
	105: {
		"types": [15],
		"stats": [50, 20, 60, 20, 60, 50],
		"steps": [1, 1, 2, 1, 2, 2],
		"is_gason": True,
		"ancestors": [],
		"price": 0.03,
		"generation": 0
	},
	106: {
		"types": [14, 6],
		"stats": [61, 68, 36, 43, 76, 36],
		"steps": [1, 2, 2, 1, 2, 1],
		"is_gason": False,
		"ancestors": [79, 97, 25],
		"next_forms": [106, 107, 108],
		"lvl_transform": 31,
		"lvl_lay": [71, 30],
		"price": 0.13
	},
	107: {
		"types": [14, 6],
		"stats": [77, 85, 45, 53, 95, 45],
		"steps": [2, 2, 2, 1, 2, 1],
		"is_gason": False,
		"ancestors": [79, 97, 25],
		"next_forms": [106, 107, 108],
		"lvl_transform": 43,
		"lvl_lay": [-1, -1],
		"transformed": True
	},
	108: {
		"types": [14, 6],
		"stats": [96, 106, 56, 66, 119, 56],
		"steps": [2, 2, 2, 2, 3, 2],
		"is_gason": False,
		"ancestors": [79, 97, 25],
		"next_forms": [106, 107, 108],
		"lvl_lay": [-1, -1],
		"transformed": True
	},
	109: {
		"types": [8],
		"stats": [50, 20, 60, 20, 60, 50],
		"steps": [1, 1, 2, 1, 2, 2],
		"is_gason": True,
		"ancestors": []
	},
	110: {
		"types": [12],
		"stats": [50, 20, 60, 20, 60, 50],
		"steps": [1, 1, 2, 1, 2, 2],
		"is_gason": True,
		"ancestors": []
	},
	111: {
		"types": [1],
		"stats": [50, 20, 60, 20, 60, 50],
		"steps": [1, 1, 2, 1, 2, 2],
		"is_gason": True,
		"ancestors": []
	},
	112: {
		"types": [17],
		"stats": [50, 20, 60, 20, 60, 50],
		"steps": [1, 1, 2, 1, 2, 2],
		"is_gason": True,
		"ancestors": []
	},
	113: {
		"types": [2],
		"stats": [50, 20, 60, 20, 60, 50],
		"steps": [1, 1, 2, 1, 2, 2],
		"is_gason": True,
		"ancestors": []
	},
	114: {
		"types": [11],
		"stats": [50, 20, 60, 20, 60, 50],
		"steps": [1, 1, 2, 1, 2, 2],
		"is_gason": True,
		"ancestors": []
	},
	115: {
		"types": [7],
		"stats": [50, 20, 60, 20, 60, 50],
		"steps": [1, 1, 2, 1, 2, 2],
		"is_gason": True,
		"ancestors": []
	},
	116: {
		"types": [18, 9],
		"stats": [56, 56, 54, 55, 55, 52],
		"steps": [2, 1, 2, 2, 1, 1],
		"is_gason": False,
		"ancestors": [101, 34, 80],
		"next_forms": [116, 117, 118],
		"lvl_lay": [-1, -1],
		"lvl_transform": 27
	},
	117: {
		"types": [18, 9],
		"stats": [70, 70, 67, 68, 68, 64],
		"steps": [2, 2, 2, 2, 1, 2],
		"is_gason": False,
		"ancestors": [101, 34, 80],
		"next_forms": [116, 117, 118],
		"lvl_lay": [-1, -1],
		"lvl_transform": 37,
		"transformed": True
	},
	118: {
		"types": [18, 9],
		"stats": [87, 87, 83, 84, 85, 80],
		"steps": [2, 2, 3, 3, 1, 2],
		"is_gason": False,
		"ancestors": [101, 34, 80],
		"next_forms": [116, 117, 118],
		"lvl_lay": [-1, -1],
		"transformed": True
	},
	119: {
		"types": [1, 11],
		"stats": [48, 55, 48, 56, 61, 58],
		"steps": [2, 2, 1, 1, 2, 2],
		"is_gason": False,
		"ancestors": [28, 104, 80],
		"next_forms": [119, 120, 121],
		"lvl_lay": [-1, -1],
		"lvl_transform": 28
	},
	120: {
		"types": [1, 11],
		"stats": [60, 68, 60, 70, 76, 72],
		"steps": [2, 2, 2, 1, 2, 2],
		"is_gason": False,
		"ancestors": [28, 104, 80],
		"next_forms": [119, 120, 121],
		"lvl_lay": [-1, -1],
		"lvl_transform": 37,
		"transformed": True
	},
	121: {
		"types": [1, 11],
		"stats": [75, 85, 75, 87, 95, 89],
		"steps": [2, 2, 2, 2, 3, 2],
		"is_gason": False,
		"ancestors": [28, 104, 80],
		"next_forms": [119, 120, 121],
		"lvl_lay": [-1, -1],
		"transformed": True
	},
	122: {
		"types": [16, 9],
		"stats": [53, 52, 58, 52, 56, 52],
		"steps": [2, 1, 1, 2, 2, 2],
		"is_gason": False,
		"ancestors": [97, 106, 5],
		"next_forms": [122, 123, 124],
		"lvl_lay": [-1, -1],
		"lvl_transform": 29,
	},
	123: {
		"types": [16, 9],
		"stats": [66, 64, 72, 64, 69, 65],
		"steps": [2, 2, 1, 2, 2, 2],
		"is_gason": False,
		"ancestors": [97, 106, 5],
		"next_forms": [122, 123, 124],
		"lvl_lay": [-1, -1],
		"lvl_transform": 36,
		"transformed": True
	},
	124: {
		"types": [16, 9],
		"stats": [82, 80, 90, 80, 86, 81],
		"steps": [2, 2, 2, 2, 3, 2],
		"is_gason": False,
		"ancestors": [97, 106, 5],
		"next_forms": [122, 123, 124],
		"lvl_lay": [-1, -1],
		"transformed": True
	},
	125: {
		"types": [15, 17],
		"stats": [56, 55, 52, 50, 56, 60],
		"steps": [2, 2, 2, 1, 1, 2],
		"is_gason": False,
		"ancestors": [93, 79, 34],
		"next_forms": [125, 126, 127],
		"lvl_lay": [-1, -1],
		"lvl_transform": 26,
	},
	126: {
		"types": [15, 17],
		"stats": [69, 68, 64, 62, 70, 74],
		"steps": [2, 2, 2, 1, 2, 2],
		"is_gason": False,
		"ancestors": [34, 79, 93],
		"next_forms": [125, 126, 127],
		"lvl_lay": [-1, -1],
		"lvl_transform": 37,
		"transformed": True
	},
	127: {
		"types": [15, 17],
		"stats": [86, 84, 80, 77, 87, 92],
		"steps": [2, 2, 3, 1, 2, 3],
		"is_gason": False,
		"ancestors": [34, 79, 93],
		"next_forms": [125, 126, 127],
		"lvl_lay": [-1, -1],
		"transformed": True
	},
	128: {
		"types": [14, 12],
		"stats": [53, 60, 55, 56, 52, 52],
		"steps": [2, 2, 1, 2, 1, 2],
		"is_gason": False,
		"ancestors": [31, 99, 32],
		"next_forms": [128, 129, 130],
		"lvl_lay": [-1, -1],
		"lvl_transform": 26,
	},
	129: {
		"types": [14, 12],
		"stats": [66, 75, 68, 69, 64, 65],
		"steps": [2, 2, 2, 2, 1, 2],
		"is_gason": False,
		"ancestors": [31, 99, 32],
		"next_forms": [128, 129, 130],
		"lvl_lay": [-1, -1],
		"lvl_transform": 38,
		"transformed": True
	},
	130: {
		"types": [14, 12],
		"stats": [82, 93, 84, 86, 80, 81],
		"steps": [3, 3, 2, 2, 1, 2],
		"is_gason": False,
		"ancestors": [31, 99, 32],
		"next_forms": [128, 129, 130],
		"lvl_lay": [-1, -1],
		"transformed": True
	},
	131: {
		"types": [2, 4],
		"stats": [56, 57, 51, 57, 53, 54],
		"steps": [2, 2, 1, 1, 2, 2],
		"is_gason": False,
		"ancestors": [90, 97, 30],
		"next_forms": [131, 132, 133],
		"lvl_lay": [-1, -1],
		"lvl_transform": 27,
	},
	132: {
		"types": [2, 4],
		"stats": [70, 71, 63, 71, 66, 67],
		"steps": [2, 2, 2, 1, 2, 2],
		"is_gason": False,
		"ancestors": [90, 97, 30],
		"next_forms": [131, 132, 133],
		"lvl_lay": [-1, -1],
		"lvl_transform": 37,
		"transformed": True
	},
	133: {
		"types": [2, 4],
		"stats": [87, 88, 78, 88, 82, 83],
		"steps": [2, 2, 2, 1, 3, 3],
		"is_gason": False,
		"ancestors": [90, 97, 30],
		"next_forms": [131, 132, 133],
		"lvl_lay": [-1, -1],
		"transformed": True
	},
	134: {
		"types": [9, 3],
		"stats": [61, 57, 68, 64, 70, 64],
		"steps": [2, 2, 2, 2, 1, 2],
		"is_gason": False,
		"ancestors": [79, 7, 81],
		"next_forms": [134, 135],
		"lvl_lay": [-1, -1],
		"lvl_transform": 35,
	},
	135: {
		"types": [9, 3],
		"stats": [80, 75, 90, 85, 92, 84],
		"steps": [2, 2, 2, 3, 2, 2],
		"is_gason": False,
		"ancestors": [79, 7, 81],
		"next_forms": [134, 135],
		"lvl_lay": [-1, -1],
		"transformed": True
	},
	136: {
		"types": [1, 17],
		"stats": [70, 64, 60, 68, 60, 61],
		"steps": [2, 2, 2, 2, 1, 2],
		"is_gason": False,
		"ancestors": [80, 97, 79],
		"next_forms": [136, 137],
		"lvl_lay": [-1, -1],
		"lvl_transform": 36,
	},
	137: {
		"types": [1, 17],
		"stats": [93, 85, 79, 90, 79, 80],
		"steps": [2, 3, 2, 3, 1, 2],
		"is_gason": False,
		"ancestors": [80, 97, 79],
		"next_forms": [136, 137],
		"lvl_lay": [-1, -1],
		"transformed": True
	},
	138: {
		"types": [5, 11],
		"stats": [63, 70, 61, 60, 60, 70],
		"steps": [2, 2, 1, 2, 2, 2],
		"is_gason": False,
		"ancestors": [9, 81, 103],
		"next_forms": [138, 139],
		"lvl_lay": [-1, -1],
		"lvl_transform": 36,
	},
	139: {
		"types": [5, 11],
		"stats": [83, 93, 80, 79, 79, 92],
		"steps": [2, 3, 1, 2, 2, 3],
		"is_gason": False,
		"ancestors": [9, 81, 103],
		"next_forms": [138, 139],
		"lvl_lay": [-1, -1],
		"transformed": True
	},
	140: {
		"types": [3, 16],
		"stats": [62, 62, 61, 70, 64, 64],
		"steps": [2, 2, 1, 2, 2, 2],
		"is_gason": False,
		"ancestors": [33, 82, 5],
		"next_forms": [140, 141],
		"lvl_lay": [-1, -1],
		"lvl_transform": 35,
	},
	141: {
		"types": [3, 16],
		"stats": [82, 82, 81, 92, 85, 84],
		"steps": [2, 2, 2, 3, 2, 2],
		"is_gason": False,
		"ancestors": [33, 82, 5],
		"next_forms": [140, 141],
		"lvl_lay": [-1, -1],
		"transformed": True
	},
	142: {
		"types": [5, 13],
		"stats": [60, 63, 57, 72, 69, 63],
		"steps": [2, 2, 1, 2, 2, 2],
		"is_gason": False,
		"ancestors": [29, 101, 78],
		"next_forms": [142, 143],
		"lvl_lay": [-1, -1],
		"lvl_transform": 36,
	},
	143: {
		"types": [5, 13],
		"stats": [79, 83, 75, 95, 91, 83],
		"steps": [3, 2, 1, 3, 2, 2],
		"is_gason": False,
		"ancestors": [29, 101, 78],
		"next_forms": [142, 143],
		"lvl_lay": [-1, -1],
		"transformed": True
	},
	144: {
		"types": [1, 6],
		"stats": [64, 65, 63, 64, 64, 64],
		"steps": [2, 2, 2, 1, 2, 2],
		"is_gason": False,
		"ancestors": [34, 37, 79],
		"next_forms": [144, 145],
		"lvl_lay": [-1, -1],
		"lvl_transform": 34,
	},
	145: {
		"types": [1, 6],
		"stats": [84, 86, 83, 85, 84, 84],
		"steps": [2, 2, 2, 2, 2, 3],
		"is_gason": False,
		"ancestors": [34, 37, 79],
		"next_forms": [144, 145],
		"lvl_lay": [-1, -1],
		"transformed": True
	},
	146: {
		"types": [8, 12],
		"stats": [61, 70, 67, 61, 60, 65],
		"steps": [2, 2, 1, 2, 2, 2],
		"is_gason": False,
		"ancestors": [78, 29, 11],
		"next_forms": [146, 147],
		"lvl_lay": [-1, -1],
		"lvl_transform": 36,
	},
	147: {
		"types": [8, 12],
		"stats": [80, 92, 88, 81, 79, 86],
		"steps": [2, 3, 1, 3, 2, 2],
		"is_gason": False,
		"ancestors": [78, 29, 11],
		"next_forms": [146, 147],
		"lvl_lay": [-1, -1],
		"transformed": True
	},
	148: {
		"types": [2, 7],
		"stats": [56, 54, 56, 56, 56, 56],
		"steps": [2, 2, 2, 1, 1, 2],
		"is_gason": False,
		"ancestors": [33, 8, 30],
		"next_forms": [148, 149, 150],
		"lvl_lay": [-1, -1],
		"lvl_transform": 26,
	},
	149: {
		"types": [2, 7],
		"stats": [69, 67, 69, 70, 69, 70],
		"steps": [2, 2, 2, 2, 1, 2],
		"is_gason": False,
		"ancestors": [33, 8, 30],
		"next_forms": [148, 149, 150],
		"lvl_lay": [-1, -1],
		"lvl_transform": 37,
		"transformed": True
	},
	150: {
		"types": [2, 7],
		"stats": [86, 83, 86, 87, 86, 87],
		"steps": [2, 3, 2, 3, 1, 2],
		"is_gason": False,
		"ancestors": [33, 8, 30],
		"next_forms": [148, 149, 150],
		"lvl_lay": [-1, -1],
		"transformed": True
	},
	151: {
		"types": [14],
		"stats": [63, 63, 65, 64, 64, 64],
		"steps": [2, 2, 2, 1, 2, 2],
		"is_gason": False,
		"ancestors": [32, 79, 24],
		"next_forms": [151, 152],
		"lvl_lay": [-1, -1],
		"lvl_transform": 36,
	},
	152: {
		"types": [14],
		"stats": [83, 83, 86, 85, 84, 85],
		"steps": [2, 2, 3, 2, 2, 2],
		"is_gason": False,
		"ancestors": [32, 79, 24],
		"next_forms": [151, 152],
		"lvl_lay": [-1, -1],
		"transformed": True
	},
	153: {
		"types": [6, 17],
		"stats": [85, 87, 87, 86, 85, 83],
		"steps": [2, 2, 2, 3, 3, 2],
		"is_gason": False,
		"ancestors": [62, 87, 82],
		"lvl_lay": [-1, -1],
	},
	154: {
		"types": [8, 3],
		"stats": [82, 85, 78, 87, 85, 93],
		"steps": [2, 2, 3, 3, 2, 2],
		"is_gason": False,
		"ancestors": [89, 71, 70],
		"lvl_lay": [-1, -1],
	},
	155: {
		"types": [2, 5],
		"stats": [90, 98, 87, 95, 85, 88],
		"steps": [3, 2, 2, 2, 2, 3],
		"is_gason": False,
		"ancestors": [17, 57, 83],
		"lvl_lay": [-1, -1],
	},
	156: {
		"types": [9, 17],
		"stats": [67, 61, 68, 61, 61, 69],
		"steps": [2, 2, 2, 1, 2, 2],
		"is_gason": False,
		"ancestors": [97, 79, 80],
		"next_forms": [156, 157],
		"lvl_transform": 38,
		"price": 0.2
	},
	157: {
		"types": [9, 17],
		"stats": [89, 80, 90, 81, 80, 91],
		"steps": [2, 2, 3, 2, 2, 2],
		"is_gason": False,
		"ancestors": [97, 79, 80],
		"next_forms": [156, 157],
		"transformed": True
	},
	158: {
		"types": [7, 14],
		"stats": [100, 103, 94, 89, 95, 67],
		"steps": [3, 3, 2, 2, 1, 2],
		"is_gason": False,
		"ancestors": [],
		"next_forms": [24, 89, 158],
		"generation": 0,
		"transformed": True
	},
	159: {
		"types": [3, 14],
		"stats": [64, 70, 67, 72, 67, 91],
		"steps": [2, 2, 1, 2, 2, 2],
		"is_gason": False,
		"ancestors": [106, 77, 134],
		"next_forms": [159, 160],
		"lvl_transform": 30,
		"price": 0.3
	},
	160: {
		"types": [3, 14],
		"stats": [84, 92, 88, 95, 89, 120],
		"steps": [2, 2, 3, 2, 2, 3],
		"is_gason": False,
		"ancestors": [106, 77, 134],
		"next_forms": [159, 160],
		"generation": 5,
		"transformed": True
	},
	161: {
		"types": [6, 15],
		"stats": [71, 74, 67, 68, 60, 67],
		"steps": [2, 2, 2, 2, 1, 2],
		"is_gason": False,
		"ancestors": [144, 136, 125],
		"next_forms": [161, 162],
		"lvl_transform": 32,
	},
	162: {
		"types": [6, 15],
		"stats": [88, 92, 83, 84, 75, 83],
		"steps": [2, 3, 2, 2, 2, 2],
		"is_gason": False,
		"ancestors": [144, 136, 125],
		"next_forms": [161, 162],
		"transformed": True
	},
	163: {
		"types": [18, 1],
		"stats": [67, 68, 60, 75, 70, 60],
		"steps": [2, 2, 1, 2, 2, 2],
		"is_gason": False,
		"ancestors": [116, 140, 119],
		"next_forms": [163, 164],
		"lvl_transform": 33,
	},
	164: {
		"types": [18, 1],
		"stats": [83, 84, 75, 93, 87, 75],
		"steps": [2, 2, 2, 3, 2, 2],
		"is_gason": False,
		"ancestors": [116, 140, 119],
		"next_forms": [163, 164],
		"transformed": True
	},
	165: { #kumabaggu
    	"types": [9, 8],
    	"stats": [73, 74, 83, 75, 88, 79],
    	"steps": [2, 2, 2, 1, 2, 2],
    	"is_gason": False,
    	"ancestors": [122, 146, 156],
    	"lvl_lay": [-1, -1],
	},
	166: {
    	"types": [1, 17],
    	"stats": [61, 69, 68, 69, 69, 62],
    	"steps": [2, 2, 2, 1, 2, 2],
    	"is_gason": False,
    	"ancestors": [80, 136, 163],
    	"next_forms": [166, 167],
    	"lvl_transform": 40, #need for form 1
    	"lvl_lay": [-1, -1],
	},
	  167: {
	    "types": [1, 17],
	    "stats": [98, 88, 85, 81, 93, 86],
	    "steps": [2, 2, 2, 2, 3, 2],
	    "is_gason": False,
	    "ancestors": [80, 136, 163],
	    "next_forms": [166, 167],
	    "lvl_lay": [-1, -1],
	    "transformed": True #need for any transforms
	  },
  168: { #Foxeez
    "types": [15, 5],
    "stats": [68, 62, 61, 59, 56, 57],
    "steps": [1, 2, 2, 2, 2, 2],
    "is_gason": False,
    "ancestors": [138, 161, 33],
    "next_forms": [168, 169],
    "lvl_transform": 40,
    "lvl_lay": [-1, -1],
  },
  169: { #Coyoteez
    "types": [15, 5],
    "stats": [88, 87, 85, 91, 93, 90],
    "steps": [2, 2, 2, 3, 2, 2],
    "is_gason": False,
    "ancestors": [138, 161, 33],
    "next_forms": [168, 169],
    "lvl_lay": [-1, -1],
    "transformed": True
  },
  170: { #Roichirp (3 form)
    "types": [13],
    "stats": [57, 66, 69, 55, 65, 55],
    "steps": [1, 2, 1, 2, 2, 2],
    "is_gason": False,
    "ancestors": [101, 142, 16],
    "next_forms": [170, 171, 172],
    "lvl_transform": 30,
    "lvl_lay": [-1, -1],
  },
  171: { #Hawkrey
    "types": [13],
    "stats": [79, 78, 71, 76, 79, 74],
    "steps": [2, 2, 1, 2, 2, 2],
    "is_gason": False,
    "ancestors": [101, 142, 16],
    "next_forms": [170, 171, 172],
    "lvl_transform": 45,
    "lvl_lay": [-1, -1],
    "transformed": True
  },
  172: { #Emperazor
    "types": [13],
    "stats": [88, 99, 85, 92, 86, 96],
    "steps": [2, 2, 1, 3, 3, 2],
    "is_gason": False,
    "ancestors": [101, 142, 16],
    "next_forms": [170, 171, 172],
    "lvl_lay": [-1, -1],
    "transformed": True
  },
  173: { #Batflare (3 form)  BATFLARE IS technically BUGGED IN CONTRACT TYPES MISSING 13 (FLYER), so we don't add it here
    "types": [4],
    "stats": [59, 60, 63, 54, 63, 59],
    "steps": [1, 1, 1, 2, 2, 2],
    "is_gason": False,
    "ancestors": [131, 77, 10],
    "next_forms": [173, 174, 175],
    "lvl_transform": 30,
    "lvl_lay": [-1, -1],
  },
  174: { #Inferbat
    "types": [4, 13],
    "stats": [79, 77, 72, 71, 70, 76],
    "steps": [2, 2, 1, 2, 2, 2],
    "is_gason": False,
    "ancestors": [131, 77, 10],
    "next_forms": [173, 174, 175],
    "lvl_transform": 45,
    "lvl_lay": [-1, -1],
    "transformed": True
  },
  175: { #Zyracier
    "types": [4, 13],
    "stats": [89, 97, 86, 92, 90, 98],
    "steps": [3, 3, 1, 2, 2, 2],
    "is_gason": False,
    "ancestors": [131, 77, 10],
    "next_forms": [173, 174, 175],
    "lvl_lay": [-1, -1],
    "transformed": True
  },
  176: { #Watuber form1 (3 form) (8 stats)
    "types": [18, 12],
    "stats": [60, 69, 60, 54, 60, 59],
    "steps": [2, 2, 1, 2, 1, 2],
    "is_gason": False,
    "ancestors": [146, 116, 106],
    "next_forms": [176, 177, 178],
    "lvl_transform": 30,
    "lvl_lay": [-1, -1],
  },
  177: { #Floatuber form2 (9 stats)
    "types": [18, 12],
    "stats": [77, 74, 72, 75, 76, 72],
    "steps": [2, 2, 2, 2, 1, 2],
    "is_gason": False,
    "ancestors": [146, 116, 106],
    "next_forms": [176, 177, 178],
    "lvl_transform": 45,
    "lvl_lay": [-1, -1],
    "transformed": True
  },
  178: { #Chambrawl form3 (8 stats)
    "types": [18, 12],
    "stats": [86, 94, 104, 87, 92, 94],
    "steps": [2, 3, 3, 2, 1, 2],
    "is_gason": False,
    "ancestors": [146, 116, 106],
    "next_forms": [176, 177, 178],
    "lvl_lay": [-1, -1],
    "transformed": True
  },
  197: { #Vaudequin form1 of 1 Legendary (6 stats)
    "types": [4, 3],
    "stats": [109, 94, 97, 102, 99, 84],
    "steps": [3, 2, 2, 3, 2, 2],
    "is_gason": False,
    "ancestors": [159, 19, 10],
    "lvl_lay": [-1, -1],
  },
}

MONSTER_CLASS_STATS = {}
MONSTER_TYPES_TO_CLASSES = {}
MONSTER_FORMS_TO_CLASSES = {1: [], 2: [], 3: [], 4: []}
MONSTER_GENS_TO_CLASSES = {-1: [], 0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: []}


def _process_monster(_class_id, _info):
	if _class_id in MONSTER_CLASS_STATS:
		return

	if "ancestors" in _info and len(_info["ancestors"]):
		for a in _info["ancestors"]:
			_process_monster(a, _MONSTER_CLASS_STATS[a])

	# Check types
	for t in _info["types"]:
		if t not in MONSTER_TYPES_TO_CLASSES:
			MONSTER_TYPES_TO_CLASSES[t] = set()
		MONSTER_TYPES_TO_CLASSES[t].add(_class_id)

	# Check forms
	if "next_forms" not in _info:
		MONSTER_FORMS_TO_CLASSES[1].append(_class_id)
	else:
		MONSTER_FORMS_TO_CLASSES[_info["next_forms"].index(_class_id)+1].append(_class_id)

	# Update info
	MONSTER_CLASS_STATS[_class_id] = _info

	# Calculate gen
	gen = 0
	if "ancestors" in _info and len(_info["ancestors"]):
		gen = max(MONSTER_CLASS_STATS[a]["gen"] for a in _info["ancestors"]) + 1
	MONSTER_CLASS_STATS[_class_id]["gen"] = gen
	MONSTER_GENS_TO_CLASSES[gen].append(_class_id)
	if _info.get("is_gason", False):
		MONSTER_GENS_TO_CLASSES[-1].append(_class_id)


for _class_id, _info in _MONSTER_CLASS_STATS.items():
	_process_monster(_class_id, _info)


DUMMY_MONS = [-1, -2, -3]


FORBIDDEN_MONS = [21]
NEW_MONS = []


class MonLocations:
	STORE = 0
	ADVENTURE = 1
	EGG = 2