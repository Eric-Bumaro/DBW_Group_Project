import datetime
import json
import math
import os

import jieba
import nltk
from PIL import Image
from django.core.paginator import Paginator, EmptyPage
from django.db import transaction
from django.db.models import Count
from django.http import *
from django.shortcuts import render, redirect
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
    suggestions = user.Suggestion.filter(visible=True).order_by("postTime")
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
                   "suggestionPageList": suggestionPageList, "user": user})


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


def userViewOneSuggestion(request, suggestionID, num):
    try:
        user = CommonUser.object.get(commonUserID=request.session.get('commonUserID', 5))
        suggestion = Suggestion.object.get(suggestionID=suggestionID)
        if user.isVerified():
            if suggestion.commonUser.area in user.VerifiedUser.adminArea.all():
                return HttpResponseRedirect(reverse("USFP:adminViewOneSuggestion", args=(suggestionID, 1)))
        if suggestion.isReplied():
            replySuggestionList = suggestion.ReplySuggestion.filter(selfSuggestion__isDelete=False,
                                                                    selfSuggestion__visible=True).order_by(
                "selfSuggestion__postTime")
        else:
            replySuggestionList = []
        if int(num) < 1:
            replyNum = 1
        else:
            replyNum = int(num)
        replySuggestionPager = Paginator(replySuggestionList, 10)
        try:
            replySuggestionPrepageData = replySuggestionPager.page(replyNum)
        except EmptyPage:
            replySuggestionPrepageData = replySuggestionPager.page(replySuggestionPager.num_pages)
        begin = (replyNum - int(math.ceil(10.0 / 2)))
        if begin < 1:
            begin = 1
        end = begin + 4
        if end > replySuggestionPager.num_pages:
            end = replySuggestionPager.num_pages
        if end <= 5:
            begin = 1
        else:
            begin = end - 4
        replySuggestionPageList = range(begin, end + 1)
        return render(request, "CommonUser/userViewOneSuggestion.html", {"suggestion": suggestion,
                                                                         "isAuthor": suggestion.commonUser == user,
                                                                         'user': user, 'isVerified': user.isVerified(),
                                                                         'replySuggestionPrepageData': replySuggestionPrepageData,
                                                                         'replySuggestionPageList': replySuggestionPageList,
                                                                         "suggestion_tags": suggestion.tags.all()})
    except Exception as e:
        print(e)
        return redirect("welcome")


def userChangeSuggestion(request, suggestionID):
    user = CommonUser.object.get(commonUserID=request.session.get("commonUserID", 5))
    if request.method == "GET":
        return render(request, "CommonUser/userChangeSuggestion.html", {'suggestionID': suggestionID, 'user': user})
    suggestion = Suggestion.object.get(suggestionID=suggestionID)
    save_tag = transaction.savepoint()
    try:
        for i in suggestion.tags.all():
            i.tagShowNum = i.tagShowNum - 1
            suggestion.tags.remove(i)
            i.save()
        newContent = request.POST.get("newSuggestionContent")
        suggestionCuttedList = jieba.cut_for_search(newContent)
        suggestionCuttedList = " ".join(suggestionCuttedList)
        allTagsList = list(Tag.objects.values_list("tagName", flat=True))
        suggestion.content = newContent
        for i in nltk.pos_tag(nltk.word_tokenize(suggestionCuttedList)):
            if i[1].startswith('N'):
                if i[0].lower() in allTagsList:
                    tag = Tag.objects.get(tagName=i[0].lower())
                    suggestion.tags.add(tag)
                    tag.tagShowNum = tag.tagShowNum + 1
                    tag.save()
                else:
                    newTag = Tag.objects.create(tagName=i[0].lower(), tagShowNum=1)
                    suggestion.tags.add(newTag)
        suggestion.save()
        if not user.isVerified():
            suggestion.visible = False
        suggestion.save()
        return render(request, "CommonUser/userSuChangeSuggestion.html", {'suggestionID': suggestion.suggestionID})
    except Exception as e:
        print(e)
        transaction.savepoint_rollback(save_tag)
        return redirect("welcome")


def userSubmitComment(request, suggestionID):
    try:
        content = request.POST.get("replySuggestionContent")
        user = CommonUser.object.get(commonUserID=request.session.get("commonUserID", 5))
        newComment = Suggestion.objects.create(content=content, commonUser=user, visible=True)
        ReplySuggestion.objects.create(selfSuggestion=newComment,
                                       suggestionToReply=Suggestion.objects.get(suggestionID=suggestionID))
        return HttpResponseRedirect(reverse("USFP:userViewOneSuggestion", args=(suggestionID, 1)))
    except Exception as e:
        print(e)
        return redirect("welcome")


def viewTag(request, tagID, num):
    tag = Tag.objects.get(tagID=tagID)
    suggestions = tag.Suggestion.filter(visible=True).order_by("postTime")
    user = CommonUser.objects.get(commonUserID=request.session.get("commonUserID", 5))
    if int(num) < 1:
        num = 1
    else:
        num = int(num)
    suggestionPager = Paginator(suggestions, 10)
    try:
        suggestionPrepageData = suggestionPager.page(num)
    except EmptyPage:
        suggestionPrepageData = suggestionPager.page(suggestionPager.num_pages)
    begin = (num - int(math.ceil(10.0 / 2)))
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
    isAdmin = False
    if user.isVerified():
        if user.VerifiedUser.isAdmin:
            isAdmin = True
    return render(request, "View/viewTag.html",
                  {"suggestionPager": suggestionPager, 'suggestionPrepageData': suggestionPrepageData,
                   "suggestionPageList": suggestionPageList, "user": user, "isAdmin": isAdmin, "tag": tag})
