# -*- coding: UTF-8 -*-
# base_message.py 文件用来保存基本信息模块的所有视图函数
from models import *
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .management.testcaserunner import TestCaseRunner
from django.views.generic import TemplateView
import json


# 用例相关处理
class TestCasesView(TemplateView):
    template_name = "basemessage.html"

    # 页面刷新展示 http://127.0.0.1:8000/projects/37/testcases/87
    # 响应的用例数据
    # 显示所选用例的所有接口信息
    def get_context_data(self, **kwargs):
        context = super(TestCasesView, self).get_context_data(**kwargs)
        context["project_table"] = Project.objects.all()
        context["selected_project"] = Project.objects.get(id=kwargs["project_id"])
        dir_tree = DirectoryTree.objects.get(id=kwargs["node_id"])
        test_case = TestCase.objects.filter(belong=dir_tree)  # 找到对应用例
        if test_case.exists():
            # 返回用例数据表到页面，构造合适数据结构
            context["all_steps"] = get_steps(test_case[0])
            project = Project.objects.get(id=kwargs["project_id"])
            context["its"] = get_its(project=project)
            context["tc"] = test_case[0]
            context["user_table"] = Account.objects.all()
            context["project_id"] = self.request.session["project_id"]
            context["path"] = current_position(project, context["tc"])
            context["statuses"] = STATUS_CHOICES
        return context

    @staticmethod
    def add_step(request, project_id, testcase_id):
        current_step_index = None
        if request.method == "POST":
            tc = get_object_or_404(TestCase, pk=testcase_id)
            if request.session.has_key("current_step_index"):
                current_step_index = request.session["current_step_index"]
                if current_step_index != "last":
                    tc_steps_gt_selected_step = TestCaseStep.objects.filter(tc=tc, index__gt=current_step_index)
                    # step_index之后的step的index都加一
                    for step in tc_steps_gt_selected_step:
                        step.index += 1
                        step.save()

            it_id = request.POST["selected_it"]  # 被选择接口的 id
            it = get_object_or_404(ITStatement, pk=it_id)  # 已选中的接口
            alias = request.POST["step_alias"]  # 用例步骤的别名
            if not alias:  # 如果别名为空，就用接口的名称作为别名
                alias = it.name
            # 如果是最后一个
            if current_step_index == "last":
                index = TestCaseStep.objects.filter(tc=tc).count() + 1
            else:
                index = int(current_step_index) + 1
            tc_step = TestCaseStep(tc=tc, it=it, index=index, name=alias)
            tc_step.save()
            # return render(request, TestCasesView.template_name, meta)
            return redirect("show_testcases", project_id, request.session["node_id"])
            # return render(request, "_basemsg.html", case_table(request, tc))

    @staticmethod
    def case_log(request, tc_id):
        """
        响应AJAX的执行日志请求
        :param request: HTTP请求，必须要有
        :param tc_id: 用例ID
        :return:json数据
        """
        if request.is_ajax() and request.method == "GET":
            print tc_id
            case = get_object_or_404(TestCase, pk=tc_id)
            print case.id, case
            # 用例执行
            case_runner = TestCaseRunner(case.id)
            execute_ret = case_runner.runner()  # 返回执行结果，通过、失败、未执行
            case.status = execute_ret  # 修改用例状态
            case.save()  # 更新数据库用例状态
            # 获取日志
            log = case_runner.get_log()  # 前端要展示的执行日志
            print u"执行结果", execute_ret
            context = dict()
            context["case_log"] = log
            context["status"] = execute_ret
            return HttpResponse(json.dumps(context))
        return HttpResponse("fail")

    @staticmethod
    def case_logs(request, tc_id):
        """
        返回用例所有执行日志
        :param request: HTTP请求，必须要有
        :param tc_id: 用例ID
        :return:json数据
        """
        if request.is_ajax() and request.method == "GET":
            logs = get_all_log(tc_id)
            context = dict()
            context["case_logs"] = list(logs.values("id", "name"))
            return HttpResponse(json.dumps(context))
        return HttpResponse("fail")

    @staticmethod
    def show_log(request, log_id):
        """
        返回用例执行日志的文件内容
        :param request: HTTP请求，必须要有
        :param log_id: 日志ID
        :return:json数据
        """
        if request.is_ajax() and request.method == "GET":
            context = dict()
            context["logs"] = get_log(log_id)
            return HttpResponse(json.dumps(context))
        return HttpResponse("fail")


