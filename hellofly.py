from flask import Flask, render_template
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import Summary, make_wsgi_app
import time

app = Flask(__name__)

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
    time.sleep(2)
    return render_template('hello.html', name=name)