/**
 * Created by Administrator on 2018/7/10.
 */

function show_bar(title, sub_title, id, code, field) {
    var dom = document.getElementById(id);
    var myChart = echarts.init(dom);
    var app = {};
    app.title = code;

    var option = {
        backgroundColor: '#121f34',
        title: {
            text: title,
            subtext: sub_title,
            left: 12,
            top: 12,
            textStyle: {
                color: '#e5eefb',
                fontSize: 15,
                fontWeight: 700
            },
            subtextStyle: {
                color: '#94a3b8',
                fontSize: 11
            }
        },
        color: ['#00c805'],
        tooltip: {
            trigger: 'axis',
            backgroundColor: 'rgba(7, 17, 31, 0.92)',
            borderColor: 'rgba(148, 163, 184, 0.22)',
            textStyle: {
                color: '#e5eefb'
            },
            axisPointer: {            // 坐标轴指示器，坐标轴触发有效
                type: 'shadow'        // 默认为直线，可选为：'line' | 'shadow'
            }
        },
        grid: {
            left: '4%',
            right: '4%',
            top: 68,
            bottom: '8%',
            containLabel: true
        },
        xAxis: [
            {
                type: 'category',
                data: [],
                axisLine: {
                    lineStyle: {
                        color: 'rgba(148, 163, 184, 0.35)'
                    }
                },
                axisLabel: {
                    color: '#94a3b8'
                },
                axisTick: {
                    alignWithLabel: true
                }
            }
        ],
        yAxis: [
            {
                type: 'value',
                axisLine: {
                    lineStyle: {
                        color: 'rgba(148, 163, 184, 0.35)'
                    }
                },
                axisLabel: {
                    color: '#94a3b8'
                },
                splitLine: {
                    lineStyle: {
                        color: 'rgba(148, 163, 184, 0.12)'
                    }
                }
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