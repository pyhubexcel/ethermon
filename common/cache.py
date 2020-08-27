# pylint: disable=redefined-builtin, too-many-lines, too-many-public-methods
import sys
import re
try:
	import cPickle as pickle
except ImportError:  # pragma: no cover
	import pickle
import random
from collections import defaultdict
import platform
import time
import binascii
import etheremon_lib.crypt

_set = set

_PY2 = sys.version_info[0] == 2

if _PY2:

	_integer_types = (int, long)

	_iteritems = lambda d: d.iteritems()

	def _to_native(x, charset='utf-8', errors='strict'):
		if x is None or isinstance(x, str):
			return x
		return x.encode(charset, errors)

else:

	_integer_types = (int, )

	_iteritems = lambda d: iter(d.items())

	def _to_native(x, charset='utf-8', errors='strict'):
		if x is None or isinstance(x, str):
			return x
		return x.decode(charset, errors)

def _items(dictorseq):
	"""Wrapper for efficient iteration over dict represented by dicts
	or sequences::

		>>> for k, v in _items((i, i*i) for i in xrange(5)):
		...	assert k*k == v

		>>> for k, v in _items(dict((i, i*i) for i in xrange(5))):
		...	assert k*k == v

	"""
	if hasattr(dictorseq, 'items'):
		return _iteritems(dictorseq)
	return dictorseq

def _cmemcache_hash(key):
	return (((binascii.crc32(_to_native(key)) & 0xffffffff) >> 16) & 0x7fff) or 1

_DEFAULT_CACHE_TIMEOUT = 300
_DEFAULT_SOCKET_TIMEOUT = 3

if platform.system().lower() == 'linux':
	import socket
	_TCP_KEEP_ALIVE_OPTIONS = {
		socket.TCP_KEEPIDLE: 30,
		socket.TCP_KEEPINTVL: 5,
		socket.TCP_KEEPCNT: 5,
	}
else:
	_TCP_KEEP_ALIVE_OPTIONS = {}

