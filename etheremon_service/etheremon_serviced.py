import os
import sys
import time
import json
from django.core.wsgi import get_wsgi_application

curr_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(curr_dir)
sys.path.append(os.path.join(curr_dir, '../'))

import settings
from common import context
from common import crontask

context.init_django('.', 'settings')
application = get_wsgi_application()

from contract import cron_world_contract
from contract import cron_trade_contract
from contract import cron_exp_contract
from contract import cron_erc721_contract
from contract import cron_transform_contract

from contract import cron_energy_contract
from contract import cron_claim_contract
from contract import cron_erc20_contract
from contract import cron_adventure_nft_contract

from contract import cron_world_nft_contract
from contract import cron_adventure_explore
from contract import cron_adventure_revenue_contract
from contract import cron_kyber_contract

from contract import cron_claim_reward_contract
from contract import cron_burn_mon_contract

from contract import dcl_cron
from contract import free_energy_boost_cron
from contract import dcl_cron_free_food

from scripts import tournament

from etheremon_service.revenue_crawl import cal_txn


#from crawl import crawl_adventure_presale

#from crawl import crawl_egg

#from crawl import crawl_explore

from crawl import crawl_market_history

from crawl import crawl_market

from crawl import crawl_monster

from crawl import crawl_rank_data


UPDATE_CONTRACT_RANK = "*/20 * * * * *"
UPDATE_CONTRACT_WORLD = "*/20 * * * * *"
UPDATE_CONTRACT_TRADE = "*/20 * * * * *"
UPDATE_CONTRACT_EXP = "*/20 * * * * *"
UPDATE_CONTRACT_ERC721 = "*/20 * * * * *"
UPDATE_CONTRACT_TRANSFORM = "*/20 * * * * *"

UPDATE_CONTRACT_ENERGY = "*/20 * * * * *"
UPDATE_CONTRACT_CLAIM = "*/20 * * * * *"
UPDATE_CONTRACT_ERC20 = "*/20 * * * * *"

UPDATE_CONTRACT_ADVENTURE_ITEM = "*/20 * * * * *"
UPDATE_CONTRACT_WORD_NFT = "*/20 * * * * *"

UPDATE_CONTRACT_ADVENTURE_EXPLORE = "*/12 * * * * *"
UPDATE_CONTRACT_ADVENTURE_REVENUE = "*/12 * * * * *"

UPDATE_CONTRACT_KYBER = "*/18 * * * * *"

UPDATE_CONTRACT_CLAIM_REWARD = "*/25 * * * * *"

UPDATE_CONTRACT_BURN_MON = "*/23 * * * * *"


UPDATE_DCL_STATS = "0 */4 * * * *"
PLAYER_ENERGY_BOOST = "0 0 */12 * * *"
#FREE_FOOD_FOR_GARDENS = "0 0 */24 * * *"


if __name__ == "__main__":
	def main():
		crontask.register_task(PLAYER_ENERGY_BOOST, task=free_energy_boost_cron.free_energy)
		#crontask.register_task(FREE_FOOD_FOR_GARDENS, task=dcl_cron_free_food.update_free_food)
		crontask.register_task(UPDATE_DCL_STATS, task=dcl_cron.dcl_stats)
		crontask.register_task(UPDATE_CONTRACT_WORLD, task=cron_world_contract.update_world_contract)
		crontask.register_task(UPDATE_CONTRACT_TRADE, task=cron_trade_contract.update_trade_contract)
		crontask.register_task(UPDATE_CONTRACT_ERC721, task=cron_erc721_contract.update_erc721_contract)
		crontask.register_task(UPDATE_CONTRACT_EXP, task=cron_exp_contract.update_exp)
		crontask.register_task(UPDATE_CONTRACT_TRANSFORM, task=cron_transform_contract.update_transform_contract)
		crontask.register_task(UPDATE_CONTRACT_TRANSFORM, task=cron_transform_contract.update_internal_transform_contract)
		# crontask.register_task(UPDATE_CONTRACT_TRANSFORM, task=cron_transform_contract.update_lunar_egg_rebate)

		crontask.register_task(UPDATE_CONTRACT_ENERGY, task=cron_energy_contract.update_energy_contract)
		crontask.register_task(UPDATE_CONTRACT_CLAIM, task=cron_claim_contract.update_claim_contract)
		crontask.register_task(UPDATE_CONTRACT_ERC20, task=cron_erc20_contract.update_erc20_contract)
		crontask.register_task(UPDATE_CONTRACT_CLAIM_REWARD, task=cron_claim_reward_contract.update_claim_reward_contract)

		crontask.register_task(UPDATE_CONTRACT_ADVENTURE_ITEM, task=cron_adventure_nft_contract.update_adventure_nft_contract)
		crontask.register_task(UPDATE_CONTRACT_WORD_NFT, task=cron_world_nft_contract.update_worldnft_contract)

		crontask.register_task(UPDATE_CONTRACT_ADVENTURE_EXPLORE, task=cron_adventure_explore.update_adventure_contract)
		crontask.register_task(UPDATE_CONTRACT_ADVENTURE_REVENUE, task=cron_adventure_revenue_contract.update_adventure_revenue_contract)

		crontask.register_task(UPDATE_CONTRACT_KYBER, task=cron_kyber_contract.update_kyber_wrapper_contract)

		crontask.register_task(UPDATE_CONTRACT_BURN_MON, task=cron_burn_mon_contract.update_burn_mon_contract)

		crontask.register_task("0 59 7 * * 0,4", task=tournament.add_tournament)
		crontask.register_task("0 1 8 * * 2,6", task=tournament.start_tournaments)

	#	crontask.register_task("*/50 * * * *", task=crawl_adventure_presale.crawl_adventure_presale)

	#	crontask.register_task("*/30 * * * *", task=crawl_egg.crawl_monster_egg_data)
		#crontask.register_task("*/20 * * * *", task=crawl_egg.fix_bonus_egg)
		#crontask.register_task("*/40 * * * *", task=crawl_egg.fix_egg_info)

		#crontask.register_task("*/50 * * * *", task=crawl_explore.cron_run_setting)

		crontask.register_task("0 0 1 * *", task=cal_txn.call)
		#crontask.register_task("*/70 * * * *", task=crawl_market_history.craw_market_seller)

		#crontask.register_task("*/50 * * * *", task=crawl_market.crawl_market)
		# crontask.register_task("0 59 7 * * 0,4", task=crawl_market.fix_borrow_problem)

		# crontask.register_task("*/50 * * * *", task=crawl_monster.crawl_monster)
		# crontask.register_task("0 59 7 * * 0,4", task=crawl_monster.fix_stats_monster)

		# crontask.register_task("*/20 * * * * *", task=crawl_rank_data.crawl_rank_data)
		# crontask.register_task("*/25 * * * * *", task=crawl_rank_data.re_craw_energy)
		# crontask.register_task("0 59 7 * * 0,4", task=crawl_rank_data.clone_player_data)

		crontask.run()

	from common.daemon import Daemon
	Daemon(main, os.path.abspath(__file__).replace(".py", ".pid"), "./log/service_daemon.log").main()

