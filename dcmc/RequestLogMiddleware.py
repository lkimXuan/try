#!/usr/bin/env python
# -*- coding: utf-8 -*-
# # 自定义中间件

import logging
import threading
import rest_framework_simplejwt

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object
local = threading.local()

class RequestLogFilter(logging.Filter):
    '''
    日志过滤器，将当前请求线程的request信息保存到日志的record上下文
    record带有formater需要的信息
    '''
    def filter(self, record):
        record.uri = getattr(local, 'uri', None)
        record.source_ip = getattr(local, 'source_ip', None)  # 请求IP
        record.username = getattr(local, 'username', None)  # 请求用户
        return True

class RequestLogMiddleware(MiddlewareMixin):
    '''
    将request的信息记录在当前的请求线程上。
    '''
    def process_request(self, request):
        uri = request.path_info
        local.uri = uri

        setattr(request, '_dont_enforce_csrf_checks', True)
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if x_forwarded_for:
            # 所以这里是真实的ip
            source_ip = x_forwarded_for
        else:
            # 这里获得代理ip
            source_ip = request.META.get('REMOTE_ADDR')
        local.source_ip = source_ip

        # 处理JWT，获得用户对象
        # try:
        #     token = request.headers.get('Authorization')
        #     print(token)
        #     token_msg = rest_framework_simplejwt.authentication.JWTAuthentication().get_validated_token(token)
        #     user_object = rest_framework_simplejwt.authentication.JWTAuthentication().get_user(token_msg)
        #     request.user = user_object
        #     local.username = request.user.username
        # except:
        #     local.username = request.user

    def process_response(self, request, response):
        return response
