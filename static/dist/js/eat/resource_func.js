/**
 * Created by hzdonghao on 2017/1/11.
 */
// 需要被监听的元素
// 新建变量，自动保存，删除，选择接口后的返回值    
var res_elems = ".new-var, .var-href, .val, .v-save, .var-delete, .it-return, #variable_type";

$("div.main").delegate(res_elems, {
    "click": function () {
        var elem = $(this);
        // 新建变量
        // if (elem.text() == "新建变量") {
        //     $.ajax({
        //         url: new_var_url,
        //         type: "GET",
        //         success: function (data) {
        //              $("div.main").html(data);
        //         }
        //     });
        // }
        // 资源变量的链接跳转
        // if (elem.hasClass("var-href")) {
        //     var url = elem.attr("name");
        //     $.ajax({
        //         url: url,
        //         type: "GET",
        //         success: function (data) {
        //             $("div.main").html(data);
        //         }
        //     });
        // }

        // 接口返回值弹出窗口
        if (elem.hasClass("val")) {
            // 变量详情页面
            var variable_type_res = $("#variable_type").val();
            if (variable_type_res == "接口返回值") {
                $("#modal-interface").modal("toggle");
            }
            // 新建变量页面
            var variable_type_form = $('#variable_type input[name="variable_type"]:checked ').val();
            if (variable_type_form == "2") {
                $("#modal-interface").modal("toggle");
            }
        }
        // 变量删除
        if (elem.hasClass("var-delete")) {
            if (confirm("确认删除吗？")) {
                $.ajax({
                    url: delete_variable_url,
                    type: "GET",
                    data: {"var_id": elem.attr('name')},
                    success: function (data) {
                        if(data == "success"){
                            elem.parent().parent().eq(0).remove();
                        }
                    }
                });

            }
        }
        // 获取选择接口后的返回值
        if (elem.hasClass("it-return")) {
            // console.log("it_return");
            // console.log(elem.attr("name"));
            var selectedIt = $("input[type='radio'][name='test']:checked");
            var selectedPara = $("input[type='radio'][name='return_choice']:checked");//选中的接口响应参数
            //接口响应参数值写到input#variable_value输入框中
            var valueInput = $("input#variable_value");
            var retValue = selectedPara.parents('tr').find('td:eq(0)').text();
            valueInput.val(retValue);
            if (elem.attr("name") == "create_var"){ //创建“接口返回值”变量时
                if(selectedPara.val()){
                    var para = selectedPara.val().split('/');
                    $("input#rep_para_id").val(para[0]);
                    $("input#rep_para_type").val(para[1]);
                    $("input#assoc_it").val(selectedIt.val());
                }
            }else if(elem.attr("name") == "update_var"){ //更新“接口返回值”变量时
                if(selectedPara.val()){
                    var para = selectedPara.val().split('/');
                    var data = {"name": "variable_value", "value": valueInput.val(), "it_id": selectedIt.val(),
                                "assoc_id": para[0], "assoc_type":para[1], "flag": "it_return"};
                    $.ajax({
                        url: update_variable_url,
                        type: "GET",
                        dataType: "json",
                        data: data,
                        success: function (data) {
                            if (data["code"] == "201") {
                                $("#variable_responsible").val(data["responsible"]);
                            }
                        }
                    });
                }

            }


        }
    },
    "change": function () {
        var elem = $(this);
        // 新建变量页和变量详情页：当变量类型改变，值自动清除
        if (elem.attr("id") == "variable_type"){
            $("input#variable_value").val("");
        }
        // 变量详情页自动保存修改
        if (elem.hasClass("v-save")) {
            var data = {"name": elem.attr("name"), "value": elem.val()};
            // alert(data["name"]+"/"+data["value"]);
            $.ajax({
                url: update_variable_url,
                type: "GET",
                dataType: "json",
                data: data,
                success: function (data) {
                    if (data["code"] == "201") {
                        $("#variable_responsible").val(data["responsible"]);
                    }
                }
            });
        }
    }
});

function getInterface() {
    /**新建"接口返回值"变量时，点击‘值’对应的input框时弹出选择接口框，该函数是对应选择接口的js**/
    var choosedTr = $("input[type='radio'][name='test']:checked").parent().parent();
    var tr_name = choosedTr.find('td:eq(0)').text();
    var tr_url = choosedTr.find('td:eq(1)').text();
    var tr_req_typ = choosedTr.find('td:eq(2)').text();
    var tr_req_para = choosedTr.find('td:eq(3)').text();
    var tr_exp_val = choosedTr.find('td:eq(4)').text();
    /** 在已选择接口表里填写已选中的接口信息  **/
    $("tr#chose_tr").find('td:eq(0)').text(tr_name);
    $("tr#chose_tr").find('td:eq(1)').text(tr_url);
    $("tr#chose_tr").find('td:eq(2)').text(tr_req_typ);
    $("tr#chose_tr").find('td:eq(3)').text(tr_req_para);
    $("tr#chose_tr").find('td:eq(4)').text(tr_exp_val);
    /** 显示选择接口的所有响应参数**/
    var selectedIt = $("input[type='radio'][name='test']:checked").val();
    // alert(selectedIt);
    $.ajax({
        url: getItVar,
        type: "GET",
        dataType: "json",
        data: {"it_id": selectedIt},
        success: function (varTable) {
            console.log(varTable);
            var head = varTable["rep_heads"];
            // alert(head);
            var head_html = process_str(head,"head");
            // alert(head_html);
            $('table#it_response_head tbody#it_response_head_tbody').html(head_html);
            var body = varTable["rep_bodies"]
            var body_html = process_str(body, "body");
            $('table#it_response_body tbody#it_response_body_tbody').html(body_html);
        }

    });
}

function process_str(paras, type) {
    var html = "";
    for(var i=0; i<paras.length; i++){
        var p = paras[i];
        if (type == "head"){
            var value = p.id + "/" + type;
            var tr = '<tr>' +
                     '<td>' + p.name + '</td>' +
                     '<td>' + p.value + '</td>' +
                     '<td><input type="radio" name="return_choice" value="'+ value +'"/></td>' +
                     '</tr>';
        }else if(type == "body"){
            var value = p.id + "/" + type;
            var tr = '<tr>' +
                     '<td>' + p.name + '</td>' +
                     '<td>' + p.value + '</td>' +
                     '<td><input type="radio" name="return_choice" value="'+ value +'"/></td>' +
                     '</tr>';
        }

        html += tr;
    }
    return html;
}