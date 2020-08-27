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
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pylab as plt
from matplotlib.figure import Figure
from matplotlib import pylab
from pylab import *
import PIL, PIL.Image, StringIO
import datetime as dt
import datetime
import numpy as np
import pandas as pd



financeform = {
    "type": "object",
    "properties": {
            "startDate": {
            "type": "int",
        },
            "endDate": {
            "type": "int",
        },
    },
    "required": ["startDate","endDate"],
}


@csrf_exempt
@parse_params(form=financeform, method='GET', data_format='FORM', error_handler=api_response_error_params)
def FinanceGraph(request, data):
    startDate = data['startDate']
    endDate = data['endDate']
    current_record = EtheremonDB.RevenueTxnTab.objects.filter(timestamp__range=(startDate, endDate)).values_list('usd_amount','timestamp')
    usd_amount = []
    datetim = []
    if current_record:
        for cur in current_record:
            usd_amount.append(int(cur[0]))
            dat = datetime.datetime.fromtimestamp(cur[1])
            datee = dat.strftime('%Y-%m-%d')
            datetim.append(datee)
        x = usd_amount
        s = datetim
        df = pd.DataFrame(x, s)
        df.plot(rot=20,figsize=(10,6.5),grid=True)
        """
        df = pd.DataFrame(np.cumsum(np.random.randn(len(s))), 
                    columns=['error'], index=pd.to_datetime(s))
        fig, ax = plt.subplots()
        ax.plot(s,x)
        fig.autofmt_xdate()
        """
        xlabel('Transaction Datetime')
        ylabel('Amount in USD')
        title('RevenueTxnTab Table Transactions graph for all contracts')
        grid(False)

        # Store image in a string buffer
        buffer = StringIO.StringIO()
        canvas = pylab.get_current_fig_manager().canvas
        canvas.draw()
        pilImage = PIL.Image.fromstring("RGB", canvas.get_width_height(), canvas.tostring_rgb())
        pilImage.save(buffer, "PNG")
        pylab.close()

        # Send buffer in a http response the the browser with the mime type image/png set
        return HttpResponse(buffer.getvalue(),content_type="image/png")
    else:
        return HttpResponse("No data available between in time range")

