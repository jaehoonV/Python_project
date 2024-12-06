$(document).ready(function () {
    // Highlight drop zone on drag over
    $('#drop-zone').on('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        $(this).addClass('drag-over');
    });

    // Remove highlight on drag leave
    $('#drop-zone').on('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        $(this).removeClass('drag-over');
    });

    // Handle file drop
    $('#drop-zone').on('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        $(this).removeClass('drag-over');

        const files = Array.from(e.originalEvent.dataTransfer.files);
        const fileInput = $('#file-input')[0];
        const newFileList = new DataTransfer();  // 새로운 FileList 객체 생성

        files.forEach((file) => {
            if (file instanceof File) {
                newFileList.items.add(file);
            } else {
                console.warn('Non-file item detected:', file);
            }
        });

        // #file-input의 files 속성 업데이트
        fileInput.files = newFileList.files;
        handleFiles(files);
    });

    // Handle click to open file dialog
    $('#drop-zone').on('click', () => {
        $('#file-input').click();
    });

    // Handle file selection via input
    $('#file-input').on('change', () => {
        const files = $('#file-input')[0].files;
        console.log(files); // files 객체 확인
        if (files && files.length > 0) {
            // 파일이 선택되었으면 handleFiles 호출
            handleFiles(Array.from(files));
        } else {
            console.log('No files selected');
        }
    });

    function handleFiles(files) {
        // Clear and update file list
        $('#file-list').html(""); // Reset file list

        files.forEach((file) => {
            const listItem = $('<li>').text(file.name);
            $('#file-list').append(listItem);
        });
    }

    // CSRF 토큰 가져오기
    function getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }

    // Form 비동기 전송
    $('form').on('submit', function (e) {
        e.preventDefault(); // 기본 동작 막기
        body_loading(true);
        const formData = new FormData();
        // Add files from file input
        const files = $('#file-input')[0].files;
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }
        // Add other form data (like quality)
        const quality = $('#quality').val();
        formData.append('quality', quality);

        let img_optimization_url = $('#image-form').data('url');

        $.ajax({
            url: img_optimization_url,
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            headers: { 
                'X-CSRFToken': getCSRFToken() // CSRF 토큰 추가
            },
            success: function (response) {
                if (response.file_urls) {
                    $('#optimized-image-ul').empty(); // 기존 리스트 비우기
                    response.file_urls.forEach(url => {
                        const imgItem = $('<li class="optimized-image-li">')
                            .append($('<img>').attr('src', url).attr('alt', url));
                            $('#optimized-image-ul').append(imgItem);
                    });
                }
            },
            complete: function(xhr, status){
                body_loading(false);
            },
            error: function (xhr, status, error) {
                alert('An error occurred: ' + error);
            }
        });
    });

});