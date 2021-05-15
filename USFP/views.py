from django.shortcuts import render
import json
import os
import random
from PIL import Image
from django.http import *
from django.shortcuts import render, redirect
from django.urls import reverse
from USFP.models import *


# Create your views here.

def login(request, error):
    if request.method == "GET":
        if 'login' in request.COOKIES.keys():
            login = request.get_signed_cookie("login", salt="hello").split(',')
            commonUserID = login[0]
            commonUserPassword = login[1]
            return render(request, "View/login.html",
                          {"error": json.dumps(error), "commonUserID": commonUserID,
                           "commonUserPassword": commonUserPassword})
        else:
            return render(request, "View/login.html", {"error": json.dumps(error)})
    commonUserPassword = request.POST.get("commonUserPassword", "")
    remind = request.POST.get("cookie", "")
    commonUserID = int(request.POST.get("commonUserID", ""))
    result = CommonUser.object.filter(commonUserID=commonUserID, commonUserPassword=commonUserPassword)
    if len(result) == 0:
        response = HttpResponseRedirect(reverse('USFP:login', args=(1,)))
        response.delete_cookie("login")
        return response
    request.session.set_expiry(3 * 60 * 60)
    request.session['commonUserID'] = commonUserID
    response = redirect("welcome")
    if remind == "1":
        response.set_signed_cookie('login', str(commonUserID) + "," + commonUserPassword,
                                   max_age=24 * 60 * 60 * 3, salt="hello")
    return response


def register(request):
    if request.method == 'GET':
        return render(request, "View/register.html")
    commonUserName = request.POST.get("commonUserName", "")
    commonUserPassword = request.POST.get("commonUserPassword", "")
    commonUserEmail = request.POST.get("commonUserEmail", "")
    areaIDList = Area.object.all()
    try:
        photo = request.FILES.get("photo", "")
        phototype = photo.name.split(".")[-1]
        try:
            photoName = str(CommonUser.objects.last().commonUserID + 1) + "." + phototype
        except:
            photoName = "1." + phototype
        photoLocation = os.path.join(".", ".", os.getcwd(), "media", "userImage", photoName)
        photo_resize = Image.open(photo)
        photo_resize.thumbnail((371, 475), Image.ANTIALIAS)
        photo_resize.save(photoLocation)
        user = CommonUser.objects.create(commonUserName=commonUserName, commonUserPassword=commonUserPassword,
                                         commonUserEmail=commonUserEmail, commonUserImage="userImage/"+photoName,
                                         area=Area.object.get(arID=random.randint(1, len(areaIDList) + 1)))
    except Exception as e:
        user = CommonUser.objects.create(commonUserName=commonUserName, commonUserPassword=commonUserPassword,
                                         commonUserEmail=commonUserEmail,
                                         area=Area.object.get(areaID=random.randint(0, len(areaIDList) + 1)))
    if commonUserEmail.endswith('@mail.uic.edu.cn'):
        if request.POST.get('wantToBeAdmin', '') == 'wantToBeAdmin':
            VerifiedUser.objects.create(commonUser=user, isAdmin=True)
        else:
            VerifiedUser.objects.create(commonUser=user, isAdmin=False)
    return HttpResponseRedirect(reverse('USFP:suRegister'))


def suRegister(request):
    return render(request, "View/suRegister.html", {"commonUserID": CommonUser.objects.last().commonUserID})


def forgetPassword(request):
    if request.method == 'GET':
        return render(request, "View/forgetpwd.html")
    commonUserPassword = request.POST.get("commonUserPassword", "")
    commonUserID = request.POST.get("commonUserID", "")
    try:
        CommonUser.object.filter(commonUserID=int(commonUserID)).update(commonUserPassword=commonUserPassword)
        return redirect('USFP:suChangePwd')
    except Exception as e:
        return HttpResponse("Fail")


def suChangePwd(request):
    return render(request, "View/suChangePwd.html")
