$(document).ready(function () {
    stockSearch();

    $(document).on("click",".view_chart",function(){
        monthChartSearch($(this).data('itemnm'), $(this).data('months'));
    })

    function stockSearch(){
        loading($('#stock_table_div1'), true)
        let formData = {
            "type": "S",
        }
        $.ajax({
            url: '/krStockSearch',
            type: "GET",
            data: formData,
            success: function (response) {
                makeDataTable(response);
            },
            error: function (xhr) {
                alert("Error generating chart: " + (xhr.responseJSON?.error || "Unknown error"));
            }
        });
    }

    function monthChartSearch(itemNm, months){
        loading($('#stock_table_div2'), true)
        let today = new Date();   
        const year = today.getFullYear(); // 년
        const month = today.getMonth();   // 월
        const day = today.getDate();      // 일

        let cal_month = new Date(year, month - months, day);
        let beginBasDt = "".concat(cal_month.getFullYear(), lpad(cal_month.getMonth() + 1, 2), lpad(cal_month.getDate(), 2));
        let endBasDt = "".concat(today.getFullYear(), lpad(today.getMonth() + 1, 2), lpad(today.getDate(), 2));
        
        let formData = {
            "type": "M",
            "beginBasDt": beginBasDt,
            "endBasDt": endBasDt,
            "itemNm": itemNm
        }

        $.ajax({
            url: '/krStockSearch',
            type: "GET",
            data: formData,
            success: function (response) {
                makeMonthDataTable(response);
            },
            error: function (xhr) {
                alert("Error generating chart: " + (xhr.responseJSON?.error || "Unknown error"));
            }
        });
    }

    function makeDataTable(data) {
        let items = data.data.response.body.items.item;
        let date = data.date;
        let output = "";

        if(items.length == 0){
            output = "<div class='load_text'>기준일자 " + date + "은 휴장일 입니다.</div>";
        }else{
            output = "<div class='load_text'>기준일자 : " + dateForamt(date) + "</div>"
            + "<table id='stock_table' class='display'><thead><tr>"
            + "<th>종목명</th>"
            + "<th>시장구분</th>"
            + "<th>시가</th>"
            + "<th>고가</th>"
            + "<th>저가</th>"
            + "<th>종가</th>"
            + "<th>대비</th>"
            + "<th>등락률</th>"
            + "<th>거래량</th>"
            + "<th>분석 차트</th>"
            + "</tr></thead>";

            for (let i in items) {
                let item = items[i];

                let itmsNm = item.itmsNm; // 종목명
                let mrktCtg = item.mrktCtg; // 시장구분 (KOSPI/KOSDAQ/KONEX)
                
                if(mrktCtg == 'KONEX') continue; // KONEX 제외

                let mkp = item.mkp; // 시가
                let hipr = item.hipr; // 고가
                let lopr = item.lopr; // 저가
                let clpr = item.clpr; // 종가
                let vs = item.vs; // 전일 대비 등락
                let fltRt = Number(item.fltRt); // 등락률
                let trqu = item.trqu; // 거래량
                let srtnCd = item.srtnCd; // 종목코드

                output += "<tr>"
                    + "<td>" + "<a href='https://finance.naver.com/item/main.naver?code=" + srtnCd +"' target='_blank'>" + itmsNm + "</a>" + "</td>"
                    + "<td>" + mrktCtg + "</td>"
                    + "<td>" + mkp + "</td>"
                    + "<td>" + hipr + "</td>"
                    + "<td>" + lopr + "</td>";

                output += make_color_td(vs, clpr);
                output += make_color_td(vs, vs);
                output += make_color_td(fltRt, fltRt);
                output += "<td>" + trqu + "</td>";
                output += "<td><button class='view_chart' data-months='3' data-itemnm='" + itmsNm +"'>3개월</button>"
                    + "<button class='view_chart' data-months='12' data-itemnm='" + itmsNm +"'>1년</button>"
                    + "<button class='view_chart' data-months='24' data-itemnm='" + itmsNm +"'>2년</button></td>";
                    + "</tr>";
            }
            output += "</table>";
        }

        $('#stock_table_div1').html(output);
        $('#stock_table').DataTable({
            order: [[0, 'asc']],
            pageLength: 25,
            columnDefs: [
                            {targets: 2, render: $.fn.dataTable.render.number(',')},
                            {targets: 3, render: $.fn.dataTable.render.number(',')},
                            {targets: 4, render: $.fn.dataTable.render.number(',')},
                            {targets: 5, render: $.fn.dataTable.render.number(',')},
                            {targets: 6, render: $.fn.dataTable.render.number(',')},
                            {targets: 7, render: function(data, type, row){ 
                                return data >= 0 ? data == 0 ? '⚊ ' + data : '▲ ' + data : '▼ ' + data
                            }, type: 'formatted-num'},
                            {targets: 8, render: $.fn.dataTable.render.number(',')}
                        ]
        });
    }

    function makeMonthDataTable(data){
        let items = data.response.body.items.item;
        let output = "";
        let title = ""; // 종목명
        let beginBasDt = "";
        let endBasDt = "";
        if(items.length > 0){
            title = items[0].itmsNm;
            endBasDt = items[0].basDt;
            beginBasDt = items[items.length - 1].basDt;
        }

        output = "<div class='load_text'>["+ title +"] 기준일자 : " + dateForamt(beginBasDt) + " ~ " + dateForamt(endBasDt) + "</div>"
        + "<table id='stock_month_table' class='display'><thead><tr>"
        + "<th>종목명</th>"
        + "<th>시장구분</th>"
        + "<th>시가</th>"
        + "<th>고가</th>"
        + "<th>저가</th>"
        + "<th>종가</th>"
        + "<th>대비</th>"
        + "<th>등락률</th>"
        + "<th>거래량</th>"
        + "<th>일자</th>"
        + "</tr></thead>";

        for (let i = items.length - 1; i >= 0; i--) {
            let item = items[i];

            let itmsNm = item.itmsNm; // 종목명
            let mrktCtg = item.mrktCtg; // 시장구분 (KOSPI/KOSDAQ/KONEX)
            if(mrktCtg == 'KONEX') continue; // KONEX 제외

            let mkp = Number(item.mkp); // 시가
            let hipr = Number(item.hipr); // 고가
            let lopr = Number(item.lopr); // 저가
            let clpr = Number(item.clpr); // 종가
            let vs = item.vs; // 전일 대비 등락
            let fltRt = Number(item.fltRt); // 등락률
            let trqu = item.trqu; // 거래량
            let basDt = item.basDt; // 기준일자
            let srtnCd = item.srtnCd; // 종목코드

            output += "<tr>"
                + "<td>" + "<a href='https://finance.naver.com/item/main.naver?code=" + srtnCd +"' target='_blank'>" + itmsNm + "</a>" + "</td>"
                + "<td>" + mrktCtg + "</td>"
                + "<td>" + mkp + "</td>"
                + "<td>" + hipr + "</td>"
                + "<td>" + lopr + "</td>";

            output += make_color_td(vs, clpr);
            output += make_color_td(vs, vs);
            output += make_color_td(fltRt, fltRt);
            output += "<td>" + trqu + "</td>"
                + "<td>" + basDt+ "</td>"
                + "</tr>";
        }
        output += "</table>";

        $('#stock_table_div2').html(output);
        $('#stock_month_table').DataTable({
            order: [[9, 'desc']],
            pageLength: 25,
            columnDefs: [
                            {targets: 2, render: $.fn.dataTable.render.number(',')},
                            {targets: 3, render: $.fn.dataTable.render.number(',')},
                            {targets: 4, render: $.fn.dataTable.render.number(',')},
                            {targets: 5, render: $.fn.dataTable.render.number(',')},
                            {targets: 6, render: $.fn.dataTable.render.number(',')},
                            {targets: 7, render: function(data, type, row){ 
                                return data >= 0 ? data == 0 ? '⚊ ' + data : '▲ ' + data : '▼ ' + data
                            }, type: 'formatted-num'},
                            {targets: 8, render: $.fn.dataTable.render.number(',')},
                            {targets: 9, render: function(data, type, row){ 
                                return data.substring(0, 4) + '년' + data.substring(4, 6) + '월' + data.substring(6, 8) + '일'
                            }, type: 'formatted-num'}
                        ]
        });
    }

    function make_color_td(val, num){
        if(val < 0){
            return "<td class='tag_minus_blue'>" + num + "</td>";
        }else if(val > 0){
            return "<td class='tag_plus_red'>" + num + "</td>";
        }else{
            return "<td class='tag_none'>" + num + "</td>";
        }
    }
});