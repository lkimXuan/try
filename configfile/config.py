# -*- coding: utf-8 -*-
# @Time : 2023/8/14 14:35
# @Author : Samuel
# @FileName: config.py
import os
import configparser

def getConfig(section, key):
    '''
    获取配置信息
    '''
    path = os.path.join(os.path.split(os.path.realpath(__file__))[0], 'config.conf')

    try:
        config = configparser.ConfigParser()
        config.read(path, encoding="utf-8")
    except:
        return {
            'state': 'error',
            'info': 'open configfile file error.'
        }

    try:
        return {
            'state': 'success',
            'configfile': config.get(section, key)
        }
    except:
        return {
            'state': 'error',
            'info': 'no such configfile section.'
        }
