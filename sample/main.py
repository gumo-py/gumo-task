import flask
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = flask.Flask(__name__)


@app.route('/')
def hello():
    return f'Hello, world. (gumo-task)'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
