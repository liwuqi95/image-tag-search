from flask import (
    Blueprint, jsonify, g, redirect, render_template, request, url_for, send_from_directory
)
from werkzeug.exceptions import abort
from app.aws import move_to_s3, get_db
from boto3.dynamodb.conditions import Key, Attr
from app.auth import login_required
from random import sample

bp = Blueprint('engine', __name__)


@bp.route('/')
@login_required
def index():
    table = get_db().Table('Index')

    return render_template('engine/index.html')


@bp.route('/engine/batch/<string:query>')
def image_batch(query):
    table = get_db().Table('Index')

    if query != '$ANY$':
        aggr_ids = set([])
        for s in query.split():
            resp = table.scan(
                FilterExpression=Key('label').eq(s.lower())
            )
            if 'Items' in resp:
                for item in resp['Items']:
                    keys = set(item['ids'].keys())
                    if len(aggr_ids)== 0:
                        aggr_ids = keys
                    else:
                        aggr_ids = aggr_ids.intersection(keys)
        response = {'Items' : []}
        if len(aggr_ids) != 0:
            response['Items'].append({'ids': {}, 'label' : query.lower()})
        for imageId in aggr_ids:
            response['Items'][0]['ids'][imageId] = True
            
    else:
        table = get_db().Table('Images')
        response = table.scan()

        if response['Items'] is None:
            response['Items'] = []

        data = response['Items'] if len(response['Items']) <= 12 else sample(response['Items'], 12)
        r = {}
        for d in data:
            r[d['imageid']] = True

        response['Items'] = [{'ids': r}]

    images = response['Items'] if response['Items'] else []

    response = table.scan(
        FilterExpression=Attr('label').contains(query.lower())
    )

    similars = response['Items'] if response['Items'] else []

    similars = list(map(lambda x: x['label'], similars))

    return jsonify({'images': images, 'similars': similars})
