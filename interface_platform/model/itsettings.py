# -*- coding: UTF-8 -*-
import logging
import  time
try:
    import codecs
except ImportError:
    codecs = None

# 定义接口通用数据
# 项目定制数据

# 端口号
port = "0"
# 当前cookie
cookie = ""
# 当前uid
uid = ""
# 定制Web头部
#获取当前时间
current_time = long(time.time())

web_headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded", "Cookie": cookie,
               "uid": uid}
# 如果POST不传入数据
web_headers1 = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded", "Cookie": cookie,
                "uid": uid}
# 如果POST传入数据则使用json格式
web_headers2 = {"Accept": "application/json", "Content-Type": "application/json", "Cookie": cookie, "uid": uid}
# 定制Mobile头部
mobile_headers ={'Content-Type': 'text/plain', 'time': str(current_time), 'uid': uid, 'ua': 'IOS/1.0.0'}


# 继承logging.FileHandler，设置文件读写模式为："w"，覆盖原文件
class OverwriteFileHandler(logging.FileHandler):
    def __init__(self, filename, mode="w", encoding=None, delay=0):
        """
        Use the specified mode for streamed logging
        """
        if codecs is None:
            encoding = None
        logging.FileHandler.__init__(self, filename, mode, encoding, delay)
