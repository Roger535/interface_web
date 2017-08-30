# -*- coding: UTF-8 -*-
import requests
import json


# 自己写的接口测试库，支持任何形式的接口
class MyLibrary(object):
    def __init__(self):
        pass

    def get(self, url, headers=None, data=None, files=None):
        r = requests.get(url, headers=headers, data=data, files=files)
        return r.text
