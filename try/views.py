import random
import re
from django import forms
from django.shortcuts import redirect, render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db import models
from django.forms import ValidationError
from django.urls import reverse
from django_redis import get_redis_connection
from django.views.decorators.csrf import csrf_exempt


from mid import settings 

@csrf_exempt   
def getphone(request):
    if request.method == 'POST':
        name = request.POST.get('user')
        phone = request.POST.get('mobile')
        
        # 进行手机号码验证并发送短信
        print(name, phone) 
        print("假装发送了验证码")
        return render(request, 'IDverify.html')
    else:
        return render(request, 'IDverify.html')

@csrf_exempt
def getcode(request):
    testcode = "0609"
    if request.method == 'POST':
        name = request.POST.get('user')
        phone = request.POST.get('mobile')
        code = request.POST.get('code')
        if code:
            print(name, phone, code) 
            if code == testcode:
                return redirect('/reset')
            else:
                return HttpResponse("匹配不成功")
        else:
            getphone(request)
            return render(request, 'IDverify.html')
    else:
        return render(request, 'IDverify.html')

def reset(request):
    if request.method == 'POST':
        return HttpResponse("修改密码")
    else:
        return render(request, 'password.html')
