import sys
import time
from functools import wraps
from lxml import etree
from django import http
from django.views import defaults
from django.core.signals import request_finished
from django.template.defaultfilters import register
from django.utils.safestring import mark_safe
from jsonschema import Draft4Validator
import common.jsonutils
import logging
from common.useragent import UserAgent
from common.form_validator import FormValidator
import common.convert

def response_http_400(request):
	return defaults.bad_request(request)

def response_http_404(request):
	return defaults.page_not_found(request)

def response_http_500(request):
	return defaults.server_error(request)

def response_redirect(request, uri):
	response = http.HttpResponse()
	response.status_code = 302
	response['Location'] = uri
	return response

def api_xml_response(request, data, xml_declaration=True, encoding='utf-8'):
	response = http.HttpResponse(etree.tostring(data, pretty_print=True, xml_declaration=xml_declaration, encoding=encoding))
	return response

def api_response(request, data):
	response = http.HttpResponse(jsonutils.to_json(data), content_type='application/json; charset=utf-8')
	return response

def get_request_ip(request):
	return request.META['REMOTE_ADDR']

def ip_restrict(allow_list, error_handler=response_http_404):
	def _ip_restrict(func):
		@wraps(func)
		def _func(request, *args, **kwargs):
			ip = get_request_ip(request)
			if ip not in allow_list:
				logging.warning('unauthorized_ip|ip=%s', ip)
				return error_handler(request)
			return func(request, *args, **kwargs)
		return _func
	return _ip_restrict

def parse_params(form, method='GET', data_format='FORM', error_handler=response_http_404, parse_ua=False, check_method=True, encoding=None):

	if isinstance(form, dict):
		if data_format == 'FORM':
			form = FormValidator(form)
		elif data_format == 'JSON':
			form = Draft4Validator(form)
	def _parse_params(func):
		@wraps(func)
		

		def _func(request, *args, **kwargs):

			if check_method and request.method != method:
				logging.warning('view_method_error|url=%s,method=%s', request.get_full_path().encode('utf-8'), request.method)
				return error_handler(request)
			if encoding:
				request.encoding = encoding
			if data_format == 'XML':
				try:
					xml_data = etree.XML(request.body)
				except:
					logging.warning('view_params_error|format=xml,url=%s,body=%s', request.get_full_path().encode('utf-8'), request.body)
					return error_handler(request)
				if not form(xml_data):
					logging.warning('view_params_schema_error|format=xml,url=%s,error=%s,body=%s', request.get_full_path().encode('utf-8'), form.error_log, request.body)
					return error_handler(request)
				data = {'xml_data': xml_data}
			else:
				if isinstance(form, (FormValidator, Draft4Validator)):
					if method == 'GET':
						formdata = request.GET
					elif data_format == 'JSON':
						try:
							formdata = common.jsonutils.from_json(request.body)
						except:
							logging.warning('view_params_error|format=json,url=%s,body=%s', request.get_full_path().encode('utf-8'), request.body)
							#return error_handler(request)
							formdata = {}
					else:
						formdata = request.POST
					try:
						if isinstance(form, FormValidator):
							data = form.normalize(formdata)
							print (data)
						else:
							form.validate(formdata)
							data = formdata
					except Exception as ex:
						print ('printing from django_utils')
						print(ex)	
						logging.warning('view_params_error|format=form,url=%s,error=%s,body=%s', request.get_full_path().encode('utf-8'), ex, formdata)
						return error_handler(request)
				else:
					if method == 'GET':
						dataform = form(request.GET)
					elif data_format == 'JSON':
						try:
							dataform = form(jsonutils.from_json(request.body))
						except:
							logging.warning('view_params_error|format=json,url=%s,body=%s', request.get_full_path().encode('utf-8'), request.body)
							return error_handler(request)
					elif data_format == 'MULTIPART':
						dataform = form(request.POST, request.FILES)
					else:
						dataform = form(request.POST)

					if not dataform.is_valid():
						if hasattr(request, '_body'):
							request_body = request.body
						else:
							request_body = '<unreadable>'
						logging.warning('view_params_error|format=form,url=%s,error=%s,body=%s', request.get_full_path().encode('utf-8'), dataform.errors.__repr__(), request_body)
						return error_handler(request)
					data = dataform.cleaned_data
			data['request_ip'] = get_request_ip(request)
			if parse_ua:
				data['request_ua'] = UserAgent(request.META.get('HTTP_USER_AGENT', ''))
			return func(request, data, *args, **kwargs)
		return _func
	return _parse_params

