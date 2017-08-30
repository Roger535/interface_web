/* 基本信息页 */
// 保存责任人、创建人修改
var save_creator_url = "/save_creator/";
var save_responsible_url = "/save_responsible/";
// 操作区按钮响应
var inside_add_step_url = "/next_add_step/";
var delete_step_url = "/delete_step/";
var up_move_url = "/up_move/";
var down_move_url = "/down_move/";
var case_log_url = "/case_log/";
var case_logs_url = "/case_logs/";
var case_show_url = "/case/log/";

// 接口管理和资源配置
var it_manage_url = "/projects/" + $.cookie("selected_project") + "/itmanage/";
var res_config_url = "/projects/" + $.cookie("selected_project") + "/resconfig/";

/* 接口管理页 */
var new_it_url = "/projects/" + $.cookie("selected_project") + "/interfaces/";
var del_it_url = "/delete_interface/";
var del_it_para = "/delete_interface_para/";


/* 接口详情页 */
var update_interface_message = "/interfaces/" + $.cookie("it_id") + "/update/";
var update_interface_url = "/interfaces/" + $.cookie("it_id") + "/url_para/";
var update_interface_req_head = "/interfaces/" + $.cookie("it_id") + "/request_head/";
var update_interface_req_body = "/interfaces/" + $.cookie("it_id") + "/request_body/";
var update_interface_rep_head = "/interfaces/" + $.cookie("it_id") + "/response_head/";
var update_interface_rep_body = "/interfaces/" + $.cookie("it_id") + "/response_body/";
var it_log_url = "/interfaces/" + $.cookie("it_id") + "/log/";
var it_logs_url = "/interfaces/" + $.cookie("it_id") + "/logs/";
var it_show_url = "/interfaces/" + $.cookie("it_id") + "/logs/show/";


/* 资源配置页 */
var new_var_url = "/projects/" + $.cookie("selected_project") + "/variables/";
/* 资源变量详情页 */
var update_variable_url = "/variables/" + $.cookie("var_id") + "/update/";
var delete_variable_url = "/variables/delete/";
var getItVar = "/it_rep_var/";  //获取接口所有响应参数

/* 用例执行 */
var save_suite_url = "/projects/" + $.cookie("selected_project") + "/execution/suite/save/";
var suite_reports_url = "/projects/" + $.cookie("selected_project") + "/execution/suites/";
var run_reports_url = "/projects/" + $.cookie("selected_project") + "/execution/suite/run/";
