from etheremon_lib import config
from common import dbmodel
import time

db = dbmodel.get_db()
if not db:
	db = dbmodel.init_db(config.DATABASE_BACKEND, None)

class EtheremonDB:
	'''
	class EtheremonDBConfig:
		class Config:
			db_for_read = 'etheremon_db.read'
			db_for_write = 'etheremon_db.write'
	'''

	class CastleTab(db.Model):
		id = db.BigAutoField(primary_key=True)
		castle_id = db.IntegerField()
		name = db.CharField(max_length=128)
		owner_address = db.CharField(max_length=128)
		brick_number = db.IntegerField()
		castle_create_time = db.PositiveIntegerField()

		monster_id_1 = db.IntegerField()
		monster_id_2 = db.IntegerField()
		monster_id_3 = db.IntegerField()
		supporter_id_1 = db.IntegerField()
		supporter_id_2 = db.IntegerField()
		supporter_id_3 = db.IntegerField()

		total_win = db.IntegerField()
		total_lose = db.IntegerField()

		extra_data = db.TextField()

		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()

		def save(self, *args, **kwargs):
			if not self.create_time:
				self.create_time = int(time.time())
			self.update_time = int(time.time())
			super(EtheremonDB.CastleTab, self).save(*args, **kwargs)

		class Meta:
			db_table = u'castle_tab'

	class MarketHistoryTab(db.Model):
		id = db.BigAutoField(primary_key=True)
		monster_id = db.IntegerField()

		txn_hash = db.CharField(max_length=128)
		seller = db.CharField(max_length=128)
		buyer = db.CharField(max_length=128)

		price = db.BigIntegerField()
		is_sold = db.BooleanField()

		class_id = db.IntegerField()
		base_bp = db.IntegerField()
		exp = db.IntegerField()
		create_index = db.IntegerField()

		block_number = db.IntegerField()
		sell_time = db.PositiveIntegerField()
		buy_time = db.PositiveIntegerField()

		extra_data = db.TextField()
		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()

		def save(self, *args, **kwargs):
			if not self.create_time:
				self.create_time = int(time.time())
			self.update_time = int(time.time())
			super(EtheremonDB.MarketHistoryTab, self).save(*args, **kwargs)

		class Meta:
			db_table = u'market_history_tab'  # Flip when do resync

	'''
	class MarketHistoryTabBackup(db.Model):
		id = db.BigAutoField(primary_key=True)

		monster_id = db.IntegerField()
		price = db.BigIntegerField()
		is_sold = db.BooleanField()

		class_id = db.IntegerField()
		base_bp = db.IntegerField()
		create_index = db.IntegerField()

		block_number = db.IntegerField()
		sell_time = db.PositiveIntegerField()
		buy_time = db.PositiveIntegerField()

		extra_data = db.TextField()
		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()

		def save(self, *args, **kwargs):
			if not self.create_time:
				self.create_time = int(time.time())
			self.update_time = int(time.time())
			super(EtheremonDB.MarketHistoryTabBackup, self).save(*args, **kwargs)

		class Meta:
			db_table = u'market_history_tab_backup'  # Flip when do resync
	'''

	class BattleLogTab(db.Model):
		id = db.BigAutoField(primary_key=True)
		battle_id = db.IntegerField()
		castle_id = db.IntegerField()
		attacker_address = db.CharField(max_length=128)

		attacker_monster_id_1 = db.IntegerField()
		attacker_monster_id_2 = db.IntegerField()
		attacker_monster_id_3 = db.IntegerField()
		attacker_supporter_id_1 = db.IntegerField()
		attacker_supporter_id_2 = db.IntegerField()
		attacker_supporter_id_3 = db.IntegerField()

		result = db.IntegerField()

		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()

		'''
		extra data
		attacker_monster_exp_1 = db.IntegerField()
		attacker_monster_exp_2 = db.IntegerField()
		attacker_monster_exp_3 = db.IntegerField()

		castle_monster_exp_1 = db.IntegerField()
		castle_monster_exp_2 = db.IntegerField()
		castle_monster_exp_3 = db.IntegerField()
		'''
		extra_data = db.TextField()

		def save(self, *args, **kwargs):
			if not self.create_time:
				self.create_time = int(time.time())
			self.update_time = int(time.time())
			super(EtheremonDB.BattleLogTab, self).save(*args, **kwargs)

		class Meta:
			db_table = u'battle_tab'

	'''
	class MonsterTab(db.Model):
		id = db.BigAutoField(primary_key=True)
		monster_id = db.IntegerField()
		class_id = db.IntegerField()
		name = db.CharField()
		owner_address = db.CharField()
		exp = db.IntegerField()
		level = db.IntegerField()
		create_index = db.IntegerField()
		last_claim_index = db.IntegerField()
		monster_create_time = db.IntegerField()

		base_stat_1 = db.IntegerField()
		base_stat_2 = db.IntegerField()
		base_stat_3 = db.IntegerField()
		base_stat_4 = db.IntegerField()
		base_stat_5 = db.IntegerField()
		base_stat_6 = db.IntegerField()
		stat_1 = db.IntegerField()
		stat_2 = db.IntegerField()
		stat_3 = db.IntegerField()
		stat_4 = db.IntegerField()
		stat_5 = db.IntegerField()
		stat_6 = db.IntegerField()
		bp = db.IntegerField()

		extra_data = db.TextField()

		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()

		def save(self, *args, **kwargs):
			if not self.create_time:
				self.create_time = int(time.time())
			self.update_time = int(time.time())
			super(EtheremonDB.MonsterTab, self).save(*args, **kwargs)

		class Meta:
			db_table = u'monster_tab'
	'''

	class UserTab(db.Model):
		uid = db.PositiveAutoField(primary_key=True)
		address = db.CharField(max_length=128)
		email = db.CharField(max_length=128)
		username = db.CharField(max_length=128)
		status = db.PositiveTinyIntegerField()
		flag = db.PositiveIntegerField()
		ip = db.CharField(max_length=32)
		country = db.CharField(max_length=4)
		refer_uid = db.PositiveIntegerField()
		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'user_tab'

	class UserLadderTab(db.Model):
		player_id = db.PositiveIntegerField(primary_key=True)
		trainer = db.CharField(max_length=128)
		point = db.PositiveIntegerField()
		total_win = db.PositiveIntegerField()
		total_lose = db.PositiveIntegerField()
		total_match = db.PositiveIntegerField()
		a0 = db.PositiveBigIntegerField()
		a1 = db.PositiveBigIntegerField()
		a2 = db.PositiveBigIntegerField()
		s0 = db.PositiveBigIntegerField()
		s1 = db.PositiveBigIntegerField()
		s2 = db.PositiveBigIntegerField()
		avg_bp = db.PositiveIntegerField()
		avg_level = db.PositiveIntegerField()
		energy = db.PositiveIntegerField()
		last_claim = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'user_ladder_tab'

	class BattleLadderTab(db.Model):
		battle_id = db.PositiveBigAutoField(primary_key=True)
		refer_id = db.PositiveBigIntegerField()
		defender_id = db.PositiveIntegerField()
		attacker_id = db.PositiveIntegerField()
		defender_before_point = db.PositiveIntegerField()
		defender_after_point = db.PositiveIntegerField()
		attacker_before_point = db.PositiveIntegerField()
		attacker_after_point = db.PositiveIntegerField()
		result = db.PositiveIntegerField()
		monster_data = db.TextField()
		status = db.PositiveTinyIntegerField()
		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'battle_ladder_tab'

	class PracticeLadderTab(db.Model):
		id = db.PositiveBigAutoField(primary_key=True)
		trainee = db.CharField(max_length=64)
		player_id = db.PositiveIntegerField()
		monster_1 = db.PositiveBigIntegerField()
		monster_2 = db.PositiveBigIntegerField()
		monster_3 = db.PositiveBigIntegerField()
		exp_gain1 = db.PositiveIntegerField()
		exp_gain2 = db.PositiveIntegerField()
		exp_gain3 = db.PositiveIntegerField()
		status = db.PositiveTinyIntegerField()
		create_time = db.PositiveIntegerField()
		def save(self, *args, **kwargs):
			if not self.create_time:
				self.create_time = int(time.time())
			super(EtheremonDB.PracticeLadderTab, self).save(*args, **kwargs)
		class Meta:
			db_table = u'practice_ladder_tab'

	class PracticeLadderBattleTab(db.Model):
		id = db.PositiveBigAutoField(primary_key=True)
		practice_id = db.PositiveBigIntegerField()
		player_id = db.PositiveIntegerField()
		monster_data = db.TextField()
		class Meta:
			db_table = u'practice_ladder_battle_tab'

	class ClaimRankLadderTab(db.Model):
		id = db.PositiveAutoField(primary_key=True)
		player_id = db.PositiveIntegerField()
		rank = db.PositiveIntegerField()
		point = db.PositiveIntegerField()
		status = db.PositiveIntegerField()
		create_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'claim_rank_ladder_tab'

	class WorldTrainerTab(db.Model):
		id = db.PositiveAutoField(primary_key=True)
		trainer = db.CharField(max_length=64)
		flag = db.PositiveIntegerField()
		extra_data = db.TextField()
		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'world_trainer_tab'

	class ClaimReferTab(db.Model):
		id = db.PositiveAutoField(primary_key=True)
		uid = db.PositiveIntegerField()
		amount = db.PositiveBigIntegerField()
		status = db.PositiveIntegerField()
		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'claim_refer_tab'

	class EmontBonusTab(db.Model):
		id = db.PositiveAutoField(primary_key=True)
		uid = db.PositiveIntegerField()
		bonus_data = db.TextField()
		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'emont_bonus_tab'

	#### EMONT Alliance
	class EmaMonsterDataTab(db.Model):
		id = db.PositiveBigAutoField(primary_key=True)
		monster_id = db.PositiveIntegerField()
		class_id = db.PositiveIntegerField()
		trainer = db.CharField(max_length=128)
		name = db.CharField(max_length=128)
		exp = db.PositiveIntegerField()
		b0 = db.PositiveTinyIntegerField()
		b1 = db.PositiveTinyIntegerField()
		b2 = db.PositiveTinyIntegerField()
		b3 = db.PositiveTinyIntegerField()
		b4 = db.PositiveTinyIntegerField()
		b5 = db.PositiveTinyIntegerField()
		bp = db.PositiveIntegerField()
		egg_bonus = db.PositiveIntegerField()
		create_index = db.PositiveIntegerField()
		last_claim_index = db.PositiveIntegerField()
		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'ema_monster_data_tab'

	class EmaMonsterExpTab(db.Model):
		monster_id = db.PositiveIntegerField(primary_key=True)
		adding_exp = db.PositiveIntegerField()
		added_exp = db.PositiveIntegerField()
		bp = db.PositiveIntegerField()
		status = db.PositiveIntegerField()
		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'ema_monster_exp_tab'



	class EmaPlayerEnergyTab(db.Model):
		id = db.PositiveAutoField(primary_key=True)
		trainer = db.CharField(max_length=128)
		init_amount = db.PositiveBigIntegerField()
		free_amount = db.PositiveBigIntegerField()
		paid_amount = db.PositiveBigIntegerField()
		invalid_amount = db.PositiveBigIntegerField()
		consumed_amount = db.PositiveBigIntegerField()
		last_claim_time = db.PositiveIntegerField()
		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'ema_player_energy_tab'


	class EmaSettingsTab(db.Model):
		setting_id = db.PositiveIntegerField(primary_key=True)
		name = db.CharField(max_length=64)
		value = db.PositiveBigIntegerField()
		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'ema_settings_tab'

	class EmaMarketTab(db.Model):
		id = db.PositiveBigAutoField(primary_key=True)
		type = db.PositiveTinyIntegerField()
		player = db.CharField(max_length=128)
		monster_id = db.PositiveIntegerField()
		price = db.PositiveBigIntegerField()
		status = db.PositiveIntegerField()
		extra_data = db.TextField()
		create_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'ema_market_tab'

	class EmaEggDataTab(db.Model):
		egg_id = db.PositiveBigIntegerField(primary_key=True)
		mother_id = db.PositiveBigIntegerField()
		class_id = db.PositiveIntegerField()
		trainer = db.CharField(max_length=128)
		hatch_time = db.PositiveIntegerField()
		new_obj_id = db.PositiveBigIntegerField()
		create_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'ema_egg_data_tab'

	class EmaPlayerRankData(db.Model):
		player_id = db.PositiveIntegerField(primary_key=True)
		trainer = db.CharField(max_length=128)
		point = db.PositiveIntegerField()
		total_win = db.PositiveIntegerField()
		total_lose = db.PositiveIntegerField()
		total_claimed = db.PositiveIntegerField()
		a0 = db.IntegerField()
		a1 = db.IntegerField()
		a2 = db.IntegerField()
		s0 = db.IntegerField()
		s1 = db.IntegerField()
		s2 = db.IntegerField()
		avg_bp = db.PositiveIntegerField()
		avg_level = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'ema_player_rank_data'


	class EmaPlayerRankRKTData(db.Model):
		player_id = db.PositiveIntegerField(primary_key=True)
		trainer = db.CharField(max_length=128)
		point = db.PositiveIntegerField()
		total_win = db.PositiveIntegerField()
		total_lose = db.PositiveIntegerField()
		total_claimed = db.PositiveIntegerField()
		a0 = db.IntegerField()
		a1 = db.IntegerField()
		a2 = db.IntegerField()
		s0 = db.IntegerField()
		s1 = db.IntegerField()
		s2 = db.IntegerField()
		avg_bp = db.PositiveIntegerField()
		avg_level = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'ema_player_rank_rkt_data'


	class EmaBattleBlockedUsers(db.Model):
		id = db.PositiveIntegerField(primary_key=True)
		trainer = db.CharField(max_length=128)
		create_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'ema_battle_blocked_trainers'

	class EmaRankBattleTab(db.Model):
		id = db.PositiveBigAutoField(primary_key=True)
		attacker_id = db.PositiveIntegerField()
		defender_id = db.PositiveIntegerField()
		attacker_before_point = db.PositiveIntegerField()
		attacker_after_point = db.PositiveIntegerField()
		defender_before_point = db.PositiveIntegerField()
		defender_after_point = db.PositiveIntegerField()
		result = db.PositiveIntegerField()
		monster_data = db.TextField()
		exp_gain = db.TextField()
		status = db.PositiveIntegerField()
		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'ema_rank_battle_tab'

	class EmaRankBattleRKTTab(db.Model):
		id = db.PositiveBigAutoField(primary_key=True)
		attacker_id = db.PositiveIntegerField()
		defender_id = db.PositiveIntegerField()
		attacker_before_point = db.PositiveIntegerField()
		attacker_after_point = db.PositiveIntegerField()
		defender_before_point = db.PositiveIntegerField()
		defender_after_point = db.PositiveIntegerField()
		result = db.PositiveIntegerField()
		monster_data = db.TextField()
		exp_gain = db.TextField()
		status = db.PositiveIntegerField()
		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'ema_rank_battle_tab_rkt'

	class EmaRankBattleTabBP(db.Model):
		id = db.PositiveBigAutoField(primary_key=True)
		attacker_id = db.PositiveIntegerField()
		defender_id = db.PositiveIntegerField()
		attacker_before_point = db.PositiveIntegerField()
		attacker_after_point = db.PositiveIntegerField()
		defender_before_point = db.PositiveIntegerField()
		defender_after_point = db.PositiveIntegerField()
		result = db.PositiveIntegerField()
		monster_data = db.TextField()
		status = db.PositiveIntegerField()
		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'ema_rank_battle_tab_bp'

	class EmaPracticeBattleTab(db.Model):
		id = db.PositiveBigAutoField(primary_key=True)
		trainer = db.CharField(max_length=128)
		defender_id = db.PositiveIntegerField()
		result = db.PositiveIntegerField()
		monster_data = db.TextField()
		status = db.PositiveIntegerField()
		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'ema_practice_battle_tab'

	class EmaClaimMonExpTab(db.Model):
		id = db.PositiveBigAutoField(primary_key=True)
		monster_id = db.PositiveIntegerField()
		exp = db.PositiveIntegerField()
		status = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'ema_claim_mon_exp_tab'

	class EmaClaimRankWinTab(db.Model):
		id = db.PositiveBigAutoField(primary_key=True)
		player_id = db.PositiveIntegerField()
		count_win = db.PositiveIntegerField()
		count_emont = db.PositiveBigIntegerField()
		status = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'ema_claim_rank_win_tab'

	class EmaClaimRankTopTab(db.Model):
		id = db.PositiveBigAutoField(primary_key=True)
		player_id = db.PositiveIntegerField()
		rank = db.PositiveIntegerField()
		status = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'ema_claim_rank_top_tab'

	class EmaAdventurePresaleTab(db.Model):
		id = db.PositiveAutoField(primary_key=True)
		site_id = db.PositiveIntegerField()
		site_index = db.PositiveIntegerField()
		bid_id = db.PositiveIntegerField()
		bidder = db.CharField(max_length=128)
		bid_amount = db.PositiveBigIntegerField()
		bid_time = db.PositiveIntegerField()
		token_id = db.PositiveBigIntegerField()
		update_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'ema_adventure_presale_tab'

	class EmaAdventureItemTab(db.Model):
		id = db.PositiveAutoField(primary_key=True)
		token_id = db.PositiveIntegerField()
		owner = db.CharField(max_length=128)
		class_id = db.PositiveIntegerField()
		value = db.PositiveBigIntegerField()
		update_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'ema_adventure_item_tab'

	class EmaAdventureExploreTab(db.Model):
		id = db.PositiveAutoField(primary_key=True)
		explore_id = db.PositiveIntegerField()
		fee_type = db.PositiveTinyIntegerField()
		sender = db.CharField(max_length=64)
		monster_type = db.PositiveIntegerField()
		monster_id = db.PositiveIntegerField()
		site_id = db.PositiveIntegerField()
		reward_monster_class = db.PositiveIntegerField()
		reward_item_class = db.PositiveIntegerField()
		reward_item_value = db.CharField(max_length=128)
		start_block = db.PositiveIntegerField()
		end_block = db.PositiveIntegerField()
		claim_txn_hash = db.CharField(max_length=128)
		create_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'ema_adventure_explore_tab'

	class EmaAdventureRevenueSiteTab(db.Model):
		site_id = db.PositiveIntegerField(primary_key=True)
		eth_amount = db.FloatField()
		emont_amount = db.FloatField()
		update_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'ema_adventure_revenue_site_tab'

	class EmaAdventureClaimTokenTab(db.Model):
		token_id = db.PositiveIntegerField(primary_key=True)
		claimed_eth_amount = db.FloatField()
		claimed_emont_amount = db.FloatField()
		update_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'ema_adventure_claim_token_tab'

	class EmaAdventureVoteTab(db.Model):
		id = db.PositiveAutoField(primary_key=True)
		owner = db.CharField(max_length=64)
		explore_eth_fee = db.FloatField()
		explore_emont_fee = db.FloatField()
		challenge_eth_fee = db.FloatField()
		challenge_emont_fee = db.FloatField()
		update_time = db.PositiveIntegerField()
		class Meta:
			db_table = u'ema_adventure_vote_tab'

	class RevenueMonsterTab(db.Model):
		id = db.PositiveBigAutoField(primary_key=True)
		monster_id = db.PositiveBigIntegerField()
		trainer = db.CharField(max_length=128)
		class_id = db.PositiveIntegerField()
		eth_amount = db.FloatField()
		usd_amount = db.FloatField()
		catch_date = db.PositiveIntegerField()
		timestamp = db.PositiveIntegerField()
		class Meta:
			db_table = u'revenue_monster_tab'

	class RevenueTxnTab(db.Model):
		id = db.PositiveBigAutoField(primary_key=True)
		contract_address = db.CharField(max_length=128)
		method_id = db.CharField(max_length=128)
		txn_hash = db.CharField(max_length=128)
		sender = db.CharField(max_length=128)
		eth_amount = db.FloatField()
		usd_amount = db.FloatField()
		block_number = db.PositiveIntegerField()
		create_date = db.PositiveIntegerField()
		timestamp = db.PositiveIntegerField()
		class Meta:
			db_table = u'revenue_txn_tab'

	# 3rd party
	class PartnerMchPresaleTab(db.Model):
		id = db.PositiveAutoField(primary_key=True)
		player = db.CharField(max_length=64)
		amount = db.FloatField()
		flag = db.PositiveIntegerField()
		country = db.CharField(max_length=4)
		txn_count = db.PositiveIntegerField()
		latest_block_number = db.PositiveIntegerField()
		class Meta:
			db_table = u'partner_mch_presale_tab'

	# Quest
	class QuestTab(db.Model):
		player_address = db.CharField(max_length=128)
		player_uid = db.PositiveIntegerField()
		quest_id = db.PositiveIntegerField()
		quest_type = db.PositiveTinyIntegerField()
		quest_level = db.PositiveTinyIntegerField()
		quest_name = db.CharField(max_length=128)
		quest_target = db.PositiveIntegerField()
		quest_progress = db.PositiveIntegerField()
		reward_type = db.PositiveTinyIntegerField()
		reward_value = db.FloatField()
		status = db.PositiveTinyIntegerField()
		start_time = db.PositiveIntegerField()
		end_time = db.PositiveIntegerField()
		last_check = db.PositiveIntegerField()
		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()
		extra = db.TextField()

		class Meta:
			db_table = u'quest_tab'

	# Quest
	class TransactionTab(db.Model):
		player_address = db.CharField(max_length=128)
		player_uid = db.PositiveIntegerField()
		txn_type = db.PositiveTinyIntegerField()
		txn_info = db.CharField(max_length=128)
		txn_hash = db.CharField(max_length=128)
		status = db.PositiveTinyIntegerField()
		amount_type = db.PositiveTinyIntegerField()
		amount_value = db.FloatField()
		extra = db.TextField()
		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()

		class Meta:
			db_table = u'transaction_tab'

	# Balance tab
	class BalanceTab(db.Model):
		player_address = db.CharField(max_length=128)
		player_uid = db.PositiveIntegerField()
		balance_type = db.PositiveTinyIntegerField()
		balance_value = db.FloatField()
		status = db.PositiveTinyIntegerField()
		extra = db.TextField()
		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()

		class Meta:
			db_table = u'user_balance_tab'

	# Burn Mon
	class BurnMonTab(db.Model):
		player_address = db.CharField(max_length=128)
		mon_id = db.PositiveIntegerField()
		mon_level = db.PositiveIntegerField()
		mon_exp = db.PositiveIntegerField()
		amount_type = db.PositiveTinyIntegerField()
		amount_value = db.PositiveBigIntegerField()
		status = db.PositiveTinyIntegerField()
		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()

		class Meta:
			db_table = u'burn_mon_tab'

	# Monster Offchain Tab
	class EmaMonsterOffchainTab(db.Model):
		class_id = db.PositiveIntegerField()
		trainer = db.CharField(max_length=128)
		name = db.CharField(max_length=128)
		exp = db.PositiveIntegerField()
		bp = db.PositiveIntegerField()
		b0 = db.PositiveTinyIntegerField()
		b1 = db.PositiveTinyIntegerField()
		b2 = db.PositiveTinyIntegerField()
		b3 = db.PositiveTinyIntegerField()
		b4 = db.PositiveTinyIntegerField()
		b5 = db.PositiveTinyIntegerField()
		status = db.PositiveTinyIntegerField()
		extra = db.TextField()
		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()

		class Meta:
			db_table = u'ema_monster_offchain_tab'

	# Tournament Info
	class TournamentInfoTab(db.Model):
		tournament_type = db.PositiveTinyIntegerField()
		mon_level_min = db.PositiveIntegerField()
		mon_level_max = db.PositiveIntegerField()
		registrations = db.PositiveIntegerField()
		price_pool_emont = db.PositiveBigIntegerField()
		price_pool_eth = db.PositiveBigIntegerField()
		start_time = db.PositiveIntegerField()
		status = db.PositiveTinyIntegerField()
		result = db.TextField()
		reward = db.TextField()
		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()

		class Meta:
			db_table = u'tournament_info_tab'

	# Tournament Registration
	class TournamentRegistrationTab(db.Model):
		player_id = db.PositiveIntegerField()
		player_address = db.CharField(max_length=128)
		tournament_id = db.PositiveIntegerField()
		fee_paid_emont = db.PositiveBigIntegerField()
		fee_paid_eth = db.PositiveBigIntegerField()
		team_info = db.TextField()
		status = db.PositiveTinyIntegerField()
		extra = db.TextField()
		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()

		class Meta:
			db_table = u'tournament_registration_tab'

	# General Battle
	class BattleMatchTab(db.Model):
		attacker_id = db.PositiveIntegerField()
		attacker_address = db.CharField(max_length=128)
		defender_id = db.PositiveIntegerField()
		defender_address = db.CharField(max_length=128)

		battle_type = db.PositiveTinyIntegerField()
		monster_data = db.TextField()
		before_battle_data = db.TextField()
		result = db.PositiveIntegerField()
		after_battle_data = db.TextField()

		status = db.PositiveTinyIntegerField()
		extra = db.TextField()
		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()

		class Meta:
			db_table = u'battle_match_tab'

	class UserGeneralInfoTab(db.Model):
		uid = db.PositiveIntegerField()
		address = db.CharField(max_length=128)
		tournament_win = db.PositiveIntegerField()
		tournament_loss = db.PositiveIntegerField()
		create_time = db.PositiveIntegerField()
		update_time = db.PositiveIntegerField()

		class Meta:
			db_table = u'user_general_info_tab'

	class DCLItemClassConfig(db.Model):
		dcl_item_class_ID = db.PositiveIntegerField(primary_key=True)
		ItemClass = db.CharField(max_length=50)
		ItemVariety = db.CharField(max_length=50)
		craft_timer = db.PositiveIntegerField()
		cost = db.PositiveIntegerField()
		craft_formula = db.PositiveIntegerField()
		dxp_bonus = db.PositiveIntegerField()
		hunger_bonus = db.PositiveIntegerField()
		energy_bonus = db.PositiveIntegerField()
		hp_bonus = db.PositiveIntegerField()
		mood_bonus = db.PositiveIntegerField()
		alignment_status = db.PositiveIntegerField()
		buff_status = db.PositiveIntegerField()
		hunger_state_time_bonus = db.PositiveIntegerField()
		mon_lv_req = db.PositiveIntegerField()
		create_time = db.PositiveIntegerField()
		user_default_qty = db.PositiveIntegerField()
		metazone_sku = db.CharField(max_length=15)
		
		class Meta:
			db_table = u'dcl_item_class_config'


	class DCLItemWip(db.Model):
		dcl_item_id = db.PositiveIntegerField(primary_key=True)
		ItemClass = db.CharField(max_length=50)
		ItemVariety = db.CharField(max_length=50)
		wild = db.CharField(max_length=3)
		wild_count = db.PositiveIntegerField()
		address = db.CharField(max_length=100)
		growth_state = db.PositiveIntegerField()
		host_id = db.PositiveIntegerField()
		meta_id = db.PositiveIntegerField()
		start_timer = db.PositiveIntegerField()
		end_timer = db.PositiveIntegerField()
		

		class Meta:
			db_table = u'dcl_item_wip'		

	class DCLEthermonWild(db.Model):
		id = db.PositiveIntegerField(primary_key=True)
		mon_class = db.PositiveIntegerField()
		wild = db.CharField(max_length=3)
		wild_count = db.PositiveIntegerField()
		address = db.CharField(max_length=100)
		spawn_start = db.PositiveIntegerField()
		spawn_end = db.PositiveIntegerField()
		host_id = db.PositiveIntegerField()
		meta_id = db.PositiveIntegerField()
		create_time = db.PositiveIntegerField()
		

		class Meta:
			db_table = u'dcl_ethermon_wild'	


	class DCLUserFungible(db.Model):
		dcl_fungible_id = db.PositiveIntegerField(primary_key=True)
		craft_hierachy = db.PositiveIntegerField()
		address = db.CharField(max_length=100)
		ItemClass = db.CharField(max_length=50)
		ItemVariety = db.CharField(max_length=50)
		qty = db.PositiveIntegerField()
		create_time = db.PositiveIntegerField()
		

		class Meta:
			db_table = u'dcl_user_fungible'			

	class DCLMonsterData(db.Model):
		Mon_ID = db.PositiveIntegerField(primary_key=True)
		dxp = db.PositiveIntegerField()
		last_saved = db.PositiveIntegerField()
		HP_current = db.PositiveIntegerField()
		energy_current = db.PositiveIntegerField()
		hunger_current = db.PositiveIntegerField()
		mood_current = db.PositiveIntegerField()
		HP_max = db.PositiveIntegerField()
		Energy_max = db.PositiveIntegerField()
		Hunger_max = db.PositiveIntegerField()
		Mood_max = db.PositiveIntegerField()
		hunger_state = db.PositiveIntegerField()
		hunger_state_end_timer = db.PositiveIntegerField()
		sleep_end_timer = db.PositiveIntegerField()
		address = db.CharField(max_length=100)
		
		
		

		class Meta:
			db_table = u'dcl_monster_data'	

	class DCLUserActiveStatus(db.Model):
		user_id = db.PositiveIntegerField(primary_key=True)
		address = db.CharField(max_length=100)
		active_dcl_fungible_ID = db.PositiveIntegerField()
		a0 = db.PositiveIntegerField()
		a1 = db.PositiveIntegerField()
		a2 = db.PositiveIntegerField()
		s0 = db.PositiveIntegerField()
		s1 = db.PositiveIntegerField()
		s2 = db.PositiveIntegerField()
		is_live	 = db.PositiveIntegerField()
		last_seen = db.PositiveIntegerField()
		class Meta:
			db_table = u'dcl_user_active_stats'		

	class DCLMetazoePurchase(db.Model):
		id = db.PositiveIntegerField(primary_key=True)
		action = db.CharField(max_length=255)
		meta_id = db.PositiveIntegerField()
		host_id = db.PositiveIntegerField()
		plot_unique = db.CharField(max_length=255)
		txn_token = db.CharField(max_length=255)
		eth_from = db.CharField(max_length=255)
		dcl_name = db.CharField(max_length=255)
		sku = db.CharField(max_length=255)
		create_date = db.PositiveIntegerField()

		class Meta:
			db_table = u'dcl_metazone_purchase'			


