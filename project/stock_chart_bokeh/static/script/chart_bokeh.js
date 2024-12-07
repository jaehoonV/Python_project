$(document).ready(function () {

    function updateChart() {
        loading('#chart-image-div', true);
        // 선택된 옵션 가져오기
        let formData = {
            ticker: $('#ticker-search').val(),
            period: $('#period').val(),
            show_ma5: $('#show_ma5').is(':checked'),
            show_ma20: $('#show_ma20').is(':checked'),
            show_ma60: $('#show_ma60').is(':checked'),
            show_ma120: $('#show_ma120').is(':checked'),
            show_baseline: $('#show_baseline').is(':checked'),
            show_conversionLine: $('#show_conversionLine').is(':checked'),
            show_bb: $('#show_bb').is(':checked'),
            show_volume: $('#show_volume').is(':checked'),
            show_psar: $('#show_psar').is(':checked')
        };
        let updateChart_url = $('#chart-image-div').data('url');

        // AJAX 요청
        $.ajax({
            url: updateChart_url,
            type: "GET",
            data: formData,
            success: function (response) {
                loading('#chart-image-div', false);
                if (response.bokeh_script && response.bokeh_div) {
                    // 기존 차트 삭제
                    $('#chart-container').empty();
    
                    // Bokeh 차트 삽입
                    $('#chart-image-div').append(response.bokeh_script);
                    $('#chart-image-div').append(response.bokeh_div);
    
                    $('#selected-ticker-name').text($('#ticker-name').val());
                }
            },
            error: function (xhr) {
                alert("Error generating chart: " + (xhr.responseJSON?.error || "Unknown error"));
            }
        });
    }

    // 옵션 변경 시 AJAX 호출
    $('.show_options, #period').on('change', function () {
        updateChart();
    });
    
    // 자동완성 기능
    let currentIndex = -1;
    $('#ticker-search').on('input', function() {
        let query = $(this).val();
        let search_url = $(this).data('url');
        if (query.length > 0) {
            // AJAX 요청 보내기
            $.ajax({
                url: search_url,
                data: {
                    'q': query
                },
                success: function(data) {
                    // 자동완성 목록 표시
                    let results = $('#autocomplete-results');
                    results.empty();
                    if (data.length > 0) {
                        currentIndex = -1;
                        
                        data.forEach(function(ticker) {
                            results.append('<div>' + ticker.symbol + ' - ' + ticker.name + '</div>');
                        });
                        results.show();
                    } else {
                        results.hide();
                    }
                }
            });
        } else {
            $('#autocomplete-results').hide();
        }
    });

    // 키보드 이벤트 처리
    $('#ticker-search').on('keydown', function (e) {
        let results = $('#autocomplete-results div');
        if (results.length > 0) {
            if (e.key === 'ArrowDown') {
                // 아래 방향키
                e.preventDefault(); // 기본 동작 방지
                if (currentIndex < results.length - 1) {
                    currentIndex++;
                    results.removeClass('selected_hover');
                    $(results[currentIndex]).addClass('selected_hover');
                }
            } else if (e.key === 'ArrowUp') {
                // 위 방향키
                e.preventDefault(); // 기본 동작 방지
                if (currentIndex > 0) {
                    currentIndex--;
                    results.removeClass('selected_hover');
                    $(results[currentIndex]).addClass('selected_hover');
                }
            } else if (e.key === 'Enter') {
                // Enter 키
                e.preventDefault();
                if (currentIndex >= 0 && currentIndex < results.length) {
                    let selectedText = $(results[currentIndex]).text();
                    $('#ticker-search').val(selectedText.split(' - ')[0]); // 티커 심볼만 입력
                    $('#ticker-name').val(selectedText.split(' - ')[1]); // 티커 name
                    $('#autocomplete-results').hide(); // 자동완성 목록 숨기기
                    updateChart();
                }
            }
        }
    });

    // 사용자가 선택한 항목을 입력창에 넣기
    $(document).on('click', '#autocomplete-results div', function() {
        let selectedText = $(this).text();
        $('#ticker-search').val(selectedText.split(' - ')[0]);  // 티커 심볼만 넣기
        $('#ticker-name').val(selectedText.split(' - ')[1]);  // 티커 name
        $('#autocomplete-results').hide();
    });

    // 입력창에서 벗어나면 자동완성 목록 숨기기
    $(document).on('click', function(e) {
        if (!$(e.target).closest('#ticker-search').length) {
            $('#autocomplete-results').hide();
        }
    });

    // 초기 차트 생성
    updateChart();

});