import functools
from werkzeug.exceptions import abort

from flask import (
    Blueprint, flash, g, redirect, request, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from app.auth import login_required
from app.aws import move_to_s3, get_db, delete_on_s3

import os
from app import app
from app.aws import move_to_s3

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/register', methods=['POST'])
def register():
    '''
    handle requests to api/register

    params:
    username and password

    return: ok if success, otherwise a error message will be returned with request content type
    '''
    username = request.form['username']
    password = request.form['password']

    table = get_db().Table('Users')
    error = None

   
    if not username:
        error = 'Username is required.'
    elif not password:
        error = 'Password is required.'
    elif '\'' in password or '\"' in password:
        error = 'Password cannot contain quotation marks.'
    elif '\'' in username or '\"' in username:
        error = 'Username cannot contain quotation marks.'
    else:
        response = table.get_item(
            Key={
                'username': username
            }
        )

        if 'Item' in response:
            error = 'User {0} is already registered.'.format(username)

    if error is None:
        table.put_item(
            Item={
                'username': username,
                'password': generate_password_hash(password)
            }
        )

        return 'ok\n'

    return abort(404, error)


##TODO add more image types
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'jp2', 'bmp', 'ppm', 'pgm', 'pbm', 'tiff'])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/upload', methods=['POST'])
def upload():
    '''
    handle requests to api/upload

    params:
    username, password and the file content

    return: ok if success, otherwise a error message will be returned with request content type
    '''
    error = None
    username = request.form['username']
    password = request.form['password']

    table = get_db().Table('Users')

    response = table.get_item(
        Key={
            'username': username
        }
    )

    user = response['Item'] if 'Item' in response else None

    if user is None:
        error = 'User is not valid'
    elif not check_password_hash(user["password"], password):
        error = 'Incorrect password.'

    if error is not None:
        return abort(404, error)

    if 'file' not in request.files:
        error = 'You cannot upload empty file.'
    elif request.files['file'].filename == '':
        error = "Your file name is not valid."
    elif not allowed_file(request.files['file'].filename):
        error = "Your File format is not correct: {}".format(request.files['file'].filename)
    elif '\'' in request.files['file'].filename or '\"' in request.files['file'].filename:
        error = "Invalid file name."
    else:
        file = request.files['file']
        filename = file.filename
        id = datetime.utcnow().strftime("%Y-%m-%d-%H-%M-%S-%f") + user['username'].replace('.', '').replace('/','')
        filename = str(id) + '.' + filename.rsplit('.', 1)[1].lower()

        table = get_db().Table('Images')

        table.put_item(
            Item={
                'imageid': filename,
                'user': user['username']
            }
        )

        move_to_s3(file, filename)

        return 'ok\n'

    return abort(404, error)