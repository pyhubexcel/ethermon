import os
from etheremon_lib import config

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DEBUG = config.DEBUG
TEST = config.TEST

LOGGER_CONFIG = {
	'log_dir': os.path.join(BASE_DIR, 'log'),
}

INSTALLED_APPS = (
	'etheremon_lib',
)

GEOIP_PATH = config.GEOIP_PATH

SECRET_KEY = '55j^pn#=dkep6+6t!c!hm)*oe0%y+4=n^xq18_hzr!i1qutil8'
DATABASES = config.DATABASES
DATABASE_ROUTERS = ['common.django_model.DatabaseRouter',]
TIME_ZONE = 'Asia/Singapore'