import json
from logging import getLogger
from injector import inject
from typing import Optional

from google.cloud import tasks_v2beta3
from google.protobuf import timestamp_pb2

from gumo.core import GumoConfiguration
from gumo.task.domain.configuration import TaskConfiguration
from gumo.task.domain import GumoTask

logger = getLogger(__name__)


class CloudTasksPayloadFactory:
    def __init__(
            self,
            parent: str,
            task: GumoTask,
    ):
        self._parent = parent
        self._task = task

    def _payload_as_bytes(self) -> str:
        return json.dumps(self._task.payload, ensure_ascii=False).encode('utf-8')

    def _schedule_time_as_pb(self) -> timestamp_pb2.Timestamp:
        return timestamp_pb2.Timestamp(
            seconds=int(self._task.schedule_time.timestamp())
        )

    def build(self) -> dict:
        app_engine_http_request = {
            'http_method': self._task.method,
            'relative_uri': self._task.relative_uri,
        }

        if self._task.payload is not None:
            app_engine_http_request['body'] = self._task.payload

        if self._task.schedule_time is not None:
            app_engine_http_request['schedule_time'] = self._task.schedule_time

        task_dict = {
            'app_engine_http_request': app_engine_http_request,
            'name': f'{self._parent}/tasks/{self._task.key.name()}',
        }

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
        self._cloud_tasks_client = tasks_v2beta3.CloudTasksClient()

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
        task_dict = CloudTasksPayloadFactory(parent=parent, task=task).build()

        logger.debug(f'Create task parent={parent}, task={task_dict}')

        created_task = self._cloud_tasks_client.create_task(
            parent=parent,
            task=task_dict,
        )
        logger.debug(f'Created task = {created_task}')
