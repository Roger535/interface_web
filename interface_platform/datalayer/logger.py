# -*- coding:utf-8 -*-

import logging.config
from interface_platform.datalayer.log import set_log_filename


# filename = u'中文.log'
filename = '中文.log'
set_log_filename(filename.decode('utf-8'))
logger = logging.getLogger('eat_logger')
logger.info("中文")


