# -*- coding: UTF-8 -*-
from models import SuiteReport, TestSuite
from serializers import SuiteReportSerializers, TestSuiteSerializers
from rest_framework import generics


class SuiteReportMixin(object):
    model = SuiteReport
    queryset = SuiteReport.objects.all()
    serializer_class = SuiteReportSerializers


class TestSuiteMixin(object):
    model = TestSuite
    queryset = TestSuite.objects.all()
    serializer_class = TestSuiteSerializers


class ReportDetail(SuiteReportMixin, generics.RetrieveAPIView):
    pass


class ReportList(SuiteReportMixin, generics.ListAPIView):
    pass


class SuiteReportDetail(SuiteReportMixin, generics.RetrieveAPIView):
    pass


class SuiteReportList(SuiteReportMixin, generics.ListAPIView):
    def get_queryset(self):
        queryset = super(SuiteReportList, self).get_queryset()
        return queryset.filter(suite__pk=self.kwargs.get('suite_id'))


class TestSuiteList(TestSuiteMixin, generics.ListCreateAPIView):
    """
    返回指定项目下的所有用例执行集
    """
    def get_queryset(self):
        queryset = super(TestSuiteList, self).get_queryset()
        return queryset.filter(project__pk=self.kwargs.get('project_id'))


class TestSuiteDetail(TestSuiteMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    指定项目下新建用例执行集
    """

