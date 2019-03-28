from injector import inject

from typing import Optional

from gumo.core.domain import GumoConfiguration
from gumo.datastore.domain.configuration import DatastoreConfiguration
from gumo.task.domain.configuration import TaskConfiguration
from gumo.task.domain import GumoTask


class GumoTaskRepository:
    @inject
    def __init__(
            self,
            gumo_configuration: GumoConfiguration,
            datastore_configuration: DatastoreConfiguration,
            task_configuration: TaskConfiguration,
    ):
        self._gumo_configuration = gumo_configuration
        self._datastore_configuration = datastore_configuration
        self._task_configuration = task_configuration

    def enqueue(
            self,
            task: GumoTask,
            queue_name: Optional[str] = None
    ):
        if self._task_configuration.use_local_task_emulator:
            self._enqueue_to_local_emulator(task, queue_name)
        else:
            self._enqueue_to_cloud_tasks(task, queue_name)

    def _enqueue_to_local_emulator(
            self,
            task: GumoTask,
            queue_name: Optional[str] = None
    ):
        raise NotImplementedError()

    def _enqueue_to_cloud_tasks(
            self,
            task: GumoTask,
            queue_name: Optional[str] = None
    ):
        raise NotImplementedError()
