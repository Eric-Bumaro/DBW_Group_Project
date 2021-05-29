import os
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import render
from USFP.littleTools import *
from USFP.models import *


def welcome(request, logout=0):
    if logout:
        request.session.clear()
        return render(request, 'View/welcome.html',{"allTags":Tag.objects.filter(tagShowNum__gt=0).order_by("-tagShowNum")})
    try:
        user = CommonUser.object.get(commonUserID=request.session['commonUserID'])
        try:
            if user.VerifiedUser.isAdmin:
                return render(request, 'View/welcome.html', {'user': user,'isAdmin':True,
                                                             "allTags":Tag.objects.filter(tagShowNum__gt=0).order_by("-tagShowNum")})
        except:
            return render(request, 'View/welcome.html', {'user': user, 'isAdmin': False,
                                                         "allTags":Tag.objects.filter(tagShowNum__gt=0).order_by("-tagShowNum")})
    except KeyError as e:
        return render(request, 'View/welcome.html',{'user.commonUserID':5,
                                                    "allTags":Tag.objects.filter(tagShowNum__gt=0).order_by("-tagShowNum")})


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
        assert request.session['commonUserID']== 1
        assert request.method=="POST"
    except Exception as e:
        print(e)
        return HttpResponse("Fail")
    userList=CommonUser.objects.filter(isDelete=True)
    areaList=Area.objects.filter(isDelete=True)
    suggestionList=Suggestion.objects.filter(isDelete=True)
    deleteList=[userList,areaList,suggestionList]
    nowDate=datetime.now()
    for i in deleteList:
        for j in i:
            try:
                if ((nowDate - j.deleteDate).days > 14):
                    j.delete()
            except Exception as e:
                print(e)
    return HttpResponse("Success")


def page_not_found(request,exception):
    return render(request,'Error/404.html',{"allTags":Tag.objects.filter(tagShowNum__gt=0).order_by("-tagShowNum")})


def startScrapy(request):
    # try:
    #     assert request.session['commonUserID']== 1
    #     assert request.method=="POST"
    # except Exception as e:
    #     print(e)
    #     return HttpResponse("Fail")
    # os.system('cd ZhiHuScrapy;scrapy crawl ZhiHuScrapy')
    return HttpResponse("Done")