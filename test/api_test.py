import unittest
from test_common import *
from etheremon_lib.constants import *


class GeneralSmokeTest(unittest.TestCase):
	def setUp(self):
		pass

	def test_get_type_metadata(self):
		result_code, reply = request_service_api(API_GENERAL_GET_TYPE_METADATA, {}, "GET")
		self.assertEqual(result_code, ResultCode.SUCCESS)

	def test_get_class_metadata(self):
		result_code, reply = request_service_api(API_GENERAL_GET_CLASS_METADATA, {"class_ids": "1,2"}, "GET")
		self.assertEqual(result_code, ResultCode.SUCCESS)


class MonsterSmokeTest(unittest.TestCase):
	def setUp(self):
		pass

	def test_get_data(self):
		result_code, reply = request_service_api(API_MONSTER_GET_DATA, {"monster_ids": "1,2"}, "GET")
		self.assertEqual(result_code, ResultCode.SUCCESS)


class UserSmokeTest(unittest.TestCase):
	def setUp(self):
		pass

	def test_get_my_monster(self):
		result_code, reply = request_service_api(API_USER_GET_MY_MONSTER, {"trainer_address": "0x8ad8eb8b08d90022a4637bf3fbadad6cbd4f1739"}, "GET")
		self.assertEqual(result_code, ResultCode.SUCCESS)

	def test_get_sold_monster(self):
		result_code, reply = request_service_api(API_USER_GET_SOLD_MONSTER, {"trainer_address": "0x00adb04741091aa987a800dce951dfd8a164f978"}, "GET")
		self.assertEqual(result_code, ResultCode.SUCCESS)

	def test_get_info(self):
		result_code, reply = request_service_api(API_USER_GET_INFO, {"trainer_address": "0x8ad8eb8b08d90022a4637bf3fbadad6cbd4f1739"}, "GET")
		self.assertEqual(result_code, ResultCode.SUCCESS)

	def test_subcribe(self):
		result_code, reply = request_service_api(API_USER_SUBCRIBE, {"email_address": "contact@etheremon.com"}, "POST")
		self.assertEqual(result_code, ResultCode.SUCCESS)

	def test_update_info(self):
		result_code, reply = request_service_api(API_USER_UPDATE_INFO, {
			"trainer_address": "0x1f73AE5F280379da160f1575cedb8aBfE3Bb6681",
			"email": "nhudinhtuan@gmail.com",
			"username": "steven",
			"signature": "0x65ee5f104106962eb232acae8444a63c211564b5fc2993e524f053e511d2df433066120acdcdee2182ef3234772b4d68b041d1c85a83a7dfc2cd8be496c3f1341c"
		}, "POST")
		self.assertEqual(result_code, ResultCode.SUCCESS)


class TradingSmokeTest(unittest.TestCase):
	def setUp(self):
		pass

	def test_get_sell_order_list(self):
		result_code, reply = request_service_api(API_TRADING_GET_SELL_ORDER_LIST, {}, "GET")
		self.assertEqual(result_code, ResultCode.SUCCESS)

	def test_get_borrow_order_list(self):
		result_code, reply = request_service_api(API_TRADING_GET_BORROW_ORDER_LIST, {}, "GET")
		self.assertEqual(result_code, ResultCode.SUCCESS)


class EmaBattleSmokeTest(unittest.TestCase):
	def setUp(self):
		pass

	def test_get_user_stats(self):
		result_code, reply = request_service_api(API_EMA_BATTLE_GET_USER_STATS, {"trainer_address": "0x8ad8eb8b08d90022a4637bf3fbadad6cbd4f1739"}, "GET")
		self.assertEqual(result_code, ResultCode.SUCCESS)

	def test_get_rank_castle(self):
		result_code, reply = request_service_api(API_EMA_BATTLE_GET_RANK_CASTLES, {"trainer_address": "0x8ad8eb8b08d90022a4637bf3fbadad6cbd4f1739"}, "GET")
		self.assertEqual(result_code, ResultCode.SUCCESS)

	def test_get_rank_history(self):
		result_code, reply = request_service_api(API_EMA_BATTLE_GET_RANK_HISTORY, {"trainer_address": "0x8ad8eb8b08d90022a4637bf3fbadad6cbd4f1739"}, "GET")
		self.assertEqual(result_code, ResultCode.SUCCESS)

	def test_get_practice_castles(self):
		result_code, reply = request_service_api(API_EMA_BATTLE_GET_PRACTICE_CASTLES, {"trainer_address": "0x8ad8eb8b08d90022a4637bf3fbadad6cbd4f1739", "avg_level": 10}, "GET")
		self.assertEqual(result_code, ResultCode.SUCCESS)

	def test_get_practice_history(self):
		result_code, reply = request_service_api(API_EMA_BATTLE_GET_PRACTICE_HISTORY, {"trainer_address": "0x8ad8eb8b08d90022a4637bf3fbadad6cbd4f1739"}, "GET")
		self.assertEqual(result_code, ResultCode.SUCCESS)

	def test_get_rank_battle(self):
		result_code, reply = request_service_api(API_EMA_BATTLE_GET_RANK_BATTLE, {"battle_id": 1}, "GET")
		self.assertEqual(result_code, ResultCode.SUCCESS)


