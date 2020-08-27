# coding=utf-8
import csv

from common.utils import parse_params, log_request
from etheremon_lib.cache_manager import cache_set_json, cache_get_json
from etheremon_lib.ema_monster_manager import get_mon_info
from etheremon_lib.contract_manager import *
from etheremon_lib.form_schema import *
from etheremon_lib.models import EtheremonDB
from etheremon_lib.constants import *
from django.db.models import Q, Sum, Count, Min
from etheremon_lib import cache_manager, user_manager
from etheremon_lib import ema_player_manager
from etheremon_lib.monster_config import *
from  etheremon_api.views.helper import is_from_egg
from etheremon_lib.utils import *

import time

MAX_LEADERBOARD_ITEM = 1000


def get_general_stats(request):
	try:
		response_data = cache_manager.get_general_stats()
		if response_data is None:
			monster_count = EtheremonDB.EmaMonsterDataTab.objects.filter(~Q(trainer=EMPTY_ADDRESS)).count()
			trainer_count = EtheremonDB.EmaMonsterDataTab.objects.values('trainer').distinct().count()
			old_rank_data = 908587 
			battle_count = EtheremonDB.BattleLogTab.objects.count() + EtheremonDB.BattleLadderTab.objects.count() + \
						EtheremonDB.EmaRankBattleTab.objects.count() +	old_rank_data +	EtheremonDB.EmaPracticeBattleTab.objects.count()
			explore_count = EtheremonDB.EmaAdventureExploreTab.objects.count()
			# open_sea_stats = get_open_sea_total_volume()
			# market_sales = (EtheremonDB.MarketHistoryTab.objects.aggregate(Sum("price"))["price__sum"] or 0) * 1.0 / 1000000 + get_open_sea_total_volume()
			# market_count = EtheremonDB.MarketHistoryTab.objects.count() + open_sea_stats["items_sold"]
			response_data = {
				'monster_count': monster_count,
				'trainer_count': trainer_count,
				'battle_count': battle_count,
				'explore_count': explore_count,
				# 'total_market_sales': market_sales,
				# 'total_market_sold': market_count,
			}
			#cache_manager.set_general_stats(response_data)
		return api_response_result(request, ResultCode.SUCCESS, response_data)
	except Exception as ex:
		logging.exception("get_general_stats_fail|ex=%s", ex)
		return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": ex.message})