financeformbyaddress = {
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

@csrf_exempt
@parse_params(form=financeformbyaddress, method='GET', data_format='FORM', error_handler=api_response_error_params)
def FinanceGraphByaddress(request, data):
    address = data['address']
    startDate = data['startDate']
    endDate = data['endDate']
    current_record = EtheremonDB.RevenueTxnTab.objects.filter(timestamp__range=(startDate, endDate),contract_address=address).values_list('usd_amount','timestamp')
    usd_amount = []
    datetim = []
    if current_record:
        for cur in current_record:
            usd_amount.append(int(cur[0]))
            dat = datetime.datetime.fromtimestamp(cur[1])
            datee = dat.strftime('%Y-%m-%d')
            datetim.append(datee)
            
        x = usd_amount
        s = datetim
        df = pd.DataFrame(x, s)
        df.plot(rot=20,figsize=(10,6.5))
        """
        fig, ax = plt.subplots()
        ax.plot(s,x)
        fig.autofmt_xdate()
        """
        xlabel('Transaction Datetime')
        ylabel('Amount in USD')
        title('RevenueTxnTab Table Transactions graph \n contract="'+address+'"')
        grid(False)

        # Store image in a string buffer
        buffer = StringIO.StringIO()
        canvas = pylab.get_current_fig_manager().canvas
        canvas.draw()
        pilImage = PIL.Image.fromstring("RGB", canvas.get_width_height(), canvas.tostring_rgb())
        pilImage.save(buffer, "PNG")
        pylab.close()

        # Send buffer in a http response the the browser with the mime type image/png set
        return HttpResponse(buffer.getvalue(),content_type="image/png")
    else:
        return HttpResponse("No data available between in time range")

RevenueMonsterForm = {
    "type": "object",
    "properties": {
        "startDate": {
            "type": "int",
        },
        "endDate": {
            "type": "int",
        },
    },
    "required": ["startDate","endDate"],
}


@csrf_exempt
@parse_params(form=RevenueMonsterForm, method='GET', data_format='FORM', error_handler=api_response_error_params)
def RevenueMonsterTabGraph(request, data):
    startDate = data['startDate']
    endDate = data['endDate']
    current_record = EtheremonDB.RevenueMonsterTab.objects.filter(timestamp__range=(startDate, endDate)).values_list('usd_amount','timestamp')
    usd_amount = []
    datetim = []
    if current_record:
        for cur in current_record:
            usd_amount.append(int(cur[0]))
            dat = datetime.datetime.fromtimestamp(cur[1])
            datee = dat.strftime('%Y-%m-%d')
            datetim.append(datee)
        x = usd_amount
        s = datetim
        """
        fig, ax = plt.subplots()
        ax.plot(s,x)
        fig.autofmt_xdate()
        """
        df = pd.DataFrame(x, s)
        df.plot(rot=20,figsize=(10,6.5))
        xlabel('Transaction Datetime')
        ylabel('Amount in USD')
        title('RevenueMonsterTab Table Transactions graph')
        grid(False)

<<<<<<< HEAD
        # Store image in a string buffer
        buffer = StringIO.StringIO()
        canvas = pylab.get_current_fig_manager().canvas
        canvas.draw()
        pilImage = PIL.Image.fromstring("RGB", canvas.get_width_height(), canvas.tostring_rgb())
        pilImage.save(buffer, "PNG")
        pylab.close()
=======

    # Store image in a string buffer
    buffer = StringIO.StringIO()
    canvas = pylab.get_current_fig_manager().canvas
    canvas.draw()
    pilImage = PIL.Image.fromstring("RGB", canvas.get_width_height(), canvas.tostring_rgb())
    pilImage.save(buffer, "PNG")
    pylab.close()

    # Send buffer in a http response the the browser with the mime type image/png set
    return HttpResponse(buffer.getvalue(),content_type="image/png")
>>>>>>> 8930d32df7ef07fc98ba84e508703a58889fd796

        # Send buffer in a http response the the browser with the mime type image/png set
        return HttpResponse(buffer.getvalue(),content_type="image/png")
    else:
        return HttpResponse("No data available between in time range")

    
    
    
#------------------------dummy code----------------------

"""
def PrrPlotMapFig(x_cord,y_cord):
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.scatter(x_cord,y_cord,color='green')
    axis.set_title('PRR Cordinates Dot Plot Graph',color='brown')
    axis.set_xlabel('x_cordinates',color='tab:brown')
    axis.set_ylabel('y_cordinates',color='tab:brown')
    axis.plot()
    return fig
"""

"""
    
def getimage(request):
    # Construct the graph
    x = arange(0, 2*pi, 0.01)
    s = cos(x)**2
    plot(x, s)

    xlabel('xlabel(X)')
    ylabel('ylabel(Y)')
    title('Simple Graph!')
    grid(True)

    # Store image in a string buffer
    buffer = StringIO.StringIO()
    canvas = pylab.get_current_fig_manager().canvas
    canvas.draw()
    pilImage = PIL.Image.fromstring("RGB", canvas.get_width_height(), canvas.tostring_rgb())
    pilImage.save(buffer, "PNG")
    pylab.close()

    # Send buffer in a http response the the browser with the mime type image/png set
    return HttpResponse(buffer.getvalue(), mimetype="image/png")
"""
"""
plt.plot(usd_amount)
plt.ylabel('usd payments')
plt.show()

fig = PrrPlotMapFig(usd_amount,datetim)
output = io.BytesIO()
img= FigureCanvas(fig).print_png(output)
response = HttpResponse(content_type="image/png")
img.save(response, "PNG")
return response
"""
#return Response(output.getvalue(), mimetype='image/png')
"""
qr = qrcode.QRCode(version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=15,
                    border=2)
qr.add_data("safdsafdsafsafas")
qr.make(fit=True)
img = qr.make_image()
response = HttpResponse(content_type="image/png")
img.save(response, "PNG")
return response
"""

"""
qr = qrcode.QRCode(version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=15,
                    border=2)
qr.add_data(address)
qr.make(fit=True)
img = qr.make_image()
response = HttpResponse(content_type="image/png")
img.save(response, "PNG")
return response
"""