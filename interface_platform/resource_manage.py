# -*- coding: UTF-8 -*-
from models import *
from account.models import Account
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from base_message import get_its
from django.views.generic import TemplateView
from model.typemap import VAR_TYPE
import json


class ResourcesView(TemplateView):
    """
    资源配置相关处理
    """
    template_name = "resource_config.html"

    def get_context_data(self, **kwargs):
        context = super(ResourcesView, self).get_context_data(**kwargs)
        context["selected_project"] = get_object_or_404(Project, pk=int(kwargs["project_id"]))
        context["project_table"] = Project.objects.all()
        context["variable_table"] = Variable.objects.filter(project=context["selected_project"])
        return context

    @staticmethod
    def create_variable(request, project_id):
        """
        新建变量
        :param request: HTTP请求
        :param project_id: 当前项目ID
        :return: 新建变量页面
        """
        project = get_object_or_404(Project, pk=int(project_id))
        its = get_its(project)
        user_table = User.objects.all()[1:]
        context = {"selected_project": project, "user_table": user_table, "its": its,
                   "project_table": Project.objects.all()}
        return render(request, "new_variable.html", context)

    @staticmethod
    def variable_detail(request, project_id, var_id):
        """
        变量详情
        :param request: HTTP请求
        :param project_id: 当前项目ID
        :param var_id: 当前变量ID
        :return: 变量详情页面
        """
        project_id = int(project_id)
        project = get_object_or_404(Project, pk=project_id)

        var_id = int(var_id)
        var = get_object_or_404(Variable, pk=var_id)
        user_table = User.objects.all()[1:]
        its = get_its(project)
        context = dict()
        context["project"] = project
        context["var"] = var
        context["user_table"] = user_table
        context["its"] = its
        context["selected_project"] = project
        context["var_types"] = VAR_TYPE
        context["project_table"] = Project.objects.all()
        return render(request, "variable_detail.html", context)

    @staticmethod
    def save_variable(request, project_id):
        """
        保存新建变量
        :param request: HTTP请求
        :param project_id: 当前项目ID
        :return: 保存结果
        """
        project = get_object_or_404(Project, pk=int(project_id))
        if request.method == "POST":
            # print request.POST
            name = request.POST["variable_name"].strip()
            var_type = request.POST["variable_type"]
            value = request.POST["variable_value"].strip()
            desc = request.POST["variable_desc"]
            creator_name = request.POST['variable_creator']
            user = User.objects.get(username=creator_name)
            creator = Account.objects.get(user=user)
            responsible = Account.objects.get(user=user)

            if var_type == "1":  # 创建host变量
                val_type = "HOST"
            elif var_type == "3":
                val_type = "普通变量"
            elif var_type == "2":
                val_type = "接口返回值"

            if name and len(name) <= 100:
                var = Variable(name=name, value=value, type=val_type, desc=desc, project=project, creator=creator,
                               responsible=responsible)
                var.save()
                if var.type == "接口返回值":
                    # 当变量是“接口返回值”类型时要记录该变量所关联的接口，以及该接口的某一具体参数
                    rep_para_id = int(request.POST["rep_para_id"])
                    rep_para_type = request.POST["rep_para_type"]
                    assoc_it_id = int(request.POST["assoc_it"])
                    it = get_object_or_404(ITStatement, pk=assoc_it_id)
                    if rep_para_type == "body":
                        assoc_type = "6"
                        VariableIT.objects.create(var=var, it=it, assoc_id=rep_para_id, assoc_type=assoc_type)
                    elif rep_para_type == "head":
                        assoc_type = "5"
                        VariableIT.objects.create(var=var, it=it, assoc_id=rep_para_id, assoc_type=assoc_type)
                return redirect("resource_configuration", project_id)

        return redirect("resource_configuration", project.id)

    # 变量详情页更改后保存
    @staticmethod
    def update_variable(request, var_id):
        meta = {"code": 0, "message": "fail"}
        if request.is_ajax() and request.method == "GET":
            var_id = int(var_id)
            var = get_object_or_404(Variable, pk=var_id)
            # 对变量进行修改,点击保存
            update_flag = False
            name = request.GET["name"]
            value = request.GET["value"]
            if name == "variable_name" and value != var.name:
                var.name = value
                update_flag = True
            elif name == "variable_type" and value != var.type:
                if var.type == u"接口返回值":  # 如果之前时接口返回值类型的变量,更改变量类型时要去除变量和接口的关联关系
                    VariableIT.objects.get(var=var).delete()  # 删除var和接口某一响应参数的关联关系
                var.type = value
                update_flag = True
            elif name == "variable_value" and value != var.value:
                if "flag" in request.GET and request.GET["flag"] == "it_return":
                    it_id = int(request.GET["it_id"])
                    it = get_object_or_404(ITStatement, pk=it_id)
                    assoc_id = int(request.GET["assoc_id"])
                    assoc_type = request.GET["assoc_type"]
                    if assoc_type == "body":
                        VariableIT.objects.create(var=var, it=it, assoc_id=assoc_id, assoc_type="6")
                    elif assoc_type == "head":
                        VariableIT.objects.create(var=var, it=it, assoc_id=assoc_id, assoc_type="5")
                var.value = value
                update_flag = True
            elif name == "variable_desc" and value != var.desc:
                var.desc = value
                update_flag = True
            if update_flag and request.user.is_authenticated():
                user = request.user
                var.responsible = Account.objects.get(user=user)
            var.save()
            meta["code"] = 201
            meta["message"] = "变量修改成功"
            meta["responsible"] = request.user.username
            return HttpResponse(json.dumps(meta))
        return HttpResponse(json.dumps(meta))

    @staticmethod
    def delete_variable(request):
        """
        删除变量
        :param request:HTTP请求
        :return:删除结果
        """
        if request.is_ajax() and request.method == "GET":
            var_id = int(request.GET["var_id"])
            if Variable.objects.filter(id=var_id).exists():
                Variable.objects.get(pk=var_id).delete()
                return HttpResponse("success")
            else:
                return HttpResponse("不存在的变量ID: %s" % var_id)


