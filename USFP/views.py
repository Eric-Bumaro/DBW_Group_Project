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
            cuID = login[0]
            cuPassword = login[1]
            return render(request, "View/login.html",
                          {"error": json.dumps(error), "cuID": cuID, "cuPassword": cuPassword})
        else:
            return render(request, "View/login.html", {"error": json.dumps(error)})
    cuPassword = request.POST.get("cuPassword", "")
    remind = request.POST.get("cookie", "")
    cuID = int(request.POST.get("uID", "1"))
    result = CommonUser.object.filter(cuID=cuID, cuPassword=cuPassword)
    if (len(result) == 0):
        response = HttpResponseRedirect(reverse('USFP:login', args=(1,)))
        response.delete_cookie("login")
        return response
    request.session.set_expiry(3 * 60 * 60)
    request.session['cuID'] = cuID
    response = redirect("welcome")
    if remind == "1":
        response.set_signed_cookie('login', str(cuID) + "," + cuPassword,
                                   max_age=24 * 60 * 60 * 3, salt="hello")
    return response


def register(request):
    if request.method == 'GET':
        return render(request, "View/register.html")
    cuName = request.POST.get("cuName", "")
    cuPassword = request.POST.get("cuPassword", "")
    cuEmail = request.POST.get("cuEmail", "")
    areaIDList = Area.object.all()
    try:
        photo = request.FILES.get("photo", "")
        phototype = photo.name.split(".")[-1]
        try:
            photoName = str(CommonUser.objects.last().uID + 1) + "." + phototype
        except:
            photoName = "1." + phototype
        photoLocation = os.path.join(".", ".", os.getcwd(), "media", "user_image", photoName)
        photo_resize = Image.open(photo)
        photo_resize.thumbnail((371, 475), Image.ANTIALIAS)
        photo_resize.save(photoLocation)
        user=CommonUser.objects.create(cuName=cuName, cuPassword=cuPassword, cuEmail=cuEmail, cuImage="user_image/" +
                                                                                                 photoName,
                                  area=Area.object.get(arID=random.randint(1, len(areaIDList) + 1)))
    except Exception as e:
        user=CommonUser.objects.create(cuName=cuName, cuPassword=cuPassword, uEmail=cuEmail,
                                  area=Area.object.get(arID=random.randint(1, len(areaIDList) + 1)))
    if(cuEmail.endswith('@mail.uic.edu.cn')):
        if request.POST.get('wantToBeAdmin','')=='wantToBeAdmin':
            VerifiedUser.objects.create(cu=user,isAdmin=True)
        else:
            VerifiedUser.objects.create(cu=user, isAdmin=False)
    return HttpResponseRedirect(reverse('loginModel:suRegister'))


def suRegister(request):
    return render(request, "View/suRegister.html", {"cuID": CommonUser.objects.last().cuID})



def forgetPassword(request):
    if request.method == 'GET':
        return render(request, "View/forgetpwd.html")
    cuPassword = request.POST.get("cuPassword", "")
    cuID = request.POST.get("cuID", "")
    try:
        CommonUser.object.filter(uID=int(cuID)).update(uPassword=cuPassword)
        return redirect('loginModel:suChangePwd')
    except Exception as e:
        return HttpResponse("Fail")

def suChangePwd(request):
    return render(request,"View/suChangePwd.html")
