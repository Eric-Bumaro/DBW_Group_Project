from django.conf.urls import url

from . import views, commonUser, myAdmin
from .models import *

urlpatterns = [
    url(r'^login/#error=(?P<error>[0-1]{1})$', views.login, name='login'),
    url(r'^register/$', views.register, name='register'),
    url(r'^register/successful/$', views.suRegister, name="suRegister"),
    url(r'^forgetPassword/$', views.forgetPassword, name="forgetPassword"),
    url(r'^suChangePwd/$', views.suChangePwd, name="suChangePwd"),
    url(r'^CommonUser/userInfor/$', commonUser.userInfor, name="userInfor"),
    url(r'^CommonUser/userChange/#changeType=(?P<changeType>.*)$', commonUser.userChange, name="userChangeInfor"),
    url(r'^CommonUser/userSuChange#changeType=(?P<changeType>.*)$', commonUser.userSuChange, name="userSuChange"),
    url(r'^CommonUser/userInfor/userViewSuggestion/#num=(?P<num>\d*)$', commonUser.userViewSuggestion, name="userViewSuggestion"),
    url(r'^Admin/adminInfor/$', myAdmin.adminInfor, name="adminInfor"),
    url(r'^Admin/adminInfor/viewOperations/#areaOperationNum=(?P<areaOperationNum>\d*)&userOperationNum=('
        r'?P<userOperationNum>\d*)$', myAdmin.viewOperations, name="viewOperations"),
    url(r'^Admin/adminChangeInfor/#changeType=(?P<changeType>.*)$', myAdmin.adminChangeInfor, name="adminChangeInfor"),
    url(r'^Admin/adminSuChange/#changeType=(?P<changeType>.*)$', myAdmin.adminSuChange, name="adminSuChange"),
    url(r'^Admin/adminInfor/adminViewArea/#num=(?P<num>\d*)&areaID=(?P<areaID>\d*)$', myAdmin.adminViewArea,
        name="adminViewArea"),
    url(r'^Admin/adminDeleteUser/$', myAdmin.adminDeleteUser, name="adminDeleteUser"),
    url(r'^Admin/adminInfor/adminViewUser/#commonUserID=(?P<commonUserID>\d*)$', myAdmin.adminViewUser,
        name="adminViewUser"),
    url(r'^Admin/adminInfor/adminUpdateUser/#commonUserID=(?P<commonUserID>\d*)$', myAdmin.adminUpdateUser,
        name="adminUpdateUser")
]
