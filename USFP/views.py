import nltk
# nltk.download()
from django.db import transaction
from django.db.models import *
from django.shortcuts import render
import json
import os
import random
from PIL import Image
from django.http import *
from django.shortcuts import render, redirect
from django.urls import reverse
from nltk.corpus import stopwords

from USFP.models import *
import jieba


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
                                         commonUserEmail=commonUserEmail, commonUserImage="userImage/" + photoName,
                                         area=Area.object.get(areaID=random.randint(1, len(areaIDList) + 1)))
    except Exception as e:
        print(e)
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


@transaction.atomic
def submitSuggestion(request):
    if request.method == 'GET':
        commonUserID = request.session.get("commonUserID", 5)
        commonUser = CommonUser.object.get(commonUserID=commonUserID)
        return render(request, "View/submitSuggestion.html", {'user': commonUser})
    save_tag = transaction.savepoint()
    try:
        commonUserID = request.session.get("commonUserID", 5)
        commonUser = CommonUser.object.get(commonUserID=commonUserID)
        suggestion = request.POST.get("suggestionContent")
        suggestionObject = Suggestion.objects.create(content=suggestion, commonUser=commonUser)
        suggestionCuttedList = jieba.cut_for_search(suggestion)
        suggestionCuttedList = " ".join(suggestionCuttedList)
        allTagsList = list(Tag.objects.values_list("tagName", flat=True))
        suggestionObject.save()
        for i in nltk.pos_tag(nltk.word_tokenize(suggestionCuttedList)):
            if i[1].startswith('N') and i[0] not in stopwords.words('english'):
                if i[0].lower() in allTagsList:
                    tag = Tag.objects.get(tagName=i[0].lower())
                    suggestionObject.tags.add(tag)
                    tag.tagShowNum = tag.tagShowNum+1
                    tag.save()
                else:
                    newTag = Tag.objects.create(tagName=i[0].lower(),tagShowNum=1)
                    suggestionObject.tags.add(newTag)
        suggestionObject.save()
        return render(request, "View/submitSuggestionResult.html",
                      {"state": 1, "suggestionID": suggestionObject.suggestionID, 'user': commonUser})
    except Exception as e:
        print(e)
        transaction.savepoint_rollback(save_tag)
        return render(request, "View/submitSuggestionResult.html", {"state": 0, 'user': commonUser})


def searchSuggestion(request):
    try:
        suggestionID = int(request.POST.get("searchSuggestionID", ""))
        commonUser = CommonUser.object.get(commonUserID=request.session.get("commonUserID", 5))
        suggestion = Suggestion.object.get(suggestionID=suggestionID)
        assert not suggestion.isDelete
        if commonUser.isVerified():
            if suggestion.commonUser.area in commonUser.VerifiedUser.adminArea.all():
                return HttpResponseRedirect(reverse("USFP:adminViewOneSuggestion",args=(suggestionID,1)))
        return render(request, "View/searchSuggestion.html", {"suggestion": suggestion, "isAuthor": (suggestion.commonUser.commonUserID==commonUser.commonUserID),
                                                              'user': commonUser})
    except Exception as e:
        print(e)
        return redirect("welcome")
