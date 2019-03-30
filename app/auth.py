import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from app.aws import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


@bp.before_app_request
def load_logged_in_user():
    """load current user from session"""
    username = session.get('username')

    if username is None:
        g.user = None
    else:
        table = get_db().Table('Users')

        response = table.get_item(
            Key={
                'username': username
            }
        )

        data = {}

        if 'Item' in response:
            item = response['Item']
            data.update(item)

        g.user = data


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Register a new user and validates its username and password"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['password2']
        table = get_db().Table('Users')
        error = None

        if '\'' in password or '\"' in password:
            error = 'Password cannot contain quotation marks.'
        if '\'' in username or '\"' in username:
            error = 'Username cannot contain quotation marks.'
        if not password2 == password:
            error = 'Password is not matching with password confirmation.'
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        else:

            response = table.get_item(
                Key={
                    'username': username
                }
            )

            if 'Item' in response:
                error = 'User {0} is already registered.'.format(username)

        if error is None:
            # the name is available, store it in the database and go to
            # the login page

            table.put_item(
                Item={
                    'username': username,
                    'password': generate_password_hash(password)
                }
            )

            session['username'] = username

            return redirect(url_for('engine.index'))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """handle login request and create a new session for him"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        table = get_db().Table('Users')

        response = table.get_item(
            Key={
                'username': username
            }
        )

        user = response['Item'] if 'Item' in response else None

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user["password"], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['username'] = user["username"]
            return redirect(url_for('engine.index'))

        flash(error)

    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    """clear login session"""
    session.clear()
    return redirect(url_for('engine.index'))
