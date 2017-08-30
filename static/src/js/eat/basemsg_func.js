/**
 * Created by hzdonghao on 2017/1/3.
 */
// 新建项目
var opers = ".add-project";
$("div.my-nav").delegate(opers, {
    "click": function () {
        var oper = $(this);
        if (oper.hasClass("add-project")) {
            if (oper.text() == "新建项目") {
                $("#project-modal").modal("toggle");
            }
        }
    }
});

// 需要事件监听的元素（所有动态添加元素的）
var elems = ".add-step, select, input[name='selected_it'], table#tc_step i[type='icon'], #case_debug, .case-log";

$("div.main").delegate(elems, {
    "click": function () {
        var elem = $(this);
        if (elem.hasClass("add-step")) {
            // 插入按钮
            if (elem.attr("value") == "插入") {
                $("#my-modal").modal("toggle");
                $.ajax({
                    url: inside_add_step_url,
                    type: "GET",
                    data: {"index": elem.attr("name")}
                });
            }
            // 底部长按钮添加步骤
            if (elem.text() == "添加步骤") {
                $("#my-modal").modal("toggle");
                $.ajax({
                    url: inside_add_step_url,
                    type: "GET",
                    data: {"index": "last"}
                });
            }
        }
        // 基本信息添加步骤 选择接口
        if (elem.attr("name") == "selected_it") {
            var selectedIt = $("input[type='radio'][name='selected_it']:checked").parent().parent();
            var ts_name = selectedIt.find('td:eq(0)').text();
            var ts_req_typ = selectedIt.find('td:eq(1)').text();
            var ts_req_para = selectedIt.find('td:eq(2)').text();
            var ts_exp_val = selectedIt.find('td:eq(3)').text();
            var ts_statue = selectedIt.find('td:eq(4)').text();
            /** 在已选择接口表里填写已选中的接口信息 **/
            $("tr#chose_ts").find('td:eq(0)').text(ts_name);
            $("tr#chose_ts").find('td:eq(1)').text(ts_req_typ);
            $("tr#chose_ts").find('td:eq(2)').text(ts_req_para);
            $("tr#chose_ts").find('td:eq(3)').text(ts_exp_val);
            $("tr#chose_ts").find('td:eq(4)').text(ts_statue);
        }
        // 用例表中的操作按钮事件响应
        if ($(this).attr("type") == "icon") {
            var btn = $(this);
            switch (btn.attr("value")) {
                case "删除":
                    var conf = confirm("确认删除吗？");
                    if (conf == true) {
                        $.ajax({
                            url: delete_step_url + $.cookie("tc_id"),
                            type: "GET",
                            data: {"index": btn.attr('name')},
                            success: function (data) {
                                if (data != "fail") {
                                    // 刷新用例展示表格，重新获取数据库最新数据
                                    $("div.main").html(data);
                                }
                            }
                        });
                    }
                    break;
                case "上移":
                    $.ajax({
                        url: up_move_url + $.cookie("tc_id"),
                        type: "GET",
                        data: {"index": btn.attr("name")},
                        success: function (data) {
                            if (data == "first_step") {
                                alert("这是第一个步骤，不能上移！");
                            }
                            else if (data != "fail") {
                                // 刷新用例展示表格，重新获取数据库最新数据
                                $("div.main").html(data);
                            }

                        }
                    });
                    break;
                case "下移":
                    $.ajax({
                        url: down_move_url + $.cookie("tc_id"),
                        type: "GET",
                        data: {"index": btn.attr("name")},
                        success: function (data) {
                            if (data == "last_step") {
                                alert("这是最后一个步骤，不能下移！");
                            }
                            else if (data != "fail") {
                                // 刷新用例展示表格，重新获取数据库最新数据
                                $("div.main").html(data);
                            }
                        }
                    });
                    break;
            }
        }
        // 发送用例调试请求，接受用例调试日志
        if (elem.attr("id") == "case_debug") {
            alert(case_log_url + $.cookie("tc_id"));
            $.ajax({
                url: case_log_url + $.cookie("tc_id"),
                type: "GET",
                dataType: "json",
                success: function (data) {
                    $("div#testCase_log_box").modal("toggle");
                    console.log(data["status"]);
                    $("select#tc_status option").each(function () {
                       if ($(this).text() == data["status"]){
                           $(this).attr("selected", true);
                       } else {
                           $(this).attr("selected", false);
                       }
                    });
                    var log_array = data["case_log"];
                    // 日志显示区域设置为空
                    $("div#testCase_log_box .modal-body").html("");
                    for (var i = 0; i < log_array.length; i++) {
                        $("div#testCase_log_box .modal-body").append("<div class='font_color' style='color: #000;font-size: 16px;'>" + log_array[i] + "</div>");
                    }
                }
            });
        }
        // 历史日志弹窗
        if (elem.attr("id") == "history_log") {
            $("#history_testCaseLog_box").modal("toggle");
            $.ajax({
                url: case_logs_url + $.cookie("tc_id"),
                type: "GET",
                dataType: "json",
                success: function (data) {
                    $("div#cs_catalog ul").html("");
                    var log_array = data["case_logs"];
                    for (var i = log_array.length - 1; i > 0; i--) {
                        var id = log_array[i]["id"];
                        var value = log_array[i]["name"].substring(0, 19);
                        $("div#cs_catalog ul").append("<li class='case-log' id='" + id + "'>" + "#" + id + "&nbsp&nbsp" + "<a class='case-log' id='" + id + "'>" + value + "</a></li>");

                    }
                }
            })
        }
        // 历史日志弹窗中的日志异步展示
        if (elem.hasClass("case-log")) {
            $.ajax({
                url: case_show_url + elem.attr("id"),
                type: "GET",
                dataType: "json",
                success: function (data) {
                    $("div#cs_log").html("");
                    var log_array = data["logs"];
                    for (var i = 0; i < log_array.length; i++) {
                        $("div#cs_log").append("<div class='font_color' style='color: #000;font-size: 16px;'>" + log_array[i] + "</div>");
                    }
                    var show_id = elem.attr("id");
                    var obj = document.getElementById(show_id);
                    var objs = $(obj);
                    objs.siblings('li').removeClass("bkgd");
                    objs.addClass("bkgd");
                }
            });
        }

    },

    // 负责人和创建人选择框
    "change": function () {
        var url, value;
        // 如果是责任人被修改
        if ($(this).attr("name") == "tc_responsible") {
            url = save_responsible_url + $.cookie("tc_id");
            value = $(this).val();
        }
        // 如果是创建者被修改
        if ($(this).attr("name") == "tc_creator") {
            url = save_creator_url + $.cookie("tc_id");
            value = $(this).val();
        }
        $.ajax({
            url: url,
            type: "GET",
            data: {"name": value}
        });
    }
});
//** 基本信息添加步骤 选择接口提示窗口**//
// function radioBtnSelectConfirm() {
//     var selected_radioBtn = $("input[type='radio'][name='selected_it']:checked").val();
//     if (selected_radioBtn != null) {
//         return true;
//     } else {
//         alert('请选择一个接口!');
//         return false;
//     }
// }