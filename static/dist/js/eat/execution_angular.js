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
app.controller('RunExecution', ['$scope', '$window', '$http', '$filter', 'TestSuite', 'SuiteReport', function ($scope, $window, $http, $filter, TestSuite, SuiteReport) {
    var selectedProjectId = $.cookie("selected_project");
    var url = $window.location.pathname;
    var array_str = url.split("/");
//    $scope.selectedOption = TestSuite.get({projectId: selectedProjectId, suiteId: array_str[5]});
//    var testSuites = TestSuite.query({projectId: selectedProjectId}, function () {
//        $scope.testsuites = testSuites;
//    });
//    // 切换用例执行集报告页面
//    $scope.report = function () {
//        var url = suite_reports_url + $scope.selectedOption.id + "/reports/";
//        $window.location.href = url;
//    };

    var res = TestSuite.get({projectId: selectedProjectId, suiteId: array_str[5]}, function () {

        $scope.selectedOption = res.name;
        var testSuites = TestSuite.query({projectId: selectedProjectId}, function () {
            $scope.testsuites = testSuites;
        });
    });

    $scope.show_report = function () {
        for (i in $scope.testsuites) {
            if ($scope.testsuites[i].name == $scope.selectedOption) {
                id = $scope.testsuites[i].id
            }
        }
        console.log(res.name);
        var url = suite_reports_url + id + "/reports/";
        $window.location.href = url;
    };

    // 加载执行报告数据
    $scope.chart1_data = [];
    $scope.chart2_data = {"time": [], "Failed": [], 'Skipped': [], 'Passed': []};
    var suite_reports = SuiteReport.query({projectId: selectedProjectId, suiteId: array_str[5]}, function () {
        console.log(suite_reports.length);
        if (suite_reports.length != 0) {
            $scope.report = suite_reports[suite_reports.length - 1];
            $scope.chart1_data = [{name: "Passed", value: $scope.report.passed},
                {name: "Skipped", value: $scope.report.skipped},
                {name: "Failed", value: $scope.report.failed}];
            // 加载第一张表
            setChart1($scope.chart1_data);
            // 加载第二张表
            for (var i = 0; i < suite_reports.length; i++) {
                $scope.chart2_data["time"].push($filter('date')(suite_reports[i].start_time, 'yyyy-MM-dd HH:mm:ss'));
                $scope.chart2_data["Failed"].push(suite_reports[i].failed);
                $scope.chart2_data["Skipped"].push(suite_reports[i].skipped);
                $scope.chart2_data["Passed"].push(suite_reports[i].passed);
            }
            setChart2($scope.chart2_data);
            console.log($scope.chart2_data);
        }

    });

    $scope.run_suite = function () {
        var post_data = {"suite_id": array_str[5]};
        // 点击运行按钮后更新执行报告
        $http.post(run_reports_url, JSON.stringify(post_data)).then(function successCallback(response) {
            var reportId = response.data.reportId;
            console.log("---update chart----");
            var suite_report = SuiteReport.get({
                projectId: selectedProjectId,
                suiteId: array_str[5],
                reportId: reportId
            }, function () {
                $scope.report = suite_report;
                $scope.chart1_data[0].value = suite_report.passed;
                $scope.chart1_data[1].value = suite_report.skipped;
                $scope.chart1_data[2].value = suite_report.failed;
                $scope.chart2_data["time"].push($filter('date')(suite_report.start_time, 'yyyy-MM-dd HH:mm:ss'));
                $scope.chart2_data["Failed"].push(suite_report.failed);
                $scope.chart2_data["Skipped"].push(suite_report.skipped);
                $scope.chart2_data["Passed"].push(suite_report.passed);
                setChart1($scope.chart1_data);
                setChart2($scope.chart2_data);

            });

        });


    }
}]);


