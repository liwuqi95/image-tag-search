$(document).ready(function () {


    $.ajax({
        url: 'https://s3.amazonaws.com/ece1779projecta3bucket/faceDetails/' + $('#image-box').data("id") + '.json',
        success: function (data) {
            console.log(data);
        }
    });

    $.ajax({
        url: 'https://s3.amazonaws.com/ece1779projecta3bucket/labels/' + $('#image-box').data("id") + '.json',
        success: function (data) {
            console.log(data);
        }
    });


})