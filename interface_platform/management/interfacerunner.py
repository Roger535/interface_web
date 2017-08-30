# -*- coding: UTF-8 -*-
from ..model.interfacebuilder import InterfaceBuilder
from ..models import ITLog, ITStatement
import interface_platform.settings as settings
import logging.config
import os
from datetime import datetime


# 运行接口
# 传入it_id和验证数据
class InterfaceRunner(object):
    def __init__(self, it_id):
        print "InterfaceRunner.__init__()"
        self._it = ITStatement.objects.get(id=it_id)
        self._log_name = str(datetime.now()) + ".log"
        self.set_log_file(self._log_name)
        self._logger = logging.getLogger(settings.LOGGER_NAME)
        self._interface = None
        self._interfacebuilder = InterfaceBuilder(self._it, self._logger)

    @property
    def interfacebuilder(self):
        return self._interfacebuilder

    @property
    def logger(self):
        return self._logger

    @property
    def interface(self):
        return self._interface

    # 执行之后返回执行结果：失败、通过、未执行
    def runner(self):
        print "InterfaceRunner.runner()"
        self._interface = self._interfacebuilder.build()
        self._interface.run()
        self._interface.validate()
        self._logger.info("接口执行状态: " + self._interface.status)
        self._logger.info("接口构建完成！")
        return self._interface.status

    # 该函数实现的功能：传递一个要记录日志的文件名作为参数，默认是settings.py里的LOGGING中filename
    # 1. 设置日志存储路径
    # 2. 建立用例日志表或读取日志文件路径
    def set_log_file(self, filename):
        print "InterfaceRunner.set_log_file()"
        # 日志存储路径
        log_path = os.path.join(settings.LOG_ROOT, filename.decode("utf-8"))
        # 存储日志文件路径到数据库
        # 有中文的话这里的路径使用不方便
        logs = ITLog.objects.filter(name=filename)
        if logs.exists() is False:
            log = ITLog.objects.create(it=self._it, name=filename, log_path=log_path)
            log.save()
        else:
            # 删除文件重新创建
            # 可能文件被占用的情况，删除失败
            # remove_log(log_path)
            pass
        logging_dic = settings.LOGGING
        logging_dic['handlers']['eat']['filename'] = log_path
        logging.config.dictConfig(logging_dic)

    # 获取日志内容
    # 打开后记得关闭文件
    def get_log(self):
        print "InterfaceRunner.get_log()"
        log_path = os.path.join(settings.LOG_ROOT, self._log_name.decode('utf-8'))
        f_log = open(log_path)
        content = f_log.readlines()
        f_log.close()
        return content
