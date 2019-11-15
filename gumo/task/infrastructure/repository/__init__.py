import os

from logging import getLogger

from injector import inject
from typing import Optional

from gumo.datastore.infrastructure import DatastoreRepositoryMixin

from gumo.task.application.repository import GumoTaskRepository

from gumo.task.domain import GumoTask
from gumo.task.infrastructure.configuration import TaskConfiguration
from gumo.task.infrastructure.cloud_tasks import CloudTasksRepository
from gumo.task.infrastructure.repository.mapper import DatastoreGumoTaskMapper

logger = getLogger(__name__)


class GumoTaskRepositoryImpl(GumoTaskRepository, DatastoreRepositoryMixin):
    @inject
    def __init__(
            self,
            task_configuration: TaskConfiguration,
            cloud_tasks_repository: CloudTasksRepository,
            gumo_task_mapper: DatastoreGumoTaskMapper,
    ):
        self._task_configuration = task_configuration
        self._task_mapper = gumo_task_mapper
        self._cloud_tasks_repository = cloud_tasks_repository

    def enqueue(
            self,
            task: GumoTask,
            queue_name: Optional[str] = None
    ):
        if queue_name is None:
            queue_name = self._task_configuration.default_queue_name
            task = task.with_queue_name(queue_name=queue_name)
            logger.debug(f'queue_name is not set, fallback to default queue={queue_name}')

        if self._task_configuration.use_local_task_emulator:
            self._enqueue_to_local_emulator(task=task, queue_name=queue_name)
        else:
            self._enqueue_to_cloud_tasks(task=task, queue_name=queue_name)

    def _enqueue_to_cloud_tasks(
            self,
            task: GumoTask,
            queue_name: Optional[str] = None
    ):
        hostname = None
        if self._task_configuration.fetch_request_hostname is not None:
            hostname = self._task_configuration.fetch_request_hostname()
        elif "HTTP_HOST" in os.environ:
            hostname = os.environ["HTTP_HOST"]

        logger.debug(f'Use Cloud Tasks API (task={task}, queue_name={queue_name} with hostname={hostname})')
        self._cloud_tasks_repository.enqueue(
            task=task,
            queue_name=queue_name,
            hostname=hostname,
        )

    def _enqueue_to_local_emulator(
            self,
            task: GumoTask,
            queue_name: Optional[str] = None
    ):
        logger.debug(f'Use Tasks Local Emulator with Datastore (task={task}, queue_name={queue_name})')
        datastore_entity = self._task_mapper.to_datastore_entity(task=task)
        self.datastore_client.put(datastore_entity)
