# pylint: disable=redefined-outer-name
import sys
import time
import datetime
from functools import wraps
import flask	# pylint: disable=unused-import
from flask import Flask
from flask import request
from flask import Response
from flask import abort
from flask import sessions
from flask import session	# pylint: disable=unused-import
from jsonschema import Draft4Validator
from werkzeug.exceptions import HTTPException
from geo_utils import init_geo, geo_ip_to_country	# pylint: disable=unused-import
import jsonutils
import cache
import dbmodel
from form_validator import FormValidator
from useragent import UserAgent
from logger import log
import crypt

_app = None

def init_app(name, config):
	import socket
	if "gevent" in socket.socket.__module__:
		import pymysql
		pymysql.install_as_MySQLdb()
	static_url_path = None
	static_folder = None
	if 'STATIC_FOLDER' in dir(config):
		static_url_path = config.STATIC_URL
		static_folder = config.STATIC_FOLDER
		if static_url_path.endswith('/'):
			static_url_path = static_url_path[:-1]
	app = Flask(name, static_url_path=static_url_path, static_folder=static_folder)
	app.config.from_object(config)
	app.register_error_handler(400, error_handle_400)
	app.register_error_handler(404, error_handle_404)
	app.register_error_handler(500, error_handle_500)
	if 'LOGGER_CONFIG' in app.config and 'sentry_dsn' in app.config['LOGGER_CONFIG']:
		from raven.contrib.flask import Sentry
		Sentry(app, dsn=app.config['LOGGER_CONFIG']['sentry_dsn'])
	if 'I18N' in app.config:
		__import__(app.config['I18N'], fromlist=['*'])
	if 'CACHES' in app.config:
		cache.init_cache(app.config['CACHES'])
	if 'DATABASES' in app.config:
		db = dbmodel.init_db(app.config.get('DATABASE_BACKEND', ''), app.config['DATABASES'],
			app.config.get('DATABASE_OPTIONS'), app.config.get('DEBUG', False))
		if db.BACKEND == 'django':
			app.before_request(db.refresh_db_connections)
	if 'SESSION_COOKIE_NAME' in app.config:
		app.session_interface = _ServerSessionInterface(app)
	if 'GEOIP_PATH' in app.config:
		init_geo(app.config['GEOIP_PATH'])
	if app.config.get('HTTP_PROXY_FIX', False):
		from werkzeug.contrib.fixers import ProxyFix
		app.wsgi_app = ProxyFix(app.wsgi_app)
	global _app	# pylint: disable=global-statement
	_app = app
	return app

def get_app():
	return _app

def get_config():
	return _app.config

def route(*args, **kwargs):
	if 'endpoint' not in kwargs:
		if args:
			kwargs['endpoint'] = args[0]
		else:
			kwargs['endpoint'] = kwargs['rule']
	if 'methods' not in kwargs:
		kwargs['methods'] = ('GET', 'POST')
	return _app.route(*args, **kwargs)

def run_app():
	_app.run()

_error_pages = {
	400: '''<!DOCTYPE html>
<html>
<head>
<title>Bad request</title>
</head>
<body>
	<h1>400. Bad request</h1>
	<p>Sorry, but the request could not be understood by the server.</p>
</body>
</html>
''',
	404: '''<!DOCTYPE html>
<html>
<head>
<title>Page not found</title>
</head>
<body>
	<h1>404. Page not found</h1>
	<p>Sorry, but the requested page is not Found</p>
</body>
</html>
''',
	500: '''<!DOCTYPE html>
<html>
<head>
<title>Page unavailable</title>
</head>
<body>
	<h1>Page unavailable</h1>
	<p>Sorry, but the requested page is unavailable due to a server hiccup.</p>
	<p>Our engineers have been notified, so check back later.</p>
</body>
</html>
''',
}

def error_handle_400(error):
	return _error_pages[400], 400

def error_handle_404(error):
	return _error_pages[404], 404

def error_handle_500(error):
	return _error_pages[500], 500

def response_http_error(status_code):
	abort(status_code)

def response_http_400():
	return response_http_error(400)

def response_http_404():
	return response_http_error(404)

def response_http_500():
	return response_http_error(500)

def response_redirect(uri):
	response = Response(status=302)
	response.headers['Location'] = uri
	return response

def api_response(data):
	response = Response(jsonutils.to_json(data), content_type='application/json; charset=utf-8')
	return response

def get_request_ip(request):
	return request.environ['REMOTE_ADDR']

def get_request_url():
	return request.url[len(request.host_url):]

