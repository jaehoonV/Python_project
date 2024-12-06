function body_loading(b){
    if(b){
        $('body').append('<div class="body-loader"><span><i></i></span></div>');
    }else{
        $('body').find('.body-loader').remove();
    }
}

function loading(el, b){
    $(el).empty();
    if(b){
        $(el).append('<div class="loader"><span><i></i></span></div>');
    }else{
        $(el).find('.loader').remove();
    }
}