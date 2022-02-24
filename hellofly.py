from curses import echo
from flask import Flask, render_template
import sqlalchemy
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import Summary, make_wsgi_app
import time
import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select
import sqlalchemy as db

app = Flask(__name__)

# after attaching the app to the postgres db app,
# fly makes the connection url available in this env var
DB_CONN_STRING = os.environ['DATABASE_URL']

# fly uses "postgres://...", but sqlalchemy wants "postgresql://..."
sqlalchemy_conn_string = DB_CONN_STRING[:8] + 'ql' + DB_CONN_STRING[8:]

engine = create_engine(sqlalchemy_conn_string, echo=True)
connection = engine.connect()
meta = MetaData()

# Create simple users table to verify the connection
users = Table(
   'users', meta, 
   Column('id', Integer, primary_key = True), 
   Column('username', String), 
)
meta.create_all(engine)

# Add prometheus wsgi middleware to route /metrics requests
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

@app.route('/')
@app.route('/<name>')
def hello(name=None):
    return process_hello_request(name=name)

# Decorate function with metric.
@REQUEST_TIME.time()
def process_hello_request(name=None):
    select_query = select([users])
    ResultProxy = connection.execute(select_query)
    ResultSet = ResultProxy.fetchall()
    return render_template('hello.html', name=name, num_users=len(ResultSet))