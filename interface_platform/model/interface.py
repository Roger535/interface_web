# -*- coding: UTF-8 -*-
import requests
import traceback
import json
from ..mobile_manage import MobileManage
# from interfacebuilder import InterfaceBuilder
# 接口类主体
# 包含请求类型，地址，头部，消息体，文件
# 使用requests执行更容易
# TODO 执行用例，获取执行结果，验证执行结果
class Interface(object):
    def __init__(self, logger, request_type, url, params, headers, bodys, files, r_bodys, r_files, r_headers,key):
        print "Interface.__init__()"
        self._logger = logger
        # 请求消息
        self._request_type = request_type
        self._url = url
        self._params = params
        self._headers = headers
        self._bodys = bodys
        self._files = files
        # 响应消息（验证数据）
        self._r_headers = r_headers
        self._r_bodys = r_bodys
        self._r_files = r_files
        # 用于获取响应消息其他部分的值
        self._r = None
        # 响应消息的body部分
        self._result = None
        self._status = "Unexecuted"
        self._error_msg = None
        self._key = key

    @property
    def r(self):
        return self._r

    @property
    def result(self):
        return self._result

    @property
    def status(self):
        return self._status

    # 返回错误消息
    @property
    def error_msg(self):
        return self._error_msg

    # 执行或者调试的方法，记录执行日志
    # TODO 几种请求方式未全部验证
    # 验证过的：POST
    def run(self):
        print "Interface.run"
        if self._request_type == "GET":
            # 记录异常信息
            # 粗略一次捕获所有异常
            try:
                self._r = requests.get(url=self._url, params=self._params, headers=self._headers, data=self._bodys,
                                       files=self._files)
            except Exception as e:
                self._error_msg = traceback.format_exc()
            self._result = self._r.text

            self.standard_log()

        elif self._request_type == "POST":
            try:
                self._r = requests.post(url=self._url, params=self._params, data=self._bodys, headers=self._headers,
                                        files=self._files)
                print self._r
                print "++++++++++++++++++++++++++"
            except Exception as e:
                self._error_msg = traceback.format_exc()
            self._result = self._r.text

            print self._result
            self.standard_log()

        elif self._request_type == "PUT":
            try:
                self._r = requests.put(url=self._url, params=self._params, data=self._bodys, headers=self._headers,
                                       files=self._files)
            except Exception as e:
                self._error_msg = traceback.format_exc()
            self._result = self._r.text
            self.standard_log()

        elif self._request_type == "PATCH":
            try:
                self._r = requests.patch(url=self._url, params=self._params, data=self._bodys, headers=self._headers,
                                         files=self._files)
            except Exception as e:
                self._error_msg = traceback.format_exc()
            self._result = self._r.text
            self.standard_log()

        elif self._request_type == "DELETE":
            try:
                self._r = requests.delete(url=self._url, params=self._params, data=self._bodys, headers=self._headers,
                                          files=self._files)
            except Exception as e:
                self._error_msg = traceback.format_exc()
            self._result = self._r.text
            self.standard_log()

    def standard_log(self):
        print "interface.standard_log"
        self._logger.info(
            "\n ==================== 发送请求 ====================" +
            "\n url:" + str(self._r.url) +
            "\n 请求方式:" + self._request_type +
            "\n params:" + str(self._params) +
            "\n headers:" + str(self._headers) +
            "\n bodys:" + str(self._bodys) +
            "\n files:" + str(self._files) +
            "\n 请求返回结果:" + self._result +
            "\n ==================== 请求成功 ====================")

    # 打印错误日志
    def standard_error_log(self, *args):
        print "interface.standard_error_log"
        if len(args) == 1:
            self._error_msg = "验证数据: %s 不在接口返回消息中" % args[0]
            self._logger.info(self._error_msg)
        if len(args) == 2:
            self._error_msg = "期望值是: %s，而接口返回消息中的是值是: %s " % (args[0], args[1])
            self._logger.info(self._error_msg)

    # 验证测试数据
    def validate(self):
        # 验证响应消息的body
        print "interface.validate"
        # key = InterfaceBuilder().key
        # print key
        #
        print self._key
        if self._key != '':
            self._result = MobileManage().decrypt(self._key, self._result)
            print self._result
        result_dict = json.loads(self._result)
        print "result_dict", result_dict
        self._logger.info("\n 验证头部:" + str(self._r_headers) +
                          "\n 验证数据:" + str(self._r_bodys) +
                          "\n 验证文件:" + str(self._r_files))
        # 验证响应消息中的body
        if self._r_bodys != {}:
            print "self._r_bodys", self._r_bodys
            for (key, value) in self._r_bodys.items():
                if str(key) not in result_dict:
                    print "key not in result_dict"
                    self._status = "Fail"
                    self.standard_error_log(str(key))
                    return
                elif str(value) and str(result_dict[str(key)]) != str(value):  # 当输入的验证值为空时，不进行验证
                    print "key in but value error"
                    self._status = "Fail"
                    self.standard_error_log(value, result_dict[str(key)])
                    return
            for (key, value) in self._r_files.items():
                if str(key) not in result_dict:
                    self._status = "Fail"
                    self.standard_error_log(str(key))
                    return
                elif result_dict[str(key)] != value:
                    self._status = "Fail"
                    self.standard_error_log(value, result_dict[str(key)])
                    return
        # 验证响应消息的header
        if self._r_headers != {}:
            print "self._r_headers", self._r_headers
            for (key, value) in self._r_headers.items():
                print (key, value)
                if str(key) not in self._r.headers:
                    print "key not in self._r.headers"
                    self._status = "Fail"
                    self.standard_error_log(str(key))
                    return
                elif value and str(self._r.headers[str(key)]) != str(value):
                    print "key in but value error"
                    self._status = "Fail"
                    self.standard_error_log(value, result_dict[str(key)])
                    return

        self._status = "Pass"

    # 获取接口执行结果header中的一个值作为变量
    # 查找字典里对应的key的值
    def get_header_var(self, value):
        value_str = str(value)
        return self._r.headers[value_str]

    # 获取接口执行结果body中的一个值作为变量
    # 查找字典里对应的key的值
    def get_body_var(self, value):
        value_str = str(value)
        result_dict = json.loads(self._result)
        return result_dict[value_str]

        # if re.match(r"\$(.*)", str(value)) is not None:
        #     key = str_value[1:]
        #     result_dict = eval(self._result)
        #     # TODO 如果没有key则会报错
        #     return result_dict[key]
