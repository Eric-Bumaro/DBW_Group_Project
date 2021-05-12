import json
import math
import os
from PIL import Image
from django.core.paginator import *
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import *
from datetime import datetime

def adminInfor(request):
    try:
        admin = CommonUser.objects.get(cuID=request.session["cuID"])
    except KeyError:
        return HttpResponseRedirect(reverse("welcome", args=(1,)))
    area = admin.area.filter(isDelete=False)
    if request.method=="GET":
        return render(request, "Admin/adminInfor.html", {"admin": admin, "area_set": area,"area_IDs_js":json.dumps(list(area.values("arID")))})
    else:
        for i in area:
            try:
                if request.POST.get("deleteArea"+str(i.arID),"0")=="1":
                    i.isDelete=True
                    i.deleteDate=datetime.now()
                    operation=AreaOperation(ad=admin,ar=i,oType="delArea",objID=i.arID)
                    operation.save()
                    i.save()
                if  request.POST.get("updataAreaName"+str(i.arID),"0")=="1":
                    originalName=i.arName
                    i.arName=request.POST.get("newAreaName"+str(i.arID))
                    operation=AreaOperation(ad=admin, ar=i, oType="upArea", objID=i.arID,
                                             content="Origin Name:" + originalName + " " + "New Name:" + request.POST.get(
                                                 "newAreaName"+str(i.arID)))
                    operation.save()
                    i.save()
            except Exception as e:
                print(e)
        return HttpResponseRedirect(reverse("USFD:adminInfor"))


def adminChangeInfor(request,changeType):
    if request.method == 'GET':
        if changeType == "Email" or changeType == "Password":
            return render(request, "Admin/adminChangeInfor.html",
                          {"changeType_js": json.dumps(changeType), "changeType_py": changeType,
                           "cuID": request.session["cuID"]})
        else:
            return render(request, "Admin/adminChangeInfor.html",
                          {"changeType_js": json.dumps(changeType), "changeType_py": changeType})

    admin = CommonUser.objects.get(cuID=request.session['cuID'])
    if changeType == "Email":
        newEmailAdd = request.POST.get("newEmailAdd", "")
        admin.cuEmail = newEmailAdd
        if not newEmailAdd.endwith("@mail.uic.edu.cn"):
            admin.VerifiedUser.delete()
    if changeType == "Name":
        newName = request.POST.get("newName", "")
        admin.cuName = newName
    if changeType == "Password":
        newPassword = request.POST.get("Password", "")
        admin.cuPassword = newPassword
    if changeType == "Image":
        photo = request.FILES.get("photo","")
        photoName = str(request.session['cuID']) + "." + photo.name.split(".")[1]
        photo_resize = Image.open(photo)
        photo_resize.thumbnail((371, 475), Image.ANTIALIAS)
        if os.path.isfile(os.path.join(".", ".", os.getcwd(), "media", str(admin.uImage))):
            os.remove(os.path.join(".", ".", os.getcwd(), "media", str(admin.uImage)))
        photo_resize.save(os.path.join(".", ".", os.getcwd(), "media", "user_image", photoName))
        admin.cuImage="user_image/"+photoName
    admin.save()
    return HttpResponseRedirect(reverse("USFD:adminSuChange", args=(changeType,)))


def adminSuChange(request,changeType):
    try:
        request.session["cID"]
    except KeyError:
        return HttpResponseRedirect(reverse("welcome", args=(1,)))
    return render(request, "Admin/adminSuChange.html", {"changeType": changeType})