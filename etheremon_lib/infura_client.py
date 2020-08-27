from common.logger import log
from etheremon_lib.config import *
from web3 import Web3, HTTPProvider


class InfuraClient(object):

	def __init__(self, url):
		self.url = url
		self.web3_client = Web3(HTTPProvider(url))
		self.data_contract = None
		self.world_contract = None
		self.transform_contract = None
		self.transform_data_contract = None
		self.erc721_contract = None
		self.emont_contract = None
		self.rank_data_contract = None
		self.ladder_contract = None
		self.ladder_practice_contract = None
		self.rank_reward_contract = None
		self.trade_contract = None
		self.util_contract = None
		self.refer_contract = None

		self.energy_contract = None
		self.rank_battle_contract = None

		self.adventure_presale_contract = None
		self.adventure_item_contract = None

		self.adventure_explore_contract = None
		self.adventure_data_contract = None
		self.adventure_revenue_contract = None

		self.claim_reward_contract = None

	def getCurrentBlock(self):
		return self.web3_client.eth.blockNumber

	def getCurrentEthBalance(self, address):
		return self.web3_client.eth.getBalance(address)

	def getLatestBlockTime(self):
		return self.web3_client.eth.getBlock("latest")["timestamp"]

	def getDataContract(self):
		if self.data_contract is None:
			data_class = self.web3_client.eth.contract(abi=EtheremonDataContract.ABI)
			self.data_contract = data_class(EtheremonDataContract.ADDRESS)
		return self.data_contract

	def getWorldContract(self):
		if self.world_contract is None:
			world_class = self.web3_client.eth.contract(abi=EtheremonWorldContract.ABI)
			self.world_contract = world_class(EtheremonWorldContract.ADDRESS)
		return self.world_contract

	def getTransformDataContract(self):
		if self.transform_data_contract is None:
			transform_data_class = self.web3_client.eth.contract(abi=EtheremonTransformDataContract.ABI)
			self.transform_data_contract = transform_data_class(EtheremonTransformDataContract.ADDRESS)
		return self.transform_data_contract

	def getTransformContract(self):
		if self.transform_contract is None:
			transform_class = self.web3_client.eth.contract(abi=EtheremonTransformContract.ABI)
			self.transform_contract = transform_class(EtheremonTransformContract.ADDRESS)
		return self.transform_contract

	def getERC721Contract(self):
		if self.erc721_contract is None:
			erc721_class = self.web3_client.eth.contract(abi=EtheremonERC721Contract.ABI)
			self.erc721_contract = erc721_class(EtheremonERC721Contract.ADDRESS)
		return self.erc721_contract

	def getEmontContract(self):
		if self.emont_contract is None:
			emont_class = self.web3_client.eth.contract(abi=EtheremonEMONTContract.ABI)
			self.emont_contract = emont_class(EtheremonEMONTContract.ADDRESS)
		return self.emont_contract

	def getRankDataContract(self):
		if self.rank_data_contract is None:
			rank_data_class = self.web3_client.eth.contract(abi=EtheremonRankDataContract.ABI)
			self.rank_data_contract = rank_data_class(EtheremonRankDataContract.ADDRESS)
		return self.rank_data_contract

	def getLadderContract(self):
		if self.ladder_contract is None:
			ladder_class = self.web3_client.eth.contract(abi=EtheremonLadderContract.ABI)
			self.ladder_contract = ladder_class(EtheremonLadderContract.ADDRESS)
		return self.ladder_contract

	def getRankRewardContract(self):
		if self.rank_reward_contract is None:
			rank_reward_class = self.web3_client.eth.contract(abi=EtheremonRewardContract.ABI)
			self.rank_reward_contract = rank_reward_class(EtheremonRewardContract.ADDRESS)
		return self.rank_reward_contract

	def getTradeContract(self):
		if self.trade_contract is None:
			trade_class = self.web3_client.eth.contract(abi=EtheremonTradeContract.ABI)
			self.trade_contract = trade_class(EtheremonTradeContract.ADDRESS)
		return self.trade_contract

	def getUtilContract(self):
		if self.util_contract is None:
			util_class = self.web3_client.eth.contract(abi=EtheremonUtilsContract.ABI)
			self.util_contract = util_class(EtheremonUtilsContract.ADDRESS)
		return self.util_contract

	def getLadderPracticeContract(self):
		if self.ladder_practice_contract is None:
			ladder_practice_class = self.web3_client.eth.contract(abi=EtheremonLadderPracticeContract.ABI)
			self.ladder_practice_contract = ladder_practice_class(EtheremonLadderPracticeContract.ADDRESS)
		return self.ladder_practice_contract

	def getReferContract(self):
		if self.refer_contract is None:
			refer_class = self.web3_client.eth.contract(abi=EtheremonReferContract.ABI)
			self.refer_contract = refer_class(EtheremonReferContract.ADDRESS)
		return self.refer_contract

	def getEnergyContract(self):
		if self.energy_contract is None:
			energy_class = self.web3_client.eth.contract(abi=EtheremonEnergyContract.ABI)
			self.energy_contract = energy_class(EtheremonEnergyContract.ADDRESS)
		return self.energy_contract

	def getRankBattleContract(self):
		if self.rank_battle_contract is None:
			rank_battle_contract_class = self.web3_client.eth.contract(abi=EtheremonRankBattleContract.ABI)
			self.rank_battle_contract = rank_battle_contract_class(EtheremonEnergyContract.ADDRESS)
		return self.rank_battle_contract

	def getAdventurePresaleContract(self):
		if self.adventure_presale_contract is None:
			adventure_presale_class = self.web3_client.eth.contract(abi=EtheremonAdventurePresaleContract.ABI)
			self.adventure_presale_contract = adventure_presale_class(EtheremonAdventurePresaleContract.ADDRESS)
		return self.adventure_presale_contract

	def getAdventureItemContract(self):
		if self.adventure_item_contract is None:
			adventure_item_class = self.web3_client.eth.contract(abi=EtheremonAdventureItemContract.ABI)
			self.adventure_item_contract = adventure_item_class(EtheremonAdventureItemContract.ADDRESS)
		return self.adventure_item_contract

	def getAdventureExploreContract(self):
		if self.adventure_explore_contract is None:
			adventure_explore_class = self.web3_client.eth.contract(abi=EtheremonAdventureExploreContract.ABI)
			self.adventure_explore_contract = adventure_explore_class(EtheremonAdventureExploreContract.ADDRESS)
		return self.adventure_explore_contract

	def getAdventureDataContract(self):
		if self.adventure_data_contract is None:
			adventure_data_class = self.web3_client.eth.contract(abi=EtheremonAdventureDataContract.ABI)
			self.adventure_data_contract = adventure_data_class(EtheremonAdventureDataContract.ADDRESS)
		return self.adventure_data_contract

	def getAdventureRevenueContract(self):
		if self.adventure_revenue_contract is None:
			adventure_revenue_class = self.web3_client.eth.contract(abi=EtheremonAdventureRevenueContract.ABI)
			self.adventure_revenue_contract = adventure_revenue_class(EtheremonAdventureRevenueContract.ADDRESS)
		return self.adventure_revenue_contract

	def getClaimRewardContract(self):
		if self.claim_reward_contract is None:
			claim_reward_class = self.web3_client.eth.contract(abi=EtheremonClaimRewardContract.ABI)
			self.claim_reward_contract = claim_reward_class(EtheremonClaimRewardContract.ADDRESS)
		return self.claim_reward_contract

	def getDapperUserContract(self, address):
		c_class = self.web3_client.eth.contract(abi=DapperUser.ABI)
		c_contract = c_class(address)
		return c_contract

infura_general_client = None


def get_general_infura_client():
	global infura_general_client
	if infura_general_client is None:
		infura_general_client = InfuraClient(INFURA_API_URLS["general"])
	return infura_general_client
