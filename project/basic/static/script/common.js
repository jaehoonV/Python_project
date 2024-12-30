/**
 * 화면 로딩
 * @param {boolean} b
 */
function body_loading(b){
    if(b){
        $('body').append('<div class="body-loader"><span><i></i></span></div>');
    }else{
        $('body').find('.body-loader').remove();
    }
}

/**
 * 요소 로딩
 * @param {Element} el
 * @param {boolean} b
 */
function loading(el, b){
    $(el).empty();
    if(b){
        $(el).append('<div class="loader"><span><i></i></span></div>');
    }else{
        $(el).find('.loader').remove();
    }
}

/**
 * 자리수 맞춤 왼쪽 0으로 채움 ex) pad(7, 2) = "07"
 * @param {number} number
 * @param {length} length
 * @return {string} 
 */
function lpad(number, length) {
    var str = '' + number;
    while (str.length < length) {
        str = '0' + str;
    }
    return str;
}

/**
 * 자리수 맞춤 오른쪽 0으로 채움 ex) pad(7, 2) = "70"
 * @param {number} number
 * @param {length} length
 * @return {string} 
 */
function rpad(number, length) {
    var str = '' + number;
    while (str.length < length) {
        str += '0';
    }
    return str;
}

/**
 * 날짜 형식 반환 ex) 19960530 = 1996년 5월 30일
 * @param {string} date
 * @return {string} 
 */
function dateForamt(date) {
    let year = "";
    let month = "";
    let day = "";

    if (typeof date === 'string') {
        let t = String(date);
        year = t.substring(0,4);
        month = Number(t.substring(4,6));
        day = Number(t.substring(6,8));
    } else if (date instanceof Date) {
        let t = new Date(date);
        year = t.getFullYear();
        month = Number(t.getMonth() + 1);
        day = Number(t.getDate());
    } else {
        throw new Error("Invalid date");
    }

    return year + '년 ' + month + '월 ' + day + '일';
}

/**
 * Date type => yyyy년 mm월 dd일
 * @param {Date} date_
 * @return {string} 
 */
function dateForamt2(date_) {
    let new_date = new Date(date_);
    let year = new_date.getFullYear();
    let month = new_date.getMonth() + 1;
    let date = new_date.getDate();

    return year + '년 ' + lpad(month, 2) + '월 ' + lpad(date, 2) + '일';
}

/**
 * 1000 => 1,000
 * @param {Number} n
 * @return {string} 
 */
function addCommas(n) { 
    const option = { maximumFractionDigits: 4};
    return n.toLocaleString('ko-KR', option);
}

/**
 * 데이터 리스트에 날짜 생성
 * @param {list} candle_list
 * @param {list} list
 * @return {list} 
 */
function createDateData(candle_list, list) { 
    let output_list = [];
    
    for(let i = 0; i < candle_list.length; i++){
        output_list.push([candle_list[i][0], list[i]]);
    }
    return output_list;
}

/**
 * 볼린저밴드 리스트에 날짜 생성
 * @param {list} candle_list
 * @param {list} bb_up_list
 * @param {list} bb_down_list
 * @return {list} 
 */
function areaData(candle_list, bb_up_list, bb_down_list) { 
    let output_list = [];
    
    for(let i = 0; i < candle_list.length; i++){
        output_list.push([candle_list[i][0], bb_down_list[i], bb_up_list[i]]);
    }
    return output_list;
}

/**
 * 기준선 생성
 * @param {list} candle_list
 * @param {number} n
 * @return {list} 
 */
function createBaseData(candle_list, n) { 
    let output_list = [];
    
    for(let i = 0; i < candle_list.length; i++){
        output_list.push([candle_list[i][0], n]);
    }
    return output_list;
}