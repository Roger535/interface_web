# -*- coding: UTF-8 -*-
from ..model.testcasebuilder import TestCaseBuilder
from ..models import TestCaseLog, TestCase
import interface_platform.settings as settings
import logging.config
import os
from datetime import datetime


# 运行用例，记录执行错误信息到数据库
class TestCaseRunner(object):
    def __init__(self, case_id):
        print "TestCaseRunner.__init__()"
        self._testcase = TestCase.objects.get(id=case_id)
        self._project = self._testcase.belong.project
        self._run_testcase = None
        self._log_name = str(datetime.now()) + ".log"
        self.set_log_file(self._log_name)
        self._logger = logging.getLogger(settings.LOGGER_NAME)
        self._testcasebuilder = TestCaseBuilder(case_id, self._logger)

    @property
    def testcasebuilder(self):
        return self._testcasebuilder

    @property
    def logger(self):
        return self._logger

    # 返回用例执行错误信息
    # 没有则返回None
    @property
    def message(self):
        if self._run_testcase is not None:
            return self._run_testcase.msg
        else:
            return None

    # 返回执行结果
    def runner(self):
        print "TestCaseRunner.runner()"
        self._run_testcase = self._testcasebuilder.build()
        self._run_testcase.run()
        # 记录执行结果信息到数据库
        if self._run_testcase.msg is not None:
            self._testcase.message = self._run_testcase.msg
            self._testcase.save()
        return self._run_testcase.status

    # 该函数实现的功能：传递一个要记录日志的文件名作为参数，默认是settings.py里的LOGGING中filename
    # 1. 设置日志存储路径
    # 2. 建立用例日志表或读取日志文件路径
    def set_log_file(self, filename):
        print "TestCaseRunner.set_log_file()"
        # 日志存储路径
        log_path = os.path.join(settings.LOG_ROOT, filename.decode("utf-8"))
        # 存储日志文件路径到数据库
        # 有中文的话这里的路径使用不方便
        logs = TestCaseLog.objects.filter(name=filename)
        if logs.exists() is False:
            log = TestCaseLog.objects.create(tc=self._testcase, name=filename, log_path=log_path)
            log.save()
            # filename = log.name.decode('utf-8')
        # 该日志文件数据库中已有记录
        # 说明用例已经运行过
        else:
            # 删除文件重新创建
            # os.remove(log_path)
            pass
        logging_dic = settings.LOGGING
        logging_dic['handlers']['eat']['filename'] = log_path
        logging.config.dictConfig(logging_dic)

    # 获取日志内容
    # 打开后记得关闭文件
    def get_log(self):
        print "TestCaseRunner.get_log()"
        log_path = os.path.join(settings.LOG_ROOT, self._log_name.decode('utf-8'))
        f_log = open(log_path)
        content = f_log.readlines()
        f_log.close()
        return content

