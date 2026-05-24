/**
 * Created by Administrator on 2018/7/3.
 */
function show_chart(code) {
    var dom = document.getElementById("candlestick");
    var myChart = echarts.init(dom);
    var app = {};
    app.title = code;

    function calculateMA(dayCount, data) {
        var result = [];
        for (var i = 0, len = data.length; i < len; i++) {
            if (i < dayCount) {
                result.push('-');
                continue;
            }
            var sum = 0;
            for (var j = 0; j < dayCount; j++) {
                sum += data[i - j][1];
            }
            var avg = sum / dayCount
            result.push(avg.toFixed(2));
        }
        return result;
    }

    var option = {
        backgroundColor: '#121f34',
        legend: {
            data: ['日K'],
            inactiveColor: '#777',
            textStyle: {
                color: '#e5eefb'
            }
        },
        tooltip: {
            trigger: 'axis',
            backgroundColor: 'rgba(7, 17, 31, 0.92)',
            borderColor: 'rgba(148, 163, 184, 0.22)',
            textStyle: {
                color: '#e5eefb'
            },
            axisPointer: {
                animation: false,
                type: 'cross',
                lineStyle: {
                    color: '#94a3b8',
                    width: 2,
                    opacity: 1
                }
            }
        },
        xAxis: {
            type: 'category',
            data: [],
            axisLine: {lineStyle: {color: 'rgba(148, 163, 184, 0.35)'}},
            axisLabel: {color: '#94a3b8'}
        },
        yAxis: {
            scale: true,
            axisLine: {lineStyle: {color: 'rgba(148, 163, 184, 0.35)'}},
            axisLabel: {color: '#94a3b8'},
            splitLine: {
                lineStyle: {
                    color: 'rgba(148, 163, 184, 0.12)'
                }
            }
        },
        grid: {
            bottom: 80
        },
        animation: false,
        series: [
            {
                type: 'candlestick',
                name: '日K',
                data: [],
                itemStyle: {
                    normal: {
                        color: '#FD1050',
                        color0: '#0CF49B',
                        borderColor: '#FD1050',
                        borderColor0: '#0CF49B'
                    }
                }
            },
            {
                name: 'MA5',
                type: 'line',
                data: [],
                smooth: true,
                showSymbol: false,
                lineStyle: {
                    normal: {
                        width: 1
                    }
                }
            },
            {
                name: 'MA10',
                type: 'line',
                data: [],
                smooth: true,
                showSymbol: false,
                lineStyle: {
                    normal: {
                        width: 1
                    }
                }
            },
            {
                name: 'MA20',
                type: 'line',
                data: [],
                smooth: true,
                showSymbol: false,
                lineStyle: {
                    normal: {
                        width: 1
                    }
                }
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
            categoryData.push(rawData[i].splice(0, 1)[0]);
            values.push(rawData[i])
        }
        return {
            categoryData: categoryData,
            values: values
        };
    }

// 异步加载数据
    $.get('/candlestick/' + code + '/hq').done(function (rawData1) {
        var rawData = splitData(rawData1.rows);

        // 填入数据
        myChart.setOption({
            xAxis: {
                data: rawData.categoryData
            },
            dataZoom: [{
                type: 'inside',
                startValue: Math.max(rawData.categoryData.length-100, 0),
                endValue: rawData.categoryData.length
            }, {
                show: true,
                type: 'slider',
                y: '90%',
                startValue: Math.max(rawData.categoryData.length-100, 0),
                endValue: rawData.categoryData.length
            }],
            series: [
                {
                    name: '日K',
                    data: rawData.values
                },
                {
                    name: 'MA5',
                    data: calculateMA(5, rawData.values)
                },
                {
                    name: 'MA10',
                    data: calculateMA(10, rawData.values)
                },
                {
                    name: 'MA20',
                    data: calculateMA(20, rawData.values)
                }
            ]
        });
    });
}
