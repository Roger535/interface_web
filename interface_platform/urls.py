# -*- coding: UTF-8 -*-
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from views import *
from base_message import *
from interface_manage import *
from resource_manage import *
from django.contrib import admin
from execution.views import SuiteRun

urlpatterns = [
    url(r"^$", Login.openid_login, name="login"),
    url(r"^home$", Home.as_view(), name="home"),
    url(r"^projects/$", ProjectsView.create_project, name="create_project"),
    url(r"^projects/(?P<project_id>[0-9]{1,11})/$", ProjectsView.as_view(), name="current_project"),
    url(r"^projects/(?P<project_id>[0-9]{1,11})/testcases/(?P<node_id>[0-9]{1,11})/$",
        TestCasesView.as_view(), name="show_testcases"),
    url(r"^projects/(?P<project_id>[0-9]{1,11})/testcases/(?P<testcase_id>[0-9]{1,11})/steps/$",
        TestCasesView.add_step, name="add_step"),
    url(r"^projects/(?P<project_id>[0-9]{1,11})/itmanage/$", InterfacesView.as_view(),
        name="interface_manage"),
    url(r"^projects/(?P<project_id>[0-9]{1,11})/interfaces/$", InterfacesView.create_interface,
        name="create_interface"),
    url(r"^projects/(?P<project_id>[0-9]{1,11})/interfaces/save/$", InterfacesView.save_interface,
        name="save_interface"),
    url(r"^projects/(?P<project_id>[0-9]{1,11})/interfaces/(?P<it_id>[0-9]{1,11})/$",
        InterfacesView.interface_detail, name="interface_detail"),
    url(r"^projects/(?P<project_id>[0-9]{1,11})/resconfig/$", ResourcesView.as_view(),
        name="resource_configuration"),
    url(r"^projects/(?P<project_id>[0-9]{1,11})/variables/$", ResourcesView.create_variable,
        name="create_variable"),
    url(r"^projects/(?P<project_id>[0-9]{1,11})/variables/(?P<var_id>[0-9]{1,11})/$",
        ResourcesView.variable_detail, name="variable_detail"),
    url(r"^projects/(?P<project_id>[0-9]{1,11})/variables/save/$", ResourcesView.save_variable,
        name="save_variable"),

    #####################################
    # ---ajax---
    url(r"^delete_project/$", delete_project, name="delete_project"),
    # ----------
]

urlpatterns += [
    url(r"^admin/", include(admin.site.urls)),
    url(r"^account/", include("account.urls")),

    # AJAX
    url(r"^tree/$", Home.ajax_tree, name="ajax_tree"),
    url(r"^tree/click_node/$", ProjectsView.click_node, name="click_node"),
    url(r"^tree/add_node/$", add_node, name="add_node"),
    url(r"^tree/add_case_node/$", add_case_node, name="add_case_node"),
    url(r"^tree/add_folder_node/$", add_folder_node, name="add_folder_node"),
    url(r"^tree/remove_node/$", remove_node, name="remove_node"),
    url(r"^tree/rename_node/$", rename_node, name="rename_node"),
    # 用例执行的树加载
    url(r"^report/tree/$", SuiteRun.report_tree, name="report_tree"),

    # 基本信息页操作
    url(r"^save_creator/(?P<tc_id>[0-9]{1,11})/$", BaseMessage.save_creator, name="save_creator"),
    url(r"^save_responsible/(?P<tc_id>[0-9]{1,11})/$", BaseMessage.save_responsible, name="save_responsible"),
    url(r"^next_add_step/$", BaseMessage.next_add_step, name="next_add_step"),
    url(r"^delete_step/(?P<tc_id>[0-9]{1,11})/$", BaseMessage.delete_step, name="delete_step"),
    url(r"^up_move/(?P<tc_id>[0-9]{1,11})/$", BaseMessage.up_move, name="up_move"),
    url(r"^down_move/(?P<tc_id>[0-9]{1,11})/$", BaseMessage.down_move, name="down_move"),
    url(r"^case_log/(?P<tc_id>[0-9]{1,11})/$", TestCasesView.case_log, name="case_log"),
    url(r"^case_logs/(?P<tc_id>[0-9]{1,11})/$", TestCasesView.case_logs, name="case_logs"),
    url(r"^case/log/(?P<log_id>[0-9]{1,11})/$", TestCasesView.show_log, name="show_log"),

    # 接口详情页操作
    # 实时自动保存所有改动
    url(r"^interfaces/(?P<it_id>[0-9]{1,11})/update/$", InterfacesView.update_interface, name="update_interface"),
    url(r"^interfaces/(?P<it_id>[0-9]{1,11})/url_para/$", InterfacesView.url_para, name="url_para"),
    url(r"^interfaces/(?P<it_id>[0-9]{1,11})/request_head/$", InterfacesView.request_head, name="request_head"),
    url(r"^interfaces/(?P<it_id>[0-9]{1,11})/request_body/$", InterfacesView.request_body, name="request_body"),
    url(r"^interfaces/(?P<it_id>[0-9]{1,11})/response_head/$", InterfacesView.response_head, name="response_head"),
    url(r"^interfaces/(?P<it_id>[0-9]{1,11})/response_body/$", InterfacesView.response_body, name="response_body"),
    # 删除接口参数:url/head/body
    url(r"delete_interface_para/$", InterfacesView.delete_interface_para, name="delete_interface_para"),
    # 删除接口
    url(r"delete_interface/$", InterfacesView.delete_interface, name="delete_interface"),
    url(r"^interfaces/(?P<it_id>[0-9]{1,11})/log/$", InterfacesView.interface_log, name="interface_log"),
    url(r"^interfaces/(?P<it_id>[0-9]{1,11})/logs/$", InterfacesView.history_logs, name="history_logs"),
    url(r"^interfaces/(?P<it_id>[0-9]{1,11})/logs/show/(?P<log_id>[0-9]{1,11})/$", InterfacesView.show_log,
        name="show_log"),
    url(r"^it_rep_var/$", InterfacesView.response_para, name="response_para"),
    # 资源变量详情页操作
    # 实时自动保存所有改动
    url(r"^variables/(?P<var_id>[0-9]{1,11})/update/$", ResourcesView.update_variable, name="update_variable"),
    url(r"^variables/delete/$", ResourcesView.delete_variable, name="delete_variable"),

    # 用例执行url
    url(r'^projects/(?P<project_id>\d+)/execution/', include('execution.urls')),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