class BaseCache(object):
	"""Baseclass for the cache systems.  All the cache systems implement this
	API or a superset of it.

	:param default_timeout: the default timeout (in seconds) that is used if no
							timeout is specified on :meth:`set`.
	"""

	def __init__(self, config):
		self._client = None
		self.default_timeout = config.get('default_timeout', _DEFAULT_CACHE_TIMEOUT)

	@property
	def raw_client(self):
		"""Get raw cache client.

		:returns: Underlying cache client object.
		"""
		return self._client

	def get(self, key):
		"""Look up key in the cache and return the value for it.

		:param key: the key to be looked up.
		:returns: The value if it exists and is readable, else ``None``.
		"""
		return None

	def delete(self, key, noreply=False):
		"""Delete `key` from the cache.

		:param key: the key to delete.
		:param noreply: instructs the server to not send the reply.
		:returns: Whether the key has been deleted.
		:rtype: boolean
		"""
		return True

	def get_list(self, keys):
		"""Returns a list of values for the given keys.
		For each key a item in the list is created::

			foo, bar = cache.get_list("foo", "bar")

		Has the same error handling as :meth:`get`.

		:param keys: The function accepts multiple keys as positional
					 arguments.
		"""
		values = self.get_many(keys)
		return [values.get(key) for key in keys]

	def get_many(self, keys):
		"""Like :meth:`get_list` but return a dict::
		If the given key is missing, it will be missing from the response dict.

			d = cache.get_many("foo", "bar")
			foo = d["foo"]
			bar = d["bar"]

		:param keys: The function accepts multiple keys as positional
					 arguments.
		"""
		return dict([(key, self.get(key)) for key in keys])

	def set(self, key, value, timeout=None, noreply=False):
		"""Add a new key/value to the cache (overwrites value, if key already
		exists in the cache).

		:param key: the key to set
		:param value: the value for the key
		:param timeout: the cache timeout for the key.
						If not specified, it uses the default timeout.
						If specified 0, it will never expire.
		:param noreply: instructs the server to not send the reply.
		:returns: Whether the key existed and has been set.
		:rtype: boolean
		"""
		return True

	def add(self, key, value, timeout=None, noreply=False):
		"""Works like :meth:`set` but does not overwrite the values of already
		existing keys.

		:param key: the key to set
		:param value: the value for the key
		:param timeout: the cache timeout for the key.
						If not specified, it uses the default timeout.
						If specified 0, it will never expire.
		:param noreply: instructs the server to not send the reply.
		:returns: Same as :meth:`set`, but also ``False`` for already
				  existing keys.
		:rtype: boolean
		"""
		return True

	def set_many(self, data, timeout=None, noreply=False):
		"""Sets multiple keys and values from a dict.

		:param data: a dict with the keys/values to set.
		:param timeout: the cache timeout for the key.
						If not specified, it uses the default timeout.
						If specified 0, it will never expire.
		:param noreply: instructs the server to not send the reply.
		:returns: Whether all given keys have been set.
		:rtype: boolean
		"""
		rv = True
		for key, value in _items(data):
			if not self.set(key, value, timeout):
				rv = False
		return rv

	def delete_many(self, keys, noreply=False):
		"""Deletes multiple keys at once.

		:param keys: The function accepts multiple keys as positional
					 arguments.
		:param noreply: instructs the server to not send the reply.
		:returns: Whether all given keys have been deleted.
		:rtype: boolean
		"""
		return all(self.delete(key) for key in keys)

	def clear(self):
		"""Clears the cache.  Keep in mind that not all caches support
		completely clearing the cache.
		:returns: Whether the cache has been cleared.
		:rtype: boolean
		"""
		return True

	def incr(self, key, delta=1, noreply=False):
		"""Increments the value of a key by `delta`.  If the key does
		not yet exist it is initialized with `delta`.

		For supporting caches this is an atomic operation.

		:param key: the key to increment.
		:param delta: the delta to add.
		:param noreply: instructs the server to not send the reply.
		:returns: The new value or ``None`` for backend errors.
		"""
		value = (self.get(key) or 0) + delta
		return value if self.set(key, value) else None

	def decr(self, key, delta=1, noreply=False):
		"""Decrements the value of a key by `delta`.  If the key does
		not yet exist it is initialized with `-delta`.

		For supporting caches this is an atomic operation.

		:param key: the key to increment.
		:param delta: the delta to subtract.
		:param noreply: instructs the server to not send the reply.
		:returns: The new value or `None` for backend errors.
		"""
		value = (self.get(key) or 0) - delta
		return value if self.set(key, value) else None

	def blpop(self, key, timeout=0):
		"""Blocking pop a value from the head of the list.

		:param key: the key of list
		:param timeout: blocking timeout, 0 means block indefinitely
		:returns: The popped value or None if timeout.
		"""
		raise NotImplementedError()

	def brpop(self, key, timeout=0):
		"""Blocking pop a value from the tail of the list.

		:param key: the key of list
		:param timeout: blocking timeout, 0 means block indefinitely
		:returns: The popped value or None if timeout.
		"""
		raise NotImplementedError()

	def lindex(self, key, index):
		"""Return the item from list at position `index`.

		:param key: the key of list.
		:param index: the position, can be negative.
		:returns: The value at position `index` or None if index is out of range.
		"""
		raise NotImplementedError()

	def llen(self, key):
		"""Return the number of elements in list.

		:param key: the key of list.
		:returns: number of elements in list.
		:rtype: int
		"""
		raise NotImplementedError()

	def lpop(self, key):
		"""Pop a value from the head of list.

		:param key: the key of list.
		:returns: The popped value or None if list is empty.
		"""
		raise NotImplementedError()

	def lpush(self, key, value):
		"""Push a value to the head of the list.

		:param key: the key of list.
		:param value: the value to be pushed.
		:returns: Whether the value has been added to list.
		:rtype: boolean
		"""
		raise NotImplementedError()

	def lrange(self, key, start=0, end=-1):
		"""Return a slice of the list.

		:param key: the key of list.
		:param start: the start position, can be negative.
		:param end: the end position, can be negative.
		:returns: The values between `start` and `end`.
		:rtype: list
		"""
		raise NotImplementedError()

	def ltrim(self, key, start, end):
		"""Trim the list, removing all values not within the slice.

		:param key: the key of list.
		:param start: the start position, can be negative.
		:param end: the end position, can be negative.
		:returns: whether the list has been trimmed.
		:rtype: boolean
		"""
		raise NotImplementedError()

	def rpop(self, key):
		"""Pop a value from the tail of list.

		:param key: the key of list.
		:returns: The popped value or None if list is empty.
		"""
		raise NotImplementedError()

	def rpush(self, key, value):
		"""Push a value to the tail of the list.

		:param key: the key of list.
		:param value: the value to be pushed.
		:returns: whether the value has been added to list.
		:rtype: boolean
		"""
		raise NotImplementedError()

	def sadd(self, key, value):
		"""Add a value to the set.

		:param key: the key of set to add.
		:param value: the value to be added.
		:returns: whether the value has been added to set.
		:rtype: boolean
		"""
		raise NotImplementedError()

	def scard(self, key):
		"""Return the number of elements in set.

		:param key: the key of set.
		:returns: number of elements in set.
		:rtype: int
		"""
		raise NotImplementedError()

	def sismember(self, key, value):
		"""Return whether the value is a member of set.

		:param key: the key of set.
		:param value: the value to be checked.
		:returns: whether the `value` is a member of set.
		:rtype: boolean
		"""
		raise NotImplementedError()

	def smembers(self, key):
		"""Return all the members of set.

		:param key: the key of set.
		:returns: all the members value of set.
		:rtype: set
		"""
		raise NotImplementedError()

	def srandmember(self, key):
		"""Return a random member of set.

		:param key: the key of set.
		:returns: random member or None if set is empty.
		"""
		raise NotImplementedError()

	def srem(self, key, value):
		"""Remove value from set.

		:param key: the key of set.
		:param value: the value to be removed.
		:returns: whether the `value` has been removed from set.
		:rtype: boolean
		"""
		raise NotImplementedError()

	def hgetall(self, key):
		"""Look up hash in the cache and return all fields and values for it.

		:param key: the key of hash to be looked up.
		:returns: The dict value of hash, if empty, return {}.
		:rtype: dict
		"""
		raise NotImplementedError()

	def hget(self, key, field):
		"""Look up field in the hash and return the value for it.

		:param key: the key of hash to be looked up.
		:param field: the filed in the hash to be looked up.
		:returns: The value if it exists and is readable, else ``None``.
		"""
		raise NotImplementedError()

	def hset(self, key, field, value, timeout=None, noreply=False):
		"""Add a new filed/value to the hash in cache (overwrites value, if key already
		exists in the cache).

		:param key: the key of hash to set
		:param key: the field in the hash to set
		:param value: the value for the field
		:param timeout: the cache timeout for the field.
						If not specified, it uses the default timeout.
						If specified 0, it will never expire.
		:param noreply: instructs the server to not send the reply.
		:returns: Whether the key existed and has been set.
		:rtype: boolean
		"""
		raise NotImplementedError()

	def hdel(self, key, field, noreply=False):
		"""Delete field of hash from the cache.

		:param key: the key of hash to delete
		:param key: the field in the hash to delete
		:param noreply: instructs the server to not send the reply.
		:returns: Whether the key has been deleted.
		:rtype: boolean
		"""
		raise NotImplementedError()

	def hexists(self, key, field):
		"""Check whether `field` is an existing field in the hash.

		:param key: the key of hash.
		:param field: the filed to be checked.
		:returns: Whether `field` is an existing field in the hash.
		:rtype: boolean
		"""
		return self.hget(key, field) is not None

	def hlen(self, key):
		"""Get number of fields contained in the hash.

		:param key: the key of hash.
		:returns: The number of fields contained in the hash.
		:rtype: int
		"""
		return len(self.hgetall(key))

	def zadd(self, key, value, score):
		"""Add value to sorted set.

		:param key: the key of sorted set.
		:param value: the value to be added.
		:param score: the score of the value.
		:returns: Whether the value has been set.
		:rtype: boolean
		"""
		raise NotImplementedError()

	def zcard(self, key):
		"""Return the number of values in sorted set.

		:param key: the key of sorted set.
		:returns: The number of values in sorted set.
		:rtype: int
		"""
		raise NotImplementedError()

	def zcount(self, key, min, max):
		"""Returns the number of values in the sorted set `key` with a score between `min` and `max`.

		:param key: the key of sorted set.
		:param min: min score.
		:param max: max score.
		:returns: The number of values.
		:rtype: int
		"""
		raise NotImplementedError()

	def zincrby(self, key, value, delta=1):
		"""Increment the score of `value` in sorted set `key` by `delta`.

		:param key: the key of sorted set.
		:param value: the value to be incremented.
		:param delta: increment amount.
		:returns: The new score.
		:rtype: int
		"""
		raise NotImplementedError()

	def zrange(self, key, start=0, end=-1, reverse=False, withscores=False):
		"""Return a range of values from sorted set `key` between `start` and `end`.

		:param key: the key of sorted set.
		:param start: start index.
		:param end: end index.
		:param reverse: sorted in descending order.
		:param withscores: return the scores along with the values.
		:returns: If withscores is True, return a list of (value, score) pairs, otherwise return a list of values.
		:rtype: list
		"""
		raise NotImplementedError()

	def zrangebyscore(self, key, min, max, start=None, num=None, reverse=False, withscores=False):
		"""Return a range of values from sorted set `key` with scores between `min` and `max`.

		:param key: the key of sorted set.
		:param min: min score.
		:param max: max score.
		:param start: start offset.
		:param num: limit count.
		:param reverse: sorted in descending order.
		:param withscores: return the scores along with the values.
		:returns: If withscores is True, return a list of (value, score) pairs, otherwise return a list of values.
		:rtype: list
		"""
		raise NotImplementedError()

	def zrank(self, key, value, reverse=False):
		"""Return the rank of `value` in sorted set.

		:param key: the key of sorted set.
		:param value: the value to be checked.
		:param reverse: sorted in descending order.
		:returns: The rank of `value` in sorted set `key` or None if not existed.
		:rtype: int
		"""
		raise NotImplementedError()

	def zrem(self, key, value):
		"""Remove the `value` in sorted set.

		:param key: the key of sorted set.
		:param value: the value to be removed.
		:returns: Whether the `value` has been removed.
		:rtype: boolean
		"""
		raise NotImplementedError()

	def zremrangebyrank(self, key, start, end, reverse=False):
		"""Remove the values in sorted set with scores between `start` and `end`.

		:param key: the key of sorted set.
		:param start: start index.
		:param end: end index.
		:param reverse: sorted in descending order.
		:returns: The number of values removed.
		:rtype: int
		"""
		raise NotImplementedError()

	def zremrangebyscore(self, key, min, max):
		"""Remove the values in sorted set with scores between `min` and `max`.

		:param key: the key of sorted set.
		:param min: min score.
		:param max: max score.
		:returns: The number of values removed.
		:rtype: int
		"""
		raise NotImplementedError()

	def zscore(self, key, value):
		"""Return the score of `value` in sorted set.

		:param key: the key of sorted set.
		:param value: the value to be checked.
		:returns: The score of `value` in sorted set `key` or None if not existed.
		:rtype: float
		"""
		raise NotImplementedError()

	def zunionstore(self, dest, keys, aggregate=None):
		"""Union multiple sorted sets into a new sorted set.

		:param dest: destination sorted set.
		:param keys: keys of sorted sets to be aggregated.
		:param aggregate: specify how the results of the union are aggregated, defaults to SUM.
		:returns: The number of elements in the resulting sorted set at destination.
		:rtype: int
		"""
		raise NotImplementedError()

	def expire(self, key, timeout):
		"""Set a timeout on key. After the timeout has expired, the key will automatically be deleted.

		:param key: key to set timeout.
		:param timeout: timeout value in seconds.
		:returns: True if timeout was set, False if key does not exist or timeout could not be set.
		:rtype: boolean
		"""
		raise NotImplementedError()

	def geoadd(self,  key, longitude, latitude, member):
		"""Adds the specified geospatial items (latitude, longitude, name) to the specified key

		:param key: the key of sorted set
		:param longitude: double
		:param latitude: double
		:param member: member need to set.
		:returns: Whether the member has been added.
		:rtype: int
		"""
		raise NotImplementedError()

	def geopos(self, key, member):
		"""Return the positions (longitude,latitude) of specified membersof the geospatial index
		represented by the sorted set at key.

		:param key: the key of sorted set
		:param member: member need to get.
		:param noreply: instructs the server to not send the reply.
		:returns: position
		:rtype: list
		"""
		raise NotImplementedError()

class NullCache(BaseCache):
	"""A cache that doesn't cache.  This can be useful for unit testing.

	:param default_timeout: a dummy parameter that is ignored but exists
							for API compatibility with other caches.
	"""