class EmaAdventureSmokeTest(unittest.TestCase):
	def setUp(self):
		pass

	def test_get_item_data(self):
		result_code, reply = request_service_api(API_EMA_ADVENTURE_GET_ITEM_DATA, {"token_ids": "1,2"}, "GET")
		self.assertEqual(result_code, ResultCode.SUCCESS)

	def test_get_my_sites(self):
		result_code, reply = request_service_api(API_EMA_ADVENTURE_GET_MY_SITES, {"trainer_address": "0x8ad8eb8b08d90022a4637bf3fbadad6cbd4f1739"}, "GET")
		self.assertEqual(result_code, ResultCode.SUCCESS)

	def test_get_adventure_stats(self):
		result_code, reply = request_service_api(API_EMA_ADVENTURE_GET_STATS, {"trainer_address": "0x8ad8eb8b08d90022a4637bf3fbadad6cbd4f1739"}, "GET")
		self.assertEqual(result_code, ResultCode.SUCCESS)

	def test_get_adventure_explores(self):
		result_code, reply = request_service_api(API_EMA_ADVENTURE_GET_EXPLORES, {"trainer_address": "0x8ad8eb8b08d90022a4637bf3fbadad6cbd4f1739"}, "GET")
		self.assertEqual(result_code, ResultCode.SUCCESS)

	def test_get_adventure_items(self):
		result_code, reply = request_service_api(API_EMA_ADVENTURE_GET_ITEMS, {"trainer_address": "0x8ad8eb8b08d90022a4637bf3fbadad6cbd4f1739"}, "GET")
		self.assertEqual(result_code, ResultCode.SUCCESS)

	def test_get_pending_explore(self):
		result_code, reply = request_service_api(API_EMA_ADVENTURE_GET_PENDING_EXPLORE, {"trainer_address": "0x8ad8eb8b08d90022a4637bf3fbadad6cbd4f1739"}, "GET")
		self.assertEqual(result_code, ResultCode.SUCCESS)

	def test_count_item(self):
		result_code, reply = request_service_api(API_EMA_ADVENTURE_COUNT_ITEM, {"item_classes": "500"}, "GET")
		self.assertEqual(result_code, ResultCode.SUCCESS)


class EmaQuestSmokeTest(unittest.TestCase):
	def setUp(self):
		pass

	def test_get_quest(self):
		result_code, reply = request_service_api(API_QUEST_GET_QUEST, {"trainer_address": "0xf65e814C5150738c9B0a10DF5328322A2b7af95a", "quest_type": 0}, "GET")
		self.assertEqual(result_code, ResultCode.SUCCESS)

	def test_claim_quest(self):
		result_code, reply = request_service_api(API_QUEST_CLAIM_QUEST, {"trainer_address": "0x8ad8eb8b08d90022a4637bf3fbadad6cbd4f1739", "quest_id": 2001}, "POST")
		self.assertEqual(result_code, ResultCode.ERROR_PARAMS)

	def test_claim_all(self):
		result_code, reply = request_service_api(API_QUEST_CLAIM_ALL, {"trainer_address": "0x8ad8eb8b08d90022a4637bf3fbadad6cbd4f1739"}, "POST")
		self.assertEqual(result_code, ResultCode.ERROR_PARAMS)


if __name__ == "__main__":
	unittest.main()
