small_text = false;
page = 0;

$('#text').on('change', function () {

    if (!small_text) {
        $('#title').slideUp();
        $('#title-sm').show();
    }

    $('#results').html('');
    $('#result-text').hide();
    text = $('#text').val();


    if (text !== '') {

        $('.loading').show();

        $.ajax({
            url: "/engine/batch/" + text + '/' + page,
            success: function (result) {
                $('.loading').hide(800);

                result.forEach(function (label) {

                    ids = label.ids;
                    ids.forEach(function (id) {
                        template = $('#template').children(":first").clone();

                        template.find('img').attr("src", 'https://s3.amazonaws.com/ece1779projecta3bucket/thumbnails/' + id);

                        template.find('a').attr("href", 'image/' + id);

                        $('#results').append(template);


                        $('#result-text').find('strong').html(String($('#results').children().length));
                        $('#result-text').show();


                    });


                })

            }
        });
    } else {
        $('#title').slideDown();
        $('#title-sm').hide();
        small_text = false;
    }


});