class MemoryCache(BaseCache):
	"""A cache that save data in memory.

	:param default_timeout: the default timeout (in seconds) that is used if no
							timeout is specified on :meth:`set`.
	:param trim_interval: the interval (in seconds) to trim data.
	"""

	_DEFAULT_TRIM_INTERVAL = 60

	def __init__(self, config):
		BaseCache.__init__(self, config)
		self._trim_interval = config.get('trim_interval', self._DEFAULT_TRIM_INTERVAL)
		self._data = {}
		self._last_trim_time = time.time()

	@property
	def raw_client(self):
		return self._data

	def get(self, key):
		key = _to_native(key)
		data = self._data.get(key)
		if data is None:
			return None
		if data[0] is not None and data[0] < time.time():
			del self._data[key]
			return None
		return data[1]

	def delete(self, key, noreply=False):
		self._trim_data()
		key = _to_native(key)
		self._data.pop(key, None)
		return True

	def get_many(self, keys):
		values = {}
		now = time.time()
		for key in keys:
			key = _to_native(key)
			data = self._data.get(key)
			if data is not None and (data[0] is None or data[0] >= now):
				values[key] = data[1]
		return values

	def set(self, key, value, timeout=None, noreply=False):
		self._trim_data()
		key = _to_native(key)
		self._data[key] = (self._normalize_timeout(timeout), value)
		return True

	def add(self, key, value, timeout=None, noreply=False):
		self._trim_data()
		key = _to_native(key)
		data = self._data.get(key)
		if data is not None and (data[0] is None or data[0] >= time.time()):
			return False
		self._data[key] = (self._normalize_timeout(timeout), value)
		return True

	def clear(self):
		self._data = {}
		return True

	def incr(self, key, delta=1, noreply=False):
		key = _to_native(key)
		data = self._data.get(key)
		if data is None or (data[0] is not None and data[0] < time.time()):
			self._data[key] = (None, delta)
			return delta
		value = data[1]
		if isinstance(value, (int, long, float)):
			value += delta
		elif isinstance(value, (str, unicode)):
			try:
				value = type(value)(int(value) + delta)
			except:
				return None
		else:
			return None
		self._data[key] = (None, value)
		return int(value)

	def decr(self, key, delta=1, noreply=False):
		return self.incr(key, -delta, noreply)

	def _normalize_timeout(self, timeout):
		if timeout is None:
			timeout = time.time() + self.default_timeout
		elif timeout == 0:
			timeout = None
		else:
			timeout = time.time() + timeout
		return timeout

	def _trim_data(self):
		now = time.time()
		if self._last_trim_time + self._trim_interval < now:
			trim_keys = []
			for key, (timeout, _value) in self._data.iteritems():
				if timeout is not None and timeout < now:
					trim_keys.append(key)
			for key in trim_keys:
				del self._data[key]
			self._last_trim_time = now


_test_memcached_key = re.compile(r'[^\x00-\x21\xff]{1,250}$').match
_PYLIBMC_BEHAVIORS = {
	'connect_timeout': _DEFAULT_SOCKET_TIMEOUT * 1000,
	'send_timeout': _DEFAULT_SOCKET_TIMEOUT * 1000 * 1000,
	'receive_timeout': _DEFAULT_SOCKET_TIMEOUT * 1000 * 1000,
}

class MemcachedCache(BaseCache):
	"""A cache that uses memcached as backend.

	This cache looks into the following packages/modules to find bindings for
	memcached:

		- ``pylibmc``
		- ``google.appengine.api.memcached``
		- ``memcached``

	Implementation notes:  This cache backend works around some limitations in
	memcached to simplify the interface.  For example unicode keys are encoded
	to utf-8 on the fly.  Methods such as :meth:`~BaseCache.get_many` return
	the keys in the same format as passed.  Furthermore all get methods
	silently ignore key errors to not cause problems when untrusted user data
	is passed to the get methods which is often the case in web applications.

	:param host: memcached server host.
	:param port: memcached server port.
	:param default_timeout: the default timeout that is used if no timeout is
							specified on :meth:`~BaseCache.set`.
	:param key_prefix: a prefix that is added before all keys.  This makes it
					   possible to use the same memcached server for different
					   applications.  Keep in mind that
					   :meth:`~BaseCache.clear` will also clear keys with a
					   different prefix.
	"""

	def __init__(self, config):
		BaseCache.__init__(self, config)
		servers = ['%s:%d' % (config['host'], config['port'])]
		self.key_prefix = _to_native(config.get('key_prefix', None))
		if servers is None:
			servers = ['127.0.0.1:11211']
		self._client = self.import_preferred_memcache_lib(servers)
		if self._client is None:
			raise RuntimeError('no memcache module found')

	def _normalize_key(self, key):
		key = _to_native(key, 'utf-8')
		if self.key_prefix:
			key = self.key_prefix + key
		return key

	def _normalize_timeout(self, timeout):
		if timeout is None:
			timeout = self.default_timeout
		return timeout

	def get(self, key):
		key = self._normalize_key(key)
		# memcached doesn't support keys longer than that.  Because often
		# checks for so long keys can occur because it's tested from user
		# submitted data etc we fail silently for getting.
		if _test_memcached_key(key):
			return self._client.get(key)

	def get_many(self, keys):
		key_mapping = {}
		have_encoded_keys = False
		for key in keys:
			encoded_key = self._normalize_key(key)
			if not isinstance(key, str):
				have_encoded_keys = True
			if _test_memcached_key(key):
				key_mapping[encoded_key] = key
		d = rv = self._client.get_multi(key_mapping.keys())
		if have_encoded_keys or self.key_prefix:
			rv = {}
			for key, value in _iteritems(d):
				rv[key_mapping[key]] = value
		return rv

	def add(self, key, value, timeout=None, noreply=False):
		key = self._normalize_key(key)
		timeout = self._normalize_timeout(timeout)
		return self._client.add(key, value, timeout)

	def set(self, key, value, timeout=None, noreply=False):
		key = self._normalize_key(key)
		timeout = self._normalize_timeout(timeout)
		return self._client.set(key, value, timeout)

	def set_many(self, data, timeout=None, noreply=False):
		new_data = {}
		for key, value in _items(data):
			key = self._normalize_key(key)
			new_data[key] = value

		timeout = self._normalize_timeout(timeout)
		failed_keys = self._client.set_multi(new_data, timeout)
		return not failed_keys

	def delete(self, key, noreply=False):
		key = self._normalize_key(key)
		if _test_memcached_key(key):
			return self._client.delete(key) is not 0
		else:
			return False

	def delete_many(self, keys, noreply=False):
		new_keys = []
		for key in keys:
			key = self._normalize_key(key)
			if _test_memcached_key(key):
				new_keys.append(key)
		return self._client.delete_multi(new_keys) is not 0

	def clear(self):
		return self._client.flush_all()

	def incr(self, key, delta=1, noreply=False):
		key = self._normalize_key(key)
		return self._client.incr(key, delta)

	def decr(self, key, delta=1, noreply=False):
		key = self._normalize_key(key)
		return self._client.decr(key, delta)

	def expire(self, key, timeout):
		# This requires the version of memcached server >= 1.4.8
		return self._client.touch(self._normalize_key(key), timeout)

	def import_preferred_memcache_lib(self, servers):
		"""Returns an initialized memcache client.  Used by the constructor."""
		try:
			import pylibmc
		except ImportError:
			pass
		else:
			return pylibmc.Client(servers, behaviors=_PYLIBMC_BEHAVIORS)

		try:
			import memcache
			memcache.serverHashFunction = memcache.cmemcache_hash = _cmemcache_hash
		except ImportError:
			pass
		else:
			return memcache.Client(servers)


try:

	def _patch_pymemcache():
		try:
			from pymemcache.client import base
			import six
			base.VALID_STRING_TYPES = (six.text_type, )
		except:
			pass

	_patch_pymemcache()

	from pymemcache.client import Client as PyMemcachedClient
	from pymemcache.serde import python_memcache_serializer, python_memcache_deserializer

	class PyMemcachedCache(BaseCache):
		"""A cache client based on pymemcache. implemented by pure python and support noreply.
		"""
		def __init__(self, config):
			BaseCache.__init__(self, config)
			self._client = PyMemcachedClient((config['host'], config['port']),
				serializer=python_memcache_serializer, deserializer=python_memcache_deserializer,
				connect_timeout=_DEFAULT_SOCKET_TIMEOUT, timeout=_DEFAULT_SOCKET_TIMEOUT,
				key_prefix=config.get('key_prefix', ''))

		def get(self, key):
			return self._client.get(_to_native(key))

		def delete(self, key, noreply=False):
			self._client.delete(_to_native(key), noreply)
			return True

		def get_many(self, keys):
			return self._client.get_many([_to_native(key) for key in keys])

		def set(self, key, value, timeout=None, noreply=False):
			if timeout is None:
				timeout = self.default_timeout
			return self._client.set(_to_native(key), value, timeout, noreply)

		def add(self, key, value, timeout=None, noreply=False):
			if timeout is None:
				timeout = self.default_timeout
			return self._client.add(_to_native(key), value, timeout, noreply)

		def set_many(self, data, timeout=None, noreply=False):
			if timeout is None:
				timeout = self.default_timeout
			return self._client.set_many(dict([(_to_native(k), v) for k, v in _iteritems(data)]), timeout, noreply)

		def delete_many(self, keys, noreply=False):
			return self._client.delete_many([_to_native(key) for key in keys], noreply)

		def clear(self):
			return self._client.flush_all(noreply=False)

		def incr(self, key, delta=1, noreply=False):
			return self._client.incr(_to_native(key), delta, noreply)

		def decr(self, key, delta=1, noreply=False):
			return self._client.decr(_to_native(key), delta, noreply)

		def expire(self, key, timeout):
			# This requires the version of memcached server >= 1.4.8
			return self._client.touch(_to_native(key), timeout)

