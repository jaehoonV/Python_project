$(function () {
    window.addEventListener("message", function (event) {
        if (event.origin !== window.location.origin) {
            console.error("Origin mismatch");
            return;
        }

        let data = event.data;
        console.log(data);

        $('#itemNm').val(data.itemNm);
        $('#beginBasDt').val(data.beginBasDt_6);
        $('#endBasDt').val(data.endBasDt);

        searchStockPop();
        
    });

    function searchStockPop(){
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
                $('#check_data').text(JSON.stringify(response, null, 2));
            },
            error: function (xhr) {
                const errorMessage = xhr.responseJSON?.error || "Unknown error";
                alert("Error generating chart: " + errorMessage);
            }
        })
    }

});