def ip_restrict(allow_list, error_handler=response_http_404):
	def _ip_restrict(func):
		@wraps(func)
		def _func(request, *args, **kwargs):
			ip = get_request_ip(request)
			if ip not in allow_list:
				log.warning('unauthorized_ip|ip=%s', ip)
				return error_handler()
			return func(request, *args, **kwargs)
		return _func
	return _ip_restrict

def parse_params(form, method='GET', data_format='FORM', error_handler=response_http_404, parse_ua=False):

	if isinstance(form, dict):
		if data_format == 'FORM':
			form = FormValidator(form)
		else:
			form = Draft4Validator(form)
	def _parse_params(func):
		@wraps(func)
		def _func(*args, **kwargs):
			log.warning('HERE MNA --- MM1')
			if request.method != method:
				log.warning('view_method_error|url=%s,method=%s', get_request_url().encode('utf-8'), request.method)
				return error_handler()
			if isinstance(form, FormValidator):
				if method == 'GET':
					formdata = request.args
				else:
					formdata = request.form
				try:
					data = form.normalize(formdata)
				except Exception as ex:
					log.warning('view_params_error|format=form,url=%s,error=%s,body=%s', get_request_url().encode('utf-8'), ex, request.get_data())
					return error_handler()
			else:
				if data_format == 'JSON':
					log.warning('HERE MNA --- MM')
					request_body = request.get_data()
					try:
						data = jsonutils.from_json(request_body)
					except Exception as ex:
						log.warning('view_params_error|format=json,url=%s,error=%s,body=%s', get_request_url().encode('utf-8'), ex, request_body)
						#return error_handler()
						data = {}
					if form is not None:
						params_errors = [e.message for e in form.iter_errors(data)]
						if params_errors:
							log.warning('view_params_error|format=json,url=%s,error=json_validotor:%s,body=%s',
								get_request_url().encode('utf-8'), ';'.join(params_errors), request_body)
							return error_handler()
				else:
					data = request.values
			data['request_ip'] = get_request_ip(request)
			if parse_ua:
				data['request_ua'] = UserAgent((request.headers.get('User-Agent', '')))
			return func(data, *args, **kwargs)
		return _func
	return _parse_params

def log_request(log_response=True, max_response_length=500, log_request_body=True, max_request_body_length=None, header_prefix=None):
	def _log_request(func):
		@wraps(func)
		def _func(*args, **kwargs):
			start = time.time()
			if log_request_body and request.content_length:
				request_body = request.get_data()
				if max_request_body_length and len(request_body) > max_request_body_length:
					request_body = request_body[:max_request_body_length] + '...'
			else:
				request_body = ''
			ex = None
			try:
				response = func(*args, **kwargs)
			except Exception as ex:
				ex_type, ex_value, ex_traceback = sys.exc_info()
				if not isinstance(ex, HTTPException):
					logging.exception('%s_exception', func.__name__)
			end = time.time()
			elapsed = int((end - start) * 1000)
			if ex is None:
				status_code = response.status_code
				if log_response:
					if (status_code == 301 or status_code == 302) and 'Location' in response.headers:
						response_body = response.headers['Location']
					elif not response.is_sequence:
						response_body = '<unreadable>'
					else:
						response_body = response.data
						if max_response_length and len(response_body) > max_response_length:
							response_body = response_body[:max_response_length] + '...'
				else:
					response_body = ''
			else:
				if isinstance(ex, HTTPException):
					status_code = ex.code
				else:
					status_code = 500
				response_body = 'exception:%s' % ex
			if header_prefix:
				header_body = {}
				for header_key, header_value in request.headers.iteritems():
					if header_key.startswith(header_prefix):
						header_body[header_key.lower()] = header_value
				log.data('http_request|ip=%s,elapsed=%d,method=%s,url=%s,body=%s,status_code=%d,response=%s,header_body=%s',
					get_request_ip(request), elapsed, request.method, get_request_url().encode('utf-8'), request_body, status_code, response_body, header_body)
			else:
				log.data('http_request|ip=%s,elapsed=%d,method=%s,url=%s,body=%s,status_code=%d,response=%s',
					get_request_ip(request), elapsed, request.method, get_request_url().encode('utf-8'), request_body, status_code, response_body)
			if ex is not None:
				raise ex_type, ex_value, ex_traceback
			return response
		return _func
	return _log_request