@log_request(max_response_length=50)
@parse_params(form=GetWithPagingSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
def get_best_castle_builder(request, data):
	try:
		page_id = data['page_id']
		page_size = data['page_size']
		builder_list = cache_manager.get_best_builder_list(page_id, page_size)
		if builder_list is None:
			builder_list = list(EtheremonDB.CastleTab.objects.all().values('owner_address').annotate(total_brick=Sum('brick_number')).order_by('-total_brick')[((page_id - 1) * page_size):(page_id * page_size)])
			cache_manager.set_best_builder_list(page_id, page_size, json.dumps(builder_list))
			for builder in builder_list:
				try:
					trainer = EtheremonDB.UserTab.objects.get(address=builder["owner_address"])
					builder["trainer_name"] = trainer.username
				except EtheremonDB.UserTab.DoesNotExist:
					continue
		else:
			builder_list = json.loads(builder_list)
		response_data = {
			'builder_list': builder_list
		}
		return api_response_result(request, ResultCode.SUCCESS, response_data)
	except Exception as ex:
		logging.exception("get_best_castle_builder_fail|ex=%s", ex)
		return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": ex.message})


@log_request(max_response_length=50)
@parse_params(form=GetWithPagingSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
def get_best_castle(request, data):
	try:
		page_id = data['page_id']
		page_size = data['page_size']
		castle_list = cache_manager.get_best_castle_list(page_id, page_size)
		if castle_list is None:
			castle_list = list(EtheremonDB.BattleLogTab.objects.filter(result=BattleResult.CASTLE_WIN).values('castle_id').annotate(total_win=Count('castle_id')).order_by('-total_win')[((page_id - 1) * page_size):(page_id * page_size)])
			castle_ids = [castle['castle_id'] for castle in castle_list]
			castle_details = EtheremonDB.CastleTab.objects.filter(castle_id__in=castle_ids)
			castle_id_map = {int(castle.castle_id): castle for castle in castle_details}
			log.data('castle_id_map|map=%s', castle_id_map)
			for castle in castle_list:
				castle['owner_address'] = castle_id_map[int(castle['castle_id'])].owner_address
				castle['brick_number'] = castle_id_map[int(castle['castle_id'])].brick_number
				try:
					castle['name'] = castle_id_map[int(castle['castle_id'])].name.encode("latin1").decode("utf8").strip()
				except Exception as e:
					castle['name'] = castle_id_map[int(castle['castle_id'])].name.strip()
					log.error('error_decoding|castle_id=%s, name=%s', castle['castle_id'], castle['name'])
				castle['create_time'] = castle_id_map[int(castle['castle_id'])].create_time
				try:
					trainer = EtheremonDB.UserTab.objects.get(address=castle["owner_address"])
					castle["trainer_name"] = trainer.username
				except EtheremonDB.UserTab.DoesNotExist:
					continue
			cache_manager.set_best_castle_list(page_id, page_size, json.dumps(castle_list))
		else:
			castle_list = json.loads(castle_list)
		response_data = {
			'castle_list': castle_list
		}
		return api_response_result(request, ResultCode.SUCCESS, response_data)
	except Exception as ex:
		logging.exception("get_best_castle_builder_fail|ex=%s", ex)
		return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": ex.message})


@log_request(max_response_length=50)
@parse_params(form=GetWithPagingSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
def get_best_battler(request, data):
	try:
		page_id = data['page_id']
		page_size = data['page_size']
		battler_list = cache_manager.get_best_battler_list(page_id, page_size)
		if battler_list is None:
			battler_list = list(EtheremonDB.BattleLogTab.objects.filter(result=BattleResult.CASTLE_LOSE).values('attacker_address').annotate(total_win=Count('attacker_address')).order_by('-total_win')[((page_id - 1) * page_size):(page_id * page_size)])
			battler_address_list = [battler['attacker_address'] for battler in battler_list]
			battler_records = EtheremonDB.BattleLogTab.objects.filter(attacker_address__in=battler_address_list).values('attacker_address').annotate(total_played=Count('attacker_address'))
			battler_id_map = {battler['attacker_address']: battler for battler in battler_records}
			for battler in battler_list:
				battler['total_played'] = battler_id_map[battler['attacker_address']]['total_played']
				try:
					trainer = EtheremonDB.UserTab.objects.get(address=battler["attacker_address"])
					battler["trainer_name"] = trainer.username
				except EtheremonDB.UserTab.DoesNotExist:
					continue
			cache_manager.set_best_battler_list(page_id, page_size, json.dumps(battler_list))
		else:
			battler_list = json.loads(battler_list)
		response_data = {
			'battler_list': battler_list
		}
		return api_response_result(request, ResultCode.SUCCESS, response_data)
	except Exception as ex:
		logging.exception("get_best_castle_builder_fail|ex=%s", ex)
		return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": ex.message})


@log_request(max_response_length=50)
@parse_params(form=GetWithPagingSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
def get_best_monster(request, data):
	try:
		page_id = data['page_id']
		page_size = data['page_size']
		best_mon_list = cache_manager.get_best_mon_list(page_id, page_size)
		if best_mon_list is None:
			best_mon_list = []

			monster_data_records = list(EtheremonDB.EmaMonsterDataTab.objects.filter(~Q(trainer=EMPTY_ADDRESS)).order_by('-bp')[((page_id - 1) * page_size):(page_id * page_size)])
			trainer_list = []
			for monster_data_record in monster_data_records:
				trainer_list.append(monster_data_record.trainer)

			trainer_user_records = EtheremonDB.UserTab.objects.filter(address__in=trainer_list).all()
			trainer_user_dict = {}
			for trainer_user_record in trainer_user_records:
				trainer_user_dict[trainer_user_record.address] = trainer_user_record

			for mon_record in monster_data_records:
				base_stats = [mon_record.b0, mon_record.b1, mon_record.b2, mon_record.b3, mon_record.b4, mon_record.b5]
				stats, bp, level = get_stats(mon_record.class_id, mon_record.exp, base_stats)

				# get trainer name
				trainer_name = ""
				trainer_user_record = trainer_user_dict.get(mon_record.trainer)
				if trainer_user_record:
					trainer_name = trainer_user_record.username

				item = {
					"monster_id": mon_record.monster_id,
					"class_id": mon_record.class_id,
					"name": mon_record.name,
					"owner_address": mon_record.trainer,
					"stats": stats,
					"bp": bp,
					"trainer_name": trainer_name,
					"monster_create_time": mon_record.create_time,
					"create_index": mon_record.create_index,
					"level": level
				}
				best_mon_list.append(item)
			cache_manager.set_best_mon_list(page_id, page_size, json.dumps(best_mon_list))
		else:
			best_mon_list = json.loads(best_mon_list)
		total_record = EtheremonDB.EmaMonsterDataTab.objects.filter(~Q(trainer=EMPTY_ADDRESS)).count()
		response_data = {
			'best_mon_list': best_mon_list,
			"total_record": total_record
		}
		return api_response_result(request, ResultCode.SUCCESS, response_data)
	except Exception as ex:
		logging.exception("get_best_castle_builder_fail|ex=%s", ex)
		return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": ex.message})


@log_request(max_response_length=50)
@parse_params(form=GetWithPagingSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
def get_best_collector(request, data):
	try:
		page_id = data['page_id']
		page_size = data['page_size']
		collector_list = cache_manager.get_best_collector_list(page_id, page_size)
		if collector_list is None:
			collector_list = list(EtheremonDB.EmaMonsterDataTab.objects.filter(~Q(trainer=EMPTY_ADDRESS)).values('trainer').annotate(class_count=Count('class_id', distinct=True)).order_by('-class_count')[((page_id - 1) * page_size):(page_id * page_size)])
			for collector in collector_list:
				collector["owner_address"] = collector["trainer"]
				trainer_info = EtheremonDB.UserTab.objects.filter(address=collector["trainer"]).first()
				if trainer_info:
					collector["trainer_name"] = trainer_info.username
			cache_manager.set_best_collector_list(page_id, page_size, json.dumps(collector_list))
		else:
			collector_list = json.loads(collector_list)
		total_record = EtheremonDB.EmaMonsterDataTab.objects.values('trainer').distinct().count()
		response_data = {
			'collector_list': collector_list,
			"total_record": total_record
		}
		return api_response_result(request, ResultCode.SUCCESS, response_data)
	except Exception as ex:
		logging.exception("get_best_castle_builder_fail|ex=%s", ex)
		return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": ex.message})


@log_request(max_response_length=50)
@parse_params(form=NewPlayerCountSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
def get_new_player_count(request, data):
	try:
		period = data.get('period_in_sec', 60 * 60)
		start_time = int(time.time()) - period
		new_mon_count = 0
		new_player_count = EtheremonDB.EmaMonsterDataTab.objects.values('trainer').annotate(first_buy_time=Min('create_time')).filter(first_buy_time__gte=start_time).count()
		all_mon = EtheremonDB.EmaMonsterDataTab.objects.filter(create_time__gte=start_time).all()
		total_earned = 0
		new_paid_player_count = 0
		for mon in all_mon:
			class_id = mon.class_id
			class_price = MONSTER_CLASS_STATS[int(class_id)].get("price", 0)
			if class_price > 0 and not is_from_egg(mon.monster_id):
				new_mon_count += 1
				log.info('class_price|id=%s,price=%s', class_id, class_price)
				mon_price = get_new_monster_price(class_price, int(mon.create_index))
				total_earned += mon_price
				prev_mons = EtheremonDB.EmaMonsterDataTab.objects.filter(trainer=mon.trainer, create_time__lt=mon.create_time).all()
				paid_before = False
				for prev_mon in prev_mons:
					class_price_prev = MONSTER_CLASS_STATS[int(prev_mon.class_id)].get("price", 0)
					if class_price_prev> 0:
						paid_before = True
						break
				if not paid_before:
					new_paid_player_count += 1
		
		new_player_stats = {
			'new_non_free_mon_count': new_mon_count,
			'new_player_count': new_player_count,
			'new_paid_player_count': new_paid_player_count,
			'total_income': total_earned
		}
		response_data = new_player_stats
		return api_response_result(request, ResultCode.SUCCESS, response_data)
	except Exception as ex:
		logging.exception("get_best_castle_builder_fail|ex=%s", ex)
		return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": ex.message})


@log_request(max_response_length=50)
@parse_params(form=GetWithPagingSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
def get_best_player(request, data):
	page_id = data['page_id']
	page_size = data['page_size']
	start_index = (page_id - 1) * page_size
	to_index = page_id * page_size

	total_record = ema_player_manager.count_total_rank()
	player_records = ema_player_manager.get_rank_data_list(start_index, to_index)

	response_data = []
	for player_record in player_records:
		monster_ids = [player_record.a0, player_record.a1, player_record.a2, player_record.s0, player_record.s1, player_record.s2]
		monster_info = [get_mon_info(mon_id) for mon_id in monster_ids]

		response_data.append({
			"username": user_manager.get_user_name(player_record.trainer),
			"address": player_record.trainer,
			"point": player_record.point,
			"monster_info": monster_info,
			"total_win": player_record.total_win,
			"total_lose": player_record.total_lose,
			"total_match": player_record.total_win + player_record.total_lose
		})

	return api_response_result(request, ResultCode.SUCCESS, {"best_players": response_data, "total_record": total_record})




@log_request(max_response_length=50)
@parse_params(form=GetWithPagingSchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
def get_best_player_rkt(request, data):
	page_id = data['page_id']
	page_size = data['page_size']
	start_index = (page_id - 1) * page_size
	to_index = page_id * page_size

	total_record = ema_player_manager.count_total_rank()
	player_records = ema_player_manager.get_rank_data_list_rkt(start_index, to_index)

	response_data = []
	for player_record in player_records:
		monster_ids = [player_record.a0, player_record.a1, player_record.a2, player_record.s0, player_record.s1, player_record.s2]
		monster_info = [get_mon_info(mon_id) for mon_id in monster_ids]

		response_data.append({
			"username": user_manager.get_user_name(player_record.trainer),
			"address": player_record.trainer,
			"point": player_record.point,
			"monster_info": monster_info,
			"total_win": player_record.total_win,
			"total_lose": player_record.total_lose,
			"total_match": player_record.total_win + player_record.total_lose
		})

	return api_response_result(request, ResultCode.SUCCESS, {"best_players": response_data, "total_record": total_record})


@log_request(max_response_length=50)
@parse_params(form=GetMarketHistorySchema, method='GET', data_format='FORM', error_handler=api_response_error_params)
def get_latest_market_trades(request, data):
	page_id = data['page_id']
	page_size = data['page_size']
	class_id = data.get('class_id', 0)
	sort_by = data.get('sort_by')
	if not sort_by:
		sort_by = 'buy_time'

	market_count = cache_manager.get_market_history_count()
	if market_count is None:
		market_count = EtheremonDB.MarketHistoryTab.objects.all().filter(is_sold=True).count()
		cache_manager.set_market_history_count(market_count)

	sold_mon_list = cache_manager.get_market_sales_history(page_id, page_size, class_id, sort_by)
	if sold_mon_list is None:
		sold_mon_list = EtheremonDB.MarketHistoryTab.objects.all().filter(is_sold=True)
		if class_id:
			sold_mon_list = sold_mon_list.filter(class_id=class_id)

		if sort_by == 'create_index':
			sold_mon_list = sold_mon_list.order_by('create_index')
		elif sort_by == 'base_bp':
			sold_mon_list = sold_mon_list.order_by('-base_bp')
		elif sort_by == 'price':
			sold_mon_list = sold_mon_list.order_by('-price')
		else:
			sold_mon_list = sold_mon_list.order_by('-buy_time')

		sold_mon_list = list(sold_mon_list[((page_id - 1) * page_size):(page_id * page_size)].values())

		for sold_item in sold_mon_list:
			sold_item["price"] = sold_item["price"] * 1.0 / 1000000
			mon = EtheremonDB.EmaMonsterDataTab.objects.filter(monster_id=sold_item["monster_id"]).first()
			if mon is None:
				continue

			class_id = mon.class_id
			sold_item['class_id'] = class_id
			sold_item['base_stats'] = [mon.b0, mon.b1, mon.b2, mon.b3, mon.b4, mon.b5]
			stats, bp, level = get_stats(mon.class_id, mon.exp, sold_item['base_stats'])

			sold_item['stats'] = stats
			sold_item['level'] = level
			sold_item['create_index'] = mon.create_index
			sold_item['name'] = mon.name

		cache_manager.set_market_sales_history(page_id, page_size, class_id, sort_by, sold_mon_list)
	return api_response_result(request, ResultCode.SUCCESS, {'total': market_count, 'sold_list': sold_mon_list })


@log_request(max_response_length=50)
@parse_params(form=GetTopRank, method='GET', data_format='FORM', error_handler=api_response_error_params)
def get_top_rank(request, data):
	data_res = cache_get_json("custom_cache_top_rank")
	if not data_res:
		start_time = 1552298400
		end_time = 1553248800

		all_matches = EtheremonDB.EmaRankBattleTab.objects.filter(create_time__gte=1548979200).filter(create_time__lte=end_time).order_by('id')

		player_info = {}
		points = []

		def update_player(player_id, new_point, ts):
			if player_id not in player_info:
				player_data = ema_player_manager.get_player_rank_by_id(player_id)
				if not player_data:
					return

				address = player_data.trainer
				name = user_manager.get_user_name(address)
				player_info[player_id] = {
					"name": name,
					"address": address,
					"point": -1,
					"rank": 0,
					"rank_info": {},
					"last_update": start_time,
				}

			old_point = player_info[player_id]["point"]
			player_info[player_id]["point"] = new_point

			if old_point >= 0:
				for i in range(len(points)):
					if points[i] == old_point:
						pos = i
						break
				# pos must exist
				points[pos] = new_point
			else:
				points.append(new_point)
				pos = len(points)-1

			cc = 0

			for i in range(pos, len(points)-1, 1):
				if points[i] <= points[i+1]:
					points[i], points[i+1] = points[i+1], points[i]
					cc += 1
				else:
					break

			for i in range(pos, 0, -1):
				if points[i] >= points[i-1]:
					points[i], points[i-1] = points[i-1], points[i]
					cc += 1
				else:
					break
			for pid, info in player_info.items():
				if (info["point"] - new_point) * (info["point"] - old_point) <= 0:
					new_rank = cal_rank(points, info["point"])
					new_update = max(info["last_update"], ts)

					old_rank = info["rank"]
					last_update = info["last_update"]
					if old_rank <= 10:
						info["rank_info"][old_rank] = info["rank_info"].get(old_rank, 0) + new_update - last_update

					info["rank"] = new_rank
					info["last_update"] = new_update

		def cal_rank(a, val):
			left, right = 0, len(a)-1
			while left+1 < right:
				m = (left + right) / 2
				if a[m] >= val:
					left = m
				else:
					right = m-1
			if a[right] >= val:
				return right + 1
			if a[left] >= val:
				return left + 1
			return 0

		for match in all_matches:
			update_player(match.attacker_id, match.attacker_after_point, match.create_time)
			update_player(match.defender_id, match.defender_after_point, match.create_time)

		for _, inf in player_info.items():
			inf["rank_info"][inf["rank"]] = inf["rank_info"].get(inf["rank"], 0) + max(0, end_time - inf["last_update"])

		data_res = []
		for _, inf in player_info.items():
			res = [inf["name"].encode('ascii', 'ignore').decode('ascii'), inf["address"], inf["rank_info"].get(1, 0), inf["rank_info"].get(2, 0), inf["rank_info"].get(3, 0), inf["rank_info"].get(4, 0), inf["rank_info"].get(5, 0)]
			if sum(res[3:]) > 0:
				data_res.append(res)

		for _, inf in player_info.items():
			res = [inf["name"].encode('ascii', 'ignore').decode('ascii'), inf["address"], inf["rank"]]
			data_res.append(res)

		cache_set_json("custom_cache_top_rank", data_res, 1*60*60)		# 1 hour

	# Create the HttpResponse object with the appropriate CSV header.
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename=rank.csv'
	writer = csv.writer(response)
	for row in data_res:
		writer.writerow(row)

	return response
