# -*- coding: UTF-8 -*-
from interfacerunner import InterfaceRunner


# 定制企业易信的特殊方法，供企业易信使用
# 初始化方法同父类，传入it_id（接口ID）即可

# 有新的需求都可以添加到这里
class QiYe_InterfaceRunner(InterfaceRunner):

    # 获取cookie
    def get_cookie(self):
        if self.interface is not None:
            return self.interface.r.headers["Set-Cookie"]
        else:
            self.logger.info("接口还未运行，请先运行接口，再执行该方法")

