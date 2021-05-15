from django.conf.urls import url

from . import views, commonUser, myAdmin

urlpatterns = [
    url(r'^login/#error=(?P<error>[0-1]{1})$', views.login, name='login'),
    url(r'^register/$', views.register, name='register'),
    url(r'^register/successful/$', views.suRegister, name="suRegister"),
    url(r'^forgetPassword/$', views.forgetPassword, name="forgetPassword"),
    url(r'^suChangePwd/$', views.suChangePwd, name="suChangePwd"),
    url(r'^CommonUser/userInfor/$', commonUser.userInfor, name="userInfor"),
    url(r'^CommonUser/userChange/#changeType=(?P<changeType>.*)$', commonUser.userChange, name="userChangeInfor"),
    url(r'^CommonUser/userSuChange#changeType=(?P<changeType>.*)$', commonUser.userSuChange, name="userSuChange"),
    url(r'^CommonUser/userInfor/userViewSuggestions/#num=(?P<num>\d*)$', commonUser.userViewSuggestions,
        name="userViewSuggestions"),
    url(r'^CommonUser/userInfor/userDeleteSuggestions/$', commonUser.userDeleteSuggestions,
        name="userDeleteSuggestions"),
    url(r'^CommonUser/userViewOneSuggestion/#suggesionID=(?P<suggesionID>.*)$', commonUser.userViewOneSuggestion,
        name="userViewOneSuggestion"),
    url(r'^Admin/adminInfor/$', myAdmin.adminInfor, name="adminInfor"),
    url(r'^Admin/adminInfor/adminViewOperations/#areaOperationNum=(?P<areaOperationNum>\d*)&userOperationNum=('
        r'?P<userOperationNum>\d*)$', myAdmin.adminViewOperations, name="adminViewOperations"),
    url(r'^Admin/adminChangeInfor/#changeType=(?P<changeType>.*)$', myAdmin.adminChangeInfor, name="adminChangeInfor"),
    url(r'^Admin/adminSuChange/#changeType=(?P<changeType>.*)$', myAdmin.adminSuChange, name="adminSuChange"),
    url(r'^Admin/adminInfor/adminViewArea/#num=(?P<num>\d*)&areaID=(?P<areaID>\d*)$', myAdmin.adminViewArea,
        name="adminViewArea"),
    url(r'^Admin/adminDeleteUsers/$', myAdmin.adminDeleteUsers, name="adminDeleteUsers"),
    url(r'^Admin/adminInfor/adminViewUser/#commonUserID=(?P<commonUserID>\d*)$', myAdmin.adminViewUser,
        name="adminViewUser"),
    url(r'^Admin/adminInfor/adminUpdateUser/#commonUserID=(?P<commonUserID>\d*)$', myAdmin.adminUpdateUser,
        name="adminUpdateUser"),
    url(r'^Admin/adminInfor/adminViewUserSuggestions/#commonUserID=(?P<commonUserID>\d*)&num=(?P<num>\d*)$',
        myAdmin.adminViewUserSuggestions, name="adminViewUserSuggestions"),
    url(r'^Admin/adminInfor/adminViewUserSuggestions/adminOperateSuggestions$',
        myAdmin.adminOperateSuggestions,name="adminOperateSuggestions"),
    url(r'^Admin/adminViewOneSuggestion/#suggestionID=(?P<suggestionID>\d*)$',myAdmin.adminViewOneSuggestion,
        name="adminViewOneSuggestion"),
]
