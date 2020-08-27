from common.logger import log
import common.convert

class _Context:
	geoip = None
	ip2location = None

class GeoLibType:
	GEOIP = 1
	IP2LOCATION = 2

def init_geo(geoip_path, lib_type=GeoLibType.GEOIP):
	_Context.geoip = None
	_Context.ip2location = None
	try:
		if lib_type == GeoLibType.GEOIP:
			import pygeoip
			_Context.geoip = pygeoip.GeoIP(geoip_path, pygeoip.MEMORY_CACHE)
		elif lib_type == GeoLibType.IP2LOCATION:
			import IP2Location
			_Context.ip2location = IP2Location.IP2Location(geoip_path)
		else:
			raise Exception('unsupported_geo_lib_type')
	except:
		logging.exception('geo_init_failed|type=%d,path=%s', lib_type, geoip_path)

def geo_ip_to_country(ip):
	try:
		if isinstance(ip, (int, long)):
			ip = convert.int_to_ip(ip)
		if _Context.geoip is not None:
			return _Context.geoip.country_code_by_addr(ip) or 'ZZ'
		elif _Context.ip2location is not None:
			country = _Context.ip2location.get_country_short(ip)
			if country == '-':
				country = 'ZZ'
			return country
		else:
			return 'ZZ'
	except:
		logging.exception('geo_ip_to_country_exception')
		return 'ZZ'
