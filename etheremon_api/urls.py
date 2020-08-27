from django.conf.urls import include, url

from etheremon_api.views import lucky_draw_api, dex_api, tournament_api, general_battle_api
from etheremon_api.views import auth_api, general_api, user_api, trading_api, monster_api, ema_battle, adventure_api, quest_api, stats_api, store_api,player_api, ema_battle_api, dcl_api , finance_graph,datadownload

import debug_toolbar


urlpatterns = [
	url(r'^__debug__/', include(debug_toolbar.urls)),

	url(r'^api/auth/get_user_session', auth_api.get_user_session),
	url(r'^api/auth/sign_in', auth_api.sign_in),
	url(r'^api/auth/sign_out', auth_api.sign_out),
	url(r'^api/auth/test_api', auth_api.test_api),

	url(r'^api/general/get_type_metadata', general_api.get_type_metadata),
	url(r'^api/general/get_class_metadata', general_api.get_class_metadata),

	# users
	url(r'^api/user/get_info', user_api.get_info),
	url(r'^api/user/update_info', user_api.update_info),
	url(r'^api/user/subscribe', user_api.subscribe),
	url(r'^api/user/qr', user_api.qr_code),

	url(r'^api/user/claim_refer_reward', user_api.cash_out_in_game_emont),
	url(r'^api/user/claim_reward', user_api.claim_reward),
	url(r'^api/user/get_rewards', user_api.get_rewards),

	# Market
	url(r'^api/trading/get_sell_order_list', trading_api.get_sell_order_list),
	url(r'^api/trading/get_borrow_order_list', trading_api.get_borrow_order_list),
	url(r'^api/trading/get_lending_list', trading_api.get_lending_list),

	# Stats & Leader-board
	url(r'^api/stats/get_general_stats', stats_api.get_general_stats),
	url(r'^api/stats/get_new_player_count', stats_api.get_new_player_count),
	url(r'^api/stats/get_best_castle_builder', stats_api.get_best_castle_builder),
	url(r'^api/stats/get_best_castle', stats_api.get_best_castle),
	url(r'^api/stats/get_best_battler', stats_api.get_best_battler),
	url(r'^api/stats/get_best_monster', stats_api.get_best_monster),
	url(r'^api/stats/get_best_collector', stats_api.get_best_collector),
	url(r'^api/stats/get_best_player_rkt', stats_api.get_best_player_rkt),

	url(r'^api/stats/get_best_player', stats_api.get_best_player),
	url(r'^api/stats/get_latest_market_trades', stats_api.get_latest_market_trades),

	url(r'^api/stats/get_top_rank', stats_api.get_top_rank),

	url(r'^api/internal/get_battle_revenue', stats_api.get_best_collector),

	# Dex
	url(r'^api/dex/get_species', dex_api.get_species),
	url(r'^api/dex/get_monsters', dex_api.get_monsters),

	# Store
	url(r'^api/store/get_classes', store_api.get_classes),

	#finance graph
	url(r'^api/RevenueTxnTab/graph', finance_graph.FinanceGraph),
	url(r'^api/RevenueTxnTab/bycontract/graph', finance_graph.FinanceGraphByaddress),
	url(r'^api/RevenueMonsterTab/graph', finance_graph.RevenueMonsterTabGraph),


	#datadownloadapi
	url(r'^api/RevenueTxnTab/download', datadownload.RevenueTxnTabData),
	url(r'^api/RevenueTxnTab/bycontract/download', datadownload.RevenueTxnByaddress),
	url(r'^api/EmaEggDataTab/download', datadownload.EmaEggDataTabData),
	url(r'^api/RevenueMonsterTab/download', datadownload.RevenueMonsterTabData),


	#monster 
	url(r'^api/add_exp_to_mon', monster_api.add_exp_to_mon),

	# Off-chain
	url(r'^api/user/get_my_monster', user_api.get_my_monster),
	url(r'^api/user/get_sold_monster', user_api.get_sold_monster),
	url(r'^api/monster/get_data', monster_api.get_data),
	url(r'^api/monster/get_metadata', monster_api.get_metadata),

	url(r'^api/ema_battle/get_user_stats', ema_battle.get_user_stats),
	url(r'^api/ema_battle/set_rank_team_rkt', ema_battle.set_rank_team_rkt),
	url(r'^api/ema_battle/set_rank_team', ema_battle.set_rank_team),

	url(r'^api/ema_battle/get_rank_castles_rkt', ema_battle.get_rank_castles_rkt),
	url(r'^api/ema_battle/get_rank_castles', ema_battle.get_rank_castles),
	url(r'^api/ema_battle/attack_rank_castle', ema_battle.attack_rank_castle),
	url(r'^api/ema_battle/attack_rookie_tournament', ema_battle.attack_rookie_tournament),
	url(r'^api/ema_battle/get_rank_history_rkt', ema_battle.get_rank_history_rkt),
	url(r'^api/ema_battle/get_rank_history', ema_battle.get_rank_history),
	url(r'^api/ema_battle/get_rank_battle', ema_battle.get_rank_battle),
	#new rank battle added in 2019 by Idon
	url(r'^api/ema_battle/get_rank_battle_bp', ema_battle.get_rank_battle_bp),

	url(r'^api/ema_battle/get_practice_castles', ema_battle.get_practice_castles),
	url(r'^api/ema_battle/attack_practice_castle', ema_battle.attack_practice_castle),
	url(r'^api/ema_battle/get_practice_history', ema_battle.get_practice_history),

	url(r'^api/ema_battle/claim_monster_exp', ema_battle.claim_monster_exp),

	# Adventure
	url(r'^api/adventure/get_item_data', adventure_api.get_item_data),
	url(r'^api/adventure/get_item_metadata', adventure_api.get_item_metadata),
	url(r'^api/adventure/get_my_sites', adventure_api.get_my_sites),
	url(r'^api/adventure/get_my_items', adventure_api.get_my_adventure_items),
	url(r'^api/adventure/get_my_explores', adventure_api.get_my_explores),
	url(r'^api/adventure/get_pending_explore', adventure_api.get_adventure_pending_explore),
	url(r'^api/adventure/get_stats', adventure_api.get_adventure_stats),
	url(r'^api/adventure/vote', adventure_api.vote),
	url(r'^api/adventure/count_item', adventure_api.count_item),

	# Manual sync for user
	url(r'^api/user/sync_data', user_api.sync_data),

	# Quest
	url(r'^api/quest/get_quests', quest_api.get_player_quests),
	url(r'^api/quest/claim_quest', quest_api.claim_player_quest),
	url(r'^api/quest/claim_all', quest_api.claim_all_player_quests),

	# Event
	url(r'^api/lucky_draw/info', lucky_draw_api.get_lucky_draw_info),
	url(r'^api/lucky_draw/spin', lucky_draw_api.spin_lucky_wheel),
	# url(r'^api/event/lunar/claim_adventure', event_lunar_api.claim_adventure_hongbao)

	# Monster
	url(r'^api/monster/burn_request', monster_api.request_burn_mon),
	url(r'^api/monster/claim_offchain_mons', monster_api.claim_offchain_mons),

	# Tournament
	url(r'^api/tournament/get_info', tournament_api.get_tournament_info),
	url(r'^api/tournament/register_team', tournament_api.register_team),

	# General Battle
	url(r'^api/general_battle/get_info', general_battle_api.get_battle_info),

	# IP to Location
	url(r'^api/ip/get_info', general_api.get_ip_info),

	#player 
	url(r'^api/player/get_all_energy', player_api.get_all_energy),
	url(r'^api/player/get_energy', player_api.get_energy),

	url(r'^api/player/get_all_rank_data', player_api.get_all_rank_data),
	url(r'^api/player/get_rank_data', player_api.get_rank_data),

	url(r'^api/battle/get_all_battle', ema_battle_api.get_all_battle),
	url(r'^api/battle/get_battle', ema_battle_api.get_battle),

	#dcl
	#GET
	url(r'^api/dcl/item_class_config', dcl_api.get_item_class_config),
	url(r'^api/dcl/item_wip', dcl_api.get_item_wip),
	url(r'^api/dcl/ethermon_wild', dcl_api.get_ethermon_wild),
	url(r'^api/dcl/user_fungible', dcl_api.get_user_fungible),
	url(r'^api/dcl/monster_data', dcl_api.get_monster_data),
	#not used presently..as it is taken care by cron
	#url(r'^api/dcl/user_active_stats', dcl_api.get_user_active_stats),
	

	#POST		
	url(r'^api/dcl/purchase_callback', dcl_api.purchase_callback),

	url(r'^api/dcl/user_login', dcl_api.user_login),
	#url(r'^api/dcl/update_user_fungible_qty', dcl_api.update_user_fungible_qty),
	#plant
	url(r'^api/dcl/use_dcl_user_fungible', dcl_api.use_dcl_user_fungible),
	#eat
	url(r'^api/dcl/use_item_wip', dcl_api.use_item_wip),
	url(r'^api/dcl/put_mon_to_sleep', dcl_api.put_mon_to_sleep),
	

]
