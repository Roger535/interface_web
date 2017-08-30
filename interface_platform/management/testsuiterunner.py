# -*- coding: UTF-8 -*-
from testcaserunner import TestCaseRunner
from ..models import TestSuite


# 用例集执行
# 统计数据，输出执行报告
class TestSuiteRunner(object):
    # 传入用例集的ID
    def __int__(self, suite_id):
        self._suite_id = suite_id
        self._test_suite = TestSuite.objects.get(id=suite_id)

    # 执行
    def runner(self):
        # 查询用例集下所有用例
        testcases = self._test_suite.testcases.all()
        for case in testcases:
            testcaserunner = TestCaseRunner(case.id)
            testcaserunner.runner()

