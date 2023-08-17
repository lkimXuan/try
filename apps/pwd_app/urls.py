# -*- coding: utf-8 -*-
# @Time : 2023/8/14 14:25
# @Author : Samuel
# @FileName: urls.py
from django.conf.urls.static import static
from django.urls import path
from dcmc import settings
from .views import *


urlpatterns = [
    path('update/',UpdatePWD.as_view()),
    path('send_msg/',SendMSG.as_view()),
    path('verify_code/',VerifyCode.as_view()),
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)