except ImportError:

	PyMemcachedCache = MemcachedCache


_redis_kwargs_exclusions = set(('id', 'type', 'replica', 'default', 'default_timeout', 'key_prefix'))
_DEFAULT_REDIS_BLOCKING_POOL_TIMEOUT = 5

class RedisCache(BaseCache):
	"""Uses the Redis key-value store as a cache backend.

	:param host: address of the Redis server or an object which API is
				 compatible with the official Python Redis client (redis-py).
	:param port: port number on which Redis server listens for connections.
	:param unix_socket_path: unix socket file path.
	:param password: password authentication for the Redis server.
	:param db: db (zero-based numeric index) on Redis Server to connect.
	:param default_timeout: the default timeout that is used if no timeout is
							specified on :meth:`~BaseCache.set`.
	:param key_prefix: A prefix that should be added to all keys.

	Any additional keyword arguments will be passed to ``redis.Redis``.
	"""

	def __init__(self, config):
		BaseCache.__init__(self, config)
		self.key_prefix = config.get('key_prefix', '')
		try:
			import redis
		except ImportError:
			raise RuntimeError('no redis module found')
		kwargs = dict((k, v) for k, v in config.items() if k not in _redis_kwargs_exclusions)
		if 'socket_timeout' not in kwargs:
			kwargs['socket_timeout'] = _DEFAULT_SOCKET_TIMEOUT
		if 'socket_connect_timeout' not in kwargs:
			kwargs['socket_connect_timeout'] = _DEFAULT_SOCKET_TIMEOUT
		if 'socket_keepalive' not in kwargs:
			kwargs['socket_keepalive'] = 1
		if 'socket_keepalive_options' not in kwargs:
			kwargs['socket_keepalive_options'] = _TCP_KEEP_ALIVE_OPTIONS
		self._client = redis.Redis(**kwargs)

	def _normalize_key(self, key):
		key = _to_native(key, 'utf-8')
		if self.key_prefix:
			key = self.key_prefix + key
		return key

	def dump_object(self, value):
		"""Dumps an object into a string for redis.  By default it serializes
		integers as regular string and pickle dumps everything else.
		"""
		t = type(value)
		if t in _integer_types:
			return str(value).encode('ascii')
		return b'!' + pickle.dumps(value)

	def load_object(self, value):
		"""The reversal of :meth:`dump_object`.  This might be callde with
		None.
		"""
		if value is None:
			return None
		if value.startswith(b'!'):
			try:
				return pickle.loads(value[1:])
			except pickle.PickleError:
				return None
		try:
			return int(value)
		except ValueError:
			return value

	def get(self, key):
		return self.load_object(self._client.get(self._normalize_key(key)))

	def get_list(self, keys):
		keys = [self._normalize_key(key) for key in keys]
		return [self.load_object(x) for x in self._client.mget(keys)]

	def get_many(self, keys):
		query_keys = [self._normalize_key(key) for key in keys]
		values_list = self._client.mget(query_keys)
		values = {}
		for i in xrange(len(keys)):
			value = values_list[i]
			if value is not None:
				values[keys[i]] = self.load_object(value)
		return values

	def set(self, key, value, timeout=None, noreply=False):
		if timeout is None:
			timeout = self.default_timeout
		dump = self.dump_object(value)
		if timeout == 0:
			return self._client.set(name=self._normalize_key(key), value=dump)
		else:
			return self._client.setex(name=self._normalize_key(key), value=dump, time=timeout)

	def add(self, key, value, timeout=None, noreply=False):
		if timeout is None:
			timeout = self.default_timeout
		if timeout == 0:
			# set with `EX` 0 is invalid.
			timeout = None
		dump = self.dump_object(value)
		# This requires the version of redis server >= 2.6.12, please refer
		# https://github.com/andymccurdy/redis-py/issues/387 for more details.
		result = self._client.set(self._normalize_key(key), dump, nx=True, ex=timeout)
		return result

	def set_many(self, data, timeout=None, noreply=False):
		if timeout is None:
			timeout = self.default_timeout
		pipe = self._client.pipeline()
		for key, value in _items(data):
			dump = self.dump_object(value)
			if timeout == 0:
				pipe.set(name=self._normalize_key(key), value=dump)
			else:
				pipe.setex(name=self._normalize_key(key), value=dump, time=timeout)
		return pipe.execute()

	def delete(self, key, noreply=False):
		self._client.delete(self._normalize_key(key))
		return True

	def delete_many(self, keys, noreply=False):
		if not keys:
			return True
		keys = [self._normalize_key(key) for key in keys]
		self._client.delete(*keys)
		return True

	def clear(self):
		status = False
		if self.key_prefix:
			keys = self._client.keys(self.key_prefix + '*')
			if keys:
				status = self._client.delete(*keys)
		else:
			status = self._client.flushdb()
		return status

	def incr(self, key, delta=1, noreply=False):
		return self._client.incr(name=self._normalize_key(key), amount=delta)

	def decr(self, key, delta=1, noreply=False):
		return self._client.decr(name=self._normalize_key(key), amount=delta)

	def blpop(self, key, timeout=0):
		result = self._client.blpop([self._normalize_key(key)], timeout)
		if result is not None:
			result = self.load_object(result[1])
		return result

	def brpop(self, key, timeout=0):
		result = self._client.brpop([self._normalize_key(key)], timeout)
		if result is not None:
			result = self.load_object(result[1])
		return result

	def lindex(self, key, index):
		return self.load_object(self._client.lindex(self._normalize_key(key), index))

	def llen(self, key):
		return self._client.llen(self._normalize_key(key))

	def lpop(self, key):
		return self.load_object(self._client.lpop(self._normalize_key(key)))

	def lpush(self, key, value):
		return self._client.lpush(self._normalize_key(key), self.dump_object(value))

	def lrange(self, key, start=0, end=-1):
		return [self.load_object(v) for v in self._client.lrange(self._normalize_key(key), start, end)]

	def ltrim(self, key, start, end):
		return self._client.ltrim(self._normalize_key(key), start, end)

	def rpop(self, key):
		return self.load_object(self._client.rpop(self._normalize_key(key)))

	def rpush(self, key, value):
		return self._client.rpush(self._normalize_key(key), self.dump_object(value))

	def sadd(self, key, value):
		return self._client.sadd(self._normalize_key(key), self.dump_object(value)) >= 0

	def scard(self, key):
		return self._client.scard(self._normalize_key(key))

	def sismember(self, key, value):
		return self._client.sismember(self._normalize_key(key), self.dump_object(value))

	def smembers(self, key):
		value = self._client.smembers(self._normalize_key(key))
		if value:
			value = _set([self.load_object(v) for v in value])
		return value

	def srandmember(self, key):
		return self.load_object(self._client.srandmember(self._normalize_key(key)))

	def srem(self, key, value):
		return self._client.srem(self._normalize_key(key), self.dump_object(value)) >= 0

	def hgetall(self, key):
		value = self._client.hgetall(self._normalize_key(key))
		if value is not None:
			for field in value:
				value[field] = self.load_object(value[field])
		return value

	def hget(self, key, field):
		return self.load_object(self._client.hget(self._normalize_key(key), field))

	def hset(self, key, field, value, timeout=None, noreply=False):
		self._client.hset(self._normalize_key(key), field, self.dump_object(value))
		return True

	def hdel(self, key, field, noreply=False):
		self._client.hdel(self._normalize_key(key), field)
		return True

	def hexists(self, key, field):
		return self._client.hexists(self._normalize_key(key), field)

	def hlen(self, key):
		return self._client.hlen(self._normalize_key(key))

	def zadd(self, key, value, score):
		return self._client.zadd(self._normalize_key(key), self.dump_object(value), score) >= 0

	def zcard(self, key):
		return self._client.zcard(self._normalize_key(key))

	def zcount(self, key, min, max):
		return self._client.zcount(self._normalize_key(key), min, max)

	def zincrby(self, key, value, delta=1):
		return self._client.zincrby(self._normalize_key(key), self.dump_object(value), delta)

	def zrange(self, key, start=0, end=-1, reverse=False, withscores=False):
		result = self._client.zrange(self._normalize_key(key), start, end, reverse, withscores)
		if withscores:
			result = [(self.load_object(v), s) for v, s in result]
		else:
			result = [self.load_object(v) for v in result]
		return result

	def zrangebyscore(self, key, min, max, start=None, num=None, reverse=False, withscores=False):
		if reverse:
			result = self._client.zrevrangebyscore(self._normalize_key(key), max, min, start, num, withscores)
		else:
			result = self._client.zrangebyscore(self._normalize_key(key), min, max, start, num, withscores)
		if withscores:
			result = [(self.load_object(v), s) for v, s in result]
		else:
			result = [self.load_object(v) for v in result]
		return result

	def zrank(self, key, value, reverse=False):
		if reverse:
			return self._client.zrevrank(self._normalize_key(key), self.dump_object(value))
		else:
			return self._client.zrank(self._normalize_key(key), self.dump_object(value))

	def zrem(self, key, value):
		return self._client.zrem(self._normalize_key(key), self.dump_object(value)) >= 0

	def zremrangebyrank(self, key, start, end, reverse=False):
		if reverse:
			start, end = -end - 1, -start - 1
		return self._client.zremrangebyrank(self._normalize_key(key), start, end)

	def zremrangebyscore(self, key, min, max):
		return self._client.zremrangebyscore(self._normalize_key(key), min, max)

	def zscore(self, key, value):
		return self._client.zscore(self._normalize_key(key), self.dump_object(value))

	def zunionstore(self, dest, keys, aggregate=None):
		return self._client.zunionstore(self._normalize_key(dest), [self._normalize_key(k) for k in keys], aggregate)

	def expire(self, key, timeout):
		return self._client.expire(self._normalize_key(key), timeout)

	def geoadd(self, key, longitude, latitude, member):
		return self._client.execute_command('GEOADD', self._normalize_key(key), longitude, latitude, member)

	def geopos(self, key, member):
		return self._client.execute_command('GEOPOS', self._normalize_key(key), member)

