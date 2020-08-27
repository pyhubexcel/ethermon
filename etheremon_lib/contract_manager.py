from common.logger import log
from common.utils import get_timestamp
from common.config import *
from web3 import Web3, KeepAliveRPCProvider

from etheremon_lib import crypt
from etheremon_lib.infura_client import InfuraClient
from etheremon_lib.private_config import OWNER_PRIVATE_KEY, OWNER_PASSPHRASE, OWNER_ADDRESS
from common.utils import *

web3_client = None

# if web3_client is None:
# 	web3_client = Web3(KeepAliveRPCProvider(host=GETH_SERVER['host'], port=GETH_SERVER['port']))
# 	try:
# 		web3_client.personal.importRawKey(OWNER_PRIVATE_KEY, OWNER_PASSPHRASE)
# 	except ValueError:
# 		pass
# 	except:
# 		logging.exception("web3_init_fail|host=%s,port=%s", GETH_SERVER['host'], GETH_SERVER['port'])

# 	try:
# 		web3_client.personal.unlockAccount(OWNER_ADDRESS, OWNER_PASSPHRASE)
# 		web3_client.eth.defaultAccount = OWNER_ADDRESS
# 	except:
# 		logging.exception("web3_unlock_fail|host=%s,port=%s", GETH_SERVER['host'], GETH_SERVER['port'])

def unlock_account():
	try:
		web3_client.personal.unlockAccount(OWNER_ADDRESS, OWNER_PASSPHRASE)
	except:
		logging.exception("web3_unlock_fail|host=%s,port=%s", GETH_SERVER['host'], GETH_SERVER['port'])

def namehash(name):
	node = '0x0000000000000000000000000000000000000000000000000000000000000000'
	if name != '':
		labels = name.split(".")
		for i in xrange(len(labels) - 1, -1, -1):
			node = web3_hash((node + web3_hash(labels[i])[2:])[2:].decode("hex"))
	return str(node)

def sign_message(msg):
	signature = web3_client.eth.sign(OWNER_ADDRESS, str(msg))
	r = signature[0:66]
	s = "0x" + signature[66:130]
	v = int("0x" + signature[130:132], 16)
	return r, s, v

def sign_practice(pt, et):
	unlock_account()
	value = hex(long(Web3.sha3(pt), 16) ^ long(Web3.sha3(et), 16))
	if value[-1] == 'L':
		value = value[:-1]
	value = value[2:]
	if len(value) < 64:
		value = '0' * (64 - len(value)) + value
	try:
		value = value.decode("hex")
	except:
		logging.exception("decode_hex_value_fail|pt=%s,et=%s,value=%s", pt, et, value)
		return None
	return sign_message(value)

def sign_ladder(t1, t2, t3):
	unlock_account()
	value = hex(long(Web3.sha3(t1), 16) ^ long(Web3.sha3(t2), 16) ^ long(Web3.sha3(t3), 16))
	if value[-1] == 'L':
		value = value[:-1]
	value = value[2:]
	if len(value) < 64:
		value = '0' * (64 - len(value)) + value
	try:
		value = value.decode("hex")
	except:
		logging.exception("decode_hex_value_fail|t1=%s,t2=%s,t3=%s,value=%s", t1, t2, t3, value)
		return None
	return sign_message(value)

def sign_rank_claim(token):
	unlock_account()
	return sign_message(token.decode("hex"))

def sign_refer_claim(token, address):
	unlock_account()
	address = address[2:]
	value = hex(long(Web3.sha3(token), 16) ^ long(Web3.sha3(address), 16))
	if value[-1] == 'L':
		value = value[:-1]
	value = value[2:]
	if len(value) < 64:
		value = '0' * (64 - len(value)) + value
	try:
		value = value.decode("hex")
	except:
		logging.exception("decode_hex_value_fail|t1=%s,t2=%s,t3=%s,value=%s", t1, t2, t3, value)
		return None
	return sign_message(value)


def sign_claim_reward(token, address):
	unlock_account()
	address = address[2:]
	infura_client = InfuraClient(INFURA_API_URLS["static_methods"])
	claim_reward_contract = infura_client.getClaimRewardContract()
	hashed_message = claim_reward_contract.call().getVerifySignature("0x"+address, Web3.toBytes(hexstr="0x"+token))

	try:
		hashed_message = hashed_message.encode("latin1")
		return sign_message(hashed_message)
	except:
		logging.exception("decode_hex_value_fail|token=%s,address=%s,value=%s", token, address, hashed_message)
		return None


def sign_single_token(token):
	unlock_account()
	return sign_message(token.decode("hex"))


def generate_claim_reward_signature(trainer_address, txn_id, reward_type, reward_value):
	current_ts = get_timestamp()
	claim_reward_token = crypt.create_claim_reward_token(txn_id, reward_type, reward_value, current_ts)
	r, s, v = sign_claim_reward(claim_reward_token, trainer_address)
	return {
		"r": r,
		"s": s,
		"v": v,
		"address": trainer_address,
		"txn_id": txn_id,
		"reward_type": reward_type,
		"reward_value": reward_value
	}
