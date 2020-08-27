# https://mainnet.infura.io/h2s5XPxRh0XcbzUvI53Q

import os
import sys
import random

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.append('../')

from web3 import Web3, HTTPProvider
from etheremon_lib import config


web3Client = None

def init_client():
	web3Client = Web3(HTTPProvider("https://mainnet.infura.io/h2s5XPxRh0XcbzUvI53Q"))
	energy_contract = web3Client.eth.contract(abi=config.EtheremonEnergyContract.ABI, address=config.EtheremonEnergyContract.ADDRESS)
	(free_amount, paid_amount, last_claim) = energy_contract.call().getPlayerEnergy("0x088e25e6027816c753d01d7f243c367710f20497")
	print "free_amount:", free_amount, ", paid_amount:", paid_amount, ",last_claim: ", last_claim
	print "current_block:", web3Client.eth.blockNumber
	# get event
	'''
	ladder_contract = web3Client.eth.contract(abi=config.EtheremonLadderContract.ABI, address=config.EtheremonLadderContract.ADDRESS)
	event_filter = ladder_contract.events.EventUpdateEnegery.createFilter(fromBlock=0)
	'''


init_client()

