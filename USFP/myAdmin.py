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
        return render(request, "Admin/adminInfor.html", {"admin": admin, "areaSet": area,"areaIDs_js":json.dumps(list(area.values("arID")))})
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
        photo_resize.save(os.path.join(".", ".", os.getcwd(), "media", "userImage", photoName))
        admin.cuImage="userImage/"+photoName
    admin.save()
    return HttpResponseRedirect(reverse("USFD:adminSuChange", args=(changeType,)))


def adminSuChange(request,changeType):
    try:
        request.session["cID"]
    except KeyError:
        return HttpResponseRedirect(reverse("welcome", args=(1,)))
    return render(request, "Admin/adminSuChange.html", {"changeType": changeType})


def adminViewArea(request,num,arID):
    try:
        CommonUser.object.get(cuID=request.session["cuID"]).VerifiedUser
    except KeyError:
        return HttpResponseRedirect(reverse("welcome",args=(1,)))
    area=Area.object.get(arID=arID)
    users=[]
    for i in area.CommonUser.filter(isDelete=False):
        try:
            VerifiedUser.objects.get(cu=i)
        except:
            users.append(i)
    if int(num) < 1:
        num = 1
    else:
        num = int(num)
    pager = Paginator(users, 10)
    try:
        prepageData=pager.page(num)
    except EmptyPage:
        prepageData=pager.page(pager.num_pages)
    begin=(num-int(math.ceil(10.0/2)))
    if begin<1:
        begin=1
    end=begin+4
    if end>pager.num_pages:
        end=pager.num_pages
    if end<=5:
        begin=1
    else:
        begin=end-4
    pagelist=range(begin,end+1)
    return render(request, "Admin/adminViewArea.html",
                  {"pager": pager, 'prepageData': prepageData, "pageList": pagelist, "arID": arID,"arName":Area.object.get(arID=arID)})


def adminDeleteUser(request):
    try:
        try:
            cuID = request.session['cuID']
        except KeyError:
            return HttpResponseRedirect(reverse("welcome", args=(1,)))
        listToDelete = request.POST.get("listToDelete")
        delete_list = listToDelete.split("-")
        delete_list = [i for i in delete_list if len(i) != 0]
        try:
            for i in delete_list:
                userToDelete = CommonUser.object.get(cuID=int(i))
                userToDelete.isDelete = True
                userToDelete.deleteDate = datetime.now()
                userToDelete.save()
                UserOperation.objects.create(user=userToDelete, oType='delUser',content="Delete the user",
                                         vu=CommonUser.objects.get(cuID=cuID))
        except Exception as e:
            print(e)
            return HttpResponse("Fail")
        return HttpResponse("Success")
    except:
        return HttpResponse("Fail")


def viewOperations(request,areaOpNum,userOpNum):
    try:
        user = CommonUser.objects.get(cuID=request.session['cuID'])
        user.VerifiedUser
    except KeyError:
        return HttpResponseRedirect(reverse("welcome",args=(1,)))
    areaOperations=AreaOperation.objects.filter(cu=user).order_by("-oTakeDate")
    if int(areaOpNum) < 1:
        areaOpNum = 1
    else:
        areaOpNum = int(areaOpNum)
    areaPager = Paginator(areaOperations, 10)
    try:
        areaPrepageData = areaPager.page(areaOpNum)
    except EmptyPage:
        areaPrepageData = areaPager.page(areaPager.num_pages)
    begin = (areaOpNum - int(math.ceil(10.0 / 2)))
    if begin < 1:
        begin = 1
    end = begin + 4
    if end > areaPager.num_pages:
        end = areaPager.num_pages
    if end <= 5:
        begin = 1
    else:
        begin = end - 4
    areaPageList = range(begin, end + 1)
    userOperations=UserOperation.objects.filter(cu=user).order_by("-oTakeDate")
    if int(userOpNum) < 1:
        userOpNum = 1
    else:
        userOpNum = int(userOpNum)
    userPager = Paginator(userOperations, 10)
    try:
        userPrepageData = userPager.page(userOpNum)
    except EmptyPage:
        userPrepageData = userPager.page(userPager.num_pages)
    begin = (userOpNum - int(math.ceil(10.0 / 2)))
    if begin < 1:
        begin = 1
    end = begin + 4
    if end > userPager.num_pages:
        end = userPager.num_pages
    if end <= 5:
        begin = 1
    else:
        begin = end - 4
    userPageList = range(begin, end + 1)
    return render(request, "Admin/viewOperations.html",
                  {"areaCurPage": areaOpNum, 'areaPrepageData': areaPrepageData, "areaPageList": areaPageList,
                   "userCurPage":userOpNum,"userPrepageData":userPrepageData,"userPageList":userPageList},
                  )