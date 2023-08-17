# -*- coding: utf-8 -*-
# @Time : 2023/8/14 14:44
# @Author : Samuel
# @FileName: ad_init.py

import logging
import ldap3
from ldap3 import *
# 导入config
from configfile import config

logger_ad = logging.getLogger('ad')

try:
    ad_host = config.getConfig('ADInfo', 'ad_host')['configfile']
    ad_port = config.getConfig('ADInfo', 'ad_port')['configfile']
    base = config.getConfig('ADInfo', 'base')['configfile']
    user_admin = config.getConfig('ADInfo', 'user')['configfile']
    passwd_admin = config.getConfig('ADInfo', 'passwd')['configfile']
except:
    logger_ad.error('import ad configfile error.')
class AD():
    '''
    AD域连接模块
    '''
    # 默认账号连接获取信息
    def __init__(self,login_user=user_admin, login_pw=passwd_admin):
        server = Server(
            host = ad_host,
            port = int(ad_port),
            use_ssl = True,
            get_info = ALL,
            connect_timeout = 5
        )
        self.server = server
        conn = Connection(
            server = server,
            user = login_user,
            password = login_pw,
            auto_bind = True,
            read_only = True,
            receive_timeout = 20
        )
        self.conn = conn

    def __del__(self):
        pass

    #获取用户域账号信息
    def getAccountInfo(self, account):
        '''
        获取账号的域信息
        '''
        conn = self.conn
        # 过滤出指定用户
        # 可用用户、密码会过期的用户、密码最后设置时间不为零
        search_filter = '''(
            &(objectCategory=person)
            (objectClass=user)
            (!(userAccountControl:1.2.840.113556.1.4.803:=2))
            (!(userAccountControl:1.2.840.113556.1.4.803:=65536))
            (!(pwdLastSet=0))
            (sAMAccountName={0})
            )
            '''.format(account)
        attribute = ['Name', 'sAMAccountName']

        Flag = False
        while True:
            if not Flag:
                conn.search(
                    search_base=base,
                    search_filter=search_filter,
                    search_scope=ldap3.SUBTREE,
                    attributes=attribute,
                    size_limit=0,
                    time_limit=0,
                    types_only=False,
                    get_operational_attributes=False,
                    controls=None,
                    paged_size=1000,
                    paged_criticality=False,
                    paged_cookie=None,
                    auto_escape=None
                )
                Flag = True
            else:
                conn.search(
                    search_base=base,
                    search_filter=search_filter,
                    search_scope=ldap3.SUBTREE,
                    attributes=attribute,
                    size_limit=0,
                    time_limit=0,
                    types_only=False,
                    get_operational_attributes=False,
                    controls=None,
                    paged_size=1000,
                    paged_criticality=False,
                    paged_cookie=cookie,
                    auto_escape=None
                )
            response = conn.response
            if len(response) == 1:
                response = response[0]
                return {
                    'state': 'success',
                    'account': response['attributes']['sAMAccountName'],
                    'username': response['attributes']['Name'],
                    'ou': response['dn'],
                }

            # 分页拉取
            cookie = self.conn.result['controls']['1.2.840.113556.1.4.319']['value']['cookie']
            if not cookie:
                break

        return {'state': 'fail'}