def log_request(log_response=True, max_response_length=500, log_request_body=True, max_request_body_length=None, header_prefix=None):
	def _log_request(func):
		@wraps(func)
		def _func(request, *args, **kwargs):
			start = time.time()
			ex = None
			try:
				response = func(request, *args, **kwargs)
			except Exception as ex:
				ex_type, ex_value, ex_traceback = sys.exc_info()
				logging.exception('%s_exception', func.__name__)
			end = time.time()
			elapsed = int((end - start) * 1000)
			if log_request_body:
				if hasattr(request, '_body'):
					request_body = request.body
				elif request.POST:
					request_body = 'POST:' + jsonutils.to_json(request.POST, ensure_bytes=True)
					if request.FILES:
						files_info = dict([(k, {v.name: v.size}) for k, v in request.FILES.iteritems()])
						request_body += ';FILES:' + jsonutils.to_json(files_info, ensure_bytes=True)
				else:
					request_body = ''
				if max_request_body_length and len(request_body) > max_request_body_length:
					request_body = request_body[:max_request_body_length] + '...'
			else:
				request_body = ''
			if ex is None:
				status_code = response.status_code
				if log_response:
					if (status_code == 301 or status_code == 302) and 'Location' in response:
						response_body = response['Location']
					else:
						response_body = response.content
						if max_response_length and len(response_body) > max_response_length:
							print ("$$$$")
							print (response_body[:max_response_length])
							print ("$$$$")
							response_body = response_body[:max_response_length] + '...'
				else:
					response_body = ''
			else:
				if ex is http.Http404:
					status_code = 404
				else:
					status_code = 500
				response_body = 'exception:%s' % ex
			if header_prefix:
				header_body = {}
				for header_key, header_value in request.META.iteritems():
					if header_key.startswith(header_prefix):
						header_body[header_key.lower()] = header_value
				logging.info('http_request|ip=%s,elapsed=%d,method=%s,url=%s,body=%s,status_code=%d,response=%s,header_body=%s',
					get_request_ip(request), elapsed, request.method, request.get_full_path().encode('utf-8'), request_body, status_code, response_body, header_body)
			else:
				logging.info('http_request|ip=%s,elapsed=%d,method=%s,url=%s,body=%s,status_code=%d,response=%s',
					get_request_ip(request), elapsed, request.method, request.get_full_path().encode('utf-8'), request_body, status_code, response_body)
			if ex is not None:
				raise ex_type, ex_value, ex_traceback
				#raise ex_type
			return response
		return _func
	return _log_request

def geo_ip_to_country(ip):
	try:
		from django.contrib.gis.geoip import GeoIP
		if isinstance(ip, (int, long)):
			return GeoIP().country(convert.int_to_ip(ip))['country_code'] or 'ZZ'
		else:
			return GeoIP().country(ip)['country_code'] or 'ZZ'
	except:
		logging.exception('geo_ip_to_country_exception')
		return 'ZZ'

_function_queue = []

def _run_all(sender, **kwargs):
	for func, args, kwargs in _function_queue:
		func(*args, **kwargs)
	_function_queue[:] = []

def init_after_response():
	request_finished.connect(_run_all)

def add_after_response(func, *args, **kwargs):
	_function_queue.append((func, args, kwargs))

@register.filter
def tojson(v):
	return mark_safe(jsonutils.to_json_html_safe(v))

class ProxyFixMiddleware(object):
	def process_request(self, request):
		meta = request.META
		forwarded_proto = meta.get('HTTP_X_FORWARDED_PROTO', '')
		forwarded_for = meta.get('HTTP_X_FORWARDED_FOR', '').split(',')
		forwarded_host = meta.get('HTTP_X_FORWARDED_HOST', '')
		forwarded_for = [x for x in [x.strip() for x in forwarded_for] if x]
		remote_addr = None
		if forwarded_for:
			remote_addr = forwarded_for[-1]
		if remote_addr is not None:
			meta['REMOTE_ADDR'] = remote_addr
		if forwarded_host:
			meta['HTTP_HOST'] = forwarded_host
		if forwarded_proto:
			meta['wsgi.url_scheme'] = forwarded_proto