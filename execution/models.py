# -*- coding: UTF-8 -*-
from django.db import models
from account.models import Account
from interface_platform.models import Project


# 目录树表，表示项目与测试用例的关系
class SuiteTree(models.Model):
    # 存储mId，复制的节点id
    mid = models.IntegerField()
    # 最上层的文件夹的起始parent从1开始, 0表示还可以新建同级的最上层文件夹
    parent = models.IntegerField()
    name = models.CharField(max_length=254)
    # key 0：表示叶子节点-用例，1：表示子节点-文件夹
    key = models.CharField(max_length=100)
    level = models.IntegerField()

    def __unicode__(self):
        return self.name


# 用例集表，记录执行的用例集，存储目录树的根目录
class TestSuite(models.Model):
    name = models.CharField(max_length=100)
    # 包含的用例集，用树的根节点表示，可能包含多个根节点
    roots = models.ManyToManyField(SuiteTree, related_name="roots", verbose_name="roots")
    project = models.ForeignKey(Project)

    def __unicode__(self):
        return self.name


class SuiteReport(models.Model):
    suite = models.ForeignKey(TestSuite, related_name="suite_report", verbose_name="suite_report")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    runner = models.ForeignKey(Account, related_name="runner", verbose_name="runner")
    rerun = models.SmallIntegerField()  # 记录重跑次数，起始值为0
    count = models.IntegerField()  # 用例总数
    duration = models.DurationField()  # 用例执行耗时，MySQL存储的时候使用bigint存储，即毫秒数
    passed = models.IntegerField()
    failed = models.IntegerField()
    skipped = models.IntegerField()
    result = models.CharField(max_length=10)  # 执行结果

    def __unicode__(self):
        return self.suite.name + " " + str(self.start_time)





