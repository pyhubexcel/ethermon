# coding=utf-8
from common.utils import get_timestamp
from common.logger import log
from etheremon_lib.utils import api_response_result, geo_ip_to_country
import common.config
from etheremon_lib.constants import *


def pre_process_header():
	def _pre_process_header(func):
		def _func(request, *args, **kwargs):
			data = {}
			if len(args) > 0:
				data = args[0]

			headers = request.META
			try:
				data["_app_id"] = int(headers.get("HTTP_X_EMON_APP_ID", 0))
				data["_access_token"] = headers.get("HTTP_X_EMON_ACCESS_TOKEN")
				data["_api_version"] = headers.get("HTTP_X_EMON_API_VERSION", 0)
				data["_client_type"] = int(headers.get("HTTP_X_EMON_CLIENT_TYPE", 0))
				data["_client_version"] = str(headers.get("HTTP_X_EMON_CLIENT_VERSION", ""))
				data["_client_id"] = str(headers.get("HTTP_X_EMON_CLIENT_ID", ""))
				data["_client_language"] = str(headers.get("HTTP_X_EMON_CLIENT_LANGUAGE", "en"))
			except Exception as err:
				logging.exception("header_invalid|headers=%s", headers)
				return api_response_result(request, ResultCode.ERROR_HEADER)

			# find ip country
			country_code_by_ip = geo_ip_to_country(request.META['REMOTE_ADDR'])  # 'ZZ'
			data['_country_by_ip'] = country_code_by_ip
			data['_ip'] = request.META['REMOTE_ADDR']

			if len(args) > 0:
				return func(request, *args, **kwargs)
			else:
				return func(request, data, *args, **kwargs)

		return _func

	return _pre_process_header
