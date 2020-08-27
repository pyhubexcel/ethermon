from etheremon_lib.models import *
from common.utils import get_timestamp


def get_setting(setting_id):
	return EtheremonDB.EmaSettingsTab.objects.filter(setting_id=setting_id).first()


def get_setting_value(setting_id):
	record = EtheremonDB.EmaSettingsTab.objects.filter(setting_id=setting_id).first()
	if not record:
		return 0
	return record.value


def set_setting(setting_id, value):
	return EtheremonDB.EmaSettingsTab.objects.filter(setting_id=setting_id).update(value=value, update_time=get_timestamp())


def set_or_create_setting(setting_id, name, value):
	setting = get_setting(setting_id)
	if not setting:
		setting = EtheremonDB.EmaSettingsTab(
			setting_id=setting_id,
			name=name,
			value=value,
			create_time=get_timestamp(),
			update_time=get_timestamp()
		)
	else:
		setting.value = value
		setting.update_time = get_timestamp()

	setting.save()
	return setting
