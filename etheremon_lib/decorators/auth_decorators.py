from etheremon_lib import user_manager
from etheremon_lib.constants import ResultCode, SessionKeys
from etheremon_lib.utils import api_response_result


def sign_in_required():
	def wrapper(func):
		def new_func(request, *args, **kwargs):

			data = {} if len(args) == 0 else args[0]
			trainer_address = data.get("trainer_address", "").lower()

			if not request.session.get(SessionKeys.SIGNED_IN_ADDRESS, False):
				return api_response_result(request, ResultCode.ERROR_FORBIDDEN)
			elif trainer_address != "" and trainer_address != request.session[SessionKeys.SIGNED_IN_ADDRESS]:
				return api_response_result(request, ResultCode.ERROR_FORBIDDEN)

			if len(args) > 0:
				return func(request, *args, **kwargs)
			else:
				return func(request, data, *args, **kwargs)

		return new_func

	return wrapper


def register_required():
	def wrapper(func):
		def new_func(request, *args, **kwargs):

			data = {} if len(args) == 0 else args[0]
			trainer_address = data.get("trainer_address", "").lower()

			player_uid = user_manager.get_uid_by_address_default_0(trainer_address)
			if player_uid == 0:
				return api_response_result(request, ResultCode.ERROR_FORBIDDEN)

			data["player_uid"] = player_uid

			if len(args) > 0:
				return func(request, *args, **kwargs)
			else:
				return func(request, data, *args, **kwargs)

		return new_func

	return wrapper