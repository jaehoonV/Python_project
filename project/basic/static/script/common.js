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