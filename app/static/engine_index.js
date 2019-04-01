small_text = false;
page = 0;

$('#text').on('change', function () {

    if (!small_text) {
        $('#title').slideUp();
        $('#title-sm').show();
    }

    $('#results').html('');


    text = $('#text').val();

    if (text !== '') {

        $('.loading').show();

        $.ajax({
            url: "/engine/batch/" + text + '/' + page,
            success: function (result) {
                $('.loading').hide(1000);

                result.every(function (label) {
                    ids = label.ids;
                    ids.every(function (id) {

                        template = $('#template').children(":first").clone();

                        template.find('img').attr("src", 'https://s3.amazonaws.com/ece1779projecta3bucket/thumbnails/' + id);

                        $('#results').append(template);


                    });


                })

            }
        });
    }


});