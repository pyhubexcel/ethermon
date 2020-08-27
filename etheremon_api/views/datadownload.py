# coding=utf-8
import requests
from random import randint
import json
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from common.utils import parse_params, log_request, get_timestamp
from common.logger import log
from etheremon_lib.decorators.auth_decorators import sign_in_required
from etheremon_lib.transaction_manager import TxnStatus, TxnAmountTypes, TxnTypes
from etheremon_lib.utils import *
from etheremon_lib.form_schema import *
from etheremon_lib.preprocessor import pre_process_header
from etheremon_lib import user_manager, ladder_manager, crypt, emont_bonus_manager, ema_energy_manager, \
    transaction_manager
from etheremon_lib import ema_monster_manager, ema_egg_manager
from etheremon_lib import ema_market_manager, ema_battle_manager, ema_player_manager, ema_adventure_manager
from etheremon_lib.models import EtheremonDB
from etheremon_lib.infura_client import get_general_infura_client
from etheremon_api.views.helper import *
from etheremon_api.views.ema_helper import _verify_signature
import qrcode
from io import BytesIO
from etheremon_service.contract.helper import _sync_player_dex
from django.http import FileResponse
from django.utils.encoding import smart_str
import time
import numpy as np
import pandas as pd
import csv
import datetime
from django.http import StreamingHttpResponse
from django.db.models import Avg
from django.db.models.aggregates import StdDev

dataform = {
    "type": "object",
    "properties": {
            "startDate": {
            "type": "int",
        },
            "endDate": {
            "type": "int",
        },
    },
    "required": ["startDate","endDate"]
}


class Echo:
    def write(self, value):
        return value

