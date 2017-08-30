# -*- coding: UTF-8 -*-
from models import *
from account.models import Account
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.contrib import auth
from django.contrib.auth.models import User
from base_message import case_table
import urllib
import urllib2
import hmac
import hashlib
import base64
import json
import time
import urlparse


# 删除项目，ajax
def delete_project(request):
    if request.method == "POST":
        project_id = int(request.body)
        Project.objects.get(pk=project_id).delete()
        return HttpResponse("del_success")


# 目录树中新建的是测试用例时，也要新建相应的TestCase实例
def add_case_node(request):
    if request.session.has_key("project_id"):
        project_id = request.session["project_id"]
        project = get_object_or_404(Project, pk=int(project_id))
        account = Account.objects.get(user=request.user)

        if request.method == "GET":
            print request.GET
            new_node = request.GET
            new_node_parent_id = int(new_node["parent"])
            clicked_node = DirectoryTree.objects.get(pk=int(new_node_parent_id))  # 获取被点击的节点

            # 叶节点，会对应测试用例
            case_node = DirectoryTree(parent=new_node_parent_id, name=new_node["name"], key="0", project=project,
                                      level=clicked_node.level + 1)  # 新建节点保存到数据库, key为0表示用例
            case_node.save()
            new_tc = TestCase(name=new_node["name"], belong=case_node, status="Unexecuted", author=account,
                              responsible=account)  # 对应新建的测试用例也保存到数据库
            new_tc.save()
            print case_node.id, new_tc.id
            return HttpResponse(case_node.id)


# 目录树中新建的是文件夹节点
def add_folder_node(request):
    if request.session.has_key("project_id"):
        project_id = request.session["project_id"]
        project = get_object_or_404(Project, pk=int(project_id))
        print project.id
        if request.method == "GET":
            print request.GET
            new_node = request.GET
            new_node_parent_id = int(new_node["parent"])
            print new_node_parent_id
            if new_node_parent_id == 0:
                folder_node = DirectoryTree(parent=new_node_parent_id, name=new_node["name"], key="1", project=project,
                                            level=0)
            else:
                clicked_node = DirectoryTree.objects.get(pk=int(new_node_parent_id))  # 获取被点击的节点
                # 叶节点，会对应测试用例
                folder_node = DirectoryTree(parent=new_node_parent_id, name=new_node["name"], key="1", project=project,
                                            level=clicked_node.level + 1)  # 新建节点保存到数据库，key为1表示文件夹
            folder_node.save()
            return HttpResponse(folder_node.id)


def remove_all_child(selected_node):
    print selected_node.key
    if selected_node.key == "0":  # 要删除的树节点是用例
        TestCase.objects.filter(belong=selected_node).delete()  # 删除对应的测试用例
        selected_node.delete()  # 删除用例节点
    elif selected_node.key == "1":  # 要删除的树节点是文件夹
        child_nodes = DirectoryTree.objects.filter(parent=selected_node.id)
        if child_nodes:
            for child in child_nodes:
                remove_all_child(child)  # 删除该节点的所有子节点
            selected_node.delete()  # 再删除该节点
        else:
            selected_node.delete()  # 删除文件夹节点


def remove_node(request):
    if request.method == "GET":
        print request.GET
        selected_node_id = request.GET["parent"]
        print selected_node_id
        selected_node = DirectoryTree.objects.get(pk=int(selected_node_id))
        remove_all_child(selected_node)

        return HttpResponse("delete successfully")


# 重命名树节点
def rename_node(request):
    if request.method == "GET":
        print request.GET
        new_name_node = request.GET
        rename_node_id = new_name_node["id"]
        rename_node_name = new_name_node["name"]
        node = DirectoryTree.objects.get(pk=int(rename_node_id))
        node.name = rename_node_name  # 更新节点名称
        node.save()
        print node, "node"
        if node.key == "0":  # 重命名的树节点是用例节点时，也要更新对应用例的名称
            tc = TestCase.objects.get(belong=node)
            tc.name = rename_node_name
            print tc, "case"
            tc.save()
            return HttpResponse("case_rename")
        elif node.key == "1":  # 重命名的树节点是文件夹节点时，只要更新节点名称
            return HttpResponse("folder_rename")
    return HttpResponse("fail")