class RawRedisCache(RedisCache):
	"""Same cache client as RedisCache, but only support string value.
	"""

	def __init__(self, config):
		RedisCache.__init__(self, config)

	def dump_object(self, value):
		if not isinstance(value, str):
			raise Exception('raw_redis_unsupport_value_type:' + str(type(value)))
		return value

	def load_object(self, value):
		return value


class _SsdbConnectionPool(object):

	def __init__(self, connection):
		self._connection = connection

	def get_connection(self, command_name, *keys, **options):
		return self._connection

	def release(self, connection):
		return


class SsdbCache(BaseCache):
	"""Uses the SSDB key-value store as a cache backend.

	:param host: address of the SSDB server.
	:param port: port number on which SSDB server listens for connections.
	:param default_timeout: the default timeout that is used if no timeout is
							specified on :meth:`~BaseCache.set`.
							defaults to 0, means never expire.
	:param key_prefix: A prefix that should be added to all keys.

	Any additional keyword arguments will be passed to ``ssdb.Connection``.
	"""

	def __init__(self, config):
		BaseCache.__init__(self, config)
		self.default_timeout = config.get('default_timeout', 0)
		self.key_prefix = config.get('key_prefix', '')
		try:
			import ssdb
			#patch ssdb
			import six
			import datetime
			ssdb.connection.iteritems = six.iteritems
			def expire(self, name, ttl):	# pylint: disable=redefined-outer-name
				if isinstance(ttl, datetime.timedelta):
					ttl = ttl.seconds + ttl.days * 24 * 3600
				return self.execute_command('expire', name, ttl)
			ssdb.SSDB.expire = expire
		except ImportError:
			raise RuntimeError('no ssdb module found')
		kwargs = dict((k, v) for k, v in config.items() if k not in _redis_kwargs_exclusions)
		if 'socket_timeout' not in kwargs:
			kwargs['socket_timeout'] = _DEFAULT_SOCKET_TIMEOUT
		if 'socket_connect_timeout' not in kwargs:
			kwargs['socket_connect_timeout'] = _DEFAULT_SOCKET_TIMEOUT
		if 'socket_keepalive' not in kwargs:
			kwargs['socket_keepalive'] = 1
		if 'socket_keepalive_options' not in kwargs:
			kwargs['socket_keepalive_options'] = _TCP_KEEP_ALIVE_OPTIONS
		connection_pool = _SsdbConnectionPool(ssdb.Connection(**kwargs))
		self._client = ssdb.SSDB(connection_pool=connection_pool)

	def get(self, key):
		if self.key_prefix:
			key = self.key_prefix + key
		return self._client.get(key)

	def get_many(self, keys):
		if self.key_prefix:
			keys = [self.key_prefix + key for key in keys]
		values = self._client.multi_get(*keys)
		if self.key_prefix:
			values = dict([(key[len(self.key_prefix):], value) for key, value in values.iteritems()])
		return values

	def set(self, key, value, timeout=None, noreply=False):
		if self.key_prefix:
			key = self.key_prefix + key
		if timeout is None:
			timeout = self.default_timeout
		if timeout == 0:
			return self._client.set(key, value)
		else:
			return self._client.setx(key, value, timeout)

	def add(self, key, value, timeout=None, noreply=False):
		if self.key_prefix:
			key = self.key_prefix + key
		if timeout is None:
			timeout = self.default_timeout
		result = self._client.setnx(key, value)
		if result and timeout != 0:
			result = self._client.expire(key, timeout)
		return result

	def set_many(self, data, timeout=None, noreply=False):
		if timeout is None:
			timeout = self.default_timeout
		if self.key_prefix:
			new_data = {}
			for key in data:
				new_data[self.key_prefix + key] = data[key]
			data = new_data
		result = self._client.multi_set(**data)
		if result and timeout != 0:
			for key in data:
				result = self._client.expire(key, timeout)
		return result

	def delete(self, key, noreply=False):
		if self.key_prefix:
			key = self.key_prefix + key
		self._client.delete(key)
		return True

	def delete_many(self, keys, noreply=False):
		if not keys:
			return True
		if self.key_prefix:
			keys = [self.key_prefix + key for key in keys]
		self._client.multi_del(*keys)
		return True

	def clear(self):
		keys = self._client.keys('', '')
		if self.key_prefix:
			keys = [key for key in keys if key.startswith(self.key_prefix)]
		status = self._client.delete(*keys)
		return status

	def incr(self, key, delta=1, noreply=False):
		if self.key_prefix:
			key = self.key_prefix + key
		return self._client.incr(self.key_prefix + key, delta)

	def decr(self, key, delta=1, noreply=False):
		if self.key_prefix:
			key = self.key_prefix + key
		return self._client.decr(self.key_prefix + key, delta)

	def hgetall(self, key):
		if self.key_prefix:
			key = self.key_prefix + key
		return self._client.hgetall(key)

	def hget(self, key, field):
		if self.key_prefix:
			key = self.key_prefix + key
		return self._client.hget(key, field)

	def hset(self, key, field, value, timeout=None, noreply=False):
		if self.key_prefix:
			key = self.key_prefix + key
		return self._client.hset(key, field, value)

	def hdel(self, key, field, noreply=False):
		if self.key_prefix:
			key = self.key_prefix + key
		return self._client.hdel(key, field)

	def hexists(self, key, field):
		if self.key_prefix:
			key = self.key_prefix + key
		return self._client.hexists(key, field)

	def hlen(self, key):
		if self.key_prefix:
			key = self.key_prefix + key
		return self._client.hlen(key)


