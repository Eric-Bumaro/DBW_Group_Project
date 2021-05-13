import datetime
import json
import math
import os
from PIL import Image
from django.core.paginator import Paginator, EmptyPage
from django.http import *
from django.shortcuts import render
from django.urls import reverse
from USFP.models import *


def userInfor(request):
    user = CommonUser.objects.get(commonUserID=request.session['commonUserID'])
    try:
        user.VerifiedUser
        return render(request, "CommonUser/userInfor.html",
                      {"user": user, 'verified': 1})
    except:
        return render(request, "CommonUser/userInfor.html",
                      {"user": user, 'verified': 0})


def userChange(request, changeType):
    if request.method == 'GET':
        if changeType == "EmailAdd" or changeType == "Password":
            return render(request, "CommonUser/userChangeInfor.html",
                          {"changeType_js": json.dumps(changeType), "changeType_py": changeType,
                           "commonUserID": request.session['commonUserID']})
        if changeType == "Image" or changeType == "Name":
            return render(request, "CommonUser/userChangeInfor.html",
                          {"changeType_js": json.dumps(changeType), "changeType_py": changeType})

    user = CommonUser.object.filter(commonUserID=request.session['commonUserID'])
    if (changeType == "EmailAdd"):
        newEmailAdd = request.POST.get("newEmailAdd", "")
        user.update(commonUseEmail=newEmailAdd)
        try:
            if newEmailAdd.endwith('@mail.uic.edu.cn'):
                verified = user[0].VerifiedUser
                if request.POST.get('wantToBeAdmin', '') == 'wantToBeAdmin':
                    verified.isAdmin = True
                    verified.save()
            else:
                verified = user[0].VerifiedUser
                verified.delete()
        except:
            if newEmailAdd.endwith('@mail.uic.edu.cn') and request.POST.get('wantToBeAdmin', '') == 'wantToBeAdmin':
                VerifiedUser.objects.create(isAdmin=True, commonUser=user[0])
    if (changeType == "Image"):
        photo = request.FILES.get("photo", "")
        photoName = str(request.session['commonUserID']) + "." + photo.name.split(".")[1]
        photo_resize = Image.open(photo)
        photo_resize.thumbnail((371, 475), Image.ANTIALIAS)
        if os.path.isfile(os.path.join(".", ".", os.getcwd(), "media", str(user[0].uImage))):
            os.remove(os.path.join(".", ".", os.getcwd(), "media", str(user[0].uImage)))
        photo_resize.save(os.path.join(".", ".", os.getcwd(), "media", "userImage", photoName))
        user.update(commonUserImage="userImage/" + photoName)
    if (changeType == "Name"):
        newName = request.POST.get("newName", "")
        user.update(commonUserName=newName)
    if (changeType == "Password"):
        newPassword = request.POST.get("password", "")
        user.update(commonUserPassword=newPassword)
    return HttpResponseRedirect(reverse("loginModel:userSuChange", args=(changeType,)))


def userSuChange(request, changeType):
    return render(request, "CommonUser/userSuChange.html", {"changeType": changeType})


def userViewSuggestion(request,num):
    try:
        user = CommonUser.objects.get(commonUserID=request.session['commonUserID'])
        user.VerifiedUser
    except KeyError:
        return HttpResponseRedirect(reverse("welcome", args=(1,)))
    suggestions=Suggestion.objects.get(commonUser=user,visible=False)
    if int(num) < 1:
        suggestionNum = 1
    else:
        suggestionNum = int(num)
    suggestionPager = Paginator(suggestions, 10)
    try:
        suggestionPrepageData = suggestionPager.page(suggestionNum)
    except EmptyPage:
        suggestionPrepageData = suggestionPager.page(suggestionPager.num_pages)
    begin = (suggestionNum - int(math.ceil(10.0 / 2)))
    if begin < 1:
        begin = 1
    end = begin + 4
    if end > suggestionPager.num_pages:
        end = suggestionPager.num_pages
    if end <= 5:
        begin = 1
    else:
        begin = end - 4
    suggestionPageList = range(begin, end + 1)
    return render(request, "CommonUser/userViewSuggestion.html",
                  {"pager": suggestionPager, 'prepageData': suggestionPrepageData, "pageList": suggestionPageList})