def add_node(request):
    if request.method == "GET":
        print request.GET
        node = request.GET
        new_node_parent = node["parent"]
        print new_node_parent
        new_node_name = node["name"]
        clicked_node = DirectoryTree.objects.get(pk=int(new_node_parent))  # 获取被点击的节点
        new_node_level = clicked_node.level + 1
        new_node_key = "-"
        new_node_project_id = request.session["project_id"]
        project = get_object_or_404(Project, pk=int(new_node_project_id))
        new_node = DirectoryTree.objects.create(parent=new_node_parent, name=new_node_name, key=new_node_key,
                                                level=new_node_level, project=project)
        new_node.save()
        print new_node.id
        return HttpResponse(new_node.id)


# Login模块的全局变量
ASSOCIATE_DATA = {
    'openid.mode': 'associate',
    'openid.assoc_type': 'HMAC-SHA256',
    'openid.session_type': 'no-encryption',
}
ASSOCIATE_DATA = urllib.urlencode(ASSOCIATE_DATA)
ASSOC = {}  # 存放关联请求返回的数据


class Login:
    """
    EAT平台对接公司openId服务,用户使用内部邮箱登录平台
    """

    def __init__(self):
        pass

    @staticmethod
    def associate():
        """
        用户访问平台前，浏览器首先向openid服务器发起关联请求，然后openid server 返回关联数据
        :return: 关联数据不空是返回True，否则返回False
        """
        ASSOC_RESP = urllib2.urlopen('https://login.netease.com/openid/', ASSOCIATE_DATA)  # 发起关联请求
        for line in ASSOC_RESP.readlines():
            line = line.strip()
            if not line:
                continue
            k, v = line.split(":")
            ASSOC[k] = v
        ASSOC['save_time'] = time.time()
        # print "%s\n" % ASSOC

        return ASSOC

    @staticmethod
    def openid_login(request):
        """重定向到openId的登录界面"""
        # 从session查找assoc_handle、assoc_type、expires_in、mca_key
        # 如果expires_in超时，新发起关联，把新的关联响应数据保存到本地同时保存当前时间
        print 'openid_login', ASSOC
        if "save_time" in request.session:
            print 'save_time_is_not_none', request.session['save_time']
            timedelta = time.time() - request.session['save_time']
            print timedelta
            if timedelta > request.session['expires_in']:  # 关联超时,重新发起关联请求
                print 'second time assoc'
                if Login.associate():
                    request.session["assoc_handle"] = ASSOC["assoc_handle"]
                    request.session["assoc_type"] = ASSOC["assoc_type"]
                    request.session["expires_in"] = ASSOC["expires_in"]
                    request.session["mac_key"] = ASSOC["mac_key"]
                    request.session["save_time"] = ASSOC["save_time"]
        else:
            print 'first time assoc'
            if Login.associate():
                request.session["assoc_handle"] = ASSOC["assoc_handle"]
                request.session["assoc_type"] = ASSOC["assoc_type"]
                request.session["expires_in"] = ASSOC["expires_in"]
                request.session["mac_key"] = ASSOC["mac_key"]
                request.session["save_time"] = ASSOC["save_time"]

        print request.session.get("assoc_handle", None)
        print request.session.get("assoc_type", None)
        print request.session.get("expires_in", None)
        print request.session.get("mac_key", None)
        print request.session.get("save_time", None)

        # 构造重定向URL，发起认证请求
        REDIRECT_DATA = {
            'openid.ns': 'http://specs.openid.net/auth/2.0',  # 固定字符串
            'openid.mode': 'checkid_setup',  # 固定字符串
            'openid.assoc_handle': request.session['assoc_handle'],  # 第一步获取的assoc_handle值
            # 当用户在OpenID Server登录成功后，你希望它跳转回来的地址
            'openid.return_to': 'http://10.240.82.169/home',
            'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',  # 固定字符串
            'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',  # 固定字符串
            # 声明你的身份（站点URL），通常这个URL要能覆盖openid.return_to
            'openid.realm': 'http://10.240.82.169/',
            'openid.ns.sreg': 'http://openid.net/extensions/sreg/1.1',  # 固定字符串
            # fullname为中文，如果您的环境有中文编码困扰，可以不要
            'openid.sreg.required': "nickname,email",
        }
        REDIRECT_DATA = urllib.urlencode(REDIRECT_DATA)
        print 'redirect to openid login page'
        REDIRECT_URL = "https://login.netease.com/openid/?%s" % REDIRECT_DATA  # 重定向URL

        return HttpResponseRedirect(REDIRECT_URL)

    @staticmethod
    def check_authentication(request_para, idp="https://login.netease.com/openid/"):
        """ check_authentication communication
            进行用户验证
        """
        check_auth = {}
        is_valid_map = {
            'false': False,
            'true': True,
        }
        request_para.update({'openid.mode': 'check_authentication'})
        for k, v in request_para.iteritems():
            if type(v) is unicode:
                request_para.update({k: v.encode('utf-8')})
        authentication_data = urllib.urlencode(request_para)
        auth_resp = urllib2.urlopen(idp, authentication_data)
        for line in auth_resp.readlines():
            line = line.strip()
            if not line:
                continue
            k, v = line.split(":", 1)
            check_auth[k] = v

        is_valid = check_auth.get('is_valid', 'false')
        return is_valid_map[is_valid]

    @staticmethod
    def get_user_message(request, OPENID_RESPONSE):
        """获取登录用户的信息"""

        if OPENID_RESPONSE['openid.mode'] != 'id_res':
            # 一定是出错了，成功认证返回的openid.mode一定是id_res
            print u"openid.mode 不是 id_res"
            return False
        print request.session['assoc_handle']
        if OPENID_RESPONSE['openid.assoc_handle'] != request.session['assoc_handle']:
            # 可能consumer没有assoc或者OpenID Server不认可之前的association handle
            print u"assoc_handle不一致，进入 check_authentication流程"
            if not Login.check_authentication(OPENID_RESPONSE, idp="https://login.netease.com/openid/"):
                print u"assoc_handle不一致，check_authentication不成功"
                return False
            else:
                print u"assoc_handle一致，check_authentication成功"
                print u"恭喜您，成功完成OpenID认证"
                print "nickname: %s" % OPENID_RESPONSE.get('openid.sreg.nickname', None)
                print "email: %s" % OPENID_RESPONSE.get('openid.sreg.email', None)
                # print "fullname: %s" % OPENID_RESPONSE.get('openid.sreg.fullname', None)

        print u"OpenID Server返回的签名值: %s" % OPENID_RESPONSE['openid.sig']
        # 构造需要检查签名的内容
        SIGNED_CONTENT = []
        for k in OPENID_RESPONSE['openid.signed'].split(","):
            response_data = OPENID_RESPONSE["openid.%s" % k]
            SIGNED_CONTENT.append(
                "%s:%s\n" % (k, response_data))
        SIGNED_CONTENT = "".join(SIGNED_CONTENT).encode("UTF-8")

        # 使用associate请求获得的mac_key与SIGNED_CONTENT进行assoc_type hash，
        # 检查是否与OpenID Server返回的一致
        print request.session['mac_key']
        mac_key = request.session['mac_key']
        SIGNED_CONTENT_SIG = base64.b64encode(
            hmac.new(base64.b64decode(mac_key), SIGNED_CONTENT, hashlib.sha256).digest())

        print u"Consumer（本地）计算出来的签名值: %s" % SIGNED_CONTENT_SIG

        if SIGNED_CONTENT_SIG != OPENID_RESPONSE['openid.sig']:
            print u"签名错误，认证不成功"
            return False

        print u"恭喜您，成功完成OpenID认证"
        print "nickname: %s" % OPENID_RESPONSE.get('openid.sreg.nickname', None)
        print "email: %s" % OPENID_RESPONSE.get('openid.sreg.email', None)
        # print "fullname: %s" % OPENID_RESPONSE.get('openid.sreg.fullname', None)

        # fullname = OPENID_RESPONSE.get('openid.sreg.fullname', None)
        nickname = OPENID_RESPONSE.get('openid.sreg.nickname', None)
        email = OPENID_RESPONSE.get('openid.sreg.email', None)

        # return {'fullname': fullname, 'nickname': nickname, 'email': email}
        return {'nickname': nickname, 'email': email}