def cache_control(**kwargs):
	"""
	Any valid Cache-Control HTTP directive is valid in cache_control(). Here's a full list:
	public=True
	private=True
	no_cache=True
	no_store=True
	no_transform=True
	must_revalidate=True
	proxy_revalidate=True
	max_age=num_seconds
	s_maxage=num_seconds
	"""
	cache_control_list = []
	if kwargs.get('public'):
		cache_control_list.append('public')
	if kwargs.get('private'):
		cache_control_list.append('private')
	if kwargs.get('no_cache'):
		cache_control_list.append('no-cache')
	if kwargs.get('no_store'):
		cache_control_list.append('no-store')
	if kwargs.get('no_transform'):
		cache_control_list.append('no-transform')
	if kwargs.get('must_revalidate'):
		cache_control_list.append('must-revalidate')
	if kwargs.get('proxy_revalidate'):
		cache_control_list.append('proxy-revalidate')
	if 'max_age' in kwargs:
		cache_control_list.append('max-age=%d' % kwargs['max_age'])
	if 's_maxage' in kwargs:
		cache_control_list.append('s-maxage=%d' % kwargs['s_maxage'])
	cache_control_str = ', '.join(cache_control_list)
	def _cache_controller(viewfunc):
		def _cache_controlled(*args, **kw):
			response = viewfunc(*args, **kw)
			response.headers['Cache-Control'] = cache_control_str
			return response
		return _cache_controlled
	return _cache_controller

class _ServerSession(sessions.CallbackDict, sessions.SessionMixin):

	_session_key_length = 32
	_session_key_charset = '1234567890abcdefghijklmnopqrstuvwxyz'

	def __init__(self, initial=None):
		def on_update(self):
			self.modified = True
		if initial is None:
			sessions.CallbackDict.__init__(self, None, on_update)
			self.session_key = None
			self.session_timeout = 0
		else:
			sessions.CallbackDict.__init__(self, initial[0], on_update)
			self.session_key = initial[1]
			self.session_timeout = initial[2]
		self.modified = False

	def generate_session_key(self):
		self.session_key = crypt.random_string(self._session_key_length, self._session_key_charset)

	def get_data(self):
		return dict(self), self.session_key, self.session_timeout

class _ServerSessionInterface(sessions.SessionInterface):
	"""
	session saved in cache server
	config:
	SESSION_COOKIE_NAME: the name of the session cookie
	SESSION_COOKIE_DOMAIN: the domain for the session cookie. If this is not set, the cookie will be valid for all subdomains of SERVER_NAME.
	SESSION_COOKIE_PATH: the path for the session cookie. If this is not set the cookie will be valid for all of APPLICATION_ROOT or if that is not set for '/'.
	SESSION_COOKIE_HTTPONLY: controls if the cookie should be set with the httponly flag. Defaults to True.
	SESSION_COOKIE_SECURE: controls if the cookie should be set with the secure flag. Defaults to False.
	PERMANENT_SESSION_LIFETIME: the lifetime of a permanent session as datetime.timedelta object. This can also be an integer representing seconds.
	SESSION_CACHE_NAME: the name of cache server to save session data. Defaults to None.
	SESSION_CACHE_KEY: cache key prefix of session data. Defaults to 'session.'.
	"""
	session_class = _ServerSession

	def __init__(self, app):
		super(_ServerSessionInterface, self).__init__()
		self._cache = cache.get_cache(app.config.get('SESSION_CACHE_NAME'))
		self._cache_key_prefix = app.config.get('SESSION_CACHE_KEY', 'session.')
		if app.permanent_session_lifetime == 0:
			self._session_timeout = 24 * 60 * 60
			self._permanent = False
		else:
			self._session_timeout = sessions.total_seconds(app.permanent_session_lifetime)
			self._permanent = True
		self._cache_timeout = self._session_timeout * 2

	def get_expiration_time(self, app, session):
		if self._permanent:
			return datetime.utcnow() + app.permanent_session_lifetime
		else:
			return None

	def open_session(self, app, request):
		session_key = request.cookies.get(app.session_cookie_name)
		if not session_key:
			return self.session_class()
		cache_key = self._cache_key_prefix + session_key
		try:
			session_data = self._cache.get(cache_key)
			return self.session_class(session_data)
		except:
			logging.exception('session_get_fail|session_key=%s', session_key)
			return self.session_class()

	def save_session(self, app, session, response):
		#check delete session
		domain = self.get_cookie_domain(app)
		path = self.get_cookie_path(app)
		if not session:
			if session.modified:
				if session.session_key is not None:
					try:
						self._cache.delete(self._cache_key_prefix + session.session_key)
					except:
						logging.exception('session_delete_fail|session_key=%s', session.session_key)
				response.delete_cookie(app.session_cookie_name, domain=domain, path=path)
			return

		#generate session key
		set_cache = False
		if session.session_key is None:
			set_cache = True
			retry = 10
			try:
				while retry > 0:
					session.generate_session_key()
					if self._cache.get(self._cache_key_prefix + session.session_key) is None:
						break
					else:
						retry -= 1
			except:
				logging.exception('session_try_get_fail|session_key=%s', session.session_key)
				return
			if retry <= 0:
				log.warn('session_generate_name_fail|session_key=%s', session.session_key)
				return

		#check need set cache
		now = int(time.time())
		if not set_cache:
			if session.modified:
				set_cache = True
			elif now + self._session_timeout > session.session_timeout:
				set_cache = True

		#set session in cache
		if set_cache:
			session.session_timeout = now + self._cache_timeout
			try:
				self._cache.set(self._cache_key_prefix + session.session_key, session.get_data(), self._cache_timeout)
			except:
				logging.exception('session_set_fail|session_key=%s', session.session_key)

		#set cookie
		httponly = self.get_cookie_httponly(app)
		secure = self.get_cookie_secure(app)
		expires = self.get_expiration_time(app, session)
		response.set_cookie(app.session_cookie_name, session.session_key,
			expires=expires, httponly=httponly, domain=domain, path=path, secure=secure)


