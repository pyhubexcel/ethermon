import os
import sys
import random

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('../')

from common.buffer_writer import BufferWriter
from common.buffer_reader import BufferReader
from web3 import Web3
'''
from etheremon_lib.contract_manager import *
from eth_utils import decode_hex

def sign_message(msg):
	print "hex=0x"+msg.encode("hex")
	signature = web3_client.eth.sign(OWNER_ADDRESS, str(msg))
	print "signature=%s" % signature
	r = signature[0:66]
	s = "0x" + signature[66:130]
	v = int("0x" + signature[130:132], 16)
	return r, s, v

def create_message(process_id, castle_id1, castle_id2, castle_id3, castle_id4, castle_id5, castle_id6, castle_id7):
	writer = BufferWriter('>')
	writer.add_uint32(process_id)
	writer.add_uint32(castle_id1)
	writer.add_uint32(castle_id2)
	writer.add_uint32(castle_id3)
	writer.add_uint32(castle_id4)
	writer.add_uint32(castle_id5)
	writer.add_uint32(castle_id6)
	writer.add_uint32(castle_id7)
	return writer.buffer


def test_string(msg):
	hash_op = Web3.sha3(text=msg)
	data = hash_op[2:].decode("hex")
	print sign_message(data)

def test_bin():
	print sign_message(create_message(1,2,3,4,5,6,7,8))

test_string("hello")
print "---"
print "---"
test_bin()
'''

def create_practice_pt(p_id, obj1, obj2, obj3, ran):
	writer = BufferWriter('>')
	writer.add_uint32(p_id)
	writer.add_uint64(obj1)
	writer.add_uint64(obj2)
	writer.add_uint64(obj3)
	writer.add_uint32(ran)
	return writer.buffer.encode('hex')

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

def sign_practice(pt, et):
	print Web3.sha3(pt)
	return hex(long(Web3.sha3(pt), 16) ^ long(Web3.sha3(et), 16))

'''
pt = create_practice_pt(1245, 22434546576576879, 123123123121333, 41234566767, 124501234)
et = create_practice_et(6, 7, 8, 9, 10, 11, 12, 13)
print "pt=", pt
print "et=", et
print sign_practice(pt, et)
'''

pt = "0x000000220000000000006d900000000000004d1a0000000000006da710f8f5c4"
et = "0x000001bd000002080000012f00000492000004800000048a0000048f00000490"

def sign_practice(pt, et):
	value = hex(long(Web3.sha3(pt), 16) ^ long(Web3.sha3(et), 16))
	return value
print sign_practice(pt, et)