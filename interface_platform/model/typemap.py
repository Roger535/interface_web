# -*- coding: UTF-8 -*-

# 消息头类型
HEADER_TYPE = {
    "0": "请求头",
    "1": "返回头",

    "101": "web_headers",  # 定制web请求头
    "102": "mobile_headers",  # 定制mobile请求头
}

# 传参格式
FORMAT = {
    "3": "格式化",
    "4": "原始",
}

# 资源配置中的环境变量类型,中文字样前要加u强制转换成utf-8编码格式
VAR_TYPE = {
    "HOST",
    u"普通变量",
    u"接口返回值",

}

