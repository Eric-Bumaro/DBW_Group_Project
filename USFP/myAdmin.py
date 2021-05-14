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
        admin = CommonUser.objects.get(commonUserID=request.session["commonUserID"])
    except KeyError:
        return HttpResponseRedirect(reverse("welcome", args=(1,)))
    adminArea = admin.adminArea.filter(isDelete=False)
    if request.method == "GET":
        return render(request, "Admin/adminInfor.html",
                      {"admin": admin, "areaSet": adminArea, "areaIDs_js": json.dumps(list(adminArea.values("arID")))})
    else:
        for i in adminArea:
            try:
                if request.POST.get("deleteArea" + str(i.areaID), "0") == "1":
                    i.isDelete = True
                    i.deleteDate = datetime.now()
                    operation = AreaOperation(verifiedUser=admin, area=i, opearionType="delArea",
                                              content="Delete the area")
                    operation.save()
                    i.save()
                if request.POST.get("updataAreaName" + str(i.areaID), "0") == "1":
                    originalName = i.areaName
                    i.arName = request.POST.get("newAreaName" + str(i.arID))
                    operation = AreaOperation(verifiedUser=admin, ar=i, opearionType="upArea", area=i,
                                              content="Origin Name:" + originalName + " " + "New Name:" + request.POST.get(
                                                  "newAreaName" + str(i.arID)))
                    operation.save()
                    i.save()
            except Exception as e:
                print(e)
        return HttpResponseRedirect(reverse("USFP:adminInfor"))


def adminChangeInfor(request, changeType):
    if request.method == 'GET':
        if changeType == "Email" or changeType == "Password":
            return render(request, "Admin/adminChangeInfor.html",
                          {"changeType_js": json.dumps(changeType), "changeType_py": changeType,
                           "commonUserID": request.session["commonUserID"]})
        else:
            return render(request, "Admin/adminChangeInfor.html",
                          {"changeType_js": json.dumps(changeType), "changeType_py": changeType})

    admin = CommonUser.objects.get(commonUserID=request.session['commonUserID'])
    if changeType == "Email":
        newEmailAdd = request.POST.get("newEmailAdd", "")
        admin.commonEmail = newEmailAdd
        if not newEmailAdd.endwith("@mail.uic.edu.cn"):
            admin.VerifiedUser.delete()
    if changeType == "Name":
        newName = request.POST.get("newName", "")
        admin.commonName = newName
    if changeType == "Password":
        newPassword = request.POST.get("Password", "")
        admin.commonPassword = newPassword
    if changeType == "Image":
        photo = request.FILES.get("photo", "")
        photoName = str(request.session['commonUserID']) + "." + photo.name.split(".")[1]
        photo_resize = Image.open(photo)
        photo_resize.thumbnail((371, 475), Image.ANTIALIAS)
        if os.path.isfile(os.path.join(".", ".", os.getcwd(), "media", str(admin.uImage))):
            os.remove(os.path.join(".", ".", os.getcwd(), "media", str(admin.uImage)))
        photo_resize.save(os.path.join(".", ".", os.getcwd(), "media", "userImage", photoName))
        admin.commonUserImage = "userImage/" + photoName
    admin.save()
    return HttpResponseRedirect(reverse("USFP:adminSuChange", args=(changeType,)))


def adminSuChange(request, changeType):
    try:
        request.session["cID"]
    except KeyError:
        return HttpResponseRedirect(reverse("welcome", args=(1,)))
    return render(request, "Admin/adminSuChange.html", {"changeType": changeType})


def adminViewArea(request, num, areaID):
    try:
        admin = CommonUser.object.get(commonUserID=request.session["commonUserID"]).VerifiedUser
    except KeyError:
        return HttpResponseRedirect(reverse("welcome", args=(1,)))
    area = Area.object.get(areaID=areaID)
    if area not in admin.adminArea.all():
        return HttpResponseRedirect(reverse("welcome", args=(1,)))
    users = [i for i in area.CommonUser.filter(isDelete=False) if not i.isVerified()]
    if int(num) < 1:
        num = 1
    else:
        num = int(num)
    pager = Paginator(users, 10)
    try:
        prepageData = pager.page(num)
    except EmptyPage:
        prepageData = pager.page(pager.num_pages)
    begin = (num - int(math.ceil(10.0 / 2)))
    if begin < 1:
        begin = 1
    end = begin + 4
    if end > pager.num_pages:
        end = pager.num_pages
    if end <= 5:
        begin = 1
    else:
        begin = end - 4
    pagelist = range(begin, end + 1)
    return render(request, "Admin/adminViewArea.html",
                  {"pager": pager, 'prepageData': prepageData, "pageList": pagelist, "areaID": area.areaID,
                   "areaName": area.areaName})


