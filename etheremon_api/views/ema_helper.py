from common.logger import log
from etheremon_lib.config import INFURA_API_URLS, ERC1271_MAGIC_VALUE
from etheremon_lib.infura_client import InfuraClient
from web3 import Web3


def _verify_signature(message, signature, sender):
	infura_client = InfuraClient(INFURA_API_URLS["verify_signature"])
	util_contract = infura_client.getUtilContract()
	try:
		if len(signature) < 132:
			return False
		elif len(signature) == 132:
			# Case metamask
			r = signature[0:66]
			s = "0x" + signature[66:130]
			v = int("0x" + signature[130:132], 16)
			# Specific case if using ecrecover, according to https://github.com/ethereum/wiki/wiki/JavaScript-API#web3ethsign
			if v in [0, 1]:
				v += 27

			# print(r, s, v)

			string_message = u'\u0019Ethereum Signed Message:\n%s%s' % (len(message), message)

			hash_message = Web3.sha3(hexstr=Web3.toHex(string_message))
			bytes_hash_message = Web3.toBytes(hexstr=hash_message.encode("latin1"))
			bytes_r = Web3.toBytes(hexstr=r)
			bytes_s = Web3.toBytes(hexstr=s)
			verify_address = util_contract.call().verifySignature(bytes_hash_message, v, bytes_r, bytes_s)

			return verify_address.lower() == sender

		else:

			# string_message = u'\u0019Ethereum Signed Message:\n%s%s' % (len(message), message)
			hash_message = Web3.sha3(hexstr=Web3.toHex(message)).encode("latin1")
			bytes_hash_message = Web3.toBytes(hexstr=hash_message.encode("latin1"))

			# Case Dapper
			erc1271_core_contract = infura_client.getDapperUserContract(sender)
			magic_value = erc1271_core_contract.call().isValidSignature(bytes_hash_message, Web3.toBytes(hexstr=signature))

			return "0x" + magic_value.encode("latin1").encode("hex") == ERC1271_MAGIC_VALUE

	except:
		print("verify_signature_fail|message=%s,signature=%s,sender=%s", message, signature, sender)
		return False
