import datetime
import json
import os
from PIL import Image
from django.http import *
from django.shortcuts import render
from django.urls import reverse
from USFP.models import *

def userInfor(request):
    user = CommonUser.objects.get(cuID=request.session['cuID'])
    try:
        verifiedUser=user.VerifiedUser
        return render(request, "CommonUser/userInfor.html",
                  {"user": user,'verified':1})
    except:
        return render(request, "CommonUser/userInfor.html",
                  {"user": user,'verified':0})


def userChange(request,changeType):
    if request.method == 'GET':
        if (changeType == "EmailAdd"):
            return render(request, "CommonUser/userChangeInfor.html",
                          {"changeType_js": json.dumps(changeType), "changeType_py": changeType})
        if (changeType == "Image"):
            return render(request, "CommonUser/userChangeInfor.html",
                          {"changeType_js": json.dumps(changeType), "changeType_py": changeType})
        if (changeType == "Name"):
            return render(request, "CommonUser/userChangeInfor.html",
                          {"changeType_js": json.dumps(changeType), "changeType_py": changeType})
        if (changeType == "Password"):
            return render(request, "CommonUser/userChangeInfor.html",
                          {"changeType_js": json.dumps(changeType), "changeType_py": changeType,
                           "cuID": request.session['cuID']})
    user = CommonUser.object.filter(cuID=request.session['cuID'])
    if (changeType == "EmailAdd"):
        newEmailAdd = request.POST.get("newEmailAdd", "")
        user.update(cuEmail=newEmailAdd)
        try:
            if newEmailAdd.endwith('@mail.uic.edu.cn'):
                verified=user[0].VerifiedUser
                if request.POST.get('wantToBeAdmin', '') == 'wantToBeAdmin':
                    verified.isAdmin=True
                    verified.save()
            else:
                verified = user[0].VerifiedUser
                verified.delete()
        except:
            if newEmailAdd.endwith('@mail.uic.edu.cn') and request.POST.get('wantToBeAdmin', '') == 'wantToBeAdmin':
                    VerifiedUser.objects.create(isAdmin=True,cu=user[0])
    if (changeType == "Image"):
        photo = request.FILES.get("photo", "")
        photoName = str(request.session['cuID']) + "." + photo.name.split(".")[1]
        photo_resize = Image.open(photo)
        photo_resize.thumbnail((371, 475), Image.ANTIALIAS)
        if os.path.isfile(os.path.join(".", ".", os.getcwd(), "media", str(user[0].uImage))):
            os.remove(os.path.join(".", ".", os.getcwd(), "media", str(user[0].uImage)))
        photo_resize.save(os.path.join(".", ".", os.getcwd(), "media", "user_image", photoName))
        user.update(cuImage="user_image/"+photoName)
    if (changeType == "Name"):
        newName = request.POST.get("newName", "")
        user.update(cuName=newName)
    if (changeType == "Password"):
        newPassword = request.POST.get("password", "")
        user.update(cuPassword=newPassword)
    return HttpResponseRedirect(reverse("loginModel:userSuChange", args=(changeType,)))


def userSuChange(request,changeType):
    return render(request, "CommonUser/userSuChange.html", {"changeType":changeType})