class ReplicationCache(BaseCache):

	def __init__(self, config):
		BaseCache.__init__(self, config)
		self._client = []
		self._primary_cache = None
		self._id = config['id']
		primary = config.get('primary')
		caches = config['caches']
		for index, name in enumerate(caches.keys()):
			self._client.append(create_cache_client(name, caches[name]))
			if primary is not None and primary == name:
				self._primary_cache = self._client[index]

	def get_client(self):
		if self._primary_cache is not None:
			return self._primary_cache
		if not self._client:
			return None
		return random.choice(self._client)

	def set(self, key, value, timeout=None, noreply=False):
		result = True
		for client in self._client:
			if not client.set(key, value, timeout, noreply):
				result = False
		return result

	def add(self, key, value, timeout=None, noreply=False):
		result = True
		for client in self._client:
			if not client.add(key, value, timeout, noreply):
				result = False
		return result

	def set_many(self, data, timeout=None, noreply=False):
		result = True
		for client in self._client:
			if not client.set_many(data, timeout, noreply):
				result = False
		return result

	def get(self, key):
		client = self.get_client()
		if client is None:
			return None
		return client.get(key)

	def get_list(self, keys):
		client = self.get_client()
		if client is None:
			return None
		return client.get_list(keys)

	def get_many(self, keys):
		client = self.get_client()
		if client is None:
			return None
		return client.get_many(keys)

	def delete(self, key, noreply=False):
		result = True
		for client in self._client:
			if not client.delete(key, noreply):
				result = False
		return result

	def delete_many(self, keys, noreply=False):
		result = True
		for client in self._client:
			if not client.delete_many(keys, noreply):
				result = False
		return result

	def clear(self):
		result = True
		for client in self._client:
			if not client.clear():
				result = False
		return result

	def incr(self, key, delta=1, noreply=False):
		result = None
		for client in self._client:
			result = client.incr(key, delta, noreply)
			if result is None:
				return None
		return result

	def decr(self, key, delta=1, noreply=False):
		result = None
		for client in self._client:
			result = client.decr(key, delta, noreply)
			if result is None:
				return None
		return result

	def blpop(self, key, timeout=0):
		result = None
		for client in self._client:
			result = client.blpop(key, timeout)
		return result

	def brpop(self, key, timeout=0):
		result = None
		for client in self._client:
			result = client.brpop(key, timeout)
		return result

	def lindex(self, key, index):
		client = self.get_client()
		if client is None:
			return None
		return client.lindex(key, index)

	def llen(self, key):
		client = self.get_client()
		if client is None:
			return None
		return client.llen(key)

	def lpop(self, key):
		result = None
		for client in self._client:
			result = client.lpop(key)
		return result

	def lpush(self, key, value):
		result = True
		for client in self._client:
			if not client.lpush(key, value):
				result = False
		return result

	def lrange(self, key, start=0, end=-1):
		client = self.get_client()
		if client is None:
			return None
		return client.lrange(key, start, end)

	def ltrim(self, key, start, end):
		result = True
		for client in self._client:
			if not client.ltrim(key, start, end):
				result = False
		return result

	def rpop(self, key):
		result = None
		for client in self._client:
			result = client.rpop(key)
		return result

	def rpush(self, key, value):
		result = True
		for client in self._client:
			if not client.rpush(key, value):
				result = False
		return result

	def sadd(self, key, value):
		result = True
		for client in self._client:
			if not client.sadd(key, value):
				result = False
		return result

	def scard(self, key):
		client = self.get_client()
		if client is None:
			return None
		return client.scard(key)

	def sismember(self, key, value):
		client = self.get_client()
		if client is None:
			return None
		return client.sismember(key, value)

	def smembers(self, key):
		client = self.get_client()
		if client is None:
			return None
		return client.smembers(key)

	def srandmember(self, key):
		client = self.get_client()
		if client is None:
			return None
		return client.srandmember(key)

	def srem(self, key, value):
		result = True
		for client in self._client:
			if not client.srem(key, value):
				result = False
		return result

	def hgetall(self, key):
		client = self.get_client()
		if client is None:
			return None
		return client.hgetall(key)

	def hget(self, key, field):
		client = self.get_client()
		if client is None:
			return None
		return client.hget(key, field)

	def hset(self, key, field, value, timeout=None, noreply=False):
		result = True
		for client in self._client:
			if not client.hset(key, field, value, timeout, noreply):
				result = False
		return result

	def hdel(self, key, field, noreply=False):
		result = True
		for client in self._client:
			if not client.hdel(key, field, noreply):
				result = False
		return result

	def hexists(self, key, field):
		client = self.get_client()
		if client is None:
			return None
		return client.hexists(key, field)

	def hlen(self, key):
		client = self.get_client()
		if client is None:
			return None
		return client.hlen(key)

	def zadd(self, key, value, score):
		result = True
		for client in self._client:
			if not client.zadd(key, value, score):
				result = False
		return result

	def zcard(self, key):
		client = self.get_client()
		if client is None:
			return None
		return client.zcard(key)

	def zcount(self, key, min, max):
		client = self.get_client()
		if client is None:
			return None
		return client.zcount(key, min, max)

	def zincrby(self, key, value, delta=1):
		result = True
		for client in self._client:
			result = client.zincrby(key, value, delta)
		return result

	def zrange(self, key, start=0, end=-1, reverse=False, withscores=False):
		client = self.get_client()
		if client is None:
			return None
		return client.zrange(key, start, end, reverse, withscores)

	def zrangebyscore(self, key, min, max, start=None, num=None, reverse=False, withscores=False):
		client = self.get_client()
		if client is None:
			return None
		return client.zrangebyscore(key, min, max, start, num, reverse, withscores)

	def zrank(self, key, value, reverse=False):
		client = self.get_client()
		if client is None:
			return None
		return client.zrank(key, value, reverse)

	def zrem(self, key, value):
		result = True
		for client in self._client:
			if not client.zrem(key, value):
				result = False
		return result

	def zremrangebyrank(self, key, start, end, reverse=False):
		result = True
		for client in self._client:
			if not client.zremrangebyrank(key, start, end, reverse):
				result = False
		return result

	def zremrangebyscore(self, key, min, max):
		result = True
		for client in self._client:
			if not client.zremrangebyscore(key, min, max):
				result = False
		return result

	def zscore(self, key, value):
		client = self.get_client()
		if client is None:
			return None
		return client.zscore(key, value)

	def zunionstore(self, dest, keys, aggregate=None):
		result = None
		for client in self._client:
			result = client.zunionstore(dest, keys, aggregate)
		return result

	def expire(self, key, timeout):
		result = True
		for client in self._client:
			if not client.expire(key, timeout):
				result = False
		return result

	def geoadd(self, key, longitude, latitude, member):
		result = None
		for client in self._client:
			result = client.geoadd(key, longitude, latitude, member)
		return result

	def geopos(self, key, member):
		client = self.get_client()
		if client is None:
			return None
		return client.geopos(key, member)


class MultilayerCache(BaseCache):
	"""A multilayer cache.
	"""

	def __init__(self, config):
		BaseCache.__init__(self, config)
		self._client = []
		self._primary_cache = None
		self._id = config['id']
		caches = config['caches']
		for cache in caches:
			self._client.append(create_cache_client(cache.get('id'), cache))
		self._primary_cache = self._client[-1]
		self._reversed_caches = self._client[-2::-1]

	def set(self, key, value, timeout=None, noreply=False):
		if not self._primary_cache.set(key, value, timeout, noreply):
			return False
		for client in self._reversed_caches:
			client.set(key, value, timeout, noreply)
		return True

	def add(self, key, value, timeout=None, noreply=False):
		if not self._primary_cache.add(key, value, timeout, noreply):
			return False
		for client in self._reversed_caches:
			client.set(key, value, timeout, noreply)
		return True

	def set_many(self, data, timeout=None, noreply=False):
		if not self._primary_cache.set_many(data, timeout, noreply):
			return False
		for client in self._reversed_caches:
			client.set_many(data, timeout, noreply)
		return True

	def get(self, key):
		for i in xrange(0, len(self._client)):
			value = self._client[i].get(key)
			if value is not None:
				for j in xrange(i - 1, -1, -1):
					self._client[j].set(key, value)
				return value
		return None

	def get_list(self, keys):
		return self._primary_cache.get_list(keys)

	def get_many(self, keys):
		return self._primary_cache.get_many(keys)

	def delete(self, key, noreply=False):
		if not self._primary_cache.delete(key, noreply):
			return False
		for client in self._reversed_caches:
			client.delete(key, noreply)
		return True

	def delete_many(self, keys, noreply=False):
		if not self._primary_cache.delete_many(keys, noreply):
			return False
		for client in self._reversed_caches:
			client.delete_many(keys, noreply)
		return True

	def clear(self):
		if not self._primary_cache.clear():
			return False
		for client in self._reversed_caches:
			client.clear()
		return True

	def incr(self, key, delta=1, noreply=False):
		result = self._primary_cache.incr(key, delta, noreply)
		for client in self._reversed_caches:
			client.delete(key, noreply)
		return result

	def decr(self, key, delta=1, noreply=False):
		result = self._primary_cache.decr(key, delta, noreply)
		for client in self._reversed_caches:
			client.delete(key, noreply)
		return result

	def blpop(self, key, timeout=0):
		return self._primary_cache.blpop(key, timeout)

	def brpop(self, key, timeout=0):
		return self._primary_cache.brpop(key, timeout)

	def lindex(self, key, index):
		return self._primary_cache.lindex(key, index)

	def llen(self, key):
		return self._primary_cache.llen(key)

	def lpop(self, key):
		return self._primary_cache.lpop(key)

	def lpush(self, key, value):
		return self._primary_cache.lpush(key, value)

	def lrange(self, key, start=0, end=-1):
		return self._primary_cache.lrange(key, start, end)

	def ltrim(self, key, start, end):
		return self._primary_cache.ltrim(key, start, end)

	def rpop(self, key):
		return self._primary_cache.rpop(key)

	def rpush(self, key, value):
		return self._primary_cache.rpush(key, value)

	def sadd(self, key, value):
		return self._primary_cache.sadd(key, value)

	def scard(self, key):
		return self._primary_cache.scard(key)

	def sismember(self, key, value):
		return self._primary_cache.sismember(key, value)

	def smembers(self, key):
		return self._primary_cache.smembers(key)

	def srandmember(self, key):
		return self._primary_cache.srandmember(key)

	def srem(self, key, value):
		return self._primary_cachet.srem(key, value)

	def hgetall(self, key):
		return self._primary_cache.hgetall(key)

	def hget(self, key, field):
		for i in xrange(0, len(self._client)):
			value = self._client[i].hget(key, field)
			if value is not None:
				for j in xrange(i - 1, -1, -1):
					self._client[j].hset(key, field, value)
				return value
		return None

	def hset(self, key, field, value, timeout=None, noreply=False):
		if not self._primary_cache.hset(key, field, value, timeout, noreply):
			return False
		for client in self._reversed_caches:
			client.hset(key, field, value, timeout, noreply)
		return True

	def hdel(self, key, field, noreply=False):
		if not self._primary_cache.hdel(key, field, noreply):
			return False
		for client in self._reversed_caches:
			client.hdel(key, field, noreply)
		return True

	def hexists(self, key, field):
		return self._primary_cache.hexists(key, field)

	def hlen(self, key):
		return self._primary_cache.hlen(key)

	def zadd(self, key, value, score):
		return self._primary_cache.zadd(key, value, score)

	def zcard(self, key):
		return self._primary_cache.zcard(key)

	def zcount(self, key, min, max):
		return self._primary_cache.zcount(key, min, max)

	def zincrby(self, key, value, delta=1):
		return self._primary_cache.zincrby(key, value, delta)

	def zrange(self, key, start=0, end=-1, reverse=False, withscores=False):
		return self._primary_cache.zrange(key, start, end, reverse, withscores)

	def zrangebyscore(self, key, min, max, start=None, num=None, reverse=False, withscores=False):
		return self._primary_cache.zrangebyscore(key, min, max, start, num, reverse, withscores)

	def zrank(self, key, value, reverse=False):
		return self._primary_cache.zrank(key, value, reverse)

	def zrem(self, key, value):
		return self._primary_cache.zrem(key, value)

	def zremrangebyrank(self, key, start, end, reverse=False):
		return self._primary_cache.zremrangebyrank(key, start, end, reverse)

	def zremrangebyscore(self, key, min, max):
		return self._primary_cache.zremrangebyscore(key, min, max)

	def zscore(self, key, value):
		return self._primary_cache.zscore(key, value)

	def zunionstore(self, dest, keys, aggregate=None):
		return self._primary_cache.zunionstore(dest, keys, aggregate)

	def expire(self, key, timeout):
		return self._primary_cache.expire(key, timeout)

