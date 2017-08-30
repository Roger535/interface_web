# -*- coding: UTF-8 -*-
from models import *
from account.models import Account
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .management.interfacerunner import InterfaceRunner
from django.views.generic import TemplateView
import json


class InterfacesView(TemplateView):
    """
    接口管理相关处理
    """
    template_name = "interface_manage.html"

    def get_context_data(self, **kwargs):
        context = super(InterfacesView, self).get_context_data(**kwargs)
        project_id = int(kwargs["project_id"])
        context["project_table"] = Project.objects.all()
        context["selected_project"] = get_object_or_404(Project, pk=project_id)
        context["its_table"] = ITStatement.objects.filter(project=context["selected_project"])
        return context

    @staticmethod
    def create_interface(request, project_id):
        """
        新建接口
        :param request: HTTP请求
        :param project_id: 当前项目ID
        :return: 新建接口页面
        """
        project_id = int(project_id)
        project = get_object_or_404(Project, pk=project_id)
        user_table = User.objects.all()[1:]
        variable_table = Variable.objects.filter(type__iexact="HOST", project=project)
        # 根据经验得，context里包含此view视图函数里所有获取的对象如project等，可以让template使用时覆盖性更强
        context = dict()
        context["user_table"] = user_table
        context["variable_table"] = variable_table
        context["project_table"] = Project.objects.all()
        context["selected_project"] = get_object_or_404(Project, pk=project_id)

        return render(request, "new_interface.html", context)

    @staticmethod
    def save_interface(request, project_id):
        """
        把新建接口存储到数据库，接受POST方式的数据
        :param request: HTTP请求
        :param project_id: 当前项目ID
        :return:跳转到详情页面
        """
        if request.method == 'POST':
            project_id = int(project_id)
            c_project = get_object_or_404(Project, pk=project_id)
            name = request.POST['it_name'].strip()
            protocol_type = request.POST['protocol_type']
            request_type = request.POST['request_type']
            path = request.POST['url'].strip()
            desc = request.POST['desc']
            # 根据前端传入的用户名，查找User表获取user_id，根据user_id找到对应的账户对象
            creator_name = request.POST['creator']
            user = User.objects.get(username=creator_name)
            creator = Account.objects.get(user=user)
            # responsible 获取对象的方式同creator
            responsible_name = request.POST['responsible']
            user = User.objects.get(username=responsible_name)
            responsible = Account.objects.get(user=user)
            # HOST变量
            host_name = request.POST['host_name']
            host = Variable.objects.get(name=host_name, project=c_project)
            status = "Unexecuted"  # 新建接口时，状态默认是 2:未执行
            if name and len(name) <= 100:
                interface = ITStatement(name=name, protocol_type=protocol_type, request_type=request_type, path=path,
                                        desc=desc, creator=creator, responsible=responsible, project=c_project,
                                        host=host, status=status)
                interface.save()
                return redirect("interface_detail", project_id, interface.id)

        return redirect("interface_manage", project_id)

    @staticmethod
    def interface_detail(request, project_id, it_id):
        """
        接口详细信息
        :param request: HTTP请求
        :param project_id: 当前项目ID
        :param it_id: 当前接口ID
        :return: 接口详细信息页面
        """
        project_id = int(project_id)
        project = get_object_or_404(Project, pk=project_id)
        it_id = int(it_id)
        it = get_object_or_404(ITStatement, pk=it_id, project=project)
        context = page_context(project, it)
        context["project_table"] = Project.objects.all()
        context["selected_project"] = project
        context["it"] = it
        return render(request, "interface_detail.html", context)

    @staticmethod
    def delete_interface(request):
        """删除接口"""
        if request.is_ajax() and request.method == "GET":
            it_id = int(request.GET["it_id"])
            ITStatement.objects.get(pk=it_id).delete()
            return HttpResponse("success")
        return HttpResponse("fail")

    @staticmethod
    def update_interface(request, it_id):
        """
        接口详情页面更改后，实时自动保存
        :param request: HTTP请求
        :param it_id: 当前接口ID
        :return: 保存修改后的接口信息
        """
        if request.is_ajax() and request.method == "GET":
            project_id = request.session["project_id"]
            project = get_object_or_404(Project, pk=project_id)
            it_id = int(it_id)
            it = get_object_or_404(ITStatement, pk=it_id, project=project)
            name = request.GET["name"]
            value = request.GET["value"]
            if name == "request_type":
                it.request_type = value
            elif name == "path":
                it.path = value
            elif name == "it_name":
                it.name = value
            elif name == "host_name":
                it.host = Variable.objects.get(name=value, type__iexact="host", project=project)
            elif name == "protocol_type":
                it.protocol_type = value
            elif name == "responsible":
                it.responsible = Account.objects.get(user=User.objects.get(username=value))
            elif name == "creator":
                it.creator = Account.objects.get(user=User.objects.get(username=value))
            elif name == "desc":
                it.desc = value
            elif name == "status":
                for (k, v) in STATUS_CHOICES:
                    if v == value:
                        it.status = k
                        break
            it.save()
            return HttpResponse("success")
        return HttpResponse("fail")

    @staticmethod
    def url_para(request, it_id):
        """
        请求信息页中，URL参数修改后的实时保存
        :param request: HTTP请求
        :param it_id: 当前接口ID
        :return: 保存修改后的URL参数
        """
        if request.is_ajax() and request.method == "POST":
            # project_id = request.session["project_id"]
            # project = get_object_or_404(Project, pk=project_id)
            it_id = int(it_id)
            it = get_object_or_404(ITStatement, pk=it_id)
            url_tr = request.POST
            url_para_id = url_tr["id"]
            name = url_tr["name"]
            value = url_tr["value"]
            value_type = url_tr["valueType"]
            if url_para_id == "urlTr":
                if name and value:
                    new_url_para = ITParam(name=name, value=value, type=value_type, it=it)
                    new_url_para.save()
                    ret_msg = {"msg": "new_url", "url_id": new_url_para.id}
                    return HttpResponse(json.dumps(ret_msg))
            else:
                url_para_id = int(url_para_id)
                url_para = get_object_or_404(ITParam, pk=url_para_id)
                if name != url_para.name:
                    url_para.name = name
                if value != url_para.value:
                    url_para.value = value
                if value_type != url_para.type:
                    url_para.type = value_type
                url_para.save()
                ret_msg = {"msg": "success"}
                return HttpResponse(json.dumps(ret_msg))
        ret_msg = {"msg": "fail"}
        return HttpResponse(json.dumps(ret_msg))

    @staticmethod
    def request_head(request, it_id):
        """
        请求信息中请求头参数更改后，实时自动保存
        :param request: HTTP请求
        :param it_id: 当前接口ID
        :return: 保存修改后的请求头参数
        """
        if request.is_ajax() and request.method == "POST":
            # project_id = request.session["project_id"]
            # project = get_object_or_404(Project, pk=project_id)
            it_id = int(it_id)
            it = get_object_or_404(ITStatement, pk=it_id)
            # print request.POST
            req_head_tr = request.POST
            req_head_para_id = req_head_tr["id"]
            name = req_head_tr["name"]
            value = req_head_tr["value"]
            desc = req_head_tr["desc"]
            value_type = req_head_tr["valueType"]

            if req_head_para_id == "reqHeadTr":
                if name:  # and value:
                    new_head = ITHeader(name=name, value=value, type=value_type, desc=desc, it=it, header_type=0)
                    new_head.save()
                    ret_msg = {"msg": "new_reqHead", "head_id": new_head.id}
                    return HttpResponse(json.dumps(ret_msg))
            elif req_head_para_id == "custom":
                if name and value_type == "101":
                    new_head = ITHeader(name=name, value=value, type="Text", desc=desc, it=it, header_type=101)
                elif name and value_type == "102":
                    new_head = ITHeader(name=name, value=value, type="Text", desc=desc, it=it, header_type=102)
                new_head.save()
                ret_msg = {"msg": "custom_head", "head_id": new_head.id}
                return HttpResponse(json.dumps(ret_msg))
            else:
                req_head_para_id = int(req_head_para_id)
                req_head_para = get_object_or_404(ITHeader, pk=req_head_para_id)
                if name != req_head_para.name:
                    req_head_para.name = name
                if value != req_head_para.value:
                    req_head_para.value = value
                if desc != req_head_para.desc:
                    req_head_para.desc = desc
                if value_type != req_head_para.type:
                    req_head_para.type = value_type
                req_head_para.save()
                ret_msg = {"msg": "updated"}
                return HttpResponse(json.dumps(ret_msg))

        ret_msg = {"msg": "fail"}
        return HttpResponse(json.dumps(ret_msg))

    @staticmethod
    def request_body(request, it_id):
        """
        请求信息中请求体参数更改后，实时自动保存
        :param request: HTTP请求
        :param it_id: 当前接口ID
        :return: 保存修改后的请求体参数
        """
        if request.is_ajax() and request.method == "POST":
            # project_id = request.session["project_id"]
            # project = get_object_or_404(Project, pk=project_id)
            it_id = int(it_id)
            it = get_object_or_404(ITStatement, pk=it_id)
            req_body = request.POST
            print req_body
            req_body_id = req_body["id"]
            name = req_body["name"]
            value = req_body["value"]
            value_type = req_body["valueType"]
            desc = req_body["desc"]
            body_format = req_body["format"]

            if body_format == "3":  # 请求数据来自表格，即格式化
                if req_body_id == "reqBodyTr":
                    if name:  # and value:
                        new_body = ITBody(name=name, body_format=3, type=value_type, desc=desc, value=value, it=it,
                                          body_type=0)
                        new_body.save()
                        ret_msg = {"msg": "new_reqBody", "body_id": new_body.id}
                        return HttpResponse(json.dumps(ret_msg))
                else:
                    req_body_id = int(req_body_id)
                    req_body_para = ITBody.objects.get(pk=req_body_id)
                    if req_body_para.name != name:
                        req_body_para.name = name
                    if req_body_para.value != value:
                        req_body_para.value = value
                    if req_body_para.type != value_type:
                        req_body_para.type = value_type
                    if req_body_para.desc != desc:
                        req_body_para.desc = desc
                    req_body_para.save()
                    ret_msg = {"msg": "updated"}
                    return HttpResponse(json.dumps(ret_msg))

            elif body_format == "4":  # 请求数据来自自输入即原始
                pass

        ret_msg = {"msg": "fail"}
        return HttpResponse(json.dumps(ret_msg))

    @staticmethod
    def response_head(request, it_id):
        """
        响应信息中，响应头参数修改后的实时保存
        :param request: HTTP请求
        :param it_id: 当前接口ID
        :return: 保存修改后的响应头参数
        """
        if request.is_ajax() and request.method == "POST":

            it_id = int(it_id)
            it = get_object_or_404(ITStatement, pk=it_id)

            rep_head_para = request.POST
            print rep_head_para
            rep_head_para_id = rep_head_para["id"]
            name = rep_head_para["name"]
            value = rep_head_para["value"]
            desc = rep_head_para["desc"]

            if rep_head_para_id == "repHeadTr":
                if name:  # and value:
                    new_head = ITHeader(name=name, value=value, type="text", desc=desc, it=it, header_type=1)
                    new_head.save()
                    ret_msg = {"msg": "new_repHead", "head_id": new_head.id}
                    return HttpResponse(json.dumps(ret_msg))
            else:
                rep_head_para_id = int(rep_head_para_id)
                rep_head = ITHeader.objects.get(pk=rep_head_para_id)
                if rep_head.name != name:
                    rep_head.name = name
                if rep_head.value != value:
                    rep_head.value = value
                if rep_head.desc != desc:
                    rep_head.desc = desc
                rep_head.save()
                ret_msg = {"msg": "updated"}
                return HttpResponse(json.dumps(ret_msg))

        return HttpResponse("fail")

    @staticmethod
    def response_body(request, it_id):
        """
        响应信息页中，响应体参数修改后的实时保存
        :param request: HTTP请求
        :param it_id: 当前接口ID
        :return: 保存
        """
        if request.is_ajax() and request.method == "POST":
            # project_id = request.session["project_id"]
            # project = get_object_or_404(Project, pk=project_id)
            it_id = int(it_id)
            it = get_object_or_404(ITStatement, pk=it_id)
            rep_body = request.POST
            print rep_body
            rep_body_id = rep_body["id"]
            name = rep_body["name"]
            value = rep_body["value"]
            value_type = rep_body["valueType"]
            desc = rep_body["desc"]
            body_format = rep_body["format"]

            if body_format == "3":  # 请求数据来自表格，即格式化
                if rep_body_id == "repBodyTr":
                    if name:  # and value:
                        new_body = ITBody(name=name, body_format=3, type=value_type, desc=desc, value=value, it=it,
                                          body_type=1)
                        new_body.save()
                        ret_msg = {"msg": "new_repBody", "body_id": new_body.id}
                        return HttpResponse(json.dumps(ret_msg))
                else:
                    rep_body_id = int(rep_body_id)
                    rep_body_para = ITBody.objects.get(pk=rep_body_id)
                    if rep_body_para.name != name:
                        rep_body_para.name = name
                    if rep_body_para.value != value:
                        rep_body_para.value = value
                    if rep_body_para.type != value_type:
                        rep_body_para.type = value_type
                    if rep_body_para.desc != desc:
                        rep_body_para.desc = desc

                    rep_body_para.save()
                    ret_msg = {"msg": "updated"}
                    return HttpResponse(json.dumps(ret_msg))

            elif body_format == "4":  # 请求数据来自自输入即原始
                pass

        ret_msg = {"msg": "fail"}
        return HttpResponse(json.dumps(ret_msg))

    @staticmethod
    def response_para(request):
        it_paras = {}
        if request.is_ajax() and request.method == "GET":
            it_id = request.GET["it_id"]
            # print it_id
            it = get_object_or_404(ITStatement, pk=int(it_id))
            rep_heads = ITHeader.objects.filter(it=it, header_type=1)
            rep_bodies = ITBody.objects.filter(it=it, body_format=3, body_type=1)
            rep_head_table = []
            for head in rep_heads:
                rep_head_dict = dict()
                rep_head_dict["id"] = head.id
                rep_head_dict["name"] = head.name
                rep_head_dict["value"] = head.value
                rep_head_table.append(rep_head_dict)
            rep_body_table = []
            for body in rep_bodies:
                rep_body_dict = dict()
                rep_body_dict["id"] = body.id
                rep_body_dict["name"] = body.name
                rep_body_dict["value"] = body.value
                rep_body_table.append(rep_body_dict)
            it_paras = {"rep_heads": rep_head_table, "rep_bodies": rep_body_table}
            # print it_paras
        return HttpResponse(json.dumps(it_paras))

    @staticmethod
    def delete_interface_para(request):
        if request.is_ajax() and request.method == "GET":
            para_type = request.GET["delType"]
            para_id = int(request.GET["id"])
            if para_type == "del_url":
                ITParam.objects.get(pk=para_id).delete()
            elif para_type == "del_reqHead":
                ITHeader.objects.get(pk=para_id).delete()
            elif para_type == "del_reqBody":
                ITBody.objects.get(pk=para_id).delete()
            elif para_type == "del_repHead":
                ITHeader.objects.get(pk=para_id).delete()
            elif para_type == "del_repBody":
                ITBody.objects.get(pk=para_id).delete()
            return HttpResponse("del_success")

        return HttpResponse("fail")

    @staticmethod
    def interface_log(request, it_id):
        """
        响应AJAX的执行日志请求
        :param request: HTTP请求，必须要有
        :param it_id: 用例ID
        :return:string格式的执行日志
        """
        if request.is_ajax() and request.method == "GET":
            project_id = request.session["project_id"]
            project = get_object_or_404(Project, pk=project_id)
            it_id = int(it_id)
            it = get_object_or_404(ITStatement, pk=it_id, project=project)
            # 接口执行
            interface_runner = InterfaceRunner(it.id)
            execute_ret = interface_runner.runner()  # 返回执行结果，Pass、Fail、Unexecuted
            # 获取日志
            log = interface_runner.get_log()  # 前端要展示的执行日志
            # print 'execute_ret', execute_ret
            it.status = execute_ret  # 接口日志执行完后就修改接口状态
            it.save()
            context = dict()
            for (k, v) in STATUS_CHOICES:
                if k == execute_ret:
                    execute_ret = v
                    break
            context["it_status"] = execute_ret
            context["it_log"] = log
            return HttpResponse(json.dumps(context))

    @staticmethod
    def history_logs(request, it_id):
        """
        返回当前接口的所有日志
        :param request: HTTP请求
        :param it_id: 接口ID
        :return: 当前接口的所有日志的id和name组成的json
        """
        if request.is_ajax() and request.method == "GET":
            it = ITStatement.objects.filter(id=it_id)
            if it.exists():
                logs = ITLog.objects.filter(it=it)
                context = dict()
                context["it_logs"] = list(logs.values("id", "name"))
                return HttpResponse(json.dumps(context))
        return HttpResponse("fail")

    @staticmethod
    def show_log(request, it_id, log_id):
        """
        显示当前日志的内容
        :param request: HTTP请求
        :param it_id: 接口ID
        :param log_id: 日志ID
        :return: 当前日志内容
        """
        if request.is_ajax() and request.method == "GET":
            query_set = ITLog.objects.filter(id=log_id)
            if query_set.exists():
                log_path = query_set[0].log_path
                f_log = open(log_path)
                content = f_log.readlines()
                f_log.close()
                context = dict()
                context["logs"] = content
                return HttpResponse(json.dumps(context))
        return HttpResponse("fail")


