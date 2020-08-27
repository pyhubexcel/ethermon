# pylint: disable=protected-access
from threading import Lock
import datetime
from django import db
from django.db import models
from django.db.models.query import QuerySet
from django.conf import settings
import etheremon_lib.crypt
import common.utils

#Fields

class TinyIntegerField(models.SmallIntegerField):
	def db_type(self, connection):
		return "TINYINT"
	def formfield(self, **kwargs):
		defaults = {'min_value': -128, 'max_value': 127}
		defaults.update(kwargs)
		return super(TinyIntegerField, self).formfield(**defaults)

class PositiveTinyIntegerField(models.PositiveSmallIntegerField):
	def db_type(self, connection):
		return "TINYINT UNSIGNED"
	def formfield(self, **kwargs):
		defaults = {'min_value': 0, 'max_value': 255}
		defaults.update(kwargs)
		return super(PositiveTinyIntegerField, self).formfield(**defaults)

class PositiveAutoField(models.AutoField):
	def db_type(self, connection):
		if 'mysql' in connection.__class__.__module__:
			return 'INTEGER UNSIGNED AUTO_INCREMENT'
		return super(PositiveAutoField, self).db_type(connection)
	def formfield(self, **kwargs):
		defaults = {'min_value': 0, 'max_value': 2**32 - 1}
		defaults.update(kwargs)
		return super(PositiveAutoField, self).formfield(**defaults)

class PositiveBigIntegerField(models.BigIntegerField):
	empty_strings_allowed = False
	def db_type(self, connection):
		return "BIGINT UNSIGNED"
	def formfield(self, **kwargs):
		defaults = {'min_value': 0, 'max_value': models. BigIntegerField.MAX_BIGINT * 2 + 1}
		defaults.update(kwargs)
		return super(PositiveBigIntegerField, self).formfield(**defaults)

class BigAutoField(models.AutoField):
	def db_type(self, connection):
		if 'mysql' in connection.__class__.__module__:
			return 'BIGINT AUTO_INCREMENT'
		return super(BigAutoField, self).db_type(connection)
	def formfield(self, **kwargs):
		defaults = {'min_value': -models.BigIntegerField.MAX_BIGINT - 1, 'max_value': models.BigIntegerField.MAX_BIGINT}
		defaults.update(kwargs)
		return super(BigAutoField, self).formfield(**defaults)

class PositiveBigAutoField(models.AutoField):
	def db_type(self, connection):
		if 'mysql' in connection.__class__.__module__:
			return 'BIGINT UNSIGNED AUTO_INCREMENT'
		return super(PositiveBigAutoField, self).db_type(connection)
	def formfield(self, **kwargs):
		defaults = {'min_value': 0, 'max_value': models.BigIntegerField.MAX_BIGINT * 2 + 1}
		defaults.update(kwargs)
		return super(PositiveBigAutoField, self).formfield(**defaults)

#Database router

class DatabaseRouter(object):

	def db_for_read(self, model, **hints):
		if hasattr(model, 'Config'):
			if hasattr(model.Config, 'db_for_read'):
				return model.Config.db_for_read
			elif hasattr(model.Config, 'db_for_all'):
				return model.Config.db_for_all
		if (hasattr(settings, 'DATABASE_APPS_MAPPING') and
			(model._meta.app_label in settings.DATABASE_APPS_MAPPING)):
			return settings.DATABASE_APPS_MAPPING[model._meta.app_label]
		return 'default'

	def db_for_write(self, model, **hints):
		if hasattr(model, 'Config'):
			if hasattr(model.Config, 'db_for_write'):
				return model.Config.db_for_write
			elif hasattr(model.Config, 'db_for_all'):
				return model.Config.db_for_all
		if (hasattr(settings, 'DATABASE_APPS_MAPPING') and
			(model._meta.app_label in settings.DATABASE_APPS_MAPPING)):
			return settings.DATABASE_APPS_MAPPING[model._meta.app_label]
		return 'default'

#Advanced query set

