from flask import (
    Blueprint, jsonify, g, redirect, render_template, request, url_for, send_from_directory
)
from werkzeug.exceptions import abort
from app.aws import move_to_s3, get_db
from boto3.dynamodb.conditions import Key, Attr
from app.auth import login_required

bp = Blueprint('engine', __name__)


@bp.route('/')
@login_required
def index():
    return render_template('engine/index.html')


@bp.route('/engine/batch/<string:query>')
def image_batch(query):
    table = get_db().Table('Index')

    response = table.scan(
        FilterExpression=Key('label').eq(query)
    )

    images = response['Items'] if response['Items'] else []

    return jsonify(images)
