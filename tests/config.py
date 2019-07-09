import os

from gumo.core import configure as core_configure
from gumo.datastore import configure as datastore_configure
from gumo.task import configure as task_configure

if os.environ.get('GOOGLE_CLOUD_PROJECT') is None:
    os.environ['GOOGLE_CLOUD_PROJECT'] = 'gumo-task'

if os.environ.get('DATASTORE_EMULATOR_HOST_FOR_TEST'):
    os.environ['DATASTORE_EMULATOR_HOST'] = os.environ['DATASTORE_EMULATOR_HOST_FOR_TEST']
elif os.environ.get('DATASTORE_EMULATOR_HOST') is None:
    os.environ['DATASTORE_EMULATOR_HOST'] = '127.0.0.1:8082'

os.environ['_FALLBACK_CLOUD_TASKS_LOCATION'] = 'us-central1'

core_configure()

datastore_configure()

task_configure(
    default_queue_name='gumo-default-queue',
    use_local_task_emulator=True,
)
