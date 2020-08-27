class EnumBaseMeta(type):
	def __new__(mcs, clsname, bases, classdict):
		mcs = super(EnumBaseMeta, mcs).__new__(mcs, clsname, bases, classdict)
		d = {}
		for c in reversed(mcs.__bases__):
			if hasattr(c, 'NAME_TO_VALUE'):
				d.update(c.NAME_TO_VALUE)

		if 'MIN_VALUE' in classdict:
			classdict.pop('MIN_VALUE')
		if 'MAX_VALUE' in classdict:
			classdict.pop('MAX_VALUE')
		d.update((n, v) for n, v in classdict.items() if not n.startswith('__') and not callable(v) and not isinstance(v, (classmethod, staticmethod, dict)))
		type.__setattr__(mcs, 'NAME_TO_VALUE', d)
		type.__setattr__(mcs, 'VALUE_TO_NAME', dict((v, k) for k, v in d.items()))
		if d:
			type.__setattr__(mcs, 'MIN_VALUE', min(d.values()))
			type.__setattr__(mcs, 'MAX_VALUE', max(d.values()))
		return mcs
	def __setattr__(cls, name, value):
		raise AttributeError("Class '{0}' is read-only.".format(cls.__name__))

class EnumBase(object):
	__metaclass__ = EnumBaseMeta
	"""
		usage:
			class ExampleType(EnumBase):
				NONE, SUCCESS, FAIL = range(3)
	"""
	NAME_TO_VALUE = {}
	VALUE_TO_NAME = {}
	MIN_VALUE = 0
	MAX_VALUE = 0

	@classmethod
	def get_name(cls, value):
		return cls.VALUE_TO_NAME.get(value)

	@classmethod
	def get_value(cls, name):
		return cls.NAME_TO_VALUE.get(name)
