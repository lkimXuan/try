# -*- coding: utf-8 -*-
# @Time : 2023/8/15 09:19
# @Author : Samuel
# @FileName: send_msg.py
import json
import logging
import sys
import time

import requests
from configfile.config import getConfig

logger_sms = logging.getLogger('sms')

try:
    username = getConfig('SMSInfo', 'username')['configfile']
    password = getConfig('SMSInfo', 'password')['configfile']
    sms_url = getConfig('SMSInfo', 'sms_url')['configfile']
except:
    logger_sms.error('import sms configfile error.')


# 发送验证码
def send_msg(phone,sms_code,subid=None, msgtype=1):
    try:
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "SMS",
        }
        payload = {
            'username':username,
            'password':password,
            'text':'密码修改验证码：'.format(sms_code), #验证码
            'to':phone,
            'subid':subid,
            'msgtype':msgtype,
            'Version':1.0,
        }
        res = requests.get(sms_url,params=payload,headers=headers)
        res = json.loads(res.text)
        return res
    except Exception as e:
        log_info = {
            'info':'发送短信失败',
            'time':''.format(time.asctime(time.localtime(time.time()))),
            'detail': '异常信息：{}'.format(sys.exc_info()[0]),
        }
        logger_sms.error(json.dumps(log_info,ensure_ascii=False))
        return False