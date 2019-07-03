import os

from gumo.core import configure as core_configure
from gumo.datastore import configure as datastore_configure
from gumo.task import configure as task_configure

if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') is None:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/path/to/credential.json'

os.environ['_FALLBACK_CLOUD_TASKS_LOCATION'] = 'us-central1'

core_configure(
    google_cloud_project='gumo-task',
    google_cloud_location='asia-northeast1',
)

datastore_configure(
    use_local_emulator=True,
    emulator_host=os.environ.get('DATASTORE_EMULATOR_HOST', 'datastore_emulator:8081'),
    namespace=None,
)

task_configure(
    default_queue_name='gumo-default-queue',
    use_local_task_emulator=True,
)
