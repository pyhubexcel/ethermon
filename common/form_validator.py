import base64
import re

class FormValidateError(Exception):
	pass

class _ItemValidator(object):

	def validate(self, path, value):
		if self._validate(value):
			return None
		return self._format_error(path, value)

	def _format_error(self, path, value):
		return self._error_template % (path, value)

class _RequiredValidator(_ItemValidator):

	def __init__(self, field_name):
		self._field_name = field_name
		self._error_template = 'required:%s,%s,%s'

	def _validate(self, value):
		return self._field_name in value

	def _format_error(self, path, value):
		return self._error_template % (self._field_name, path, '')

class _MaxItemValidator(_ItemValidator):

	def __init__(self, ref):
		self._ref = ref
		self._error_template = 'maxItem:%s,%%s,%%s' % ref

	def _validate(self, value):
		return len(value) <= self._ref

	def _format_error(self, path, value):
		return self._error_template % (path, len(value))

class _MinItemValidator(_ItemValidator):

	def __init__(self, ref):
		self._ref = ref
		self._error_template = 'minItem:%s,%%s,%%s' % ref

	def _validate(self, value):
		return len(value) >= self._ref

	def _format_error(self, path, value):
		return self._error_template % (path, len(value))

class _MaximumValidator(_ItemValidator):

	def __init__(self, ref):
		self._ref = ref
		self._error_template = 'maximum:%s,%%s,%%s' % ref

	def _validate(self, value):
		return value <= self._ref

class _MinimumValidator(_ItemValidator):

	def __init__(self, ref):
		self._ref = ref
		self._error_template = 'minimum:%s,%%s,%%s' % ref

	def _validate(self, value):
		return value >= self._ref

class _LengthValidator(_ItemValidator):

	def __init__(self, ref):
		self._ref = ref
		self._error_template = 'length:%s,%%s,%%s' % ref

	def _validate(self, value):
		return len(value) == self._ref

class _MaxLengthValidator(_ItemValidator):

	def __init__(self, ref):
		self._ref = ref
		self._error_template = 'maxLength:%s,%%s,%%s' % ref

	def _validate(self, value):
		return len(value) <= self._ref

class _MinLengthValidator(_ItemValidator):

	def __init__(self, ref):
		self._ref = ref
		self._error_template = 'minLength:%s,%%s,%%s' % ref

	def _validate(self, value):
		return len(value) >= self._ref

class _PatternValidator(_ItemValidator):

	def __init__(self, pattern):
		if not pattern.endswith('$'):
			pattern += '$'
		self._pattern = re.compile(pattern)
		self._error_template = 'pattern:%s,%s,%s'

	def _validate(self, value):
		return self._pattern.match(value) is not None

	def _format_error(self, path, value):
		return self._error_template % (self._pattern.pattern, path, value)

def _create_validator(schema):
	validators = {'v': []}
	for key, value in schema.iteritems():
		if key == 'type':
			validators['t'] = value
			if value == 'array':
				validators['c'] = lambda v: v.split(schema.get('delimiter'))
			elif value == 'integer':
				validators['c'] = long
			elif value == 'number':
				validators['c'] = float
			elif value == 'bytes':
				encoding = schema.get('encoding')
				if encoding == 'hex':
					validators['c'] = lambda v: v.decode('hex')
				elif encoding == 'base64':
					validators['c'] = base64.standard_b64decode
				elif encoding == 'urlbase64':
					validators['c'] = base64.urlsafe_b64decode
				else:
					validators['c'] = lambda v: v.encode('utf-8')
		elif key == 'properties':
			validators['f'] = {}
			for pname, pvalue in value.iteritems():
				validators['f'][pname] = _create_validator(pvalue)
		elif key == 'required':
			for field_name in value:
				if schema.get('properties', {}).get(field_name, {}).get('type') != 'array':
					validators['v'].append(_RequiredValidator(field_name))
		elif key == 'items':
			validators['i'] = _create_validator(value)
		elif key == 'maxItems':
			validators['v'].append(_MaxItemValidator(value))
		elif key == 'minItems':
			validators['v'].append(_MinItemValidator(value))
		elif  key == 'maximum':
			validators['v'].append(_MaximumValidator(value))
		elif  key == 'minimum':
			validators['v'].append(_MinimumValidator(value))
		elif  key == 'length':
			validators['v'].append(_LengthValidator(value))
		elif key == 'maxLength':
			validators['v'].append(_MaxLengthValidator(value))
		elif key == 'minLength':
			validators['v'].append(_MinLengthValidator(value))
		elif key == 'pattern':
			validators['v'].append(_PatternValidator(value))
	return validators

def _normalize_data_field(validator, data, path):
	if 'c' in validator:
		try:
			ndata = validator['c'](data)
		except Exception as ex:
			raise FormValidateError('convert:%s,%s,%s,%s' % (validator['t'], ex, path, data))
	else:
		ndata = data
	if 'i' in validator:
		ivalidator = validator['i']
		for i in xrange(len(ndata)):
			ndata[i] = _normalize_data_field(ivalidator, ndata[i], '%s[%s]' % (path, i))
	for v in validator['v']:
		error = v.validate(path, ndata)
		if error is not None:
			raise FormValidateError(error)
	return ndata

def _normalize_data(validator, data):
	ndata = {}
	for v in validator['v']:
		error = v.validate('', data)
		if error is not None:
			raise FormValidateError(error)
	for fname, fvalidator in validator['f'].iteritems():
		if fname in data:
			ndata[fname] = _normalize_data_field(fvalidator, data[fname], fname)
	return ndata

class FormValidator(object):
	"""
	refer to json schema. the root should be a object
	supported schema
	common: type
	object: properties, required
	array: items, maxItems, minItems, delimiter
	integer: minimum, maximum
	number: minimum, maximum
	string: length, minLength, maxLength, pattern
	bytes: length, minLength, maxLength, encoding
	bytes encoding support raw / hex / base64 / urlbase64
	"""

	def __init__(self, schema):
		self._schema = None
		self._validator = None
		self.schema = schema

	@property
	def schema(self):
		return self._schema

	@schema.setter
	def schema(self, schema):
		self._schema = schema
		self._validator = _create_validator(self._schema)

	def normalize(self, data):
		return _normalize_data(self._validator, data)

def extend_form_schema(schema, base_schema):
	if 'type' not in schema and 'type' in base_schema:
		schema['type'] = base_schema['type']
	if 'properties' in base_schema:
		if 'properties' not in schema:
			schema['properties'] = {}
		base_schema_properties = base_schema['properties']
		schema_properties = schema['properties']
		for key in base_schema_properties:
			if key not in schema_properties:
				schema_properties[key] = base_schema_properties[key]
	if 'required' in base_schema:
		if 'required' not in schema:
			schema['required'] = []
		schema['required'].extend(base_schema['required'])
	return schema