class MasterSlaveCache(BaseCache):

	'''
	Sample:
	"my_cache": {
		"type": "master_slave",
		"master": "my_master",
		"caches": {
			"my_master": {
				....
			},
			"slave1": {
				....
			},
			....
		}
	}
	'''

	def __init__(self, config):
		BaseCache.__init__(self, config)
		self._slave_cache = []
		self._master_cache = None
		self._id = config['id']
		master = config.get('master')
		caches = config['caches']
		for index, name in enumerate(caches.keys()):
			if master is not None and master == name:
				self._master_cache = create_cache_client(name, caches[name])
			else:
				self._slave_cache.append(create_cache_client(name, caches[name]))

	def get_master_client(self):
		return self._master_cache

	def get_slave_client(self):
		if self._slave_cache:
			return random.choice(self._slave_cache)
		else:
			return self._master_cache

	def set(self, key, value, timeout=None, noreply=False):
		client = self.get_master_client()
		return client.set(key, value, timeout, noreply)

	def add(self, key, value, timeout=None, noreply=False):
		client = self.get_master_client()
		return client.add(key, value, timeout, noreply)

	def set_many(self, data, timeout=None, noreply=False):
		client = self.get_master_client()
		return client.set_many(data, timeout, noreply)

	def get(self, key):
		client = self.get_slave_client()
		if client is None:
			return None
		return client.get(key)

	def get_list(self, keys):
		client = self.get_slave_client()
		if client is None:
			return None
		return client.get_list(keys)

	def get_many(self, keys):
		client = self.get_slave_client()
		if client is None:
			return None
		return client.get_many(keys)

	def delete(self, key, noreply=False):
		client = self.get_master_client()
		return client.delete(key, noreply)

	def delete_many(self, keys, noreply=False):
		client = self.get_master_client()
		return client.delete_many(keys, noreply)

	def clear(self):
		client = self.get_master_client()
		return client.clear()

	def incr(self, key, delta=1, noreply=False):
		client = self.get_master_client()
		return client.incr(key, delta, noreply)

	def decr(self, key, delta=1, noreply=False):
		client = self.get_master_client()
		return client.decr(key, delta, noreply)

	def blpop(self, key, timeout=0):
		client = self.get_master_client()
		return client.blpop(key, timeout)

	def brpop(self, key, timeout=0):
		client = self.get_master_client()
		return client.brpop(key, timeout)

	def lindex(self, key, index):
		client = self.get_slave_client()
		if client is None:
			return None
		return client.lindex(key, index)

	def llen(self, key):
		client = self.get_slave_client()
		if client is None:
			return None
		return client.llen(key)

	def lpop(self, key):
		client = self.get_master_client()
		return client.lpop(key)

	def lpush(self, key, value):
		client = self.get_master_client()
		return client.lpush(key, value)

	def lrange(self, key, start=0, end=-1):
		client = self.get_slave_client()
		if client is None:
			return None
		return client.lrange(key, start, end)

	def ltrim(self, key, start, end):
		client = self.get_master_client()
		return client.ltrim(key, start, end)

	def rpop(self, key):
		client = self.get_master_client()
		return client.rpop(key)

	def rpush(self, key, value):
		client = self.get_master_client()
		return client.rpush(key, value)

	def sadd(self, key, value):
		client = self.get_master_client()
		return client.sadd(key, value)

	def scard(self, key):
		client = self.get_slave_client()
		if client is None:
			return None
		return client.scard(key)

	def sismember(self, key, value):
		client = self.get_slave_client()
		if client is None:
			return None
		return client.sismember(key, value)

	def smembers(self, key):
		client = self.get_slave_client()
		if client is None:
			return None
		return client.smembers(key)

	def srandmember(self, key):
		client = self.get_slave_client()
		if client is None:
			return None
		return client.srandmember(key)

	def srem(self, key, value):
		client = self.get_master_client()
		return client.srem(key, value)

	def hgetall(self, key):
		client = self.get_slave_client()
		if client is None:
			return None
		return client.hgetall(key)

	def hget(self, key, field):
		client = self.get_slave_client()
		if client is None:
			return None
		return client.hget(key, field)

	def hset(self, key, field, value, timeout=None, noreply=False):
		client = self.get_master_client()
		return client.hset(key, field, value, timeout, noreply)

	def hdel(self, key, field, noreply=False):
		client = self.get_master_client()
		return client.hdel(key, field, noreply)

	def hexists(self, key, field):
		client = self.get_slave_client()
		if client is None:
			return None
		return client.hexists(key, field)

	def hlen(self, key):
		client = self.get_slave_client()
		if client is None:
			return None
		return client.hlen(key)

	def zadd(self, key, value, score):
		client = self.get_master_client()
		return client.zadd(key, value, score)

	def zcard(self, key):
		client = self.get_slave_client()
		if client is None:
			return None
		return client.zcard(key)

	def zcount(self, key, min, max):
		client = self.get_slave_client()
		if client is None:
			return None
		return client.zcount(key, min, max)

	def zincrby(self, key, value, delta=1):
		client = self.get_master_client()
		return client.zincrby(key, value, delta)

	def zrange(self, key, start=0, end=-1, reverse=False, withscores=False):
		client = self.get_slave_client()
		if client is None:
			return None
		return client.zrange(key, start, end, reverse, withscores)

	def zrangebyscore(self, key, min, max, start=None, num=None, reverse=False, withscores=False):
		client = self.get_slave_client()
		if client is None:
			return None
		return client.zrangebyscore(key, min, max, start, num, reverse, withscores)

	def zrank(self, key, value, reverse=False):
		client = self.get_slave_client()
		if client is None:
			return None
		return client.zrank(key, value, reverse)

	def zrem(self, key, value):
		client = self.get_master_client()
		return client.zrem(key, value)

	def zremrangebyrank(self, key, start, end, reverse=False):
		client = self.get_master_client()
		return client.zremrangebyrank(key, start, end, reverse)

	def zremrangebyscore(self, key, min, max):
		client = self.get_master_client()
		return client.zremrangebyscore(key, min, max)

	def zscore(self, key, value):
		client = self.get_slave_client()
		if client is None:
			return None
		return client.zscore(key, value)

	def zunionstore(self, dest, keys, aggregate=None):
		client = self.get_master_client()
		return client.zunionstore(dest, keys, aggregate)

	def expire(self, key, timeout):
		client = self.get_master_client()
		return client.expire(key, timeout)

	def geoadd(self, key, longitude, latitude, member):
		client = self.get_master_client()
		return client.geoadd(key, longitude, latitude, member)

	def geopos(self, key, member):
		client = self.get_slave_client()
		if client is None:
			return None
		return client.geopos(key, member)

