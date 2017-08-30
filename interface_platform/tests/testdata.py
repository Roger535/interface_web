# -*- coding: UTF-8 -*-

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "interface_platform.settings")

from django.contrib.auth.models import User
from account.models import Account
from ..management.qiye_interfacerunner import QiYe_InterfaceRunner
from ..management.testcaserunner import TestCaseRunner
from ..models import *
import requests
import json


# 创建model(用例执行模块)测试数据
class CreateTestData:
    @staticmethod
    def create_account(username, password, email):
        return User.objects.create_user(username, email=email, password=password)

    @staticmethod
    def create_project(name, user):
        project = Project.objects.create(name=name, user=user)
        project.save()
        return project

    @staticmethod
    def create_host(name, value, project, type, creator, responsible):
        host = Variable.objects.create(name=name, value=value, project=project, type=type, creator=creator,
                                       responsible=responsible)
        host.save()
        return host

    @staticmethod
    def create_var(name, value, project, type, creator, responsible):
        var = Variable.objects.create(name=name, value=value, project=project, type=type, creator=creator,
                                      responsible=responsible)
        var.save()
        return var

    @staticmethod
    def create_itstatement(name, protocol_type, request_type, path, project, creator, host, responsible):
        it = ITStatement.objects.create(name=name, protocol_type=protocol_type, request_type=request_type,
                                        path=path, project=project, creator=creator,
                                        host=host, responsible=responsible)
        it.save()
        return it

    @staticmethod
    def create_itbody(name, body_format, type, value, it, body_type, upload_file=None, desc=None):
        itbody = ITBody.objects.create(name=name, body_format=body_format, type=type, value=value, it=it,
                                       body_type=body_type,
                                       upload_file=upload_file, desc=desc)
        itbody.save()
        return itbody

    @staticmethod
    def create_itheader(name, value, it, header_type, type=None, desc=None):
        itheader = ITHeader.objects.create(name=name, value=value, it=it, header_type=header_type, type=type, desc=desc)
        itheader.save()
        return itheader

    @staticmethod
    def create_itparam(name, value, it, type=None):
        itparam = ITParam.objects.create(name=name, value=value, it=it, type=type)
        itparam.save()
        return itparam

    @staticmethod
    def create_variableit(var, it, header_id=None, body_id=None):
        variableit = VariableIT.objects.create(var=var, it=it, header_id=header_id, body_id=body_id)
        variableit.save()
        return variableit

    @staticmethod
    def create_dirtree(parent, name, key, level, project):
        dirtree = DirectoryTree.objects.create(parent=parent, name=name, key=key, level=level, project=project)
        dirtree.save()
        return dirtree

    @staticmethod
    def create_testcasestep(tc, it, index, name):
        testcasestep = TestCaseStep.objects.create(tc=tc, it=it, index=index, name=name)
        testcasestep.save()
        return testcasestep

    @staticmethod
    def create_testcase(name, belong, status, author, responsible):
        testcase = TestCase.objects.create(name=name, belong=belong, status=status, author=author, responsible=responsible)
        testcase.save()
        return testcase

    # 测试创建用户
    # cookie需要及时获取的
    def test_create_user(self, cookie):
        url = "https://super.qiye.yixin.im/user/addUserAndAuth"
        headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded",
                   "Cookie": cookie,
                   "uid": ""}
        params = {"account": "testdon1g@yixin.im", "password": "Admin123", "authAll": 1,
                  "moduleIdList": "11,10,13"}
        r = requests.post(url, params=params, headers=headers)
        return r