class AdvancedQuerySet(QuerySet):
	def count(self):
		if self._result_cache is not None and not self._iter:
			return len(self._result_cache)
		query = self.query
		if (not query.where and
				query.high_mark is None and
				query.low_mark == 0 and
				not query.select and
				not query.group_by and
				not query.having and
				not query.distinct):
			cursor = db.connections[self.db].cursor()
			cursor.execute("SHOW TABLE STATUS LIKE %s", (self.model._meta.db_table,))
			return cursor.fetchall()[0][4]
		else:
			return self.query.get_count(using=self.db)

class AdvancedManager(models.Manager):
	def get_query_set(self):
		return AdvancedQuerySet(self.model, using=self._db)

class AdvancedModel(models.Model):
	objects = AdvancedManager()
	class Meta:
		app_label = ''
		abstract = True

def _partition_model_new(cls, *args, **kwargs):
	return cls(*args, **kwargs)

class PartitionModel(object):
	"""PartitionModel support db partition, table partition or both.

	Usage:

	class UserLoginLogTab(db.PartitionModel):
		id = db.BigAutoField(primary_key=True)
		uid = db.PositiveBigIntegerField()
		login_time = db.PositiveIntegerField()
		class Config:
			db_for_all = 'log_db_%s'
			# define static method as partition function
			@staticmethod
			def db_partition_func(s):
				return s.lower()
			# use helper function to define partition function
			partition_func = db.partition_by_datetime('%Y%m%d')
		class Meta:
			app_label = ''
			db_table = u'user_login_log_tab_%s'

	UserLoginLogTab(db_partition_key='SG',partition_key=time.time()).objects.filter(uid=100000)
	UserLoginLogTab(db_partition_id='sg',partition_id='20160101')(uid=100000,login_time=time.time()).save()
	"""

	_partition_models = {}
	_lock = Lock()

	def __new__(cls, *args, **kwargs):
		db_partition_id = None
		if 'db_partition_id' in kwargs:
			db_partition_id = kwargs.pop('db_partition_id')
		elif 'db_partition_key' in kwargs:
			db_partition_id = cls.Config.db_partition_func(kwargs.pop('db_partition_key'))
		partition_id = None
		if 'partition_id' in kwargs:
			partition_id = kwargs.pop('partition_id')
		elif 'partition_key' in kwargs:
			partition_id = cls.Config.partition_func(kwargs.pop('partition_key'))
		model_name = cls.__name__
		if db_partition_id is not None:
			model_name += '_%s' % db_partition_id
		if partition_id is not None:
			model_name += '_%s' % partition_id
		model_class = cls._partition_models.get(model_name)
		if model_class is not None:
			return model_class

		attrs = {}
		for key in cls.__dict__:
			attrs[key] = cls.__dict__[key]
		if 'objects' in attrs:
			attrs['objects'] = attrs['objects'].__class__()
		if db_partition_id is not None:
			if hasattr(cls, 'Config'):
				config = utils.dict_to_object(cls.Config.__dict__)
				if hasattr(config, 'db_for_read'):
					config.db_for_read = config.db_for_read % db_partition_id
				if hasattr(config, 'db_for_write'):
					config.db_for_write = config.db_for_write % db_partition_id
				if hasattr(config, 'db_for_all'):
					config.db_for_all = config.db_for_all % db_partition_id
				attrs['Config'] = config
		meta = utils.dict_to_object(cls.Meta.__dict__)
		if partition_id is not None:
			meta.db_table = meta.db_table % partition_id
		attrs['Meta'] = meta
		attrs['new'] = classmethod(_partition_model_new)

		with cls._lock:
			model_class = cls._partition_models.get(model_name)
			if model_class is not None:
				return model_class
			model_class = type(
				model_name,
				tuple([models.Model] + list(cls.__bases__[1:])),
				attrs
			)
			cls._partition_models[model_name] = model_class
		return model_class

def partition_by_mod(base):
	def func(n):
		return n % base
	return staticmethod(func)

