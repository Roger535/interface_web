# -*- coding: UTF-8 -*-
from itsettings import *
from ..models import *
from interface import Interface
from ..utils import isValidHostname, exists, set_host
from ..mobile_manage import MobileManage
import json
import sys
import uuid


# 接口创建类
# 创建接口/创建logger
# 处理Header/Param/Body中带全局变量参数的情况 11.21

class InterfaceBuilder(object):
    # global key
    # key =''
    def __init__(self, it, logger):
        print "InterfaceBuilder.__init__()"
        reload(sys)
        sys.setdefaultencoding("utf-8")
        self._it = it
        # 根据请求和响应消息类型分类
        # 请求消息
        self._headers = ITHeader.objects.filter(it=self._it, header_type__in=[0, 101, 102])
        self._bodys = ITBody.objects.filter(it=self._it, body_type=0)
        # 转换成字典格式
        # 响应消息
        self._r_headers = ITHeader.objects.filter(it=self._it, header_type=1)
        self._r_bodys = ITBody.objects.filter(it=self._it, body_type=1)
        self._params = ITParam.objects.filter(it=self._it)
        self._logger = logger
        self._key = ''

    @property
    def logger(self):
        return self._logger

    # 返回一个接口对象
    def build(self):
        print "InterfaceBuilder.build()"
        self._logger.info("开始构建接口: id=" + str(self._it.id) + " name=" + self._it.name)
        # _get_bodys返回的是两个参数
        bodys_dict, files_dict = self._get_bodys()
        # _get_r_bodys返回响应消息的验证数据
        _r_bodys_dict, _r_files_dict = self._get_r_bodys()
        if self._get_headers().has_key("ua"):
            mobile_headers, bodys_dict = self.encrpyt()
            return Interface(self._logger, self._it.request_type, self._get_url(), self._get_params(),
                         mobile_headers, bodys_dict, files_dict, _r_bodys_dict, _r_files_dict,
                         self._get_r_headers(),self._key)

        return Interface(self._logger, self._it.request_type, self._get_url(), self._get_params(),
                         self._get_headers(), bodys_dict, files_dict, _r_bodys_dict, _r_files_dict,
                         self._get_r_headers(),self._key)

    # 组成请求用的url
    # 请求类型（HTTPS/HTTP）+ HOST + PATH
    def _get_url(self):
        print "InterfaceBuilder._get_url()"
        host = self._it.host.name
        if isValidHostname(host):
            # 添加HOST到服务器hosts里
            if exists(host) is False:
                set_host({host: self._it.host.value})
            url = self._it.protocol_type + "://" + host + self._it.path
            return url
        else:
            return None

    # 返回字典格式params
    def _get_params(self):
        print "InterfaceBuilder._get_params()"
        params_dict = {}
        for param in self._params:
            if param.type == "GlobalVar":
                params_dict[param.name] = self._get_global_var(param.value)
            else:
                params_dict[param.name] = param.value
        print params_dict
        return params_dict

    # 获取请求消息体头部参数
    # 返回消息体这里不处理
    # 处理传入接口返回值作为变量的情况
    def _get_headers(self):
        print "InterfaceBuilder._get_headers()"
        print self._headers
        headers_dict = {}
        for header in self._headers:
            if header.header_type == 101:
                return web_headers
            elif header.header_type == 102:
                print mobile_headers
                return mobile_headers
            elif header.type == "GlobalVar":
                print "head globalvar"
                headers_dict[header.name] = self._get_global_var(header.value)
                print "cookie:" + headers_dict[header.name]
            else:
                headers_dict[header.name] = header.value
        return headers_dict

    def encrpyt(self):
        bodys_dict, files_dict = self._get_bodys()
        if bodys_dict.has_key("key"):
            key1 = bodys_dict["key"]
            del bodys_dict['key']
        else:
            key1 = 'a!onWY311h9cGV2L>>mxuQAx8Z#%z>+v'
        unique = str(uuid.uuid1()).replace('-', '')
        key = MobileManage().getkey(key1, unique)
        self._key = key
        bodykey = MobileManage().getkey('a!onWY311h9cGV2L>>mxuQAx8Z#%z>+v', unique)
        # 判断body里的参数是否要加密，如果是先加密
        if bodys_dict.has_key("encryptkey") == 0:
            # bodys_dict = str(bodys_dict).replace("'", "\"")
            bodys_dict = json.dumps(bodys_dict)
            enbody = MobileManage().encrpyt(key, bodys_dict)
        else:
            encryptkey = bodys_dict["encryptkey"]
            del bodys_dict["encryptkey"]
            # dicbody = eval(bodys_dict)
            dicbody = bodys_dict
            listen = eval(encryptkey)
            for element in listen:
                keys = dicbody.keys()
                if element in keys:
                    dicbody[element] = MobileManage().encrpyt(bodykey, dicbody[element])
                    print dicbody[element]
                else:
                    pass
            dicbody = json.dumps(dicbody)
            # dicbody = str(dicbody).replace("'", "\"")
            print dicbody
            enbody = MobileManage().encrpyt(key, dicbody)

        mobile_headers['unique'] = unique
        mobile_headers['sign'] = MobileManage().generate_sign(key1, enbody, unique)
        print mobile_headers
        print  enbody
        return mobile_headers, enbody


    # 获取请求消息体参数
    # 返回消息这里不处理
    # 对于上传的文件存储到对应的FileField
    # body里面传入的是全局变量处理 11.21
    # 如果body_format是原始json数据怎么处理 11.28
    def _get_bodys(self):
        print "InterfaceBuilder._get_bodys()"
        bodys_dict = {}
        files_dict = {}
        for body in self._bodys:
            # 如果是格式化传参
            if body.body_format == 3:
                # 如果是Text类型数据
                if body.type == "Text":
                    bodys_dict[body.name] = body.value
                # 如果是文件类型数据
                elif body.type == "File":
                    files_dict[body.name] = body.value
                elif body.type == "GlobalVar":
                    bodys_dict[body.name] = self._get_global_var(body.value)
            # 如果是原始格式数据，以json格式发送
            elif body.body_format == 4:
                bodys_dict = json.dumps(body.value)
        return bodys_dict, files_dict

    # 获取响应消息体头部参数
    # 处理成字典格式
    def _get_r_headers(self):
        print "InterfaceBuilder._get_r_headers()"
        r_headers_dict = {}
        for r_header in self._r_headers:
            r_headers_dict[r_header.name] = r_header.value
        return r_headers_dict

    # 响应消息body数据
    # 获取需要验证数据
    def _get_r_bodys(self):
        print "InterfaceBuilder._get_r_bodys()"
        bodys_dict = {}
        files_dict = {}
        for body in self._r_bodys:
            # 如果是格式化传参则要验证返回数据的正确性
            if body.body_format == 3:
                # 如果是Text类型数据
                if body.type == "Text" or body.type == "Boolean" or body.type == "String":
                    bodys_dict[body.name] = body.value
                elif body.type == "Int":
                    bodys_dict[body.name] = int(body.value)
                elif body.type == "Long":
                    bodys_dict[body.name] = long(body.value)
                # 如果是文件类型数据
                elif body.type == "File":
                    files_dict[body.name] = body.value

        return bodys_dict, files_dict

    # 处理参数中的全局变量（普通变量/接口返回值）
    # 传入的是变量的name
    # 执行时运行对应接口获取返回值
    # 未找到时返回None
    def _get_global_var(self, var_name):
        print "InterfaceBuilder._get_global_var()"
        global_var = Variable.objects.get(name=var_name, project=self._it.project)
        if global_var.type == "普通变量":
            return global_var.value
        elif global_var.type == "接口返回值":
            print "it_return var:", global_var
            var_it = VariableIT.objects.get(var=global_var)
            print var_it.var.name, var_it.it.id, var_it.assoc_type, var_it.assoc_id
            interface_builder = InterfaceBuilder(var_it.it, self._logger)
            print var_it.it.id, "build"
            interface = interface_builder.build()
            print "run"
            interface.run()
            print "run pass"
            # 判断是url、header还是body的值，从接口执行响应消息中获取
            # 从VariableIT找出header或者body
            if var_it.assoc_type == "5":
                r_head = ITHeader.objects.get(id=var_it.assoc_id)
                print "Var_it.assoc_type", r_head, interface.get_header_var(r_head.name)
                return interface.get_header_var(r_head.name)
            if var_it.assoc_type == "6":
                r_body = ITBody.objects.get(id=var_it.assoc_id)
                print "Var_it.assoc_type", r_body, interface.get_body_var(r_body.name)
                return interface.get_body_var(r_body.name)

        return None




