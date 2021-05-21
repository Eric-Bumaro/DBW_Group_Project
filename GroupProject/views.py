from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render

from USFP.littleTools import *
from USFP.models import *


def welcome(request, logout=0):
    if (logout):
        request.session.clear()
        return render(request, 'View/welcome.html')
    try:
        user = CommonUser.object.get(commonUserID=request.session['commonUserID'])
        try:
            if user.VerifiedUser.isAdmin:
                return render(request, 'View/welcome.html', {'user': user,'isAdmin':True,"allTags":Tag.objects.all()})
        except:
            return render(request, 'View/welcome.html', {'user': user, 'isAdmin': False})
    except KeyError as e:
        return render(request, 'View/welcome.html',{'user.commonUserID':0})


def getUserKey(request):
    try:
        commonUserID=request.POST.get('commonUserID',"")
        to_add = CommonUser.object.get(commonUserID=int(commonUserID)).commonUserEmail
        key = sendEmail(to_add)
        return HttpResponse(key)
    except Exception as e:
        return HttpResponse(1)


def getAdKey(request):
    try:
        return HttpResponse(sendAdKey())
    except:
        return HttpResponse(1)


def sendCheckKey(request):
    try:
        emailAdd = request.POST.get('emailAdd',"")
        key = sendEmail(emailAdd)
        return HttpResponse(key)
    except:
        return HttpResponse(1)


def refreshDB(request):
    try:
        assert request.session['adID']== 1
        assert request.method=="POST"
    except Exception as e:
        print(e)
        return HttpResponse("Fail")
    userList=CommonUser.objects.filter(isDelete=True)
    areaList=Area.objects.filter(isDelete=True)
    suggestionList=Suggestion.objects.filter(isDelete=True)
    replySuggestionList=ReplySuggestion.objects.filter(isDelete=True)
    deleteList=[userList,areaList,suggestionList,replySuggestionList]
    nowDate=datetime.now()
    for i in deleteList:
        for j in i:
            try:
                if ((nowDate - j.deleteDate).days > 14):
                    j.delete()
            except Exception as e:
                print(e)
    return HttpResponse("Success")