class BaseMessage:
    """
    处理基本信息页的AJAX操作
    也是用例的相关操作
    """

    def __init__(self):
        pass

    @staticmethod
    def save_creator(request, tc_id):
        if request.is_ajax() and request.method == "GET":
            tc = get_object_or_404(TestCase, pk=tc_id)
            creator = request.GET["name"]
            user = User.objects.get(username=creator)
            author = Account.objects.get(user=user)
            tc.author = author
            tc.save()
            return HttpResponse(tc.author)
        return HttpResponse("changed failed")

    @staticmethod
    def save_responsible(request, tc_id):
        if request.is_ajax() and request.method == "GET":
            tc = get_object_or_404(TestCase, pk=tc_id)
            responsible_name = request.GET["name"]
            print responsible_name
            user = User.objects.get(username=responsible_name)
            responsible = Account.objects.get(user=user)
            tc.responsible = responsible
            tc.save()
            return HttpResponse(tc.responsible)
        return HttpResponse("change failed")

    @staticmethod
    def next_add_step(request):
        if request.is_ajax() and request.method == "GET":
            print request.GET
            step_index = request.GET["index"]
            # 点击的是每个测试步骤后的"增加"按钮时，把当前step的index保存到session中
            request.session["current_step_index"] = step_index
            return HttpResponse("step_index_saved")
        return HttpResponse("fail")

    @staticmethod
    def delete_step(request, tc_id):
        if request.is_ajax() and request.method == "GET":
            tc = get_object_or_404(TestCase, pk=tc_id)
            step_index = request.GET["index"]  # 获取要删除步骤的index
            tc_step = TestCaseStep.objects.get(index=step_index, tc=tc)  # 删除步骤
            tc_step.delete()
            # 找到当前测试用例中 所有大于删除步骤索引的步骤集
            tc_steps_gt_del_index = TestCaseStep.objects.filter(tc=tc, index__gt=step_index)
            if tc_steps_gt_del_index.count():  # 若要删除步骤后还有步骤，之后所有步骤索引减一
                for step in tc_steps_gt_del_index:
                    step.index -= 1
                    step.save()
            # 展示的新用例表
            new_case_table = case_table(request, tc)
            return render(request, "_basemsg.html", new_case_table)
        return HttpResponse("fail")

    @staticmethod
    def up_move(request, tc_id):
        if request.is_ajax() and request.method == "GET":
            tc = get_object_or_404(TestCase, pk=tc_id)
            step_index = int(request.GET["index"])  # 获取要上移的步骤的index
            if step_index == 1:
                return HttpResponse("first_step")
            # 找到要交换的两个对象
            tc_step = TestCaseStep.objects.get(index=step_index, tc=tc)
            front_step = get_object_or_404(TestCaseStep, index=step_index - 1, tc=tc)
            # 交换索引
            tc_step.index = step_index - 1
            front_step.index = step_index
            tc_step.save()
            front_step.save()
            # 展示的新用例表
            new_case_table = case_table(request, tc)
            return render(request, "_basemsg.html", new_case_table)
        return HttpResponse("fail")

    @staticmethod
    def down_move(request, tc_id):
        if request.is_ajax() and request.method == "GET":
            tc = get_object_or_404(TestCase, pk=tc_id)
            step_index = int(request.GET["index"])  # 获取要上移的步骤的index
            steps_count = TestCaseStep.objects.filter(tc=tc).count()
            if step_index == steps_count:
                return HttpResponse("last_step")
            # 找到要交换的两个对象
            tc_step = TestCaseStep.objects.get(index=step_index, tc=tc)
            next_step = get_object_or_404(TestCaseStep, index=step_index + 1, tc=tc)
            # 交换索引
            tc_step.index = step_index + 1
            next_step.index = step_index
            tc_step.save()
            next_step.save()
            # 更展示的新用例表
            new_case_table = case_table(request, tc)
            return render(request, "_basemsg.html", new_case_table)
        return HttpResponse("fail")


