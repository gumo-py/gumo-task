from logging import getLogger

from injector import inject
from typing import Optional

from gumo.datastore.infrastructure import DatastoreRepositoryMixin

from gumo.task.application.repository import GumoTaskRepository

from gumo.task.domain import GumoTask
from gumo.task.infrastructure.cloud_tasks import CloudTasksRepository
from gumo.task.infrastructure.mapper import DatastoreGumoTaskMapper

logger = getLogger(__name__)


class GumoTaskRepositoryImpl(GumoTaskRepository, DatastoreRepositoryMixin):
    @inject
    def __init__(
            self,
            cloud_tasks_repository: CloudTasksRepository,
            gumo_task_mapper: DatastoreGumoTaskMapper,
    ):
        super(GumoTaskRepositoryImpl, self).__init__()
        self._task_mapper = gumo_task_mapper
        self._cloud_tasks_repository = cloud_tasks_repository

    def _enqueue_to_cloud_tasks(
            self,
            task: GumoTask,
            queue_name: Optional[str] = None
    ):
        logger.debug(f'Use Cloud Tasks API (task={task}, queue_name={queue_name})')
        self._cloud_tasks_repository.enqueue(task=task, queue_name=queue_name)

    def _enqueue_to_local_emulator(
            self,
            task: GumoTask,
            queue_name: Optional[str] = None
    ):
        logger.debug(f'Use Tasks Local Emulator with Datastore (task={task}, queue_name={queue_name})')
        datastore_key = self.entity_key_mapper.to_datastore_key(entity_key=task.key)
        datastore_entity = self.DatastoreEntity(key=datastore_key)
        datastore_entity.update(self._task_mapper.to_datastore_entity(task))
        self.datastore_client.put(datastore_entity)