@csrf_exempt
@parse_params(form=dataform, method='GET', data_format='FORM', error_handler=api_response_error_params)
def RevenueTxnTabData(request, data):
    startDate = data['startDate']
    endDate = data['endDate']
    # startDate = int(datetime.datetime.strptime(startDate, '%d/%m/%Y').strftime("%s"))
    # endDate = int(datetime.datetime.strptime(endDate, '%d/%m/%Y').strftime("%s"))

    queryset = EtheremonDB.RevenueTxnTab.objects.filter(timestamp__range=(startDate, endDate)).values_list(
        'contract_address', 'sender', 'txn_hash', 'eth_amount', 'usd_amount', 'timestamp')
    echo_buffer = Echo()
    csv_writer = csv.writer(echo_buffer)
    # By using a generator expression to write each row in the queryset
    # python calculates each row as needed, rather than all at once.
    # Note that the generator uses parentheses, instead of square
    # brackets – ( ) instead of [ ].
    #avg = queryset.values_list('usd_amount').aggregate(Avg('usd_amount')).values()[0]
    usdavg = queryset.aggregate(Avg('usd_amount')).values()[0]
    ethavg = queryset.aggregate(Avg('eth_amount')).values()[0]
    usdstd = queryset.aggregate(StdDev('usd_amount')).values()[0]
    ethstd = queryset.aggregate(StdDev('eth_amount')).values()[0]
    queryset = list(queryset)
    #print queryset
    queryset.insert(0, ('contract_address', 'sender', 'txn_hash',
                    'eth_amount', 'usd_amount', 'timestamp'))
    queryset.append(('Average',None,None,
                ethavg,usdavg,None))
    queryset.append(('STD deviation',None,None,
                ethstd,usdstd,None))
    # rows = (csv_writer.writerow(row) for row in queryset )
    rows = list()
    for row in queryset:
        row = list(row)
        try:
            dat = datetime.datetime.fromtimestamp(float(row[5]))
            datee = dat.strftime('%Y-%m-%d')
            row[5] = datee
        except Exception as err:
            print err
        rows.append(csv_writer.writerow(row))
    response = StreamingHttpResponse(rows, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="RevenueTxnTab.csv"'
    return response


dataaddress = {
    "type": "object",
    "properties": {
        "address": {
            "type": "string",
        },
        "startDate": {
            "type": "int",
                },
        "endDate": {
            "type": "int",
                },
            },
    "required": ["address","startDate","endDate"]
}


@ csrf_exempt
@ parse_params(form=dataaddress, method='GET', data_format='FORM', error_handler=api_response_error_params)
def RevenueTxnByaddress(request, data):
    address = data['address']
    startDate = data['startDate']
    endDate = data['endDate']
    queryset = EtheremonDB.RevenueTxnTab.objects.filter(timestamp__range=(startDate, endDate),contract_address=address).values_list(
        'contract_address', 'sender', 'txn_hash', 'eth_amount', 'usd_amount', 'timestamp')
    echo_buffer = Echo()
    csv_writer = csv.writer(echo_buffer)
    # By using a generator expression to write each row in the queryset
    # python calculates each row as needed, rather than all at once.
    # Note that the generator uses parentheses, instead of square
    # brackets – ( ) instead of [ ].
    usdavg = queryset.aggregate(Avg('usd_amount')).values()[0]
    ethavg = queryset.aggregate(Avg('eth_amount')).values()[0]
    usdstd = queryset.aggregate(StdDev('usd_amount')).values()[0]
    ethstd = queryset.aggregate(StdDev('eth_amount')).values()[0]

    queryset = list(queryset)
    queryset.insert(0, ('contract_address', 'sender', 'txn_hash',
                    'eth_amount', 'usd_amount', 'timestamp'))
    queryset.append(('Average',None,None,
            ethavg,usdavg,None))
    queryset.append(('STD deviation',None,None,
                ethstd,usdstd,None))


    # rows = (csv_writer.writerow(row) for row in queryset )
    rows = list()
    for row in queryset:
        row = list(row)
        try:
            dat = datetime.datetime.fromtimestamp(float(row[5]))
            datee = dat.strftime('%Y-%m-%d')
            row[5] = datee
        except Exception as err:
            print err
        rows.append(csv_writer.writerow(row))

    response = StreamingHttpResponse(rows, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="RevenueTxnTabcontract.csv"'
    return response





EmaEggform = {
    "type": "object",
    "properties": {
            "startDate": {
            "type": "int",
        },
            "endDate": {
            "type": "int",
        },
    },
    "required": ["startDate","endDate"]
}

@ csrf_exempt
@ parse_params(form=EmaEggform, method='GET', data_format='FORM', error_handler=api_response_error_params)
def EmaEggDataTabData(request, data):
    startDate = data['startDate']
    endDate = data['endDate']

    queryset = EtheremonDB.EmaEggDataTab.objects.filter(create_time__range=(startDate, endDate)).values_list(
        'egg_id', 'trainer', 'create_time')
    echo_buffer = Echo()
    csv_writer = csv.writer(echo_buffer)
    # By using a generator expression to write each row in the queryset
    # python calculates each row as needed, rather than all at once.
    # Note that the generator uses parentheses, instead of square
    # brackets – ( ) instead of [ ].
    queryset = list(queryset)
    queryset.insert(0, ('egg_id', 'trainer', 'create_time'))

    # rows = (csv_writer.writerow(row) for row in queryset )
    rows = list()
    for row in queryset:
        row = list(row)
        try:
            dat = datetime.datetime.fromtimestamp(float(row[2]))
            datee = dat.strftime('%Y-%m-%d')
            row[2] = datee
        except Exception as err:
            print err
        rows.append(csv_writer.writerow(row))

    response = StreamingHttpResponse(rows, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="EmaEggDataTab.csv"'
    return response




RevenueMonsterform = {
    "type": "object",
    "properties": {
            "startDate": {
            "type": "int",
        },
            "endDate": {
            "type": "int",
        },
    },
    "required": ["startDate","endDate"]
}

@ csrf_exempt
@ parse_params(form=RevenueMonsterform, method='GET', data_format='FORM', error_handler=api_response_error_params)
def RevenueMonsterTabData(request, data):
    startDate = data['startDate']
    endDate = data['endDate']
    queryset = EtheremonDB.RevenueMonsterTab.objects.filter(timestamp__range=(startDate, endDate)).values_list(
        'monster_id', 'trainer', 'eth_amount', 'usd_amount', 'timestamp')
    echo_buffer = Echo()
    csv_writer = csv.writer(echo_buffer)
    # By using a generator expression to write each row in the queryset
    # python calculates each row as needed, rather than all at once.
    # Note that the generator uses parentheses, instead of square
    # brackets – ( ) instead of [ ].
    usdavg = queryset.aggregate(Avg('usd_amount')).values()[0]
    ethavg = queryset.aggregate(Avg('eth_amount')).values()[0]
    usdstd = queryset.aggregate(StdDev('usd_amount')).values()[0]
    ethstd = queryset.aggregate(StdDev('eth_amount')).values()[0]

    queryset = list(queryset)
    queryset.insert(0, ('monster_id', 'trainer',
                    'eth_amount', 'usd_amount', 'timestamp'))
    queryset.append(('Average',None,
        ethavg,usdavg,None))
    queryset.append(('STD deviation',None,
        ethstd,usdstd,None))

    # rows = (csv_writer.writerow(row) for row in queryset )
    rows = list()
    for row in queryset:
        row = list(row)
        try:
            dat = datetime.datetime.fromtimestamp(float(row[4]))
            datee = dat.strftime('%Y-%m-%d')
            row[4] = datee
        except Exception as err:
            print err
        rows.append(csv_writer.writerow(row))
    response = StreamingHttpResponse(rows, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="RevenueMonsterTab.csv"'
    return response
