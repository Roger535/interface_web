/**
 * Created by Administrator on 2017/2/13.
 */

function setChart1(dataList) {
    if (dataList == "None") {
        dataList = [{value: 200, name: 'Passed'}, {value: 20, name: 'Skipped'}, {value: 30, name: 'Failed'}]
    }
    var myChart1 = echarts.init(document.getElementById('result'));
    var option1 = {
        title : {
            text: '结果占比',
            x:'left'
        },
        textStyle:{
            fontSize:16
        },
        tooltip : {
            trigger: 'item',
            formatter: "{a} <br/>{b} : {c} ({d}%)"
        },
        color: ['#28c6b9','#0580b9','#f54d4d'],
        legend: {
            orient: 'vertical',
            left:'60%',
            top:'40%',
            data:['Passed','Skipped','Failed'],
            formatter:function(name){
	        	var oa = option1.series[0].data;
	        	var num = oa[0].value + oa[1].value + oa[2].value ;
	        	for(var i = 0; i < option1.series[0].data.length; i++){
                    if(name==oa[i].name){
                    	return name + '     ' + oa[i].value + '     ' + (oa[i].value/num * 100).toFixed(2) + '%';
                    }
	        	}
	        }
        },
        series : [
            {
                name: '执行结果',
                type: 'pie',
                radius : '75%',
                center: ['35%', '50%'], //饼图的中心（圆心）坐标，数组的第一项是横坐标，第二项是纵坐标。
                data: dataList,
                itemStyle: {
                    emphasis: {  //emphasis 是图形在高亮状态下的样式
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ]
    };
    myChart1.setOption(option1);
}

function setChart2(data) {
    if (data == "None") {
        data["time"] = ['周一','周二','周三','周四','周五','周六','周日'];
        data["Failed"] = [150, 232, 201, 154, 190, 330, 410];
        data["Skipped"] = [320, 332, 301, 334, 390, 330, 320];
        data["Passed"] = [820, 932, 901, 934, 1290, 1330, 1320];
    }
   var myChart2 = echarts.init(document.getElementById('trend'));
    option2 = {
        title: {
            text: '质量趋势图'
        },
        tooltip : {
            trigger: 'axis'
        },
        color: [ '#f54d4d','#0580b9','#28c6b9'],
        legend: {
            data:['Passed','Skipped','Failed']
        },
        toolbox: {
            feature: {
                saveAsImage: {}
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis : [
            {
                type : 'category',
                boundaryGap : false,
                data : data["time"]
            }
        ],
        yAxis : [
            {
                type : 'value'
            }
        ],
        series : [
            {
                name:'Failed',
                type:'line',
                stack: '总量',
                areaStyle: {normal: {}},
                data:data["Failed"]
            },
            {
                name:'Skipped',
                type:'line',
                stack: '总量',
                areaStyle: {normal: {}},
                data:data["Skipped"]
            },
            {
                name:'Passed',
                type:'line',
                stack: '总量',
                label: {
                    normal: {
                        show: true,
                        position: 'top'
                    }
                },
                areaStyle: {normal: {}},
                data:data["Passed"]
            }
        ]
    };
    myChart2.setOption(option2);
}