_cache_classes = {
	'null': NullCache,
	'memory': MemoryCache,
	'memcached': MemcachedCache,
	'pymemcached': PyMemcachedCache,
	'redis': RedisCache,
	'rawredis': RawRedisCache,
	'ssdb': SsdbCache,
	'replication': ReplicationCache,
	'multilayer': MultilayerCache,
	'master_slave': MasterSlaveCache,
}

def create_cache_client(cache_id, config):
	cache_type = config['type']
	config['id'] = cache_id
	if cache_type not in _cache_classes:
		raise RuntimeError('unknown_cache_type: %s' % cache_type)
	return _cache_classes[cache_type](config)

class CacheManager(object):

	def __init__(self, config):
		self._config = config
		from threading import local
		self._caches = local()

	@property
	def default_client(self):
		if not hasattr(self._caches, 'clients'):
			self._init_caches()
		return self._caches.default_client

	def get_cache(self, name=None):
		if not hasattr(self._caches, 'clients'):
			self._init_caches()
		if name is None:
			return self._caches.default_client
		return self._caches.clients.get(name)

	def _init_caches(self):
		clients = {}
		default_client = None
		for name in self._config:
			item = self._config[name]
			client = create_cache_client(name, item)
			clients[name] = client
			if item.get('default') or default_client is None:
				default_client = client
		self._caches.clients = clients
		self._caches.default_client = default_client

_cache_manager = None

def init_cache(config):
	# pylint: disable=anomalous-backslash-in-string
	""" init cache clients
	:param config:
	{
		'main':  {
			'type': 'memcached',
			'host': '127.0.0.1',
			'port': 11211,
			'default_timeout': 7 * 24 * 60 * 60,
			'key_prefix': 'test.',
			'default': True,
		},
		'test':  {
			'type': 'redis',
			'host': '127.0.0.1',
			'port': 6379,
			'default_timeout': 7 * 24 * 60 * 60,
			'key_prefix': 'test.',
		},
		'null':  {
			'type': 'null',
		},
		'replication': {
			'type': 'replication',
			'primary': 'replication.main',
			'caches': {
				'replication.main': {
					'type': 'distribution',
					'caches': {
						'distribution.1': {
							'type': 'memcached',
							'host': '127.0.0.1',
							'port': 11211,
							'default_timeout': 7 * 24 * 60 * 60,
							'key_prefix': 'test',
							'replica': 32
						},
						'distribution.2': {
							'type': 'memcached',
							'host': '127.0.0.1',
							'port': 11212,
							'default_timeout': 7 * 24 * 60 * 60,
							'key_prefix': 'test',
							'replica': 32
						}
					}
				},
				'replication.bak': {
					'type': 'distribution',
					'method': 'mod',
					'key_regex': r'\w+\.(\d+)',
					'factor': 2,
					'caches': {
						'0': {
							'type': 'memcached',
							'host': '127.0.0.1',
							'port': 11211,
							'default_timeout': 7 * 24 * 60 * 60,
							'key_prefix': 'test'
						},
						'1': {
							'type': 'memcached',
							'host': '127.0.0.1',
							'port': 11212,
							'default_timeout': 7 * 24 * 60 * 60,
							'key_prefix': 'test'
						}
					}
				}
			}
		},
		'multilayer': {
			'type': 'multilayer',
			'caches': [
				{
					'type': 'memory',
					'default_timeout': 60,
					'trim_interval': 60
				},
				{
					'type': 'memcached',
					'host': '127.0.0.1',
					'port': 11211,
					'default_timeout': 7 * 24 * 60 * 60
				}
			]
		},
		"my_cache": {
			"type": "master_slave",
			"master": "my_master",
			"caches": {
				"my_master": {
					....
				},
				"slave1": {
					....
				},
				....
			}
		}
	}
	null: default_timeout
	memory: default_timeout, trim_interval
	memcached: host, port, default_timeout, key_prefix
	pymemcached: host, port, default_timeout, key_prefix. this client supports noreply.
	redis: host, port, unix_socket_path, password, db, default_timeout, key_prefix
	rawredis: host, port, password, db, default_timeout, key_prefix
	ssdb: host, port, default_timeout, key_prefix
	replication: caches, primary
	distribution: caches, method, key_regex, factor
	multilayer: caches
	there should be one instance with default=True
	:return: None
	"""
	global _cache_manager	# pylint: disable=global-statement
	_cache_manager = CacheManager(config)

def get_cache(name=None):
	if _cache_manager is None:
		return None
	return _cache_manager.get_cache(name)


def get(key):
	return _cache_manager.default_client.get(key)

def delete(key, noreply=False):
	return _cache_manager.default_client.delete(key, noreply)

def get_list(keys):
	return _cache_manager.default_client.get_list(keys)

def get_many(keys):
	return _cache_manager.default_client.get_many(keys)

def set(key, value, timeout=None, noreply=False):
	return _cache_manager.default_client.set(key, value, timeout, noreply)

def add(key, value, timeout=None, noreply=False):
	return _cache_manager.default_client.add(key, value, timeout, noreply)

def set_many(data, timeout=None, noreply=False):
	return _cache_manager.default_client.set_many(data, timeout, noreply)

def delete_many(keys, noreply=False):
	return _cache_manager.default_client.delete_many(keys, noreply)

def clear():
	return _cache_manager.default_client.clear()

def incr(key, delta=1, noreply=False):
	return _cache_manager.default_client.incr(key, delta, noreply)

def decr(key, delta=1, noreply=False):
	return _cache_manager.default_client.decr(key, delta, noreply)

def blpop(key, timeout=0):
	return _cache_manager.default_client.blpop(key, timeout)

def brpop(key, timeout=0):
	return _cache_manager.default_client.brpop(key, timeout)

def lindex(key, index):
	return _cache_manager.default_client.lindex(key, index)

def llen(key):
	return _cache_manager.default_client.llen(key)

def lpop(key):
	return _cache_manager.default_client.lpop(key)

def lpush(key, value):
	return _cache_manager.default_client.lpush(key, value)

def lrange(key, start=0, end=-1):
	return _cache_manager.default_client.lrange(key, start, end)

def ltrim(key, start, end):
	return _cache_manager.default_client.ltrim(key, start, end)

def rpop(key):
	return _cache_manager.default_client.rpop(key)

def rpush(key, value):
	return _cache_manager.default_client.rpush(key, value)

def sadd(key, value):
	return _cache_manager.default_client.sadd(key, value)

def scard(key):
	return _cache_manager.default_client.scard(key)

def sismember(key, value):
	return _cache_manager.default_client.sismember(key, value)

def smembers(key):
	return _cache_manager.default_client.smembers(key)

def srandmember(key):
	return _cache_manager.default_client.srandmember(key)

def srem(key, value):
	return _cache_manager.default_client.srem(key, value)

def hgetall(key):
	return _cache_manager.default_client.hgetall(key)

def hget(key, field):
	return _cache_manager.default_client.hget(key, field)

def hset(key, field, value, timeout=None, noreply=False):
	return _cache_manager.default_client.hset(key, field, value, timeout, noreply)

def hdel(key, field, noreply=False):
	return _cache_manager.default_client.hdel(key, field, noreply)

def hexists(key, field):
	return _cache_manager.default_client.hexists(key, field)

def hlen(key):
	return _cache_manager.default_client.hlen(key)

def zadd(key, value, score):
	return _cache_manager.default_client.zadd(key, value, score)

def zcard(key):
	return _cache_manager.default_client.zcard(key)

def zcount(key, min, max):
	return _cache_manager.default_client.zcount(key, min, max)

def zincrby(key, value, delta=1):
	return _cache_manager.default_client.zincrby(key, value, delta)

def zrange(key, start=0, end=-1, reverse=False, withscores=False):
	return _cache_manager.default_client.zrange(key, start, end, reverse, withscores)

def zrangebyscore(key, min, max, start=None, num=None, reverse=False, withscores=False):
	return _cache_manager.default_client.zrangebyscore(key, min, max, start, num, reverse, withscores)

def zrank(key, value, reverse=False):
	return _cache_manager.default_client.zrank(key, value, reverse)

def zrem(key, value):
	return _cache_manager.default_client.zrem(key, value)

def zremrangebyrank(key, start, end, reverse=False):
	return _cache_manager.default_client.zremrangebyrank(key, start, end, reverse)

def zremrangebyscore(key, min, max):
	return _cache_manager.default_client.zremrangebyscore(key, min, max)

def zscore(key, value):
	return _cache_manager.default_client.zscore(key, value)

def expire(key, timeout):
	return _cache_manager.default_client.expire(key, timeout)