def page_context(project, it):
    """
    接口详情页面，请求和响应页面需要渲染的一些信息
    :param project: 当前项目对象
    :param it: 当前接口对象
    :return: 格式化的字典
    """
    variable_global_table = Variable.objects.filter(project=project, type__in=["普通变量", "接口返回值"])
    host_table = Variable.objects.filter(type__iexact="HOST", project=project)
    user_table = Account.objects.all()[1:]
    # 获取当前接口的所有url参数
    url_para_table = ITParam.objects.filter(it=it)
    # 获取当前接口的所有请求header参数
    head_para_request_table = ITHeader.objects.filter(it=it, header_type__in=[0, 101, 102])
    # 获取当前接口的所有响应header参数
    head_para_response_table = ITHeader.objects.filter(it=it, header_type=1)
    # 获取当前接口的所有请求body参数
    body_para_request_table = ITBody.objects.filter(it=it, body_type=0)
    # 获取当前接口的所有响应body参数
    body_para_response_table = ITBody.objects.filter(it=it, body_type=1)
    para_types = {"GlobalVar", "Text", "File"}
    context = {"variable_global_table": variable_global_table, "host_table": host_table, "user_table": user_table,
               "url_para_table": url_para_table, "protocol_types": PROTOCOL_TYPE_CHOICES, "statuses": STATUS_CHOICES,
               "request_types": REQUEST_TYPE_CHOICES, "para_types": para_types,
               "head_para_request_table": head_para_request_table, "head_para_response_table": head_para_response_table,
               "body_para_request_table": body_para_request_table, "body_para_response_table": body_para_response_table}
    return context
