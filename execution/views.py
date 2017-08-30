# -*- coding: UTF-8 -*-
from django.views.generic import TemplateView
from interface_platform.models import Project, TestCase, Account, DirectoryTree
from .models import SuiteTree, TestSuite, SuiteReport
from django.http import HttpResponse
from django.forms.models import model_to_dict
from interface_platform.management.testcaserunner import TestCaseRunner
from django.shortcuts import get_object_or_404
import concurrent.futures
import json
import datetime

# 线程池最大线程数
MAX_WORKERS = 10


class CaseExecution(TemplateView):
    template_name = "test_execution.html"

    def get_context_data(self, **kwargs):
        context = super(CaseExecution, self).get_context_data(**kwargs)
        context["project_table"] = Project.objects.all()
        context["selected_project"] = Project.objects.get(id=kwargs["project_id"])
        self.request.session["project_id"] = kwargs["project_id"]
        return context


class SuitesView(TemplateView):
    template_name = "new_execution.html"

    # 显示当前项目所有信息
    def get_context_data(self, **kwargs):
        context = super(SuitesView, self).get_context_data(**kwargs)
        context["project_table"] = Project.objects.all()
        context["selected_project"] = Project.objects.get(id=kwargs["project_id"])
        # 存储project_id到session里
        self.request.session["project_id"] = kwargs["project_id"]
        return context

    @staticmethod
    def save_suite(request, project_id):
        if request.method == "POST":
            result = []
            data = json.loads(request.body)
            chosen_nodes = data["chosenNodes"]
            for chosen_node in chosen_nodes:
                if chosen_node["pId"] is None:
                    chosen_node["pId"] = 0
                suite_tree = SuiteTree(mid=chosen_node["mId"], parent=chosen_node["pId"], name=chosen_node["name"],
                                       key=chosen_node["key"], level=chosen_node["level"])
                suite_tree.save()
                result.append(model_to_dict(suite_tree))
            # 返回根节点json数据
            return HttpResponse(json.dumps(result), content_type="application/json")


class SuiteRun(TemplateView):
    template_name = "run_executions.html"

    def get_context_data(self, **kwargs):
        context = super(SuiteRun, self).get_context_data(**kwargs)
        context["project_table"] = Project.objects.all()
        context["selected_project"] = Project.objects.get(id=kwargs["project_id"])
        self.request.session["project_id"] = kwargs["project_id"]
        return context

    @staticmethod
    def report_tree(request):
        if request.is_ajax() and request.method == "GET":
            # 获取用例执行集对应SuiteTree的数据
            test_suite = get_object_or_404(TestSuite, pk=request.GET["suite_id"])
            simple_data = []
            data = test_suite.roots.all()
            if data.exists():
                for item in data:
                    it = dict()
                    # id在显示中会自动编号，这里的无效
                    it["id"] = item.mid
                    it["pId"] = item.parent
                    it["name"] = item.name
                    # 存储case id值
                    it["mId"] = item.mid
                    it["key"] = item.key
                    if item.key == "1":
                        it["isParent"] = "true"
                    simple_data.append(it)
            return HttpResponse(json.dumps(simple_data), content_type="application/json")

    @staticmethod
    def run(request, project_id):
        if request.method == "POST":
            print "run report ---------"
            data = json.loads(request.body)
            case_list = []
            case_count = {'Passed': 0, 'Skipped': 0, 'Failed': 0}
            start_time = datetime.datetime.now()
            test_suite = get_object_or_404(TestSuite, pk=data["suite_id"])
            nodes = test_suite.roots.all()
            if nodes.exists():
                for node in nodes:
                    if int(node.key) == 0:
                        real_tree = get_object_or_404(DirectoryTree, pk=node.mid)
                        case_list.append(get_object_or_404(TestCase, belong=real_tree))
            count = len(case_list)
            print "----------"
            print count
            print "----------"
            runner = get_object_or_404(Account, user=request.user)
            ### 线程池
            pool = concurrent.futures.ThreadPoolExecutor(MAX_WORKERS)  # 创建线程池
            case_in_pool = {pool.submit(SuiteRun.run_case, case): case.id for case in case_list}
            for future in concurrent.futures.as_completed(case_in_pool):
                try:
                    data = future.result()
                except Exception as exc:
                    print('generated an exception: %s' % exc)
                    case_count['failed'] += 1
                else:
                    print('case %d execute result is %s' % (case_in_pool[future], data))
                    if data == 'Pass':
                        case_count['Passed'] += 1
                    elif data == 'Fail':
                        case_count['Failed'] += 1
                    else:
                        case_count['Skipped'] += 1
            if case_count['Failed'] != 0:
                result = 'Failed'
            else:
                result = 'Passed'
            end_time = datetime.datetime.now()
            duration = end_time - start_time
            rerun = 0
            report = SuiteReport(suite=test_suite, start_time=start_time, end_time=end_time, runner=runner, rerun=rerun,
                                 count=count, duration=duration, passed=case_count['Passed'],
                                 failed=case_count['Failed'], skipped=case_count['Skipped'], result=result)
            report.save()
            response_data = {"reportId": report.id}
            return HttpResponse(json.dumps(response_data), content_type="application/json")

    @staticmethod
    def run_case(case):
        # 单个用例执行
        case_runner = TestCaseRunner(case.id)
        execute_ret = case_runner.runner()  # 返回执行结果，通过、失败、未执行
        case.status = execute_ret  # 修改用例状态
        case.save()  # 更新数据库用例状态
        return execute_ret
