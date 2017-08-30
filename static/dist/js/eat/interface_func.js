/**
 * Created by yixin.hongjie on 2016/12/30.
 */

$("select.typeChoice").each(function () {
    var $this = $(this);
    var type = $this.find("option:selected").val();
    var $varSelect = $this.parents("tr").children().eq(2).find("select");
    var $input = $this.parents("tr").children().eq(2).find("input");
    if (type == "GlobalVar"){
        $varSelect.removeAttr("disabled");
    }else if(type == "Text"){
        $input.removeAttr("readonly");
    }
});

//当url参数表里有参数时，打开页面该参数默认是显示的
$(function () {
    var urlTable = $("table#url_para tbody tr");
    if(urlTable.length > 1){
        $("div.url-show").show();
    }
});


// 被监听的元素
var it_elems = ".del, .auto-save, .variableChoice, .inputAfterSelect, .typeChoice, #it_debug, #it_history_log, .it-log";
$("div.main").delegate(it_elems, {
    "click": function () {
        var elem = $(this);
        if(elem.hasClass("del")){
            var nameAttr = elem.attr("name");
            switch (nameAttr){
                case "del_it":
                    if (confirm("确认删除吗?")) {
                        var it_id = {"it_id": elem.attr("value")};
                        $.ajax({
                            url: del_it_url,
                            type: "GET",
                            data: it_id,
                            success: function (data) {
                                if(data == "success"){
                                    elem.parent().parent().remove();
                                }
                            }
                        });
                    }
                    break;
                default:
                    if (confirm("确认删除吗?")) {
                        var paraTr = elem.parent().parent();
                        var data = {"delType": elem.attr("name"), "id": paraTr.attr("id")};
                        paraTr.remove();
                        console.log(data);
                        $.ajax({
                            url: del_it_para,
                            type: "GET",
                            data: data,
                            success: function (data) {
                                if(data == "fail"){ alert("删除失败！"); }
                            }
                        });
                    }
            }
        }
        // 发送接口调试请求，接受接口调试日志
        if (elem.attr("id") == "it_debug") {
            $("#it_log_box").modal("toggle");
            $.ajax({
                url: it_log_url,
                type: "GET",
                dataType: "json",
                success: function (data) {
                    // 修改执行状态
                    $("select#status option").each(function () {
                       if ($(this).text() == data["it_status"]){
                           $(this).attr("selected", true);
                       } else {
                           $(this).attr("selected", false);
                       }
                    });
                    // 加载执行日志
                    var log_array = data["it_log"];
                    // 日志显示区域设置为空
                    $("div#it_log_box .modal-body").html("");
                    for (var i = 0; i < log_array.length; i++) {
                        $("div#it_log_box .modal-body").append("<div class='font_color' style='color: #000;font-size: 16px;'>" + log_array[i] + "</div>");
                    }
                }
            });
        }
        //历史日志弹窗
        if (elem.attr("id") == "it_history_log") {
            $("#it_history_log_box").modal("toggle");
            $.ajax({
                url: it_logs_url,
                type: "GET",
                dataType: "json",
                success: function (data) {
                    $("div#it_catalog ul").html("");
                    var log_array = data["it_logs"];
                    for (var i = log_array.length-1; i > 0 ; i--) {
                        var id = log_array[i]["id"];
                        var value = log_array[i]["name"].substring(0, 19);
                        $("div#it_catalog ul").append("<li class='case-log' id='" + id + "'>" + "#" + id + "&nbsp&nbsp" + "<a class='it-log' id='" + id + "'>" + value + "</a></li>");
                    }
                }
            })
        }

        // 历史日志弹窗中的日志异步展示
        if (elem.hasClass("it-log")) {
            $.ajax({
                url: it_show_url + elem.attr("id"),
                type: "GET",
                dataType: "json",
                success: function (data) {
                    $("div#it_logs").html("");
                    var log_array = data["logs"];
                    for (var i = 0; i < log_array.length; i++) {
                        $("div#it_logs").append("<div class='font_color' style='color: #000;font-size: 16px;'>" + log_array[i] + "</div>");
                    }
                    var show_id = elem.attr("id");
                    var obj = document.getElementById(show_id);
                    var objs = $(obj);
                    objs.siblings('li').removeClass("bkgd");
                    objs.addClass("bkgd");
                }
            })
        }
    },
    "change": function () {
        // 实时保存改变过的元素的数据
        var elem = $(this);
        if(elem.hasClass("auto-save")){
            var elemName = elem.attr("name");
            switch (elemName){
                case "urlTr":
                    var urlTr = {
                                    "id":    elem.attr("id"),
                                    "name":  elem.children().eq(0).find('input').val(),
                                    "value": elem.children().eq(1).find('input').val(),
                                    "valueType":  elem.children().eq(1).find('input').attr("data-value-type")
                    };
                    console.log(urlTr);
                    $.ajax({
                        url: update_interface_url,
                        type: "POST",
                        dataType: "json",
                        data: urlTr,
                        success: function (data) {
                            if(data["msg"] == "new_url"){elem.attr("id", data["url_id"])}
                        }
                    });
                    break;
                case "reqHeadTr":
                    var reqHeadTr = {
                                 "id": elem.attr("id"),
                                 "name": elem.children().eq(0).find('input').val(),
                                 "value": elem.children().eq(1).find('input').val(),
                                 "desc": elem.children().eq(2).find('input').val(),
                                 "valueType": elem.children().eq(1).find('input').attr("data-value-type"),
                    };
                    console.log(reqHeadTr);
                    $.ajax({
                        url: update_interface_req_head,
                        type: "POST",
                        dataType: "json",
                        data: reqHeadTr,
                        success: function (data) {
                            if (data["msg"] == "new_reqHead"){ elem.attr("id", data["head_id"]); }
                        }
                    });
                    break;
                case "reqBodyTr":
                    var reqBodyTr = {
                                 "id": elem.attr("id"),
                                 "name": elem.children().eq(0).find('input').val(),
                                 "value": elem.children().eq(2).find('input').val(),
                                 "desc": elem.children().eq(3).find('input').val(),
                                 "valueType": elem.children().eq(1).find('select').val(),
                                 "format": $("input[type='radio'][name='request_data_source']:checked").val()
                    };
                    console.log(reqBodyTr);
                    $.ajax({
                        url: update_interface_req_body,
                        type: "POST",
                        dataType: "json",
                        data: reqBodyTr,
                        success: function (data) {
                            if (data["msg"] == "new_reqBody"){ elem.attr("id", data["body_id"]); }
                        }
                    });
                    break;
                case "repHeadTr":
                    var repHeadTr = {
                                 "id": elem.attr("id"),
                                 "name": elem.children().eq(0).find('input').val(),
                                 "value": elem.children().eq(1).find('input').val(),
                                 "desc": elem.children().eq(2).find('input').val()
                    };
                    console.log(repHeadTr);
                    $.ajax({
                        url: update_interface_rep_head,
                        type: "POST",
                        dataType: "json",
                        data: repHeadTr,
                        success: function (data) {
                            if (data["msg"] == "new_repHead"){ elem.attr("id", data["head_id"]); }
                        }
                    });
                    break;
                case "repBodyTr":
                    var repBodyTr = {
                                 "id": elem.attr("id"),
                                 "name": elem.children().eq(0).find('input').val(),
                                 "value": elem.children().eq(2).find('input').val(),
                                 "desc": elem.children().eq(3).find('input').val(),
                                 "valueType": elem.children().eq(1).find('select').val(),
                                 "format": $("input[type='radio'][name='response_data_source']:checked").val()
                    };
                    console.log(repBodyTr);
                    $.ajax({
                        url: update_interface_rep_body,
                        type: "POST",
                        dataType: "json",
                        data: repBodyTr,
                        success: function (data) {
                            if (data["msg"] == "new_repBody"){ elem.attr("id", data["body_id"]);
                                // add_tr5();
                            }

                        }
                    });
                    break;
                default:
                    var data = {"name": elem.attr("name"), "value": elem.val()};
                    console.log(data);
                    $.ajax({
                        url: update_interface_message,
                        type: "GET",
                        data: data,
                        success: function (data) {}
                    });
            }
        }
        if(elem.hasClass("variableChoice")){
            if(elem.attr("name") == "var_table"){
                var selectedOption = elem.find("option:selected").val()
                var $input = elem.next();
                $input.val(selectedOption);
                // alert($input.attr("data-value-type"));
                $input.attr("data-value-type", "GlobalVar");
            }
        }
        if(elem.hasClass("inputAfterSelect")){
            elem.attr("data-value-type", "text");
        }
        if(elem.hasClass("typeChoice")){
            if(elem.attr("name") == "para_type"){
                var type = elem.find("option:selected").val();
                var $varSelect = elem.parents("tr").children().eq(2).find("select");
                var $input = elem.parents("tr").children().eq(2).find("input");
                if (type == "GlobalVar"){
                    $input.val("");
                    $varSelect.removeAttr("disabled");
                    $input.attr("readonly", "readonly");
                }else if(type == "Text"){
                    $input.val("");
                    $input.removeAttr("readonly");
                    $varSelect.attr("disabled", "disabled");
                }
            }
        }
    },
    "mouseup": function () {
        var elem = $(this);
        // 实时数据展示
        if (elem.attr("id") == "display_request_body") {
            var request_body = "{ \n";
            $("#request_body tbody tr").each(function () {
                if ($(this).children().eq(0).find('input').val() != ""){
                    var row = '"' + $(this).children().eq(0).find('input').val() + '": "' +
                                     $(this).children().eq(2).find('input').val() + '",\n';
                    request_body += row;
                }
            });
            request_body += '}';
            elem.val(request_body);
        }else if(elem.attr("id") == "display_response_body"){
            var response_body="{ \n";
            $("#response_body tbody tr").each(function () {
                if ($(this).children().eq(0).find('input').val() != ""){
                    var row = '"' + $(this).children().eq(0).find('input').val() + '": "' +
                                    $(this).children().eq(2).find('input').val() +'",\n';
                    response_body += row;
                }
            });
            response_body += '}';
            elem.val(response_body);
        }

    }
});


