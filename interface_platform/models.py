# -*- coding: utf-8 -*-
from django.db import models
from account.models import Account

REQUEST_TYPE_CHOICES = {
    ("POST", "POST"),
    ("GET", "GET"),
    ("PUT", "PUT"),
    ("DELETE", "DELETE"),
    ("PATCH", "PATCH"),
    ("HEAD", "HEAD"),
    ("OPTIONS", "OPTIONS"),
    ("TRACE", "TRACE")
}

PROTOCOL_TYPE_CHOICES = {
    ("HTTP", "HTTP"),
    ("HTTPS", "HTTPS")
}

STATUS_CHOICES = {
    ("Fail", u"失败"),
    ("Pass", u"通过"),
    ("Unexecuted", u"未执行")
}

VAR_TYPE_CHOICES = {
    ("5", "Rep-Header"),
    ("6", "Rep-Body"),
}

BODY_VARIABLE_TYPE_CHOICES = {
    # 表示资源配置中的环境变量
    ("GlobalVar", "GlobalVar"),
    # 类型
    ("Boolean", "Boolean"),
    ("File", "File"),
    ("Int", "Int"),
    ("Long", "Long"),
    ("String", "String"),
    ("Text", "Text"),
    # 项目定制的加密方法
    ("Encryption", "Encryption"),
}


# File文件存储位置
def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.it.creator, filename)


# 项目表
class Project(models.Model):
    name = models.CharField(max_length=100)
    desc = models.CharField(max_length=254, blank=True, null=True)
    user = models.ForeignKey(Account)  # 项目所属用户

    def __unicode__(self):
        return self.name


# 项目变量表
# HOST的写法: name="super.qiye.yixin.im" value="106.2.124.114"
class Variable(models.Model):
    name = models.CharField(max_length=100)  # 项目的变量名
    desc = models.CharField(max_length=254, blank=True, null=True)
    value = models.CharField(max_length=254)
    project = models.ForeignKey(Project)  # 外建项目Project，表示该变量所属于的项目
    type = models.CharField(max_length=100)  # 全局变量的类型, HOST/普通变量/接口返回值 三种类型
    creator = models.ForeignKey(Account, related_name="variable_creator", verbose_name="variable_creator")  # 创建者
    responsible = models.ForeignKey(Account, related_name="var_responsible", verbose_name="var_responsible")  # 责任人，更改者
    timestamp = models.DateTimeField("最后修改时间", auto_now=True)  # 最后一次修改的时间

    def __unicode__(self):
        return self.name


# 接口详情表
class ITStatement(models.Model):
    name = models.CharField(max_length=100, unique=True)  # 接口名称，唯一不能重复
    protocol_type = models.CharField(max_length=10, choices=PROTOCOL_TYPE_CHOICES)
    request_type = models.CharField(max_length=10, choices=REQUEST_TYPE_CHOICES)
    path = models.CharField(max_length=100)
    desc = models.CharField(max_length=254, blank=True, null=True)
    project = models.ForeignKey(Project)  # 表示所属项目
    creator = models.ForeignKey(Account, related_name="it_creator", verbose_name="it_creator")  # 创建者
    host = models.ForeignKey(Variable)  # HOST变量
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)  # 接口执行状态:执行失败、执行成功、未执行
    responsible = models.ForeignKey(Account, related_name="it_responsible", verbose_name="it_responsible")  # 负责人
    timestamp = models.DateTimeField("最后修改时间", auto_now=True)  # 最后一次修改的时间

    def __unicode__(self):
        return self.name


# 接口body表，即请求或响应体，用body_type区分
class ITBody(models.Model):
    name = models.CharField(max_length=100)  # 参数名
    body_format = models.SmallIntegerField()  # 3:格式化   4:原始
    type = models.CharField(max_length=50, choices=BODY_VARIABLE_TYPE_CHOICES)  # 参数类型
    desc = models.CharField(max_length=254, blank=True, null=True)
    value = models.TextField(blank=True, null=True)  # 可以传入大段文本
    upload_file = models.FileField(upload_to=user_directory_path, blank=True, null=True)  # 可以接收文件
    it = models.ForeignKey(ITStatement)
    # 外建接口ItStatement，表示该body所属于的接口
    body_type = models.SmallIntegerField()  # 0:请求体  1:响应体

    def __unicode__(self):
        return self.name


# 接口头表，即请求或响应头，用header_type区分
class ITHeader(models.Model):
    name = models.CharField(max_length=100)  # 参数名
    value = models.CharField(max_length=254, blank=True, null=True)
    # 标记是否全局变量，全局变量用GlobalVar标识
    type = models.CharField(max_length=10, blank=True, null=True)
    desc = models.CharField(max_length=254, blank=True, null=True)
    it = models.ForeignKey(ITStatement)
    header_type = models.SmallIntegerField()  # 0:请求头  1:响应头

    def __unicode__(self):
        return self.name