def test_interface_return():
    # 测试用例POST执行，测试通过11.24
    data = CreateTestData()
    user = data.create_account("Tom4", "123456", "12ff520@163.com")
    account = Account.objects.get(user=user)
    project = data.create_project("企业易信2", account)
    host = data.create_host("super.qiye.yixin.im", "106.2.124.114", project, "HOST", account, account)
    itstatement = data.create_itstatement("获取Admin Cookie", "HTTPS", "POST", "/checkLogin?", project, account, host,
                                          account)
    itbody1 = data.create_itbody("account", 3, "Text", "numen_dev@163.com", it=itstatement, body_type=0)
    itbody2 = data.create_itbody("password", 3, "Text", "Admin123", it=itstatement, body_type=0)
    # 获取响应消息header里的cookie
    it_r_header = data.create_itheader("Set-Cookie", "qwecookie", itstatement, 1)
    test_body = data.create_itbody("code", 3, "Int", "200", it=itstatement, body_type=1)

    # 新建第二个接口
    itstatement = data.create_itstatement("接口2", "HTTPS", "POST", "/checkLogin?", project, account, host, account)

    itstatement = ITStatement.objects.get(name="获取Admin Cookie")
    qiye_interfacerunner = QiYe_InterfaceRunner(itstatement.id)
    qiye_interfacerunner.runner()
    print qiye_interfacerunner.get_cookie()

    # 测试新建用户接口成功
    r = data.test_create_user(qiye_interfacerunner.get_cookie())
    print r.text

    # 测试接口中使用接口返回值变量
    it2 = data.create_itstatement("添加用户并设置权限", "HTTPS", "POST", "/user/addUserAndAuth", project, account, host, account)
    var2 = data.create_var("cookie", "Set-Cookie", project, "接口返回值", account, account)
    it2_header1 = data.create_itheader("Accept", "application/json", it2, 0)
    it2_header2 = data.create_itheader("Content-Type", "application/x-www-form-urlencoded", it2, 0)
    it2_header3 = data.create_itheader("uid", "", it2, 0)
    it2_header4 = data.create_itheader("Cookie", "cookie", it2, 0, type="GlobalVar")
    varit = data.create_variableit(var2, itstatement, it_r_header.id)
    it2_param1 = data.create_itparam("account", "testdong6@yixin.im", it2)
    it2_param2 = data.create_itparam("password", "Admin123", it2)
    it2_param3 = data.create_itparam("authAll", 1, it2)
    it2_param4 = data.create_itparam("moduleIdList", "11,10,13", it2)

    qiye_interfacerunner = QiYe_InterfaceRunner(it2.id)
    qiye_interfacerunner.runner()

    # 测试用例执行，获取日志
    dirtree = data.create_dirtree(parent=1, name="用例集1", key="1", level=1, project=project)
    case1 = data.create_testcase("用例1", dirtree, "未执行", account, account)
    testcasestep = data.create_testcasestep(case1, itstatement, 1, "获取Admin Cookie")
    # 用例执行
    caserunner = TestCaseRunner(case1.id)
    caserunner.runner()
    # 获取日志
    caserunner.get_log()


def tree_setup():
    # 数据库创建数据
    project = Project.objects.get(name="企业易信2")
    set1 = CreateTestData.create_dirtree(parent=0, name="用例集1", key="", level=1, project=project)
    fun1 = CreateTestData.create_dirtree(parent=set1.id, name="后台功能A", key=str(set1.id), level=2, project=project)
    fun2 = CreateTestData.create_dirtree(parent=set1.id, name="Web功能B", key=str(set1.id), level=2, project=project)
    fun3 = CreateTestData.create_dirtree(parent=set1.id, name="后台功能C", key=str(set1.id), level=2, project=project)
    case1 = CreateTestData.create_dirtree(parent=fun1.id, name="查询用户分组列表", key=fun1.key + "-" + str(fun1.id),
                                          level=3, project=project)
    case2 = CreateTestData.create_dirtree(parent=fun1.id, name="查询用户分组列表", key=fun1.key + "-" + str(fun1.id),
                                          level=3, project=project)
    case3 = CreateTestData.create_dirtree(parent=fun2.id, name="用例1", key=fun2.key + "-" + str(fun2.id), level=3,
                                          project=project)
    case4 = CreateTestData.create_dirtree(parent=fun3.id, name="用例1", key=fun3.key + "-" + str(fun3.id), level=3,
                                          project=project)
    case5 = CreateTestData.create_dirtree(parent=fun3.id, name="用例2", key=fun3.key + "-" + str(fun3.id), level=3,
                                          project=project)
    case6 = CreateTestData.create_dirtree(parent=fun3.id, name="用例3", key=fun3.key + "-" + str(fun3.id), level=3,
                                          project=project)


def test_generate_jsontree():
    # tree_setup()
    # 从数据库读取数据，生成tree接受的json格式
    # 获取最上层的文件夹
    trees = DirectoryTree.objects.filter(parent=0)
    dir_tree = []
    for tree in trees:
        dir_tree.append(generate_jsontree(tree))
    print json.dumps(dir_tree)


# 递归实现jsontree
def generate_jsontree(top_dir):
    root = {}
    root["id"] = top_dir.id
    root["name"] = top_dir.name
    children = DirectoryTree.objects.filter(parent=top_dir.id)
    if len(children) != 0:
        children_root = []
        for child in children:
            children_root.append(generate_jsontree(child))
        root["children"] = children_root
    return root

if __name__ == "__main__":
    test_generate_jsontree()


