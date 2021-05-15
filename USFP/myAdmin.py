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
    adminArea = admin.VerifiedUser.adminArea.filter(isDelete=False)
    if request.method == "GET":
        return render(request, "Admin/adminInfor.html",
                      {"admin": admin, "areaSet": adminArea, "areaIDs_js": json.dumps(list(adminArea.values("areaID")))})
    else:
        for i in adminArea:
            try:
                if request.POST.get("deleteArea" + str(i.areaID), "0") == "1":
                    i.isDelete = True
                    i.deleteDate = datetime.now()
                    operation = AreaOperation(verifiedUser=admin.VerifiedUser, area=i, operationType="deleteArea",
                                              content="Delete the area")
                    operation.save()
                    i.save()
                if request.POST.get("updataAreaName" + str(i.areaID), "0") == "1":
                    originalName = i.areaName
                    i.areaName = request.POST.get("newAreaName" + str(i.areaID))
                    operation = AreaOperation(verifiedUser=admin.VerifiedUser, operationType="updateArea", area=i,
                                              content="Origin Name:" + originalName + " " + "New Name:" + request.POST.get(
                                                  "newAreaName" + str(i.areaID)))
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
        if os.path.isfile(os.path.join(".", ".", os.getcwd(), "media", str(admin.commonUserImage))):
            os.remove(os.path.join(".", ".", os.getcwd(), "media", str(admin.commonUserImage)))
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
                if not userToDelete.isManagedBy(admin):
                    return HttpResponse("Fail")
                userToDelete.isDelete = True
                userToDelete.deleteDate = datetime.now()
                userToDelete.save()
                CommonUserOperation.objects.create(commonUser=userToDelete, operationType='deleteUser',
                                             content="Delete the user", verifiedUser=admin.VerifiedUser)
        except Exception as e:
            print(e)
            return HttpResponse("Fail")
        return HttpResponse("Success")
    except Exception as e:
        print(e)
        return HttpResponse("Fail")


def adminViewOperations(request, areaOperationNum, userOperationNum):
    try:
        user = CommonUser.objects.get(commonUserID=request.session['commonUserID'])
        if not user.isVerified():
            return HttpResponseRedirect(reverse("welcome", args=(1,)))
    except KeyError:
        return HttpResponseRedirect(reverse("welcome", args=(1,)))
    areaOperations = user.VerifiedUser.AreaOperation.order_by("-operationTakeDate")
    if int(areaOperationNum) < 1:
        areaOperationNum = 1
    else:
        areaOperationNum = int(areaOperationNum)
    areaPager = Paginator(areaOperations, 10)
    try:
        areaPrepageData = areaPager.page(areaOperationNum)
    except EmptyPage:
        areaPrepageData = areaPager.page(areaPager.num_pages)
    begin = (areaOperationNum - int(math.ceil(10.0 / 2)))
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
    userOperations = user.VerifiedUser.UserOperation.order_by("-operationTakeDate")
    if int(userOperationNum) < 1:
        userOperationNum = 1
    else:
        userOperationNum = int(userOperationNum)
    userPager = Paginator(userOperations, 10)
    try:
        userPrepageData = userPager.page(userOperationNum)
    except EmptyPage:
        userPrepageData = userPager.page(userPager.num_pages)
    begin = (userOperationNum - int(math.ceil(10.0 / 2)))
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
                  {"areaCurPage": areaOperationNum, 'areaPrepageData': areaPrepageData, "areaPageList": areaPageList,
                   "userCurPage": userOperationNum, "userPrepageData": userPrepageData, "userPageList": userPageList},
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
    if request.method == "GET":
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
            CommonUserOperation.objects.create(verifiedUser=admin.VerifiedUser, operationType='updateUser', commonUser=CommonUser,
                                         content="Delete photo")
        if request.POST.get("changeArea", "0") == "1":
            originalName = commonUser.area.areaName
            commonUser.area = Area.objects.get(arName=request.POST.get("newArName"))
            CommonUserOperation.objects.create(verifiedUser=admin.VerifiedUser, operationType='updateUser',
                                               commonUser=CommonUser,
                                               content="Original area:" + originalName + " New area:" + request.POST.get("newArName"))
        commonUser.save()
    except Exception as e:
        print(e)
    return HttpResponseRedirect(reverse("USFP:adminViewUser", args=(commonUserID,)))


def adminViewUserSuggestions(request,commonUserID,num):
    admin=CommonUser.objects.get(commonUserID=request.session['commonUserID'])
    user=CommonUser.objects.get(commonUserID=commonUserID)
    if not user.isManagedBy(admin):
        return HttpResponseRedirect(reverse("welcome", args=(1,)))
    suggestions = [i for i in user.Suggestion.filter(isDelete=False)]
    if int(num) < 1:
        num = 1
    else:
        num = int(num)
    pager = Paginator(suggestions, 10)
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
    return render(request, "Admin/adminViewUserSuggestions.html",
                  {"pager": pager, 'prepageData': prepageData, "pageList": pagelist,"commonUserID":commonUserID})


def adminOperateSuggestions(request):
    try:
        operateType=request.POST.get("operateType")
        admin=CommonUser.object.get(commonUserID=request.session['commonUserID'])
        if not admin.isVerified():
            return HttpResponse("Fail")
        if operateType=="delete":
            listToDelete=request.POST.get("listToDelete").split("-")
            listToDelete=[i for i in listToDelete if len(i)!=0]
            for i in listToDelete:
                suggestion=Suggestion.objects.get(suggestionID=int(i))
                suggestion.isDelete=True
                suggestion.visible=False
                suggestion.deleteDate=datetime.now()
                suggestion.save()
                SuggestionOperation.objects.create(suggestion=suggestion,operationType='deleteSuggestion')
        elif operateType=="hide":
            listToHide=request.POST.get("listToHide")
            listToHide=[i for i in listToHide if len(i)!=0]
            for i in listToHide:
                suggestion=Suggestion.objects.get(suggestionID=int(i))
                suggestion.visible=False
                suggestion.save()
                SuggestionOperation.objects.create(suggestion=suggestion,operationType='hideSuggestion')
        elif operateType=="show":
            listToShow=request.POST.get("listToShow")
            listToShow=[i for i in listToShow if len(i)!=0]
            for i in listToShow:
                suggestion=Suggestion.objects.get(suggestionID=int(i))
                suggestion.visible=True
                suggestion.save()
                SuggestionOperation.objects.create(suggestion=suggestion,operationType='showSuggestion')
        else:
            return HttpResponse("Fail")
    except Exception as e:
        print(e)
        return HttpResponse("Fail")