class MetricsMiddleware(object):
	'''
	To use metrics collector based on prometheus, we need to do following steps:

	1. Add `@MetricsMiddleware.monitor_request()` in the decorators of every requests, e.g.
	```
	@route('/<key>')
	@MetricsMiddleware.monitor_request()
	def resolve_random_url(key):
		...
	```

	2. Expose metrics information via `/metrics` endpoint.

	```
	@route('/metrics')
	def prometheus_metrics():
		return MetricsMiddleware.metrics_snapshot()
	```

	3. Set `prometheus_multiproc_dir` to the path of the folder which save prometheus db files.
	'''

	_inited = False

	@classmethod
	def monitor_request(cls):
		if not cls._inited:
			cls._inited = True
			from prometheus_client import Summary, Counter
			cls.requests_total = Counter('requests_total', 'Number of requests', ['status_code', 'endpoint'])
			cls.request_latency = Summary('request_latency_seconds', 'Request latency', ['status_code', 'endpoint'])
			cls.request_size = Summary('request_size_bytes', 'Request size', ['status_code', 'endpoint'])
			cls.response_size = Summary('response_size_bytes', 'Response size', ['status_code', 'endpoint'])

		def _monitor_request(func):
			@wraps(func)
			def _func(*args, **kwargs):
				import glob
				import os

				start = time.time()
				ex = None
				try:
					response = func(*args, **kwargs)
				except Exception as ex:
					ex_type, ex_value, ex_traceback = sys.exc_info()
				end = time.time()
				elapsed = (end - start)
				if ex is None:
					status_code = response.status_code
				else:
					if isinstance(ex, HTTPException):
						status_code = ex.code
					else:
						status_code = 500

				url_rule = request.url_rule.rule[:40]

				try:
					cls.requests_total.labels(status_code=status_code, endpoint=url_rule).inc()
					cls.request_latency.labels(status_code=status_code, endpoint=url_rule).observe(elapsed)
					if request.content_length:
						cls.request_size.labels(status_code=status_code, endpoint=url_rule).observe(request.content_length)
					if ex is None and response.data:
						cls.response_size.labels(status_code=status_code, endpoint=url_rule).observe(len(response.data))
				except:
					# Purge metrics mmap files when data corrupt.
					# Refer https://github.com/prometheus/client_python/issues/127 for details.
					for f in glob.glob(os.path.join(os.environ.get('prometheus_multiproc_dir'), '*.db')):
						try:
							os.remove(f)
						except:
							pass

				if ex is not None:
					raise ex_type, ex_value, ex_traceback
				return response
			return _func
		return _monitor_request

	@staticmethod
	def metrics_snapshot():
		import glob
		import os
		from flask import make_response

		ip = get_request_ip(request)
		if not ip == '' and \
			not ip.startswith('10.') and \
			not ip.startswith('172.') and \
			not ip.startswith('192.168.') and \
			not ip.startswith('127.'):
			return response_http_404()

		from prometheus_client import multiprocess
		from prometheus_client import generate_latest, CollectorRegistry, CONTENT_TYPE_LATEST

		registry = CollectorRegistry()
		multiprocess.MultiProcessCollector(registry)
		data = generate_latest(registry)

		# Clear unnecessary prometheus db files.
		import psutil
		now = int(time.time())
		for f in glob.glob(os.path.join(os.environ.get('prometheus_multiproc_dir'), '*.db')):
			parts = os.path.basename(f).split('_')
			if len(parts) == 2:
				pid, _unused = parts[1].split('.')
				pid = int(pid)
				try:
					if not psutil.pid_exists(pid) and (now - int(os.path.getmtime(f))) > 60:
						os.remove(f)
				except:
					pass

		response = make_response(data, 200)
		response.data = data
		response.headers['Content-type'] = CONTENT_TYPE_LATEST
		response.headers['Content-Length'] = str(len(data))
		return response
