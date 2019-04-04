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
        success: function (data) {
            $('.loading').hide(800);

            result = data.images;
            similar = data.similars;

            result.forEach(function (label) {

                ids = label.ids;
                Object.keys(ids).forEach(function (id) {
                    template = $('#template').children(":first").clone();

                    template.find('img').attr("src", 'https://s3.amazonaws.com/ece1779projecta3bucket/thumbnails/' + id);

                    template.find('a').attr("href", 'image/' + id);

                    $('#results').append(template);

                    if (text !== '$ANY$') {
                        $('#result-text').find('strong').html(String($('#results').children().length));
                    }
                    $('#result-text').show();
                });
            });

            if (result.length < 1 || Object.keys(result[0].ids).length < 1) {

                if (text === '$ANY$') {
                    $('#notice').show();
                }
                else {
                    $('#notice').show();
                    refreshImages('$ANY$');
                }
            }

            similar.splice(similar.indexOf('foo'), 1);

            if (text !== '$ANY$' && similar.length > 0) {
                $('#similar-text').html('You may also like: ');
                $('#similar-text').show();

                similar.forEach(function (s) {
                    $('#similar-text').append('<a style="color:white; border-radius: 5px; padding: 2px 8px; margin-right: 5px; background-color: silver" href="/?text=' + s + '">' + s + '</a>')
                })

            }


        }
    });

};


$('#text').on('change', function () {


    $('#results').html('');
    $('#result-text').hide();
    $('#similar-text').hide();
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


