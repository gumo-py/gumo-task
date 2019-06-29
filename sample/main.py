import flask
import logging
import sys
import os
import datetime

from gumo.core import configure as core_configure
from gumo.datastore import configure as datastore_configure
from gumo.task import configure as task_configure
from gumo.task import enqueue

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# gcloud tasks queues create [QUEUE_ID]
DEFAULT_QUEUE_NAME = 'gumo-task-test-queue'
DELAYED_QUEUE_NAME = 'gumo-task-delayed-test-queue'

core_configure(
    google_cloud_project=os.environ['GOOGLE_CLOUD_PROJECT'],
    google_cloud_location='us-central1',
)

datastore_configure(
    use_local_emulator=False,
    emulator_host=None,
    namespace=None,
)

task_configure(
    default_queue_name=DEFAULT_QUEUE_NAME,
    use_local_task_emulator=False,
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
        url='/failed-task',
        method='GET',
    )

    text = f"""Task enqueued.
    ----
    task1 = {task1.key.key_literal()}
    task2 = {task2.key.key_literal()}
    task3 = {task3.key.key_literal()}
    ----
    {task1}
    ----
    {task2}
    ----
    {task3}
    """

    return flask.Response(text, content_type='text/plain')


@app.route('/enqueued-task')
def enqueued_task():
    logger.info(f'enqueued-task called.')
    logger.info(f'flask.request.args = {flask.request.args}')

    return 'ok'


@app.route('/delayed-task')
def delayed_task():
    logger.info(f'delayed-task called.')
    logger.info(f'flask.request.args = {flask.request.args}')

    return 'ok'


@app.route('/failed-task')
def failed_task():
    logger.info(f'failed-task called.')
    logger.info(f'flask.request.args = {flask.request.args}')

    return flask.Response('failed', status=500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
