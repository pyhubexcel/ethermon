# pylint: disable=ungrouped-imports, wildcard-import
import inspect
import os
import sys	# pylint: disable=unused-import
import copy
import time
import json	# pylint: disable=unused-import
from contextlib import contextmanager
from functools import wraps
from common.logger import log
from common.convert import *


class ClassPropertyMetaClass(type):
	def __setattr__(cls, key, value):
		if key in cls.__dict__:
			obj = cls.__dict__.get(key)
			if obj and isinstance(obj, ClassPropertyDescriptor):
				return obj.__set__(cls, value)
		super(ClassPropertyMetaClass, cls).__setattr__(key, value)

class ClassPropertyDescriptor(object):
	def __init__(self, fget, fset=None):
		self.fget = fget
		self.fset = fset

	def __get__(self, obj, klass=None):
		if klass is None:
			klass = type(obj)
		return self.fget.__get__(obj, klass)()

	def __set__(self, obj, value):
		if not self.fset:
			raise AttributeError("can't set attribute")
		if inspect.isclass(obj):
			type_ = obj
			obj = None
		else:
			type_ = type(obj)
		return self.fset.__get__(obj, type_)(value)

	def setter(self, func):
		if not isinstance(func, (classmethod, staticmethod)):
			func = classmethod(func)
		self.fset = func
		return self

def classproperty(func):
	"""
		-- usage --
		1) simple read:
				...
				@classproperty
				def MY_VALUE(cls):
					return cls._MY_VALUE
				...

		2) simple write: (write by instance)
				...
				// add setter
				@MY_VALUE.setter
				def MY_VALUE(cls, value):
					cls._MY_VALUE = value

		3) complete write: (write by instance or class)
				...
				// add metaclass
				__metaclass__ = ClassPropertyMetaClass

	"""
	if not isinstance(func, (classmethod, staticmethod)):
		func = classmethod(func)
	return ClassPropertyDescriptor(func)

class Object:
	def __init__(self, **kwargs):
		self.__dict__.update(kwargs)

def dict_to_object(d):
	return Object(**d)

def create_object(**kwargs):
	return Object(**kwargs)

def find_first(f, seq):
	"""Return first item in sequence where f(item) == True."""
	for item in seq:
		if f(item):
			return item
	return None

def get_timestamp():
	return int(time.time())

def find_str(text, prefix, suffix=None):
	start = text.find(prefix)
	if start < 0:
		return None
	start += len(prefix)
	if suffix is None:
		return text[start:]
	end = text.find(suffix, start)
	if end < 0:
		return None
	return text[start:end]

def truncate_unicode(text, max_length, encoding='utf-8', ending=u'...'):
	encoded_str = text.encode(encoding)
	if len(encoded_str) <= max_length:
		return text
	max_length -= len(ending)
	if max_length < 0:
		max_length = 0
	encoded_str = encoded_str[:max_length]
	return encoded_str.decode(encoding, 'ignore') + ending

def exception_safe(exception_return=None, keyword=None, return_filter=copy.copy):
	def _exception_safe(func):
		@wraps(func)
		def _func(*args, **kwargs):
			try:
				return func(*args, **kwargs)
			except:
				if keyword is None:
					logging.exception('%s_exception', func.__name__)
				else:
					logging.exception('%s_exception', keyword)
				if return_filter:
					return return_filter(exception_return)
				else:
					return exception_return
		return _func
	return _exception_safe

@contextmanager
def directory(path):
	current_dir = os.getcwd()
	os.chdir(path)
	try:
		yield
	finally:
		os.chdir(current_dir)

IS_DJANGO_APP = False
IS_FLASK_APP = False

try:
	from django.conf import settings
	IS_DJANGO_APP = settings.configured
except:
	pass

if not IS_DJANGO_APP:
	try:
		import flask	# pylint: disable=unused-import
		IS_FLASK_APP = True
	except:
		pass

if IS_DJANGO_APP:
	from common.django_utils import *
elif IS_FLASK_APP:
	from flask_utils import *