# 主页
# 基本信息展示（用例列表）
class Home(TemplateView):
    template_name = "mybase.html"

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        context["project_table"] = Project.objects.all()
        context["selected_project"] = context["project_table"][0]
        self.request.session["project_id"] = context["selected_project"].id
        return context

    def get(self, request, *args, **kwargs):
        url = self.request.get_full_path()
        print 'home'
        query = urlparse.urlparse(url).query
        OPENID_RESPONSE = dict(
            # 中文编码decode前要encode一下
            [(k, v[0].encode('UTF-8').decode('UTF-8')) for k, v in urlparse.parse_qs(query).items()]
        )
        print 'openid response', OPENID_RESPONSE
        if not OPENID_RESPONSE:
            return redirect("login")
        user_message = Login.get_user_message(request, OPENID_RESPONSE)
        if not user_message:
            print "Verify failed"
            ASSOC = {}
            return redirect("login")
        if user_message['nickname']:
            user = auth.authenticate(username=user_message["nickname"], password="0000")  # 验证用户是否存在
            if user is not None:  # Account用户存在，直接登录
                auth.login(request, user)  # 跳过Account登录界面直接登录
            else:  # 对于新用户的处理，有两种方案。使用时，二者只能选一
                # 方案一（没有白名单）：第一次用邮箱新登录EAT的用户，给其新建一个user用户，验证后再登录EAT
                # new_user = User.objects.create_user(username=user_message["nickname"], email=user_message["email"],
                #                                     password="0000")
                # user = auth.authenticate(username=new_user.username, password="0000")
                # if user is not None:
                #     auth.login(request, user)
                # 方案二（白名单即account中有该用户）不在白名单的用户不能登录，会返回提示页面
                # return redirect("login")
                return HttpResponse(
                    "<html><body><h3>对不起！您没有访问EAT平台的权限.请通知平台管理员给您添加账户。</h3></body></html>")

        return super(Home, self).get(request, *args, **kwargs)

    @staticmethod
    def ajax_tree(request):
        """
        响应加载树的请求
        :param request: HTTP请求
        :return: json格式目录树
        """
        if request.is_ajax() and request.method == "GET":
            if request.session.has_key("project_id"):
                project_id = request.session["project_id"]
                return HttpResponse(json.dumps(Home.generate_simple_data(project_id)), content_type="application/json")
        return HttpResponse("fail", content_type="application/json")

    @staticmethod
    def generate_simple_data(project_id):
        """
        当前项目的所有目录树的内容
        :param project_id: 当前项目ID
        :return: 整个目录树数据
        """
        simple_data = []
        project = Project.objects.get(id=project_id)
        data = DirectoryTree.objects.filter(project=project)
        if data.exists():
            for item in data:
                it = dict()
                # id在显示中会自动编号，这里的无效
                it["id"] = item.id
                it["pId"] = item.parent
                it["name"] = item.name
                # 存储case id值
                it["mId"] = item.id
                it["key"] = item.key
                if item.key == "1":
                    it["isParent"] = "true"
                simple_data.append(it)
        return simple_data

        # ajax方式获取目录树展示数据

        # @staticmethod
        # def ajax_tree(request):
        #     if request.POST:
        #         if request.session.has_key("project_id"):
        #             project_id = request.session["project_id"]
        #             parent_id = request.POST["id"]
        #             return HttpResponse(json.dumps(Home.generate_simple_data(project_id, parent_id)),
        #                                 content_type="application/json")
        #     else:
        #         if request.session.has_key("project_id"):
        #             project_id = request.session["project_id"]
        #             parent_id = 0
        #             return HttpResponse(json.dumps(Home.generate_simple_data(project_id, parent_id)),
        #                                 content_type="application/json")
        # return HttpResponse("目录树加载失败", content_type="application/json")

        # @staticmethod
        # def generate_simple_data(project_id, parent_id):
        #     """
        #     返回当前父节点的所有子节点
        #     :param project_id: 当前项目ID
        #     :param parent_id: 父节点的ID
        #     :return: 所有子节点
        #     """
        #     simple_data = []
        #     project = Project.objects.get(id=project_id)
        #     data = DirectoryTree.objects.filter(project=project, parent=parent_id)
        #     if data.exists():
        #         for item in data:
        #             it = dict()
        #             # id在显示中会自动编号，这里的无效
        #             it["id"] = item.id
        #             it["pId"] = item.parent
        #             it["name"] = item.name
        #             # 存储case id值
        #             it["mId"] = item.id
        #             # it["key"] = item.key
        #             if item.key == "1":
        #                 it["isParent"] = "true"
        #             simple_data.append(it)
        #     return simple_data


