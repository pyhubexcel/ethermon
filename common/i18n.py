I18N = {}

class _Context:
	DEFAULT_LANGUAGE = 'en'

def set_default_language(language):
	_Context.DEFAULT_LANGUAGE = language

def add_i18n(language, i18n):
	I18N[language] = i18n

def get_text(key, language=None, default=None):
	i18n_dict = None
	if language:
		if language in I18N:
			i18n_dict = I18N[language]
		elif len(language) > 2:
			language = language[:2]
			if language in I18N:
				i18n_dict = I18N[language]
	if i18n_dict is None:
		i18n_dict = I18N.get(_Context.DEFAULT_LANGUAGE, {})
	return i18n_dict.get(key, key if default is None else default)

_ = get_text
