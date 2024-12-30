$(function () {
    window.addEventListener("message", function (event) {
        if (event.origin !== window.location.origin) {
            console.error("Origin mismatch");
            return;
        }

        let data = event.data;

        $('#itemNm').val(data.itemNm);
        $('#beginBasDt').val(data.beginBasDt_6);
        $('#endBasDt').val(data.endBasDt);

        searchStockPop();
        
    });

    function searchStockPop(){
        body_loading(true);
        let formData = {
            "beginBasDt": $('#beginBasDt').val(),
            "endBasDt": $('#endBasDt').val(),
            "itemNm": $('#itemNm').val()
        }

        $.ajax({
            url: '/krStockSearchPop',
            type: 'GET',
            data: formData,
            success: function (response) {
                console.log(response);
                let candle_list = [];
                let candle_list_volume = [];
                for(let i = 0; i < response.basDt.length; i++){
                    candle_list.push([response.basDt[i], response.mkp[i], response.hipr[i], response.lopr[i], response.clpr[i]]);
                    candle_list_volume.push([response.basDt[i], response.trqu[i]]);
                }
                createChart($('#itemNm').val(), candle_list, candle_list_volume, response.BB_upper, response.BB_lower, response.MA5, response.MA20, response.MA60, response.MA120, response.Baseline, response.ConversionLine, response.goldenCrossList, response.deadCrossList, response.BCGoldenCross, response.BCDeadCross, response.disparityGoldenCross, response.disparityDeadCross, response.PSAR, response.RSI);
            },
            error: function (xhr) {
                const errorMessage = xhr.responseJSON?.error || "Unknown error";
                alert("Error generating chart: " + errorMessage);
            }
        })
    }

    /* createChart */
    function createChart(title, candle_list, candle_list_volume, bb_up_list, bb_down_list, average_5, average_20, average_60, average_120, baseLine, transitionLine, goldenCross_list, deadCross_list, bt_goldenCross_list, bt_deadCross_list, disparityGoldenCross_list, disparityDeadCross_list, parabolicSAR_list, RSI) {
        const groupingUnits = [[
            'week',                         // unit name
            [1]                             // allowed multiples
        ], [
            'month',
            [1, 2, 3, 4, 6]
        ]];

        // create the chart
        Highcharts.stockChart('chart-candlestick', {
            chart: {
                alignThresholds: true,
                height: 850,
            },
            rangeSelector: {
                selected: 4
            },
            title: {
                text: title
            },
            legend: {
                enabled: true
            },
            yAxis: [{
                labels: {
                    align: 'left',
                    x: 10
                },
                title: {
                    text: 'OHLC'
                },
                opposite: false,
                height: '36%',
                offset: 10,
                lineWidth: 2,
                resize: {
                    enabled: true
                }
            }, {
                labels: {
                    align: 'left',
                    x: 10
                },
                title: {
                    text: 'Volumes'
                },
                opposite: false,
                top: '38%',
                height: '10%',
                offset: 10,
                lineWidth: 2,
                resize: {
                    enabled: true
                }
            }, {
                labels: {
                    align: 'left',
                    x: 10
                },
                title: {
                    text: 'Analysis'
                },
                opposite: false,
                top: '50%',
                height: '32%',
                offset: 10,
                lineWidth: 2
            }, {
                labels: {
                    align: 'left',
                    x: 10
                },
                title: {
                    text: 'RSI'
                },
                opposite: false,
                top: '84%',
                height: '16%',
                offset: 10,
                lineWidth: 2
            }],

            tooltip: {
                style: {
                    fontWeight: 'bold'
                }
            },

            series: [{
                type: 'candlestick',
                name: title,
                data: candle_list,
                showInLegend: false,
                upColor: '#e00400', // 하락 색상
                color: '#003ace', // 상승 색상
                yAxis: 0,
                /* dataGrouping: {
                    units: groupingUnits
                }, */
                tooltip: {
                    pointFormatter: function() {
                        let s = '';
                        if(this.y !== 0){
                            if(this.series.name == title){
                                s += '<span>' + dateForamt2(this.x) + '</span>';
                                s += '<br><span style="color:' + this.color + '"> \u25CF</span> 종가 : ' + addCommas(this.y);
                            }else{

                            }
                        }
                        return s;
                    },
                },
            }, {
                type: 'column',
                name: 'Volume',
                data: candle_list_volume,
                showInLegend: false,
                yAxis: 1,
                /* dataGrouping: {
                    units: groupingUnits
                }, */
                tooltip: {
                    pointFormatter: function() {
                        let s = '';
                        if(this.y !== 0){
                            if(this.series.name == 'Volume'){
                                s += '<span style="color:' + this.color + '"> \u25CF</span> 거래량 : ' + addCommas(this.y);
                            }else{

                            }
                        }
                        return s;
                    },
                },
            }, {
                type: 'line',
                name: 'Line_bb20',
                data: createDateData(candle_list, average_20),
                showInLegend: false,
                yAxis: 0,
                /* dataGrouping: {
                    units: groupingUnits
                }, */
                marker: {
                    width: 2,
                    height: 2,
                    enabled: false,
                    symbol: 'circle',
                    radius: 1,
                    states: {
                        hover: {
                        }
                    }
                },
                color: '#FFE264',
                lineWidth: 0.5,
                tooltip: {
                    pointFormatter: function() {
                        return false;
                    },
                },
            }, {
                type: 'arearange',
                name: 'Line_bb',
                data: areaData(candle_list, bb_up_list, bb_down_list),
                showInLegend: false,
                yAxis: 0,
                /* dataGrouping: {
                    units: groupingUnits
                }, */
                lineWidth: 0,
                color: '#f8ebb180',
                tooltip: {
                    pointFormatter: function() {
                        return false;
                    },
                },
            }, {
                type: 'spline',
                name: '5Days MA',
                data: createDateData(candle_list, average_5),
                yAxis: 2,
                /* dataGrouping: {
                    units: groupingUnits
                }, */
                marker: {
                    width: 2,
                    height: 2,
                    enabled: false,
                    symbol: 'circle',
                    radius: 1,
                    states: {
                        hover: {
                            enabled: false,
                        }
                    }
                },
                color: '#25c930',
                lineWidth: 1,
                tooltip: {
                    pointFormatter: function() {
                        return false;
                    },
                },
            }, {
                type: 'spline',
                name: '20Days MA',
                data: createDateData(candle_list, average_20),
                yAxis: 2,
                /* dataGrouping: {
                    units: groupingUnits
                }, */
                marker: {
                    width: 2,
                    height: 2,
                    enabled: false,
                    symbol: 'circle',
                    radius: 1,
                    states: {
                        hover: {
                            enabled: false,
                        }
                    }
                },
                color: '#c46a6d',
                lineWidth: 1,
                tooltip: {
                    pointFormatter: function() {
                        return false;
                    },
                },
            }, {
                type: 'spline',
                name: '60Days MA',
                data: createDateData(candle_list, average_60),
                yAxis: 2,
                /* dataGrouping: {
                    units: groupingUnits
                }, */
                marker: {
                    width: 2,
                    height: 2,
                    enabled: false,
                    symbol: 'circle',
                    radius: 1,
                    states: {
                        hover: {
                            enabled: false,
                        }
                    }
                },
                color: '#c29569',
                lineWidth: 1,
                tooltip: {
                    pointFormatter: function() {
                        return false;
                    },
                },
            }, {
                type: 'spline',
                name: '120Days MA',
                data: createDateData(candle_list, average_120),
                yAxis: 2,
                /* dataGrouping: {
                    units: groupingUnits
                }, */
                marker: {
                    width: 2,
                    height: 2,
                    enabled: false,
                    symbol: 'circle',
                    radius: 1,
                    states: {
                        hover: {
                            enabled: false,
                        }
                    }
                },
                color: '#C08FFF',
                lineWidth: 1,
                tooltip: {
                    pointFormatter: function() {
                        return false;
                    },
                },
            }, {
                type: 'spline',
                name: 'Base Line',
                data: createDateData(candle_list, baseLine),
                yAxis: 2,
                /* dataGrouping: {
                    units: groupingUnits
                }, */
                marker: {
                    width: 2,
                    height: 2,
                    enabled: false,
                    symbol: 'circle',
                    radius: 1,
                    states: {
                        hover: {
                            enabled: false,
                        }
                    }
                },
                color: '#8E8E8E',
                lineWidth: 1,
                tooltip: {
                    pointFormatter: function() {
                        return false;
                    },
                },
            }, {
                type: 'spline',
                name: 'Transition Line',
                data: createDateData(candle_list, transitionLine),
                yAxis: 2,
                /* dataGrouping: {
                    units: groupingUnits
                }, */
                marker: {
                    width: 2,
                    height: 2,
                    enabled: false,
                    symbol: 'circle',
                    radius: 1,
                    states: {
                        hover: {
                            enabled: false,
                        }
                    }
                },
                color: '#658F89',
                lineWidth: 1,
                tooltip: {
                    pointFormatter: function() {
                        return false;
                    },
                },
            }, {
                type: 'scatter',
                name: 'GoldenCross',
                data: goldenCross_list,
                yAxis: 2,
                /* dataGrouping: {
                    units: groupingUnits
                }, */
                marker: {
                    symbol: 'triangle',
                    fillColor: '#808000',
                    radius: 5,
                },
                color: '#808000',
                tooltip: {
                    pointFormatter: function() {
                        let s = '';
                        if(this.y !== 0){
                            s += '<span style="color:' + this.color + '"> \u25CF</span> GoldenCross : ' + dateForamt2(this.x);
                        }
                        return s;
                    },
                },
                states: {
                    inactive: {
                    opacity: 1
                }
                },
            }, {
                type: 'scatter',
                name: 'BT-GoldenCross',
                data: bt_goldenCross_list,
                yAxis: 2,
                /* dataGrouping: {
                    units: groupingUnits
                }, */
                marker: {
                    symbol: 'triangle',
                    fillColor: '#adad00',
                    radius: 5,
                },
                color: '#adad00',
                tooltip: {
                    pointFormatter: function() {
                        let s = '';
                        if(this.y !== 0){
                            s += '<span style="color:' + this.color + '"> \u25CF</span> BT-GoldenCross : ' + dateForamt2(this.x);
                        }
                        return s;
                    },
                },
                states: {
                    inactive: {
                    opacity: 1
                }
                },
            }, {
                type: 'scatter',
                name: 'DisparityGoldenCross',
                data: disparityGoldenCross_list,
                yAxis: 2,
                /* dataGrouping: {
                    units: groupingUnits
                }, */
                marker: {
                    symbol: 'triangle',
                    fillColor: '#ffff00',
                    radius: 5,
                },
                color: '#ffff00',
                tooltip: {
                    pointFormatter: function() {
                        let s = '';
                        if(this.y !== 0){
                            s += '<span style="color:' + this.color + '"> \u25CF</span> DisparityGoldenCross : ' + dateForamt2(this.x);
                        }
                        return s;
                    },
                },
                states: {
                    inactive: {
                    opacity: 1
                }
                },
            }, {
                type: 'scatter',
                name: 'DeadCross',
                data: deadCross_list,
                yAxis: 2,
                /* dataGrouping: {
                    units: groupingUnits
                }, */
                marker: {
                    symbol: 'triangle-down',
                    fillColor: '#a5a5a5',
                    radius: 5,
                },
                color: '#a5a5a5',
                tooltip: {
                    pointFormatter: function() {
                        let s = '';
                        if(this.y !== 0){
                            s += '<span style="color:' + this.color + '"> \u25CF</span> DeadCross : ' + dateForamt2(this.x);
                        }
                        return s;
                    },
                },
                states: {
                    inactive: {
                    opacity: 1
                }
                },
            }, {
                type: 'scatter',
                name: 'BT-DeadCross',
                data: bt_deadCross_list,
                yAxis: 2,
                /* dataGrouping: {
                    units: groupingUnits
                }, */
                marker: {
                    symbol: 'triangle-down',
                    fillColor: '#585858',
                    radius: 5,
                },
                color: '#585858',
                tooltip: {
                    pointFormatter: function() {
                        let s = '';
                        if(this.y !== 0){
                            s += '<span style="color:' + this.color + '"> \u25CF</span> BT-DeadCross : ' + dateForamt2(this.x);
                        }
                        return s;
                    },
                },
                states: {
                    inactive: {
                    opacity: 1
                }
                },
            }, {
                type: 'scatter',
                name: 'DisparityDeadCross',
                data: disparityDeadCross_list,
                yAxis: 2,
                /* dataGrouping: {
                    units: groupingUnits
                }, */
                marker: {
                    symbol: 'triangle-down',
                    fillColor: '#1d1d1d',
                    radius: 5,
                },
                color: '#1d1d1d',
                tooltip: {
                    pointFormatter: function() {
                        let s = '';
                        if(this.y !== 0){
                            s += '<span style="color:' + this.color + '"> \u25CF</span> DisparityDeadCross : ' + dateForamt2(this.x);
                        }
                        return s;
                    },
                },
                states: {
                    inactive: {
                    opacity: 1
                }
                },
            }, {
                type: 'scatter',
                name: 'ParabolicSAR',
                data: createDateData(candle_list, parabolicSAR_list),
                yAxis: 0,
                /* dataGrouping: {
                    units: groupingUnits
                }, */
                marker: {
                    symbol: 'circle',
                    fillColor: '#ed2969',
                    radius: 2,
                },
                color: '#ed2969',
                tooltip: {
                    pointFormatter: function() {
                        let s = '';
                        if(this.y !== 0){
                            s += '<span style="color:' + this.color + '"> \u25CF</span> ParabolicSAR : ' + dateForamt2(this.x);
                        }
                        return s;
                    },
                },
                states: {
                    inactive: {
                    opacity: 1
                }
                },
            }, {
                type: 'spline',
                name: 'RSI',
                data: createDateData(candle_list, RSI),
                yAxis: 3,
                /* dataGrouping: {
                    units: groupingUnits
                }, */
                marker: {
                    width: 2,
                    height: 2,
                    enabled: false,
                    symbol: 'circle',
                    radius: 1,
                    states: {
                        hover: {
                            enabled: false,
                        }
                    }
                },
                color: '#C08FFF',
                lineWidth: 1,
                tooltip: {
                    pointFormatter: function() {
                        return false;
                    },
                },
            }, {
                type: 'spline',
                name: '',
                data: createBaseData(candle_list, 70),
                yAxis: 3,
                showInLegend: false,
                /* dataGrouping: {
                    units: groupingUnits
                }, */
                marker: {
                    width: 2,
                    height: 2,
                    enabled: false,
                    symbol: 'circle',
                    radius: 1,
                    states: {
                        hover: {
                            enabled: false,
                        }
                    }
                },
                color: 'red',
                lineWidth: 1,
                tooltip: {
                    pointFormatter: function() {
                        return false;
                    },
                },
            }, {
                type: 'spline',
                name: '',
                data: createBaseData(candle_list, 30),
                yAxis: 3,
                showInLegend: false,
                /* dataGrouping: {
                    units: groupingUnits
                }, */
                marker: {
                    width: 2,
                    height: 2,
                    enabled: false,
                    symbol: 'circle',
                    radius: 1,
                    states: {
                        hover: {
                            enabled: false,
                        }
                    }
                },
                color: 'blue',
                lineWidth: 1,
                tooltip: {
                    pointFormatter: function() {
                        return false;
                    },
                },
            },
            ],
            
            plotOptions: {
                candlestick: {
                    // lineColor: 'black', // 캔들스틱의 윤곽선 색상 설정
                    // 상승과 하락 시 색상 설정
                    colors: {
                        upward: '#e00400', // 상승할 때의 색상
                        downward: '#003ace' // 하락할 때의 색상
                    }
                },
                line: {
                    states: {
                    hover: {
                        halo: {
                        size: 1
                        }
                    }
                    },
                },
                spline: {
                    states: {
                    hover: {
                        halo: {
                        size: 1
                        }
                    }
                    },
                }
            },
            credits: {
                enabled: false
            },
        });

        body_loading(false);
    }
    /* createChart */

});