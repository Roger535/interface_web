from django.contrib import admin
from .models import SuiteTree, TestSuite, SuiteReport

# Register your models here.
admin.site.register(SuiteTree)
admin.site.register(TestSuite)
admin.site.register(SuiteReport)
