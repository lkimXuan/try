import json
import logging
import sys
import time
from django.http import JsonResponse
from rest_framework.views import APIView
from ad_utils.ad_init import AD

logger_user = logging.getLogger('user')

class UpdatePWD(APIView):
    def post(self,request,*args,**kwargs):
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
                logger_user.error(json.dumps(log_msg,ensure_ascii=False))
                res = {
                    'code':500,
                    'info':'用户ad信息获取失败',
                }
                return JsonResponse(res)

            #修改密码:
            try:
                conn.extend.microsoft.modify_password(account_ou, old_password=pre_pwd, new_password=current_pwd)
                result = conn.result
                if result['result'] == 0:
                    conn.unbind()
                    log_msg = {
                        'info':'修改密码成功',
                        'user':'用户'.format(ad_account),
                        'time':''.format(time.asctime(time.localtime(time.time())))
                    }
                    res = {
                        'code':200,
                        'info':'修改密码成功'
                    }
                    logger_user.info(json.dumps(log_msg,ensure_ascii=False))
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
            except Exception as e :
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
        except Exception as e :
            log_msg = {
                'info':'AD初始化失败',
                'time':''.format(time.asctime(time.localtime(time.time()))),
                'detail': '异常信息：{}'.format(sys.exc_info()[0]),
            }
            logger_user.error(json.dumps(log_msg,ensure_ascii=False))
            res = {
                'code':500,
                'info':'AD初始化失败',
            }
            return JsonResponse(res)