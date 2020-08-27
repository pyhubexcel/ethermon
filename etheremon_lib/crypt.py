from common.buffer_writer import BufferWriter
from common.buffer_reader import BufferReader
from common.logger import log

def encrypt_refer_code(uid, address):
	return "%s%04d" % (address[2:5], uid)

def decrypt_refer_code(refer_code):
	if not refer_code or len(refer_code) < 4:
		return 0
	return int(refer_code[3:])

def create_practice_pt(p_id, obj1, obj2, obj3, ran):
	writer = BufferWriter('>')
	writer.add_uint32(p_id)
	writer.add_uint64(obj1)
	writer.add_uint64(obj2)
	writer.add_uint64(obj3)
	writer.add_uint32(ran)
	return writer.buffer.encode('hex')

def decode_practice_pt(token):
	reader = BufferReader(token, '>')
	p_id = reader.get_uint32()
	obj1 = reader.get_uint64()
	obj2 = reader.get_uint64()
	obj3 = reader.get_uint64()
	ran = reader.get_uint32()
	return {"p_id": p_id, "obj1": obj1, "obj2": obj2, "obj3": obj3, "ran": ran}

def create_practice_et(exp1, exp2, exp3, c1, c2, c3, c4, c5):
	writer = BufferWriter('>')
	writer.add_uint32(exp1)
	writer.add_uint32(exp2)
	writer.add_uint32(exp3)
	writer.add_uint32(c1)
	writer.add_uint32(c2)
	writer.add_uint32(c3)
	writer.add_uint32(c4)
	writer.add_uint32(c5)
	return writer.buffer.encode('hex')

def create_ladder_token1(battle_id, aa0, aa1, aa2):
	writer = BufferWriter('>')
	writer.add_uint64(battle_id)
	writer.add_uint64(aa0)
	writer.add_uint64(aa1)
	writer.add_uint64(aa2)
	return writer.buffer.encode('hex')

def decode_ladder_token1(token):
	reader = BufferReader(token, '>')
	battle_id = reader.get_uint64()
	aa0 = reader.get_uint64()
	aa1 = reader.get_uint64()
	aa2 = reader.get_uint64()
	return {"battle_id": battle_id, "aa0": aa0, "aa1": aa1, "aa2": aa2}

def create_ladder_token2(da0, da1, da2, result, nonce):
	writer = BufferWriter('>')
	writer.add_uint64(da0)
	writer.add_uint64(da1)
	writer.add_uint64(da2)
	writer.add_uint32(result)
	writer.add_uint32(nonce)
	return writer.buffer.encode('hex')

def decode_ladder_token2(token):
	reader = BufferReader(token, '>')
	da0 = reader.get_uint64()
	da1 = reader.get_uint64()
	da2 = reader.get_uint64()
	result = reader.get_uint32()
	nonce = reader.get_uint32()
	return {"da0": da0, "da1": da1, "da2": da2, "result": result, "nonce": nonce}

def create_ladder_token3(attacker_id, defender_id, aa0Exp, aa1Exp, aa2Exp, da0Exp, da1Exp, da2Exp):
	writer = BufferWriter('>')
	writer.add_uint32(attacker_id)
	writer.add_uint32(defender_id)
	writer.add_uint32(aa0Exp)
	writer.add_uint32(aa1Exp)
	writer.add_uint32(aa2Exp)
	writer.add_uint32(da0Exp)
	writer.add_uint32(da1Exp)
	writer.add_uint32(da2Exp)
	return writer.buffer.encode('hex')

def create_claim_rank_token(claim_id, player_id, rank, create_time, point, point_range, nonce):
	writer = BufferWriter('>')
	writer.add_uint32(claim_id)
	writer.add_uint32(player_id)
	writer.add_uint32(rank)
	writer.add_uint32(create_time)
	writer.add_uint32(point)
	writer.add_uint32(point_range)
	writer.add_uint64(nonce)
	return writer.buffer.encode('hex')

def create_refer_reward_token(claim_id, uid, amount, create_time, nonce, random):
	writer = BufferWriter('>')
	writer.add_uint32(claim_id)
	writer.add_uint32(uid)
	writer.add_uint64(amount)
	writer.add_uint32(create_time)
	writer.add_uint32(nonce)
	writer.add_uint64(random)
	return writer.buffer.encode('hex')

def create_claim_exp_token(request_id, monster_id, exp, nonce1, nonce2):
	writer = BufferWriter('>')
	writer.add_uint64(request_id)
	writer.add_uint64(monster_id)
	writer.add_uint32(exp)
	writer.add_uint32(nonce1)
	writer.add_uint64(nonce2)
	return writer.buffer.encode('hex')

def decode_claim_exp_token(token):
	reader = BufferReader(token, '>')
	request_id = reader.get_uint64()
	monster_id = reader.get_uint64()
	exp = reader.get_uint32()
	nonce1 = reader.get_uint32()
	nonce2 = reader.get_uint64()
	return {"request_id": request_id, "monster_id": monster_id, "exp": exp, "nonce1": nonce1, "nonce2": nonce2}

def create_claim_win_token(request_id, amount, player_id, nonce1, nonce2):
	writer = BufferWriter('>')
	writer.add_uint64(request_id)
	writer.add_uint64(amount)
	writer.add_uint32(player_id)
	writer.add_uint32(nonce1)
	writer.add_uint64(nonce2)
	return writer.buffer.encode('hex')

def decode_claim_win_token(token):
	reader = BufferReader(token, '>')
	request_id = reader.get_uint64()
	amount = reader.get_uint64()
	player_id = reader.get_uint32()
	nonce1 = reader.get_uint32()
	nonce2 = reader.get_uint64()
	return {"request_id": request_id, "amount": amount, "player_id": player_id, "nonce1": nonce1, "nonce2": nonce2}

def create_claim_top_token(request_id, rank, player_id, nonce1, nonce2):
	writer = BufferWriter('>')
	writer.add_uint64(request_id)
	writer.add_uint32(rank)
	writer.add_uint32(player_id)
	writer.add_uint64(nonce1)
	writer.add_uint64(nonce2)
	return writer.buffer.encode('hex')

def decode_claim_top_token(token):
	reader = BufferReader(token, '>')
	request_id = reader.get_uint64()
	rank = reader.get_uint32()
	player_id = reader.get_uint32()
	nonce1 = reader.get_uint64()
	nonce2 = reader.get_uint64()
	return {"request_id": request_id, "rank": rank, "player_id": player_id, "nonce1": nonce1, "nonce2": nonce2}


def create_claim_reward_token(reward_txn_id, reward_type, reward_value, create_time, nonce1=0, nonce2=0):
	writer = BufferWriter('>')
	writer.add_uint32(reward_txn_id)
	writer.add_uint32(reward_type)
	writer.add_uint32(reward_value)
	writer.add_uint32(create_time)
	writer.add_uint64(nonce1)
	writer.add_uint64(nonce2)
	return writer.buffer.encode('hex')


def decode_claim_reward_token(token):
	reader = BufferReader(token, '>')
	reward_txn_id = reader.get_uint32()
	reward_type = reader.get_uint32()
	reward_value = reader.get_uint32()
	create_time = reader.get_uint32()
	return {"reward_id": reward_txn_id, "reward_type": reward_type, "reward_value": reward_value, "create_time": create_time}
