small_text = false;


$('#text').on('input', function () {

    if (!small_text) {
        $('#title').slideUp();
        $('#title-sm').show();
    }


});