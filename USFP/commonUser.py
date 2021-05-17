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
    if user.isVerified():
        return render(request, "CommonUser/userInfor.html",
                      {"user": user, 'verified': 1})
    else:
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
    if changeType == "EmailAdd":
        newEmailAdd = request.POST.get("newEmailAdd", "")
        user.update(commonUserEmail=newEmailAdd)
        if newEmailAdd.endswith('@mail.uic.edu.cn') and user[0].isVerified():
            verified = user[0].VerifiedUser
            if request.POST.get('wantToBeAdmin', '') == 'wantToBeAdmin':
                verified.isAdmin = True
                verified.save()
        elif newEmailAdd.endswith('@mail.uic.edu.cn'):
            if request.POST.get('wantToBeAdmin', '') == 'wantToBeAdmin':
                VerifiedUser.objects.create(isAdmin=True, commonUser=user[0])
            else:
                VerifiedUser.objects.create(commonUser=user[0])
    if changeType == "Image":
        photo = request.FILES.get("photo", "")
        photoName = str(request.session['commonUserID']) + "." + photo.name.split(".")[1]
        photo_resize = Image.open(photo)
        photo_resize.thumbnail((371, 475), Image.ANTIALIAS)
        if os.path.isfile(os.path.join(".", ".", os.getcwd(), "media", str(user[0].commonUserImage))):
            os.remove(os.path.join(".", ".", os.getcwd(), "media", str(user[0].commonUserImage)))
        photo_resize.save(os.path.join(".", ".", os.getcwd(), "media", "userImage", photoName))
        user.update(commonUserImage="userImage/" + photoName)
    if changeType == "Name":
        newName = request.POST.get("newName", "")
        user.update(commonUserName=newName)
    if changeType == "Password":
        newPassword = request.POST.get("password", "")
        user.update(commonUserPassword=newPassword)
    return HttpResponseRedirect(reverse("USFP:userSuChange", args=(changeType,)))


def userSuChange(request, changeType):
    return render(request, "CommonUser/userSuChange.html", {"changeType": changeType})


def userViewSuggestions(request, num):
    try:
        user = CommonUser.objects.get(commonUserID=request.session['commonUserID'])
    except KeyError:
        return HttpResponseRedirect(reverse("welcome", args=(1,)))
    suggestions = user.Suggestion.filter(visible=True)
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

    return render(request, "CommonUser/userViewSuggestions.html",
                  {"suggestionPager": suggestionPager, 'suggestionPrepageData': suggestionPrepageData,
                   "suggestionPageList": suggestionPageList})


def userDeleteSuggestions(request):
    if request.method == 'GET':
        return HttpResponse('Fail')
    deleteList = [i for i in request.POST.get("listToDelete").split("-") if len(i) != 0]
    try:
        for i in deleteList:
            suggestionToDelete = Suggestion.object.get(suggestionID=int(i))
            suggestionToDelete.visible = False
            suggestionToDelete.save()
    except Exception as e:
        print(e)
        return HttpResponse("Fail")
    return HttpResponse("Success")


def userViewOneSuggestion(request, suggestionID):
    try:
        user = CommonUser.object.get(commonUserID=request.session['commonUserID'])
        suggestion = Suggestion.object.get(suggestionID=suggestionID)
        if suggestion.commonUser != user:
            return HttpResponseRedirect(reverse("welcome", args=(1,)))
        return HttpResponse(suggestion.content)
    except Exception as e:
        print(e)
        return HttpResponseRedirect(reverse("welcome", args=(1,)))
