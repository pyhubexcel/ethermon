LEVEL_REQUIREMENT = None
MAX_LEVEL = 100

def gen_level_exp():
	global LEVEL_REQUIREMENT
	LEVEL_REQUIREMENT = {}
	level = 1
	requirement = 100
	sum = requirement
	while level <= MAX_LEVEL:
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

print get_level(16370)