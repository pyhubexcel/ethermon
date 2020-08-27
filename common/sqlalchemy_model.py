# pylint: disable=wildcard-import
import copy
import sqlalchemy
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

class ModelConflictException(Exception):
	pass

_sessions = {}

class _Object(object):
	pass

class _SimpleModel(object):
	def copy(self):
		return copy.copy(self)

def get_session(name):
	return _sessions.get(name)

def detach_session(inst):
	if isinstance(inst, list):
		for i in inst:
			i.detach_session()
		return inst
	elif isinstance(inst, Query):
		l = [i for i in inst]
		for i in inst:
			i.detach_session()
		return l
	else:
		inst.detach_session()
		return inst

def copy_model(result):
	if isinstance(result, (list, Query)):
		l = []
		for r in result:
			l.append(r.copy())
		return l
	else:
		return result.copy()

class _Model(object):

	_inited = False

	@classmethod
	def session(cls, master=True):
		if not cls._inited:
			if hasattr(cls, '__dbmaster__'):
				cls._session_master = _sessions.get(cls.__dbmaster__)
			else:
				cls._session_master = _sessions.get(cls.__dbname__)
			if hasattr(cls, '__dbslave__'):
				cls._session_slave = _sessions.get(cls.__dbslave__)
			else:
				cls._session_slave = _sessions.get(cls.__dbname__)
			cls._inited = True
		if master:
			return cls._session_master
		else:
			return cls._session_slave

	@classmethod
	def query(cls, master=False):
		query = cls.session(master).query(cls)
		query.model_class = cls
		return query

	@classmethod
	def execute(cls):
		query = cls.session().query(cls)
		query.model_class = cls
		return query

	@classmethod
	def clear_session_cache(cls):
		cls.session(False).expire_all()

	def save(self):
		# pylint: disable=protected-access
		session = self.session()
		status = inspect(self)
		if status.session_id != session.hash_key:
			if status.session is not None:
				status.session.expunge(self)
			if status.identity_key in session.identity_map:
				state = session.identity_map._dict[status.identity_key]
				if state._pending_mutations:
					raise ModelConflictException()
				session.identity_map.discard(state)
			session.add(self)
		if session.autocommit:
			session.flush()
		else:
			session.commit()

	def merge(self):
		session = self.session()
		status = inspect(self)
		if status.session_id != session.hash_key:
			if status.session is not None:
				status.session.expunge(self)
			session.merge(self)
		if session.autocommit:
			session.flush()
		else:
			session.commit()

	def delete(self):
		session = self.session()
		status = inspect(self)
		if status.session_id != session.hash_key:
			if status.session is not None:
				status.session.expunge(self)
		session.delete(self)
		if session.autocommit:
			session.flush()
		else:
			session.commit()

	def detach_session(self):
		status = inspect(self)
		if status.session is not None:
			status.session.expunge(self)

	def copy(self):
		obj = _SimpleModel()
		for key in dir(self):
			if not key.startswith('_') and key != 'metadata':
				value = getattr(self, key)
				if not callable(value):
					setattr(obj, key, value)
		return obj

Model = declarative_base(cls=_Model, name='Model')

def _create_db_object():
	# pylint: disable=invalid-name, attribute-defined-outside-init
	obj = _Object()
	obj.BACKEND = 'sqlalchemy'
	for module in sqlalchemy, sqlalchemy.orm:
		for key in module.__all__:
			if not hasattr(obj, key):
				setattr(obj, key, getattr(module, key))
	obj.get_session = get_session
	obj.detach_session = detach_session
	obj.copy_model = copy_model
	obj.Model = Model
	return obj

db = _create_db_object()

def init_db(config, debug=False):
	import urllib
	for key in config:
		value = config[key]
		conn_uri = '%s://%s:%s@%s:%s/%s' % (value['type'], urllib.quote(value['user'], safe=''), urllib.quote(value['password'], safe=''),
			urllib.quote(value['host'], safe=''), value.get('port', 3306), urllib.quote(value['db'], safe=''))
		if 'charset' in value:
			conn_uri += '?charset=' + urllib.quote(value['charset'], safe='')
		pool_recycle = value.get('conn_recycle_timeout', -1)
		engine = create_engine(conn_uri, max_overflow=0, pool_size=1, pool_recycle=pool_recycle, echo=debug)
		_sessions[key] = sessionmaker(bind=engine, autocommit=True)()
	return db
