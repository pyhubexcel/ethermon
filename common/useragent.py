import re

#TEST CASES: https://regex101.com/r/vB3oQ6/5

class UserAgent(object):

	_pattern = re.compile(r'(?P<product>\w+)\s*\/\s*(?P<version>\d+(?:\.\d+)*)\s*\(\s*(?P<device>(?:[^;()]|\([^;()]*\))*?)\s*;\s*(?P<os>[\w\.\-\s]*[\w\.\-])\s*;\s*(?P<lang>[\w\-]+)\s*;\s*(?:(?P<region>[\w]{2})\s*)(?:;\s*(?P<extra>(?:[\w\.\-\s]*[\w\.\-])?)\s*;?\s*)?\)')	# pylint: disable=line-too-long
	_pattern_apple = re.compile(r'ip(hone|ad|od)', re.I)
	_pattern_android = re.compile(r'android', re.I)

	def __init__(self, ua_string):
		self.raw_string = ua_string
		s = self._pattern.search(ua_string)
		if s:
			self._data = s.groupdict()
			self.version = map(int, self._data['version'].split('.'))
		else:
			self._data = {}
			if self._pattern_apple.search(ua_string):
				self._data['os'] = 'iOS'
			elif self._pattern_android.search(ua_string):
				self._data['os'] = 'Android'
			else:
				self._data['os'] = ''

	def __getattr__(self, item):
		return self._data.get(item, None)

	def is_mobile(self):
		os_string = self._data['os'].lower()
		return 'ios' in os_string or 'android' in os_string
