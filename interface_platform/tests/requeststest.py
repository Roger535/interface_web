# -*- coding: UTF-8 -*-

from ..rfit.httplibrary import HttpLibrary
import requests
import json
from ..model.interface import Interface


class RequestsTest(object):
    def __init__(self):
        pass

    # 不支持这种IP加端口的访问方式，不安全，还是要通过修改机器HOST实现
    def test_get_admincookie(self):
        url = "http://10.164.96.78:8186/checkLogin?"
        # url = "https://106.2.124.114:443/checkLogin?"
        # url = "https://super.qiye.yixin.im/checkLogin?"
        data = {"account": "numen_dev@163.com", "password": "Admin123"}
        return requests.post(url, data=data).text

    def test_get_cookie_httplibrary(self, username, password):
        lib = HttpLibrary()
        return lib.get_admin_cookie(username, password)

    def test_lib_create_user(self):
        lib = HttpLibrary()
        # lib.web_environment_config("https://super.qiye.yixin.im", 0)
        cookie = "NTESkolibri-adminSI=15F0DC58253FA7DA1DEA0C3C12751978.hzabj-kolibri-1.server.163.org-8016; Path=/; HttpOnly"
        params = {"account": "testdong@yixin.im", "password": "Admin123", "authAll": 1,
                "moduleIdList": "11, 10, 13"}
        url = "/user/addUserAndAuth"
        return lib.web_post(url, params, 'None', cookie)

    # 测试创建用户
    # cookie需要及时获取的
    def test_create_user(self):
        url = "https://super.qiye.yixin.im/user/addUserAndAuth"
        headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded",
                   "Cookie": "NTESkolibri-adminSI=15F0DC58253FA7DA1DEA0C3C12751978.hzabj-kolibri-1.server.163.org-8016; Path=/; HttpOnly",
                   "uid": ""}
        params = {"account": "testdong@yixin.im", "password": "Admin123", "authAll": 1,
                  "moduleIdList": "11,10,13"}
        r = requests.post(url, params=params, headers=headers, verify=True)
        return r


if __name__ == "__main__":
    r = RequestsTest()
    # print r.test_create_user().url
    # print r.test_create_user().text

    print r.test_lib_create_user()
    # print r.test_get_admincookie()
    # r.test_get_cookie_httplibrary("numen_dev@163.com", "Admin123")
