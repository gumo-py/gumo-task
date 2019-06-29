import json
import datetime
from logging import getLogger
from injector import inject
from typing import Optional

from google.cloud import tasks
from google.protobuf import timestamp_pb2

from gumo.core import GumoConfiguration
from gumo.task.domain.configuration import TaskConfiguration
from gumo.task.domain import GumoTask

logger = getLogger(__name__)


class CloudTasksPayloadFactory:
    def __init__(
            self,
            task_configuration: TaskConfiguration,
            parent: str,
            task: GumoTask,
    ):
        self._task_configuration = task_configuration
        self._parent = parent
        self._task = task

    def _payload_as_bytes(self) -> str:
        return json.dumps(self._task.payload, ensure_ascii=False).encode('utf-8')

    def _schedule_time_as_pb(self) -> timestamp_pb2.Timestamp:
        unix_timestamp = int((self._task.schedule_time - datetime.datetime(1970, 1, 1)).total_seconds())
        return timestamp_pb2.Timestamp(
            seconds=unix_timestamp
        )

    def build(self) -> dict:
        app_engine_http_request = {
            'http_method': self._task.method,
            'relative_uri': self._task.relative_uri,
        }

        if self._task_configuration.gae_service:
            app_engine_http_request['app_engine_routing'] = {
                'service': self._task_configuration.gae_service,
            }

        if self._task.payload is not None:
            app_engine_http_request['body'] = self._payload_as_bytes()
            if 'headers' not in app_engine_http_request:
                app_engine_http_request['headers'] = {}
            app_engine_http_request['headers']['Content-Type'] = 'application/json'

        task_dict = {
            'app_engine_http_request': app_engine_http_request,
            'name': f'{self._parent}/tasks/{self._task.key.name()}',
        }

        if self._task.schedule_time is not None:
            task_dict['schedule_time'] = self._schedule_time_as_pb()
            import datetime
            logger.info(f'now = {datetime.datetime.utcnow()}, {datetime.datetime.utcnow().timestamp()}')
            logger.info(f'task.schedule_time {self._task.schedule_time}, {self._task.schedule_time.timestamp()}')
            logger.info(f'schedule_time_as_pb {self._schedule_time_as_pb()}')

        return task_dict


class CloudTasksRepository:
    @inject
    def __init__(
            self,
            gumo_configuration: GumoConfiguration,
            task_configuration: TaskConfiguration,
    ):
        self._gumo_configuration = gumo_configuration
        self._task_configuration = task_configuration
        self._cloud_tasks_client = tasks.CloudTasksClient()

    def _build_parent_path(self, queue_name: Optional[str] = None) -> str:
        if queue_name is None:
            queue_name = self._task_configuration.default_queue_name

        return self._cloud_tasks_client.queue_path(
            project=self._gumo_configuration.google_cloud_project.value,
            location=self._gumo_configuration.google_cloud_location.value,
            queue=queue_name,
        )

    def enqueue(
            self,
            task: GumoTask,
            queue_name: Optional[str] = None
    ):
        parent = self._build_parent_path(queue_name=queue_name)
        task_dict = CloudTasksPayloadFactory(
            task_configuration=self._task_configuration,
            parent=parent,
            task=task
        ).build()

        logger.debug(f'Create task parent={parent}, task={task_dict}')

        created_task = self._cloud_tasks_client.create_task(
            parent=parent,
            task=task_dict,
        )
        logger.debug(f'Created task = {created_task}')
