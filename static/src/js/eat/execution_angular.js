/**
 * Created by hzdonghao on 2017/2/13.
 */

var app = angular.module('execution', ['ngResource']);


app.factory('TestSuite', ['$resource', function ($resource) {
    return $resource('/projects/:projectId/execution/api/testsuites/:suiteId');
}]);

app.factory('SuiteReport', ['$resource', function ($resource) {
    return $resource('/projects/:projectId/execution/api/testsuites/:suiteId/suitereports/:reportId');
}]);

// 用例执行页面
app.controller('ExecutionList', ['$scope', '$http', '$window', 'TestSuite', function ($scope, $http, $window, TestSuite) {
    var selectedProjectId = $.cookie("selected_project");
    var testSuites = TestSuite.query({projectId: selectedProjectId}, function () {
        $scope.testsuites = testSuites;
        $scope.selectedOption = testSuites[0];
    });
    // 切换用例执行集报告页面
    $scope.suite_report = function () {
        var url = suite_reports_url + $scope.selectedOption.id + "/reports/";
        $window.location.href = url;
    }
}]);
// 新建用例执行集页面
app.controller('NewSuite', ['$scope', '$http', '$window', 'TestSuite', function ($scope, $http, $window, TestSuite) {
    $scope.save_suite = function () {
        var project = angular.element("#selected_pro option:selected").attr("name");
        var name = angular.element("input[name='execution_name']").val();
        var arrayNodes = mytree.getCheckedNodes(true);
        var newArrayNodes = [];
        arrayNodes.forEach(function (node) {
            var a = {};
            a["pId"] = node.pId;
            a["name"] = node.name;
            a["mId"] = node.mId;
            a["key"] = node.key;
            a["level"] = node.level;
            a["parentTId"] = node.parentTId;
            newArrayNodes.push(a);
        });
        var post_data = {"chosenNodes": newArrayNodes};
        // 将选中的用例集（Nodes）发送到服务器，数据库需要复制一份数据
        $http.post(save_suite_url, JSON.stringify(post_data)).then(function successCallback(response) {
            var suite = {"name": name, "project": project, "roots": response.data};
            var selectedProjectId = $.cookie("selected_project");
            var testSuite = new TestSuite(suite);
            // 保存之后跳转到新的页面
            testSuite.$save({projectId: selectedProjectId}).then(function successCallback(response) {
                var url = suite_reports_url + response.id + "/reports/";
                $window.location.href = url;
            });
        });
    };
}]);
// 用例执行报告页面
app.controller('RunExecution', ['$scope', '$window', '$http', 'TestSuite', function ($scope, $window, $http, TestSuite) {
    var selectedProjectId = $.cookie("selected_project");
    var url = $window.location.pathname;
    var array_str = url.split("/");
    // console.log(array_str);
    $scope.selectedOption = TestSuite.get({projectId: selectedProjectId, suiteId: array_str[5]});
    var testSuites = TestSuite.query({projectId: selectedProjectId}, function () {
        $scope.testsuites = testSuites;
    });


    // 切换用例执行集报告页面
    $scope.report = function () {
        var url = suite_reports_url + $scope.selectedOption.id + "/reports/";
        $window.location.href = url;
    };

    $scope.run_suite = function () {
        var post_data = {"suite_id": array_str[5]};
        $http.post(run_reports_url, JSON.stringify(post_data)).then(function successCallback(response) {

        });
    }
}]);


