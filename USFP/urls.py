from django.conf.urls import url

from . import views,commonUser,myAdmin
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
    url(r'^Admin/adminInfor/$', myAdmin.adminInfor, name="adminInfor"),
    url(r'^Admin/adminInfor/viewOperations/#num=(?P<num>\d*)$', myAdmin.viewOperations, name="viewOperations"),
    url(r'^Admin/adminChangeInfor/#changeType=(?P<changeType>.*)$', myAdmin.adminChangeInfor, name="adminChangeInfor"),
    url(r'^Admin/adminSuChange/#changeType=(?P<changeType>.*)$', myAdmin.adminSuChange, name="adminSuChange"),
]