# 请求参数表，URL的后缀
class ITParam(models.Model):
    name = models.CharField(max_length=100)  # 请求参数的key
    value = models.CharField(max_length=254)
    # 标记是否全局变量，全局变量用GlobalVar标识
    type = models.CharField(max_length=10, blank=True, null=True)
    it = models.ForeignKey(ITStatement)

    def __unicode__(self):
        return self.name


# 变量参数中的接口返回值参数表
# 存储返回值的Header参数或者Body参数
class VariableIT(models.Model):
    it = models.ForeignKey(ITStatement, related_name="it_var", verbose_name="it_var")
    var = models.ForeignKey(Variable, related_name="var_it", verbose_name="var_it")
    assoc_type = models.CharField(max_length=10, choices=VAR_TYPE_CHOICES)
    assoc_id = models.IntegerField(blank=True, null=True)

    def __unicode__(self):
        return self.var.name + "-" + self.it.name


# 接口日志表
class ITLog(models.Model):
    it = models.ForeignKey(ITStatement)  # 外建接口ITStatement，表示该日志所属于的接口
    name = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now=True)
    log_path = models.CharField(max_length=254)

    def __unicode__(self):
        return self.name


# 目录树表，表示项目与测试用例的关系
class DirectoryTree(models.Model):
    # 最上层的文件夹的起始parent从1开始, 0表示还可以新建同级的最上层文件夹
    parent = models.IntegerField()
    name = models.CharField(max_length=254)
    # key 0：表示叶子节点-用例，1：表示子节点-文件夹
    key = models.CharField(max_length=100)
    level = models.IntegerField()
    project = models.ForeignKey(Project)  # 目录项属于哪一个项目，关联Project表的主键

    def __unicode__(self):
        return self.name


# 测试用例表
class TestCase(models.Model):
    name = models.CharField(max_length=254)
    belong = models.OneToOneField(DirectoryTree)  # 一个叶节点对应一个测试用例
    # 测试用例属于哪个目录项，关联DirectoryTree表的主键
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)  # 接口执行状态:执行失败/执行成功/未执行
    author = models.ForeignKey(Account, related_name="case_author", verbose_name="author")  # 作者
    responsible = models.ForeignKey(Account, related_name="case_responsible", verbose_name="responsible")  # 负责人
    timestamp = models.DateTimeField("最后一次修改时间", auto_now=True)  # 最后一次修改的时间
    tags = models.CharField(max_length=254, blank=True, null=True)  # 标签

    # message = models.CharField(max_length=254, blank=True, null=True)  # 记录用例运行相关信息，例如错误消息

    def __unicode__(self):
        return self.name


# 测试用例里的接口执行顺序流，即接口集组成一个test case
class TestCaseStep(models.Model):
    tc = models.ForeignKey(TestCase)  # 外建关联TestCase，表示该项属于哪个test case
    it = models.ForeignKey(ITStatement)  # 外键关联ITStatement，表示该项是哪个接口
    index = models.IntegerField()  # 记录接口执行的步骤
    name = models.CharField(max_length=100)  # 可对接口集重命名

    def __unicode__(self):
        return self.name


# 测试用例日志表
class TestCaseLog(models.Model):
    tc = models.ForeignKey(TestCase)  # 外键关联TestCase，表明是哪个test case 的日志
    name = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now=True)
    log_path = models.CharField(max_length=254)

    def __unicode__(self):
        return self.name


# 标签表
class Tag(models.Model):
    name = models.CharField(max_length=254)
    num = models.IntegerField()  # 标签被引用的次数

    def __unicode__(self):
        return self.name


# 标签与test case 映射表
class TagMap(models.Model):
    tag = models.ForeignKey(Tag)  # 外键关联Tag，表明是哪个tag
    tc = models.ForeignKey(TestCase)  # 外键关联TestCase，表明是哪个test case

    def __unicode__(self):
        return self.tc.name


# class UniId(models.Model):
#     """
#     统一ID表，建立用例集、用例、接口的对外统一ID
#     """
#     tc = models.ForeignKey(TestCase, related_name="UniId_TC", verbose_name="UniId_TC", blank=True, null=True)
#     it = models.ForeignKey(ITStatement, related_name="UniId_IT", verbose_name="UniId_IT", blank=True, null=True)
#     test_suite = models.ForeignKey(TestSuite, related_name="UniId_TS", verbose_name="UniId_TS", blank=True, null=True)