# 项目相关处理
class ProjectsView(TemplateView):
    template_name = "mybase.html"

    # 显示当前项目所有信息
    def get_context_data(self, **kwargs):
        context = super(ProjectsView, self).get_context_data(**kwargs)
        context["project_table"] = Project.objects.all()
        context["selected_project"] = Project.objects.get(id=kwargs["project_id"])

        # 存储project_id到session里
        self.request.session["project_id"] = kwargs["project_id"]
        return context

    # 创建项目
    # 创建成功后返回新建项目
    @staticmethod
    def create_project(request):
        if request.method == 'POST':
            name = request.POST['project_name'].strip()
            desc = request.POST['project_desc']
            user = Account.objects.get(user=request.user)
            if name and len(name) <= 100:
                project = Project(name=name, desc=desc, user=user)
                project.save()
                return redirect("current_project", project.id)

        return redirect("current_project", request.session["project_id"])

    @staticmethod
    def click_node(request):
        """
        响应目录树的用例点击，返回数据到用例表格
        :param request: HTTP请求
        :return: 返回用例信息页面
        """
        if request.method == "GET":
            dir_tree_id = request.GET["id"]
            # 叶子节点的id存到session中
            request.session["node_id"] = dir_tree_id
            dir_tree = DirectoryTree.objects.get(id=dir_tree_id)
            test_case = TestCase.objects.filter(belong=dir_tree)  # 找到对应用例
            if test_case.exists():
                # 返回用例数据表到页面，构造合适数据结构
                case_data = case_table(request, test_case[0])
                return render(request, "_basemsg.html", case_data)
            else:
                # 处理文件夹
                case_data = "folder"
                return HttpResponse(case_data)

        # 保存测试用例日志
        return HttpResponse("Click Node Failed")

    @staticmethod
    def new_test_case(request, tree_node):
        """
        新建用例，对应TestCase表
        :param tree_node: 所属目录树的叶子节点
        :param request: HTTP请求
        :return: TestCase对象
        """
        name = tree_node.name
        author = Account.objects.get(user=request.user)
        responsible = author
        status = "Unexecuted"
        test_case = TestCase.objects.create(name=name, belong=tree_node, status=status, author=author,
                                            responsible=responsible)
        test_case.save()
        return test_case
