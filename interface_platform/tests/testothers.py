# -*- coding: UTF-8 -*-

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "interface_platform.settings")

import time
import re
from datetime import datetime
from ..models import ITStatement, TestCase, TestSuite, UniId

print re.match(r"\$(.*)", "2134ss")

print "123"[1:]

print time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
print str(datetime.now())

# # 建立统一ID
# it_query_set = ITStatement.objects.all()
# for it in it_query_set:
#     ui_id = UniId.objects.create(it=it)
#     ui_id.save()
#
# tc_query_set = TestCase.objects.all()
# for tc in tc_query_set:
#     ui_tc = UniId.objects.create(tc=tc)
#     ui_tc.save()

# ts_query_set = TestSuite.objects.all()
# for ts in ts_query_set:
#     ts_id = UniId.objects.create(test_suite=ts)
#     ts_id.save()
