import sys
import os

def set_curr_path(path):
	os.chdir(os.path.dirname(os.path.abspath(path)))

def init_django(base_dir, settings):
	if base_dir not in sys.path:
		sys.path.append(base_dir)
	os.environ['DJANGO_SETTINGS_MODULE'] = settings
