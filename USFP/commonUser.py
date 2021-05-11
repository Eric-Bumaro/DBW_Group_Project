import datetime
import json
import os
from PIL import Image
from django.http import *
from django.shortcuts import render
from django.urls import reverse
from USFP.models import *

def userInfor(request):
    user = CommonUser.objects.get(uID=request.session['cuID'])
    try:
        verifiedUser=user.VerifiedUser
        return render(request, "CommonUser/userInfor.html",
                  {"user": user,'verified':1})
    except:
        return render(request, "CommonUser/userInfor.html",
                  {"user": user,'verified':0})
