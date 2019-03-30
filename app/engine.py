from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, send_from_directory
)
from werkzeug.exceptions import abort

from app.auth import login_required

bp = Blueprint('engine', __name__)


@bp.route('/')
@login_required
def index():
    images = []
    return render_template('engine/index.html', images=images)
