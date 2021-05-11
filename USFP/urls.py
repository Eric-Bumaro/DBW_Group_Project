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
]
