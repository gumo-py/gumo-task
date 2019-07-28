import json
from logging import getLogger
from injector import inject
from typing import Optional

from google.cloud import tasks
from google.protobuf import timestamp_pb2

from gumo.task.infrastructure.configuration import TaskConfiguration
from gumo.task.domain import GumoTask

logger = getLogger(__name__)


class CloudTasksPayloadFactory:
    DEFAULT_SERVICE_NAME = 'default'

    def __init__(
            self,
            parent: str,
            task: GumoTask,
            gae_service_name: Optional[str] = None,
            gae_version_name: Optional[str] = None,
    ):
        self._parent = parent
        self._task = task
        self._gae_service_name = gae_service_name
        self._gae_version_name = gae_version_name

    def _payload_as_json_bytes(self) -> str:
        return json.dumps(self._task.payload, ensure_ascii=False).encode('utf-8')

    def _schedule_time_as_pb(self) -> timestamp_pb2.Timestamp:
        return timestamp_pb2.Timestamp(
            seconds=int(self._task.schedule_time.timestamp())
        )

    def _build_app_engine_routing(self) -> dict:
        app_engine_routing = {}

        if self._gae_service_name and self._gae_service_name != self.DEFAULT_SERVICE_NAME:
            app_engine_routing['service'] = self._gae_service_name
        if self._gae_service_name is not None:
            app_engine_routing['version'] = self._gae_version_name

        return app_engine_routing

    def build(self) -> dict:
        app_engine_http_request = {
            'http_method': self._task.method,
            'relative_uri': self._task.relative_uri,
            'app_engine_routing': self._build_app_engine_routing()
        }

        if self._task.payload is not None:
            app_engine_http_request['body'] = self._payload_as_json_bytes()
            app_engine_http_request['headers'] = {
                'Content-Type': 'application/json'
            }

        task_dict = {
            'app_engine_http_request': app_engine_http_request,
            'name': f'{self._parent}/tasks/{self._task.key.name()}',
        }

        if self._task.schedule_time is not None:
            task_dict['schedule_time'] = self._schedule_time_as_pb()

        return task_dict


class CloudTasksRepository:
    @inject
    def __init__(
            self,
            task_configuration: TaskConfiguration,
    ):
        self._task_configuration = task_configuration
        self._cloud_tasks_client: tasks.CloudTasksClient = self._task_configuration.client

    def _build_parent_path(self, queue_name: Optional[str] = None) -> str:
        if queue_name is None:
            queue_name = self._task_configuration.default_queue_name

        return self._cloud_tasks_client.queue_path(
            project=self._task_configuration.google_cloud_project.value,
            location=self._task_configuration.cloud_tasks_location.location_id,
            queue=queue_name,
        )

    def enqueue(
            self,
            task: GumoTask,
            queue_name: Optional[str] = None,
            hostname: Optional[str] = None,
    ):
        if self._cloud_tasks_client is None:
            raise RuntimeError(f'CloudTasksClient does not configured.')

        parent = self._build_parent_path(queue_name=queue_name)
        task_dict = CloudTasksPayloadFactory(
            parent=parent,
            task=task,
            gae_service_name=self._task_configuration.gae_service_name,
            gae_version_name=self._task_configuration.suitable_version_name(hostname=hostname),
        ).build()

        logger.debug(f'Create task parent={parent}, task={task_dict}')

        created_task = self._cloud_tasks_client.create_task(
            parent=parent,
            task=task_dict,
        )
        logger.debug(f'Created task = {created_task}')
