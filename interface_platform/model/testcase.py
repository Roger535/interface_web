# -*- coding: UTF-8 -*-
from interfacebuilder import InterfaceBuilder


# 接口测试用例类
class TestCase(object):
    def __init__(self, testcase, logger, its):
        print "TestCase.__init__()"
        self._testcase = testcase
        self._logger = logger
        self._its = its
        self._status = "Unexecuted"
        self._msg = None

    @property
    def status(self):
        return self._status

    @property
    def msg(self):
        return self._msg

    # 运行用例，记录测试日志
    # 一个接口出错则中断执行
    def run(self):
        print "TestCase.run()"
        # self._logger.info("开始执行用例: id=" + str(self._testcase.id) + " name=" + self._testcase.name)
        for it in self._its:
            interface_builder = InterfaceBuilder(it, self._logger)
            interface = interface_builder.build()
            interface.run()
            interface.validate()
            # 如果接口执行失败，则终止用例执行
            if interface.status == "Fail":
                self._status = "Fail"
                break
            print "it:", it.id, "execute result: ", interface.status
            # 记录借口错误信息
            self._msg = interface.error_msg
            self._logger.info("接口执行状态: " + interface.status)
            self._logger.info("接口构建完成！")
        if self._status != "Fail":
            self._status = "Pass"
        self._logger.info("用例执行状态: " + self._status)
        self._logger.info("用例执行完成！")
        return self._status
