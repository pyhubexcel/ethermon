from common.utils import get_timestamp
from etheremon_lib.models import EtheremonDB

FREE_CLAIM_MAX_AMOUNT = 10
FREE_CLAIM_TIME = 60 * 60
FREE_CLAIM_AMOUNT = 1


def get_energy_by_trainer(trainer):
	return EtheremonDB.EmaPlayerEnergyTab.objects.filter(trainer=trainer).first()


def get_claimable_energy(last_claim_time, current_ts):
	if current_ts < last_claim_time:
		return 0
	period = int(current_ts - last_claim_time)
	energy_amount = (period / FREE_CLAIM_TIME) * FREE_CLAIM_AMOUNT
	if energy_amount > FREE_CLAIM_MAX_AMOUNT:
		return FREE_CLAIM_MAX_AMOUNT
	return energy_amount


def get_available_energy(trainer, record=None):
	if not record:
		record = EtheremonDB.EmaPlayerEnergyTab.objects.filter(trainer=trainer).first()
	return 0 if not record else record.init_amount + record.free_amount + record.paid_amount - record.consumed_amount - record.invalid_amount


def initialize_energy_if_not_exist(trainer_address, init_amount=10):
	record = EtheremonDB.EmaPlayerEnergyTab.objects.filter(trainer=trainer_address).first()
	current_ts = get_timestamp()

	if not record:
		record = EtheremonDB.EmaPlayerEnergyTab(
			trainer=trainer_address,
			init_amount=init_amount,
			free_amount=0,
			paid_amount=0,
			invalid_amount=0,
			consumed_amount=0,
			last_claim_time=0,
			create_time=current_ts,
			update_time=current_ts
		)
		record.save()

	return record


def add_energy(trainer_address, value):
	record = EtheremonDB.EmaPlayerEnergyTab.objects.filter(trainer=trainer_address).first()
	if record:
		record.update_time = get_timestamp()
		record.init_amount = record.init_amount + value
		record.save()
		return record
	else:
		return None


def consume_energy(trainer_address, value):
	current_ts = get_timestamp()
	record = EtheremonDB.EmaPlayerEnergyTab.objects.filter(trainer=trainer_address).first()
	available_energy = get_available_energy(trainer_address, record)

	if not record or available_energy < value:
		raise Exception("error_not_enough_energy")

	record.consumed_amount += value
	record.update_time = current_ts
	record.save()
	return record