def adminDeleteUsers(request):
    try:
        try:
            commonUserID = request.session['commonUserID']
        except KeyError:
            return HttpResponseRedirect(reverse("welcome", args=(1,)))
        listToDelete = request.POST.get("listToDelete")
        admin = CommonUser.objects.get(commonUserID=commonUserID)
        deleteList = listToDelete.split("-")
        deleteList = [i for i in deleteList if len(i) != 0]
        try:
            for i in deleteList:
                userToDelete = CommonUser.object.get(commonUserID=int(i))
                if userToDelete.isManagedBy(admin):
                    return HttpResponse("Fail")
                userToDelete.isDelete = True
                userToDelete.deleteDate = datetime.now()
                userToDelete.save()
                UserOperation.objects.create(commonUser=userToDelete, operationType='delUser',
                                             content="Delete the user", verifiedUser=admin)
        except Exception as e:
            print(e)
            return HttpResponse("Fail")
        return HttpResponse("Success")
    except:
        return HttpResponse("Fail")


def adminViewOperations(request, areaOpNum, userOpNum):
    try:
        user = CommonUser.objects.get(commonUserID=request.session['commonUserID'])
        if not user.isVerified():
            return HttpResponseRedirect(reverse("welcome", args=(1,)))
    except KeyError:
        return HttpResponseRedirect(reverse("welcome", args=(1,)))
    areaOperations = user.VerifiedUser.AreaOperation.order_by("-oTakeDate")
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
    userOperations = user.VerifiedUser.UserOperation.order_by("-oTakeDate")
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
    return render(request, "Admin/adminViewOperations.html",
                  {"areaCurPage": areaOpNum, 'areaPrepageData': areaPrepageData, "areaPageList": areaPageList,
                   "userCurPage": userOpNum, "userPrepageData": userPrepageData, "userPageList": userPageList},
                  )


def adminViewUser(request, commonUserID):
    try:
        admin = CommonUser.object.get(commonUserID=request.session["commonUserID"])
    except KeyError:
        return HttpResponseRedirect(reverse("welcome", args=(1,)))
    user = CommonUser.objects.get(commonUserID=commonUserID)
    if user.isManagedBy(admin):
        areaNames = admin.VerifiedUser.adminArea.filter(isDelete=False).values_list('arName')
        return render(request, "Admin/adminViewUser.html",
                      {"user": user, "areaNameList": list(areaNames), "isVerified": user.isVerified()})
    return HttpResponseRedirect(reverse("welcome", args=(1,)))


def adminUpdateUser(request, commonUserID):
    try:
        admin = CommonUser.objects.get(commonUserID=request.session['commonUserID'])
    except KeyError:
        return HttpResponseRedirect(reverse("welcome", args=(1,)))
    if (request.method == "GET"):
        return HttpResponseRedirect(reverse("welcome", args=(1,)))
    commonUser = CommonUser.objects.get(commonUserID=commonUserID)
    if not commonUser.isManagedBy(admin):
        return HttpResponseRedirect(reverse("welcome", args=(1,)))
    try:
        if request.POST.get("deletePhoto", "0") == "1":
            if len(str(commonUser.commonUserImage)) != 0:
                if os.path.exists(os.path.join(".", ".", os.getcwd(), "media", "userImage", str(commonUser.cuImage))):
                    os.remove(os.path.join(".", ".", os.getcwd(), "media", "userImage", str(commonUser.cuImage)))
            commonUser.commonUserImage = None
            UserOperation.objects.create(verifiedUser=admin, operationType='upUser', commonUser=CommonUser,
                                         content="Delete photo")
        if request.POST.get("changeArea", "0") == "1":
            originalName = commonUser.area.areaName
            commonUser.area = Area.objects.get(arName=request.POST.get("newArName"))
            UserOperation.objects.create(verifiedUser=admin, operationType='upUser', commonUser=CommonUser,
                                         content="Original area:" + originalName + " New area:" + request.POST.get(
                                             "newArName"))
        commonUser.save()
    except Exception as e:
        print(e)
    return HttpResponseRedirect(reverse("USFP:adminViewUser", args=(commonUserID,)))
