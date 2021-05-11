from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render

from USFP.littleTools import *
from USFP.models import *


def welcome(request, logout=0):
    if (logout):
        request.session.clear()
        return render(request, 'View/welcome.html')
    try:
        user = CommonUser.object.get(cuID=request.session['cuID'])
        return render(request, 'View/welcome.html', {'cuID': user.cuID, 'cuName': user.cuName, 'cuImage': user.cuImage})
    except KeyError as e:
        return render(request, 'View/welcome.html')


def getUserKey(request, cuID):
    try:
        to_add = CommonUser.object.get(cuID=int(cuID)).cuEmail
        key = sendEmail(to_add)
        return HttpResponse(key)
    except Exception as e:
        return HttpResponse(1)


def getAdKey(request):
    return HttpResponse(sendAdKey())


def sendCheckKey(request):
    try:
        emailAdd = request.POST.get('emailAdd')
        key = sendEmail(emailAdd)
        return HttpResponse(key)
    except:
        return HttpResponse(1)