def partition_by_div(base):
	def func(n):
		return n / base
	return staticmethod(func)

def partition_by_lower():
	def func(s):
		return s.lower()
	return staticmethod(func)

def partition_by_upper():
	def func(s):
		return s.upper()
	return staticmethod(func)

def partition_by_crc(base):
	def func(s):
		return crypt.crc32(s) % base
	return staticmethod(func)

def partition_by_datetime(fmt):
	def func(timestamp):
		return datetime.datetime.fromtimestamp(int(timestamp)).strftime(fmt)
	return staticmethod(func)

#Utils

def model_get_optional_result(func):
	""" Returns the first object of the queryset if the query returns results, else returns None. """
	def _func(*args, **kwargs):
		results = func(*args, **kwargs)
		try:
			return results[0]
		except IndexError:
			return None
	return _func

def model_to_dict(obj):
	return dict([(f.name, getattr(obj, f.name)) for f in obj._meta.fields])

def copy_model_object(obj):
	return utils.dict_to_object(model_to_dict(obj))

def copy_model_list(l):
	return [copy_model_object(v) for v in l]

def call_sp(using='default', sp_name='', args=()):
	cur = db.connections[using].cursor()
	query = 'call %s(%s);' % (sp_name, ','.join(['%s'] * len(args)))
	cur.execute(query, args)
	return cur.fetchall()

def call_sp_fetch_one(using='default', sp_name='', args=()):
	cur = db.connections[using].cursor()
	query = 'call %s(%s);' % (sp_name, ','.join(['%s'] * len(args)))
	cur.execute(query, args)
	return cur.fetchone()

def refresh_db_connections():
	db.reset_queries()
	db.close_old_connections()

#Init

def _patch_django_model():

	# apply patch for issue: https://code.djangoproject.com/ticket/26140
	if not hasattr(models.BinaryField, 'get_placeholder'):
		def default_binary_placeholder_sql(self, value):
			return '%s'
		def mysql_binary_placeholder_sql(self, value):
			return '_binary %s' if value is not None else '%s'
		def get_placeholder(self, value, connection):
			return connection.ops.binary_placeholder_sql(value)
		from django.db.backends import BaseDatabaseOperations
		from django.db.backends.mysql.base import DatabaseOperations
		BaseDatabaseOperations.binary_placeholder_sql = default_binary_placeholder_sql
		DatabaseOperations.binary_placeholder_sql = mysql_binary_placeholder_sql
		models.BinaryField.get_placeholder = get_placeholder

	# add slow log
	if hasattr(settings, 'DATABASE_OPTIONS') and settings.DATABASE_OPTIONS.get('slow_log'):
		# Example of settings:
		# DATABASE_OPTIONS = {
		# 	'slow_log': True,
		# 	'slow_log_threshold': 1000,
		# }
		import time
		import traceback
		from logger import log
		def _patch_fetch_all(func, threshold):
			def _fetch_all(self):
				start = time.time()
				result = func(self)
				elapsed = int((time.time() - start) * 1000)
				if elapsed >= threshold:
					tb = ''.join(traceback.format_list(traceback.extract_stack(limit=5)[:-2]))
					log.warning('db_slow_query|elapsed=%d,query=%s\n%s', elapsed, self.query.sql_with_params(), tb)
				return result
			return _fetch_all
		QuerySet._fetch_all = _patch_fetch_all(QuerySet._fetch_all, settings.DATABASE_OPTIONS.get('slow_log_threshold', 1000))

_patch_django_model()

def _create_db_object():
	# pylint: disable=invalid-name, attribute-defined-outside-init
	class _Object(object):
		pass
	obj = _Object()
	obj.BACKEND = 'django'
	for module in (db, models):
		for key in dir(module):
			if not hasattr(obj, key):
				setattr(obj, key, getattr(module, key))
	g = globals()
	for key in g:
		if not hasattr(obj, key):
			setattr(obj, key, g[key])
	return obj

db = _create_db_object()