# 获取给定参数的项目下的所有接口，每个接口中包含其自身信息以及所有请求参数和响应参数、URL参数、head参数
# 因为有几个页面都要用到这个功能，所以把它抽象出一个函数
def get_its(project):
    """
    获取给定参数的项目下的所有接口，每个接口中包含其自身信息以及所有请求参数和响应参数、URL参数、head参数
    :param project: Model中的项目
    :return: 所有接口
    """
    it_in_project = ITStatement.objects.filter(project=project)
    its = []  # 保存当前项目下的所有接口信息
    for it in it_in_project:
        it_dic = dict()  # 保存一个接口的所有信息包括请求、响应参数
        it_dic["id"] = it.id
        it_dic["name"] = it.name
        # it_dic["protocol_type"] = it.protocol_type
        it_dic["request_type"] = it.request_type
        it_dic["path"] = it.path
        # it_dic["desc"] = it.desc
        # it_dic["creator"] = it.creator
        # it_dic["responsible"] = it.responsible
        # it_dic["timestamp"] = it.timestamp

        # 所有body参数
        body = ITBody.objects.filter(it=it)
        request_para = []
        response_para = []
        for para in body:
            if para.body_type == 0:  # 请求body
                request_para.append("%s:%s" % (para.name, para.value))
            elif para.body_type == 1:  # 响应body
                response_para.append("%s:%s" % (para.name, para.value))

        # 所有head参数
        head = ITHeader.objects.filter(it=it)
        request_head = []
        response_head = []
        for h in head:
            if h.header_type == 0:
                request_head.append("%s:%s" % (h.name, h.value))
            elif h.header_type == 1:
                response_head.append("%s:%s" % (h.name, h.value))

        # # 所有url参数
        # urls = ITParam.objects.filter(it=it)
        # url_para = []
        # for u in urls:
        #     url_para.append("%s:%s " % (u.key, u.value))

        it_dic["request_para"] = json.dumps(request_para)
        it_dic["response_para"] = json.dumps(response_para)
        # it_dic["request_head"] = json.dumps(request_head)
        it_dic["response_head"] = json.dumps(response_head)
        # it_dic["url_para"] = json.dumps(url_para)
        it_dic["status"] = it.status

        its.append(it_dic)

    return its


# 获取当前测试用例里的所有测试步骤，一个步骤对应一个接口
# 对应基本信息页面
def get_steps(tc):
    """
    获取当前测试用例里的所有测试步骤，一个步骤对应一个接口
    对应基本信息页面
    :param tc: Model中对应TestCase
    :return:
    """
    steps = TestCaseStep.objects.filter(tc=tc).order_by("index")
    all_steps = []  # 保存当前测试用例下的所有接口步骤，为基本信息页面提供数据
    for step in steps:
        tc_step = dict()  # 记录TestCaseStep表中的一行信息
        tc_step["index"] = step.index
        tc_step["alias"] = step.name
        it = step.it  # 记录接口
        body = ITBody.objects.filter(it=it)  # 根据接口找到所有Body
        # 把body所有请求或响应参数都处理成一个字符串，键值对的形式
        body_paras_request = []  # 保存当前接口所对应的body的所有请求参数
        body_paras_response = []  # 保存当前接口所对应的body的所有响应参数
        for body_para in body:
            if body_para.body_type == 0:
                body_paras_request.append("%s : %s" % (body_para.name, body_para.value))
            elif body_para.body_type == 1:
                body_paras_response.append("%s : %s" % (body_para.name, body_para.value))
        # tc_step["name"] = it.name
        tc_step["request_type"] = it.request_type
        tc_step["request_para"] = json.dumps(body_paras_request)
        tc_step["response_para"] = json.dumps(body_paras_response)
        tc_step["timestamp"] = it.timestamp
        tc_step["status"] = it.status
        all_steps.append(tc_step)  # 添加本条记录
    return all_steps


# 返回用例展示页面数据
# test_case: 当前用例
def case_table(request, test_case):
    # 返回用例数据表到页面，构造合适数据结构
    case_data = dict()
    case_data["all_steps"] = get_steps(test_case)
    case_data["project_id"] = request.session["project_id"]
    project = Project.objects.get(id=case_data["project_id"])
    case_data["its"] = get_its(project=project)
    case_data["tc"] = test_case
    case_data["user_table"] = Account.objects.all()
    case_data["path"] = current_position(project, case_data["tc"])
    case_data["statuses"] = STATUS_CHOICES
    return case_data


def current_position(project, case):
    """
    获取目录树当前展开路径
    :param project: 当前项目
    :param case: 目录树中选中的用例
    :return: 该用例在目录树中的路径
    """
    node = case.belong  # case对应的目录树中的叶节点
    path = ""
    while node:
        if node.parent != 0:
            path = node.name + " > " + path
            node = DirectoryTree.objects.get(pk=node.parent, project=project)
        else:
            path = node.name + " > " + path
            break
    path = path[0:len(path) - 2]
    return path


def get_log(log_id):
    """
    获取log_id对应的log日志的内容，打开后记得关闭文件
    :param log_id:
    :return: 对应日志文件内容
    """
    query_set = TestCaseLog.objects.filter(id=log_id)
    if query_set.exists():
        log_path = query_set[0].log_path
        f_log = open(log_path)
        content = f_log.readlines()
        f_log.close()
        return content
    else:
        return "nothing"


def get_all_log(tc_id):
    """
    获取用例的所有日志对象
    :param tc_id: 用例ID
    :return: 所有日志对象
    """
    tc = TestCase.objects.filter(id=tc_id)
    if tc.exists():
        return TestCaseLog.objects.filter(tc=tc[0]).order_by("timestamp")
    else:
        return "no this tc"
