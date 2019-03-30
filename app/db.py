import mysql.connector
import os
import click
from flask import current_app, g
from flask.cli import with_appcontext
from app.aws import clear_s3, get_db, get_db_client
from app import app


def close_db(e=None):
    """Close mysql db connection"""
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():

    tables = get_db_client().list_tables()

    for table in tables['TableNames']:
        print('dropping ' + table)
        get_db_client().delete_table(TableName=table)
        waiter = get_db_client().get_waiter('table_not_exists')
        waiter.wait(TableName=table)

    print('creating tables')

    get_db().create_table(
        TableName='Users',
        KeySchema=[
            {
                'AttributeName': 'username',
                'KeyType': 'HASH'  # Partition key
            },

        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'username',
                'AttributeType': 'S'
            }

        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )

    get_db().create_table(
        TableName='Images',
        KeySchema=[
            {
                'AttributeName': 'id',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'user',
                'KeyType': 'RANGE'  # Partition key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'user',
                'AttributeType': 'S'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )

    print('clearing s3')
    clear_s3()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
