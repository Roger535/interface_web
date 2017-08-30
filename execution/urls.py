# -*- coding: UTF-8 -*-
from django.conf.urls import url, include
from .api import *
from .views import *

# API的后缀不需要“/”
api_urls = [
    url(r"^testsuites$", TestSuiteList.as_view(), name="testsuite-list"),
    url(r"^testsuites/(?P<pk>\d+)$", TestSuiteDetail.as_view(), name="testsuite-detail"),
    url(r"^testsuites/(?P<suite_id>\d+)/suitereports$", SuiteReportList.as_view(), name="suitereport-list"),
    url(r"^testsuites/(?P<suite_id>\d+)/suitereports/(?P<pk>\d+)$", SuiteReportDetail.as_view(), name="suitereport-detail"),
]

urlpatterns = [
    url(r"^api/", include(api_urls)),
    url(r"^$", CaseExecution.as_view(), name="execution"),
    url(r"^suites/$", SuitesView.as_view(), name="new_suite"),
    url(r"^suites/(?P<suite_id>\d+)/reports/$", SuiteRun.as_view(), name="suite_reports"),


    # AJAX
    url(r"^suite/save/$", SuitesView.save_suite, name="save_suite"),
    # url(r"^report/tree/$", SuiteRun.report_tree, name="report_tree"),
    url(r"^suite/run/$", SuiteRun.run, name="run"),
]
