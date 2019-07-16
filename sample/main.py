import flask
import logging
import sys
import datetime
import os

from gumo.core import configure as core_configure
from gumo.datastore import configure as datastore_configure
from gumo.task import configure as task_configure
from gumo.task import enqueue

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

if os.environ.get('GOOGLE_CLOUD_PROJECT') is None:
    os.environ['GOOGLE_CLOUD_PROJECT'] = 'gumo-example'

# gcloud tasks queues create [QUEUE_ID]
DEFAULT_QUEUE_NAME = 'gumo-task-test-queue'
DELAYED_QUEUE_NAME = 'gumo-task-delayed-test-queue'

core_configure()

datastore_configure()

task_configure(
    default_queue_name=DEFAULT_QUEUE_NAME,
)

app = flask.Flask(__name__)


@app.route('/')
def hello():
    return f'Hello, world. (gumo-task)'


@app.route('/enqueue')
def enqueue_handler():
    task1 = enqueue(
        url='/enqueued-task',
        method='POST',
        payload={
            'enqueued_at': datetime.datetime.utcnow().isoformat(),
            'args': flask.request.args,
        }
    )

    task2 = enqueue(
        url='/delayed-task',
        method='POST',
        payload={
            'enqueued_at': datetime.datetime.utcnow().isoformat(),
            'args': flask.request.args,
        },
        in_seconds=3600,
        queue_name=DELAYED_QUEUE_NAME
    )

    task3 = enqueue(
        url='/delayed-task',
        method='POST',
        payload={
            'enqueued_at': datetime.datetime.utcnow().isoformat(),
            'args': flask.request.args,
        },
        schedule_time=datetime.datetime.utcnow() + datetime.timedelta(hours=1),
        queue_name=DELAYED_QUEUE_NAME
    )

    task4 = enqueue(
        url='/failed-task',
        method='GET',
    )

    text = f"""Task enqueued.
    ----
    task1 = {task1.key.key_literal()}
    task2 = {task2.key.key_literal()}
    task3 = {task3.key.key_literal()}
    task4 = {task4.key.key_literal()}
    ----
    {task1}
    ----
    {task2}
    ----
    {task3}
    ----
    {task4}
    """

    return flask.Response(text, content_type='text/plain')


@app.route('/enqueued-task', methods=['GET', 'POST'])
def enqueued_task():
    logger.info(f'enqueued-task called.')
    logger.info(f'flask.request.args = {flask.request.args}')
    logger.info(f'flask.request.data = {flask.request.data}')
    logger.info(f'flask.request.json = {flask.request.json}')

    return 'ok'


@app.route('/delayed-task', methods=['GET', 'POST'])
def delayed_task():
    logger.info(f'delayed-task called.')
    logger.info(f'flask.request.args = {flask.request.args}')
    logger.info(f'flask.request.data = {flask.request.data}')
    logger.info(f'flask.request.json = {flask.request.json}')

    return 'ok'


@app.route('/failed-task', methods=['GET', 'POST'])
def failed_task():
    logger.info(f'failed-task called.')
    logger.info(f'flask.request.args = {flask.request.args}')
    logger.info(f'flask.request.data = {flask.request.data}')
    logger.info(f'flask.request.json = {flask.request.json}')

    return flask.Response('failed', status=500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
