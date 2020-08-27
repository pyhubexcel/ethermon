# After moving win reward to quest, some forgot to claim the old win reward.
# This script is to add this amount back to the emont balance.
from django.db import transaction

from etheremon_lib import ema_player_manager, ema_claim_manager, emont_bonus_manager, user_manager
from etheremon_lib.constants import BattleResult
from etheremon_lib.emont_bonus_manager import EmontBonusType
from etheremon_lib.models import EtheremonDB

LIST_PLAYERS = [
	# Rob
	"0xb7b2C4C044EbFaf6aCcc4d3e7D57CeDbfFb6F07D",
	"0x3E8150bd41B0759d32926033129B75e9f7ae6Cf4",
	"0x78aB2D92F5Cc8b76c4C6Df8A79783d502D6dAE9D",
	"0xC7cDc6d3C20ED26B1767cB8Eeb9Ff4F0f071915D",
	"0x45bc64754dF98BcA99e86D4321fAe33cfbBEbd5b",
	"0x5A53C02B95D8Da3180486BC6c934033b5a75426C",
	"0x06a6735427b9436b945C199d1edDBe6159d40664",
	"0x7Cf885CE9263CAb4edF4C59002cCDc5a6397ed61",
	"0x7Cf885CE9263CAb4edF4C59002cCDc5a6397ed61",
	# kyoronut
	"0x8e5d30f161Ba3EbB09dc3c1F06515656af34BaA1",
	# bjm
	"0xF122446e7D4D06D11c06ca93685ACC8742198183",
	# xandroc
	"0x95567C6502625ae5A8F4027aFf27221a39C5FEAb",
	# sentinelofwords
	"0x4E70e1243D91A99E19fA4c8b41407CE0a786A0cE",
]

CUTOFF_TIME = 1547193600		# 01/11/2019 @ 08:00am (UTC)


def get_rewards(address):
	player_data = ema_player_manager.get_player_rank_by_address(address)

	attack_wins = EtheremonDB.EmaRankBattleTab.objects \
		.filter(attacker_id=player_data.player_id) \
		.filter(result=BattleResult.ATTACKER_WIN) \
		.filter(create_time__lte=CUTOFF_TIME).count()
	defense_wins = EtheremonDB.EmaRankBattleTab.objects \
		.filter(defender_id=player_data.player_id) \
		.filter(result=BattleResult.ATTACKER_LOSE) \
		.filter(create_time__lte=CUTOFF_TIME).count()

	total_wins = attack_wins + defense_wins
	total_claimed = player_data.total_claimed
	claimable = total_wins - total_claimed
	pending = 0

	pending_win_reward = ema_claim_manager.get_pending_win_claim(player_data.player_id)
	if pending_win_reward:
		pending = pending_win_reward.count_win

	to_return_val = claimable - pending
	return total_wins, total_claimed, claimable, pending, to_return_val, to_return_val * 0.2


def return_reward(address):
	total_wins, total_claimed, claimable, pending, to_return_val, to_return_emont = get_rewards(address)
	player_uid = user_manager.get_uid_by_address(address)

	if to_return_val > 0:
		with transaction.atomic():
			emont_bonus_manager.add_bonus(player_uid, {
				EmontBonusType.OLD_WIN_REWARD: to_return_emont
			})

			player_data = ema_player_manager.get_player_rank_by_address(address)
			player_data.total_claimed += to_return_val
			player_data.save()


def return_rewards():
	for address in LIST_PLAYERS:
		total_wins, total_claimed, claimable, pending, to_return_val, to_return_emont = get_rewards(address)
		player_uid = user_manager.get_uid_by_address(address)

		if to_return_val > 0:
			with transaction.atomic():
				emont_bonus_manager.add_bonus(player_uid, {
					EmontBonusType.OLD_WIN_REWARD: to_return_emont
				})

				player_data = ema_player_manager.get_player_rank_by_address(address)
				player_data.total_claimed += to_return_val
				player_data.save()
