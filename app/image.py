from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory
)
from werkzeug.exceptions import abort

import os
from app.auth import login_required
from app.aws import move_to_s3, get_db
from boto3.dynamodb.conditions import Key, Attr
from app import app
from datetime import datetime

bp = Blueprint('image', __name__)
url_prefix = 'https://s3.amazonaws.com/ece1779a2group123bucket'


def get_url(type, image):
    key = '/' + str(image["id"])
    return url_prefix + key


@bp.route('/images')
@login_required
def index():
    """Show all the images, most recent first."""

    table = get_db().Table('Images')

    response = table.scan(
        FilterExpression=Key('user').eq(g.user['username'])
    )

    images = response['Items'] if response['Items'] else []

    for image in images:
        image['id'] = str(image['id'])
        image['thumb'] = get_url('thumbnails', image)

    return render_template('image/index.html', images=images)


@bp.route('/image/<string:id>')
@login_required
def show(id):
    """Show image details by given id"""
    cursor = get_db().cursor(dictionary=True)

    cursor.execute(
        'SELECT p.id, name, user_id, created'
        ' FROM images p'
        ' WHERE p.id = %s',
        (id,))

    image = cursor.fetchone()

    if image is None:
        abort(404, "Image doesn't exist.".format(id))

    if image['user_id'] != g.user['id']:
        abort(403)

    return render_template('image/show.html', image=image, image_url=get_url('images', image),
                           face_url=get_url('faces', image))


##TODO add more image types
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'jp2', 'bmp', 'ppm', 'pgm', 'pbm', 'tiff'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    """Create a new image for the current user."""
    if request.method == 'POST':
        error = None

        if 'file' not in request.files:
            error = 'You cannot upload empty file.'
        elif request.files['file'].filename == '':
            error = "Your file name is not valid."
        elif not allowed_file(request.files['file'].filename):
            error = "Your File format is not correct."
        elif '\'' in request.files['file'].filename or '\"' in request.files['file'].filename:
            error = "Invalid file name."
        else:

            file = request.files['file']
            filename = file.filename
            id = datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S") + g.user['username'].replace('.', '').replace('/', '')
            filename = str(id) + '.' + filename.rsplit('.', 1)[1].lower()

            table = get_db().Table('Images')

            table.put_item(
                Item={
                    'id': filename,
                    'user': g.user['username']
                }
            )

            move_to_s3(file, filename)

        if error is not None:
            flash(error)

    return render_template('image/create.html')
