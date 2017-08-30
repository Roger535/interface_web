from django.contrib import admin
from interface_platform.models import *


class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "desc", "user")
    ordering = ["name"]


admin.site.register(Project, ProjectAdmin)


class DirectoryTreeAdmin(admin.ModelAdmin):
    list_display = ("id", "parent", "name", "key", "level", "project")
    ordering = ["id"]


admin.site.register(DirectoryTree, DirectoryTreeAdmin)


class ITAdmin(admin.ModelAdmin):
    list_display = ("name", "protocol_type", "request_type", "path", "desc", "project", "host", "creator",
                    "responsible", "status", "timestamp")
    ordering = ["name"]


admin.site.register(ITStatement, ITAdmin)


class ITBodyAdmin(admin.ModelAdmin):
    list_display = ("name", "body_format", "type", "desc", "value", "it", "body_type", "upload_file")
    ordering = ["name"]


admin.site.register(ITBody, ITBodyAdmin)


class ITHeaderAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "value", "desc", "it", "header_type")
    ordering = ["name"]


admin.site.register(ITHeader, ITHeaderAdmin)


class ITParamAdmin(admin.ModelAdmin):
    list_display = ("name", "value", "type", "it")
    ordering = ["name"]


admin.site.register(ITParam, ITParamAdmin)


class VariableAdmin(admin.ModelAdmin):
    list_display = ("name", "desc", "value", "project", "type")
    ordering = ["name"]


admin.site.register(Variable, VariableAdmin)


class VariableITAdmin(admin.ModelAdmin):
    list_display = ("it", "var", "assoc_type", "assoc_id")
    ordering = ["var"]


admin.site.register(VariableIT, VariableITAdmin)


class TestCaseAdmin(admin.ModelAdmin):
    list_display = ("name", "belong", "status", "author", "responsible", "timestamp", "tags")
    ordering = ["belong", "name"]


admin.site.register(TestCase, TestCaseAdmin)


class TestCaseStepAdmin(admin.ModelAdmin):
    list_display = ("tc", "index", "name", "it")
    ordering = ["tc"]


admin.site.register(TestCaseStep, TestCaseStepAdmin)


class TagAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "num")
    ordering = ["name"]


admin.site.register(Tag, TagAdmin)


class TagMapAdmin(admin.ModelAdmin):
    list_display = ("id", "tag", "tc")
    ordering = ["id"]


admin.site.register(TagMap, TagMapAdmin)


class ITLogAdmin(admin.ModelAdmin):
    list_display = ("name", "log_path", "timestamp")


admin.site.register(ITLog, ITLogAdmin)


class TestCaseLogAdmin(admin.ModelAdmin):
    list_display = ("name", "log_path", "timestamp")


admin.site.register(TestCaseLog, TestCaseLogAdmin)
