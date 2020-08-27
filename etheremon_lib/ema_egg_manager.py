from etheremon_lib.models import *


def get_egg_data_by_obj(obj_id):
	return EtheremonDB.EmaEggDataTab.objects.filter(new_obj_id=obj_id).first()


def get_hatching_egg(trainer):
	return EtheremonDB.EmaEggDataTab.objects.filter(trainer=trainer).filter(new_obj_id=0).first()


def count_hatched_eggs(trainer):
	return EtheremonDB.EmaEggDataTab.objects.filter(trainer=trainer).filter(new_obj_id__gt=0).count()


def count_hatched_eggs_by_time(trainer, from_time, to_time):
	return EtheremonDB.EmaEggDataTab.objects\
		.filter(trainer=trainer)\
		.filter(new_obj_id__gt=0)\
		.filter(create_time__gte=from_time)\
		.filter(create_time__lte=to_time).count()
