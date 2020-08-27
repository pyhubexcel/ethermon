# coding=utf-8
from random import randint

from django.db import transaction
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from common.utils import parse_params, log_request
from etheremon_lib.decorators.auth_decorators import sign_in_required, register_required
from etheremon_lib.emont_bonus_manager import EmontBonusType
from etheremon_lib.form_schema import *
from etheremon_lib.models import EtheremonDB
from etheremon_lib.preprocessor import pre_process_header
from etheremon_lib import ema_energy_manager, emont_bonus_manager, transaction_manager
from etheremon_lib.transaction_manager import TxnTypes, TxnAmountTypes, TxnStatus
from etheremon_api.views.helper import *


LD_SPIN_COST_EMONT_COST = 15

LD_REWARDS = [
	{
		"idx": 5,
		"percentage": 1050,
		"reward_type": TxnAmountTypes.LUCKY_DRAW_NO_PRIZE,
		"reward_value": 1,
		"desc": ""
	},
	{
		"idx": 3,
		"percentage": 2000,
		"reward_type": TxnAmountTypes.IN_GAME_EMONT,
		"reward_value": 5,
		"desc": ""
	},
	{
		"idx": 1,
		"percentage": 50,
		"reward_type": TxnAmountTypes.IN_GAME_EMONT,
		"reward_value": 150,
		"desc": ""
	},
	{
		"idx": 2,
		"percentage": 2500,
		"reward_type": TxnAmountTypes.ENERGY,
		"reward_value": 5,
		"desc": ""
	},
	{
		"idx": 4,
		"percentage": 3500,
		"reward_type": TxnAmountTypes.ENERGY,
		"reward_value": 10,
		"desc": ""
	},
	{
		"idx": 6,
		"percentage": 700,
		"reward_type": TxnAmountTypes.ENERGY,
		"reward_value": 30,
		"desc": ""
	},
	{
		"idx": 7,
		"percentage": 150,
		"reward_type": TxnAmountTypes.ADV_LEVEL_STONE_1,
		"reward_value": 1,
		"desc": ""
	},
	{
		"idx": 0,
		"percentage": 50,
		"reward_type": TxnAmountTypes.ADV_LEVEL_STONE_2,
		"reward_value": 1,
		"desc": "emont"
	},
]


def get_rewards(player_address):
	current_rewards = [{
		"id": r.id,
		"amount_type": r.amount_type,
		"amount_value": r.amount_value,
		"status": r.status,
		"timestamp": r.create_time
	} for r in EtheremonDB.TransactionTab.objects
		.filter(player_address=player_address).filter(txn_type=TxnTypes.LUCKY_DRAW_REWARD)
		.order_by("status").order_by("id")
	]

	return {
		"current_rewards": current_rewards,
		"to_claim_rewards": [],
	}


@csrf_exempt
@log_request()
@parse_params(form=LuckyDrawGetInfoForm, method='GET', data_format='FORM', error_handler=api_response_error_params)
@pre_process_header()
@sign_in_required()
@register_required()
def get_lucky_draw_info(request, data):
	player_address = data['trainer_address'].lower()
	player_uid = data['player_uid']

	# verify trainer address
	if not Web3.isAddress(player_address):
		log.warn("send_to_address_invalid|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_send_to_address"})

	rewards = get_rewards(player_address)

	return api_response_result(request, ResultCode.SUCCESS, {
		"balance_emont_in_game": emont_bonus_manager.get_emont_balance(player_uid),
		"balance_energy": ema_energy_manager.get_available_energy(player_address),
		"current_rewards": rewards["current_rewards"],
		"to_claim_rewards": rewards["to_claim_rewards"],
		"spin_cost_emont": LD_SPIN_COST_EMONT_COST
	})


@csrf_exempt
@log_request()
@parse_params(form=LuckyDrawSpinForm, method='POST', data_format='JSON', error_handler=api_response_error_params)
@pre_process_header()
@sign_in_required()
@register_required()
def spin_lucky_wheel(request, data):
	player_address = data['trainer_address'].lower()
	player_uid = data['player_uid']

	# verify trainer address
	if not Web3.isAddress(player_address):
		log.warn("send_to_address_invalid|data=%s", data)
		return api_response_result(request, ResultCode.ERROR_PARAMS, {"error_message": "invalid_send_to_address"})

	with transaction.atomic():
		# Deduct money & Reset adventure hongbao
		emont_bonus_manager.deduct_emont_in_game_balance(player_uid, LD_SPIN_COST_EMONT_COST)

		# Add payment txn
		transaction_manager.create_transaction(
			player_uid=player_uid,
			player_address=player_address,
			txn_type=TxnTypes.LUCKY_DRAW_PAYMENT,
			txn_info="lucky draw payment",
			amount_type=TxnAmountTypes.IN_GAME_EMONT,
			amount_value=LD_SPIN_COST_EMONT_COST,
			status=TxnStatus.FINISHED
		)

		# Find random reward
		random_perc = randint(0, 10000)
		random_reward = None
		for reward in LD_REWARDS:
			if random_perc < reward["percentage"]:
				random_reward = reward
				break
			else:
				random_perc -= reward["percentage"]

		if random_reward is None:
			log.warn("random_reward_failed|data=%s", data)
			return api_response_result(request, ResultCode.ERROR_SERVER, {"error_message": "server_error"})

		# Send reward
		if random_reward["reward_type"] == TxnAmountTypes.ENERGY:
			ema_energy_manager.add_energy(player_address, random_reward["reward_value"])
			txn_status = TxnStatus.FINISHED
		elif random_reward["reward_type"] == TxnAmountTypes.IN_GAME_EMONT:
			emont_bonus_manager.add_bonus(player_uid, {EmontBonusType.EVENT_BONUS: random_reward["reward_value"]})
			txn_status = TxnStatus.FINISHED
		elif random_reward["reward_type"] in [TxnAmountTypes.ADV_LEVEL_STONE_1, TxnAmountTypes.ADV_LEVEL_STONE_2]:
			txn_status = TxnStatus.INIT
		else:
			txn_status = TxnStatus.FINISHED

		# Add reward txn
		transaction_manager.create_transaction(
			player_uid,
			player_address,
			TxnTypes.LUCKY_DRAW_REWARD,
			random_reward["desc"],
			random_reward["reward_type"],
			random_reward["reward_value"],
			status=txn_status
		)

		rewards = get_rewards(player_address)

		return api_response_result(request, ResultCode.SUCCESS, {
			"reward_idx": random_reward["idx"],
			"reward_type": random_reward["reward_type"],
			"reward_value": random_reward["reward_value"],
			"balance_emont_in_game": emont_bonus_manager.get_emont_balance(player_uid),
			"balance_energy": ema_energy_manager.get_available_energy(player_address),
			"current_rewards": rewards["current_rewards"],
			"to_claim_rewards": rewards["to_claim_rewards"],
			"spin_cost_emont": LD_SPIN_COST_EMONT_COST,
		})

