var getUrlParameter = function getUrlParameter(sParam) {
    var sPageURL = window.location.search.substring(1),
        sURLVariables = sPageURL.split('&'),
        sParameterName,
        i;

    for (i = 0; i < sURLVariables.length; i++) {
        sParameterName = sURLVariables[i].split('=');

        if (sParameterName[0] === sParam) {
            return sParameterName[1] === undefined ? true : decodeURIComponent(sParameterName[1]);
        }
    }
};

var small_text = false;

var changeTitle = function () {

    if (!small_text) {
        $('#title').slideUp();
        $('#title-sm').show();
    } else {
        $('#title').slideDown();
        $('#title-sm').hide();
    }
    small_text = !small_text;
};

var refreshImages = function (text) {
    if (!small_text)
        changeTitle();

    $('.loading').show();
    $.ajax({
        url: "/engine/batch/" + text,
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
            });

            if (result.length < 1) {
                $('#notice').show();

                refreshImages('$ANY$');
            }
        }
    });

};


$('#text').on('change', function () {


    $('#results').html('');
    $('#result-text').hide();
    $('#notice').hide();

    var text = $('#text').val();


    if (text !== '') {
        refreshImages(text)
    } else {
        changeTitle();
    }
});

$(document).ready(function () {

    var text = getUrlParameter('text');

    if (text && text !== '') {
        $('#text').val(text);
        refreshImages(text);
    }

    var uri = window.location.toString();
    if (uri.indexOf("?") > 0) {
        var clean_uri = uri.substring(0, uri.indexOf("?"));
        window.history.replaceState({}, document.title, clean_uri);
    }

});


