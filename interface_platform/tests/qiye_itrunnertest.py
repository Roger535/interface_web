# -*- coding: UTF-8 -*-

# import os
# import django
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "interface_platform.settings")
# django.setup()

from django.test import TestCase
from testdata import CreateTestData
from django.contrib.auth.models import User
from account.models import Account
from ..management.qiye_interfacerunner import QiYe_InterfaceRunner
from ..models import Project, ITStatement, ITBody, Variable

class ITRunnerTestCase(TestCase):

    def setUp(self):
        # 测试用例POST执行，测试通过11.24
        data = CreateTestData()
        user = data.create_account("Tom2", "123456", "124584120@163.com")
        account = Account.objects.get(user=user)
        project = data.create_project("企业易信2", account)
        host = data.create_host("super.qiye.yixin.im", "106.2.124.114", project, "HOST", account, account)
        itstatement = data.create_itstatement("获取Admin Cookie", "HTTPS", "POST", "/checkLogin?", project, account, host,
                                              account)
        itbody1 = data.create_itbody("account", 3, "Text", "numen_dev@163.com", it=itstatement, body_type=0)
        itbody2 = data.create_itbody("password", 3, "Text", "Admin123", it=itstatement, body_type=0)
        test_body = data.create_itbody("code", 3, "Int", "200", it=itstatement, body_type=1)

        # 新建第二个接口
        itstatement = data.create_itstatement("接口2", "HTTPS", "POST", "/checkLogin?", project, account, host, account)

    def test_itrunner_succeed(self):
        itstatement = ITStatement.objects.get(name="获取Admin Cookie")
        # interfacerunner = InterfaceRunner(itstatement.id).runner()
        qiye_interfacerunner = QiYe_InterfaceRunner(itstatement.id)
        qiye_interfacerunner.runner()
        print qiye_interfacerunner.get_cookie()
