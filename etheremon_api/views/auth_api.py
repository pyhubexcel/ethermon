# coding=utf-8
from django.views.decorators.csrf import csrf_exempt
from common.utils import parse_params, log_request, get_timestamp
from etheremon_lib.decorators.auth_decorators import sign_in_required
from etheremon_lib.form_schema import *
from etheremon_api.views.helper import *
from etheremon_api.views.ema_helper import _verify_signature
from common.logger import log


def generate_new_sign_in_message():
	return "Etheremon-sign-in-%s" % get_timestamp()


@csrf_exempt
@sign_in_required()
def test_api(request, data):
	response_data = {}
	request.session["test"] = "testing session"
	request.session["test2"] = "testing session 2"
	return api_response_result(request, ResultCode.SUCCESS, response_data)


@csrf_exempt
@parse_params(form=AuthGetUserSessionForm, method='GET', data_format='FORM', error_handler=api_response_error_params)
def get_user_session(request, data):
	trainer_address = data['trainer_address']
	current_user = request.session.get(SessionKeys.SIGNED_IN_ADDRESS, NULL_STRING)

	if current_user != trainer_address and trainer_address != NULL_STRING:
		current_user = NULL_STRING

	request.session[SessionKeys.SIGN_IN_MESSAGE] = generate_new_sign_in_message()

	if current_user != NULL_STRING:
		response = api_response_result(request, ResultCode.SUCCESS, {
			"sign_in_message": request.session[SessionKeys.SIGN_IN_MESSAGE],
			"user_address": current_user,
		})
	else:
		response = api_response_result(request, ResultCode.ERROR_PARAMS, {
			"sign_in_message": request.session[SessionKeys.SIGN_IN_MESSAGE],
		})

	return response


@csrf_exempt
@parse_params(form=SignInForm, method='POST', data_format='JSON', error_handler=api_response_error_params)
def sign_in(request, data):
	trainer_address = data['trainer_address'].lower()
	message = data['message']
	signature = data['signature']
	# if message != request.session.get(SessionKeys.SIGN_IN_MESSAGE, None) or SessionKeys.SIGN_IN_MESSAGE not in request.session:
	# 	return api_response_result(request, ResultCode.ERROR_PARAMS, {
	# 		"sign_in_message": request.session.get(SessionKeys.SIGN_IN_MESSAGE, None),
	# 	})

	# if not _verify_signature(message, signature, trainer_address):
	# 	return api_response_result(request, ResultCode.ERROR_SIGNATURE, {
	# 		"sign_in_message": request.session.get(SessionKeys.SIGN_IN_MESSAGE, None),
	# 	})

	request.session[SessionKeys.SIGNED_IN_ADDRESS] = trainer_address
	return api_response_result(request, ResultCode.SUCCESS, {
		"user_address": trainer_address,
		"sign_in_message": request.session.get(SessionKeys.SIGN_IN_MESSAGE, None),
	})


@csrf_exempt
@parse_params(form=SignOutForm, method='POST', data_format='JSON', error_handler=api_response_error_params)
def sign_out(request, data):
	del request.session[SessionKeys.SIGNED_IN_ADDRESS]
	return api_response_result(request, ResultCode.SUCCESS, {})
