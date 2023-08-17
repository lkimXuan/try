import json
import logging
import random
import sys
import time
from django.http import JsonResponse
from django_redis import get_redis_connection
from rest_framework.views import APIView
from ad_utils.ad_init import AD
from msg_utils.send_msg import send_msg

logger_user = logging.getLogger('user')
logger_sms = logging.getLogger('sms')


class UpdatePWD(APIView):
    def post(self, request, *args, **kwargs):
        try:
            ad_init = AD()
            conn = ad_init.conn
            conn.open()
            conn.bind()
            ad_account = request.data['account']
            pre_pwd = request.data['old_pwd']
            current_pwd = request.data['new_pwd']
            account_data = ad_init.getAccountInfo(ad_account)
            if account_data['state'] == 'success':
                account_ou = account_data['ou']
            else:
                log_msg = {
                    'info': '用户ad信息获取失败',
                    'user': ''.format(ad_account),
                    'time': ''.format(time.asctime(time.localtime(time.time())))
                }
                logger_user.error(json.dumps(log_msg, ensure_ascii=False))
                res = {
                    'code': 500,
                    'info': '用户ad信息获取失败',
                }
                return JsonResponse(res)

            # 修改密码:
            try:
                conn.extend.microsoft.modify_password(account_ou, old_password=pre_pwd, new_password=current_pwd)
                result = conn.result
                if result['result'] == 0:
                    conn.unbind()
                    log_msg = {
                        'info': '修改密码成功',
                        'user': '用户'.format(ad_account),
                        'time': ''.format(time.asctime(time.localtime(time.time())))
                    }
                    res = {
                        'code': 200,
                        'info': '修改密码成功'
                    }
                    logger_user.info(json.dumps(log_msg, ensure_ascii=False))
                    return JsonResponse(res)
                else:
                    log_msg = {
                        'info': '修改密码失败',
                        'user': '用户'.format(ad_account),
                        'time': ''.format(time.asctime(time.localtime(time.time())))
                    }
                    res = {
                        'code': 500,
                        'info': '修改密码失败'
                    }
                    logger_user.info(json.dumps(log_msg, ensure_ascii=False))
                    return JsonResponse(res)
            except Exception as e:
                log_msg = {
                    'info': '修改密码失败',
                    'user': '用户名',
                    'time': ''.format(time.asctime(time.localtime(time.time()))),
                    'detail': '异常信息：{}'.format(sys.exc_info()[0]),
                }
                logger_user.error(json.dumps(log_msg, ensure_ascii=False))
                res = {
                    'code': 500,
                    'info': '修改密码失败',
                }
                return JsonResponse(res)
        except Exception as e:
            log_msg = {
                'info': 'AD初始化失败',
                'time': ''.format(time.asctime(time.localtime(time.time()))),
                'detail': '异常信息：{}'.format(sys.exc_info()[0]),
            }
            logger_user.error(json.dumps(log_msg, ensure_ascii=False))
            res = {
                'code': 500,
                'info': 'AD初始化失败',
            }
            return JsonResponse(res)


class SendMSG(APIView):
    def post(self, request, *args, **kwargs):
        # TODO(samuel):检验电话号码是否在小南登记

        # phone = request.data['phone']
        phone = '19102070531'
        # 获取redis对象连接
        try:
            redis_conn = get_redis_connection('default')
            print(redis_conn)
        except Exception as e:
            log_info = {
                'info': 'redis连接失败',
                'time': ''.format(time.asctime(time.localtime(time.time()))),
                'detail': '异常信息：{}'.format(sys.exc_info()[0]),
            }
            logger_sms.error(json.dumps(log_info, ensure_ascii=False))
            res = {
                'code': 500,
                'info': 'redis连接失败',
            }
            return JsonResponse(res)
        # 获取发送标志
        send_flag = redis_conn.get('send_flag_%s' % phone)
        # 如果发送标志存在，说明用户在60秒内多次获取验证码
        if send_flag:
            log_info = {
                'info': '发送短信验证码过于频繁'
            }
            logger_sms.error(json.dumps(log_info, ensure_ascii=False))
            res = {
                'code': 500,
                'errmsg': '发送短信验证码过于频繁'
            }
            return JsonResponse(res)
        # 生成随机6位验证码
        sms_code = '%06d' % random.randint(0, 999999)
        # 存储随机验证码（1分钟的有效期）
        redis_conn.setex('sms_code_%s' % phone, 60, sms_code)
        # 设置发送标志
        redis_conn.setex('send_flag_%s' % phone, 60, 1)
        # 发送验证码
        res_code = send_msg(phone, sms_code)
        if res_code == 0:

            res = {
                'code': 200,
                'info': '短信正常发送'
            }
            return JsonResponse(res)
        else:
            res = {
                'code': 500,
                'error_code_info': ''.format(res_code),
            }
            return JsonResponse(res)


# 验证码校验
class VerifyCode(APIView):
    def post(self, request, *args, **kwargs):
        # 获取redis对象连接
        redis_conn = get_redis_connection('default')
        phone = '19102070531'
        verify_code = request.data['verify_code']
        redis_code = redis_conn.get('sms_code_%s' % phone)
        # 判断redis_code 是否有效：
        if redis_code:
            redis_code = redis_code.decode()
            if verify_code == redis_code:
                log_info = {
                    'info': '验证成功',
                    'phone': phone,
                    'time': ''.format(time.asctime(time.localtime(time.time()))),
                }
                logger_sms.info(json.dumps(log_info,ensure_ascii=False))
                res = {
                    'code': 200,
                    'info': '验证成功'
                }
                return JsonResponse(res)
            else:
                log_info = {
                    'info': '验证失败',
                    'phone': phone,
                    'time': ''.format(time.asctime(time.localtime(time.time()))),
                }
                logger_sms.info(json.dumps(log_info,ensure_ascii=False))
                res = {
                    'code': 500,
                    'info': '验证码输入错误，请重新输入'
                }
                return JsonResponse(res)
        else:
            log_info = {
                'info': '验证码已失效，请重新获取',
                'phone': phone,
                'time': ''.format(time.asctime(time.localtime(time.time()))),
            }
            logger_sms.info(json.dumps(log_info, ensure_ascii=False))
            res = {
                'code': 500,
                'info': '验证码已失效，请重新获取'
            }
            return JsonResponse(res)