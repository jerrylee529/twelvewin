/**
 * Created by Administrator on 2018/7/10.
 */

function show_bar(title, sub_title, id, code, field) {
    var dom = document.getElementById(id);
    var myChart = echarts.init(dom);
    var app = {};
    app.title = code;

    var option = {
        title: {
            text: title,
            subtext: sub_title
        },
        color: ['#3398DB'],
        tooltip: {
            trigger: 'axis',
            axisPointer: {            // 坐标轴指示器，坐标轴触发有效
                type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
            }
        },
        grid: {
            left: '3%',
            right: '4%',
            bottom: '3%',
            containLabel: true
        },
        xAxis: [
            {
                type: 'category',
                data: [],
                axisTick: {
                    alignWithLabel: true
                }
            }
        ],
        yAxis: [
            {
                type: 'value'
            }
        ],
        series: [
            {
                name: title,
                type: 'bar',
                barWidth: '60%',
                data: []
            }
        ]
    };

    if (option && typeof option === "object") {
        myChart.setOption(option, true);
    }

    function splitData(rawData) {
        var categoryData = [];
        var values = [];
        for (var i = 0; i < rawData.length; i++) {
            categoryData.push(rawData[i][0]);
            values.push(rawData[i][1])
        }
        return {
            categoryData: categoryData,
            values: values
        };
    }

    // 异步加载数据
    $.get('/bar/' + code + '/' + field).done(function (rawData1) {
        var rawData = splitData(rawData1.rows)

        // 填入数据
        myChart.setOption({
            xAxis: {
                data: rawData.categoryData
            },
            series: [
                {
                    data: rawData.values
                }
            ]
        });
    });
}