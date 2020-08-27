"""
This library provide database ORM based on django models and sqlalchemy.

Usage:

1. Use independently

# Django backend

from common import dbmodel
config = {...} # Same as DATABASES in django settings
db = dbmodel.init_db('django', config)
# The usage is same as django models

# sqlalchemy backend

from common import dbmodel

config = {
	'test_db.master':  {
		'type': 'mysql',
		'host': '127.0.0.1',
		'port': 3306,
		'user': 'test_user',
		'password': '****',
		'db': 'test_db',
		'charset': 'utf8mb4',
		'conn_recycle_timeout': 60 * 60,
	},
	'test_db.slave':  {
		'type': 'mysql',
		'host': '127.0.0.1',
		'port': 3306,
		'user': 'test_user',
		'password': '****',
		'db': 'test_db',
		'charset': 'utf8mb4',
		'conn_recycle_timeout': 60 * 60,
	},
}

db = dbmodel.init_db('sqlalchemy', config)

class TestDB:

	class TestTab(db.Model):
		__dbmaster__ = 'test_db.master'	#master db id
		__dbslave__ = 'test_db.slave'	#slave db id
		__tablename__ = 'test_tab'	#table name
		id = db.Column(db.Integer, primary_key=True, autoincrement=True)
		value = db.Column(db.Unicode(10), nullable=True)

#query
result = TestDB.TestTab.query().filter_by(value=u'v0')
for row in result:
	print row.id, row.value

#if you want to modify result but don't want to update db, call detach_session or copy_model
db.detach_session(result)
result[0].value = u'v0'	#will not affect db

#add by save
row = TestDB.TestTab(value=u'v0')
row.save()

#update by save
row = TestDB.TestTab.query().filter_by(id=1).one()
row.value = u'v1'	#if you don't call save(), this change may also updated to db
row.save()

#update by execute
TestDB.TestTab.execute().filter_by(id=1).update({'value': u'v2'})

#delete by query
TestDB.TestTab.query().filter_by(id=1).one().delete()

#delete by execute
TestDB.TestTab.execute().filter_by(id=1).delete()

Notes for sqlalchemy backend:
(1) This library is not thread safe, not support multi-threading.
(2) The query method of Model return the Query object of slave session,
    the execute method of Model  return the Query object of master session.
(3) If you modify the fields in result return by query, it may be updated to db.
    You can call detach_session or copy_model object before modify.
(4) If the db is configured as read write splitting, the reading and writing sessions are different.
    Sqlalchemy maintain cache in each session, and the writing operation will not reset the cache in read session.
    That means when you access query set after write, the data may not be updated.
    So it suggest to create new query to get data, don't reuse the query object.
    If you want to keep the query result, call copy_model or detach_session.
(5) If you integrate this with datacache, call detach_session or copy_model in load_data.
(6) Since this library uses some tricky ways to bypass sqlalchemy session and transaction mechanism,
    please test before use it for unusual case, don't assume anything.

2. Use in Django

# Directly import db from django_model without call init_db
from common.django_model import db

# Or import db from dbmodel, need call init_db
from common import dbmodel
db = dbmodel.init_db('django', None)

3. Use in Flask

# Add DATABASE_BACKEND, DATABASES, etc. in config file,
# the flask_utils.init_app will call dbmodel.init_db automatically
# then import db from dbmodel.
from dbmodel import db
"""

db = None

def init_db(backend, databases, database_options=None, debug=False):
	backend = backend.lower()
	global db	# pylint: disable=global-statement
	if backend == 'django':
		if databases is not None:
			import django
			from django.conf import settings
			django_config = {
				'DEBUG': debug,
				'DATABASES': databases,
				'DATABASE_ROUTERS': ['common.django_model.DatabaseRouter',]
			}
			if database_options is not None:
				django_config['DATABASE_OPTIONS'] = database_options
			settings.configure(**django_config)
			if hasattr(django, 'setup'):
				django.setup()
		import common.django_model
		db = common.django_model.db
	else:
		import sqlalchemy_model
		db = sqlalchemy_model.init_db(databases)
	return db

def get_db():
	return db
