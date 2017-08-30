# -*- coding: UTF-8 -*-
from ..models import TestCase, TestCaseStep
from testcase import TestCase as RunTestCase
import sys


# 创建用例
class TestCaseBuilder(object):
    def __init__(self, case_id, logger):
        print "TestCaseBuilder.__init__()"
        reload(sys)
        sys.setdefaultencoding("utf-8")
        self._testcase = TestCase.objects.get(id=case_id)
        # 用例的执行步骤——接口，按照index升序排列
        self._steps = TestCaseStep.objects.filter(tc=self._testcase).order_by("index")
        self._logger = logger

    def build(self):
        print "TestCaseBuilder.build()"
        self._logger.info("开始构建用例: id=" + str(self._testcase.id) + " name=" + self._testcase.name)
        return RunTestCase(self._testcase, self._logger, self._get_steps_its())

    @property
    def logger(self):
        return self._logger

    # 获取所有接口的id
    def _get_steps_its(self):
        it_list = []
        for step_interface in self._steps:
            it_list.append(step_interface.it)
        return it_list


