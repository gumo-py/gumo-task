import datetime
from injector import inject
from typing import Optional

from logging import getLogger

from gumo.core.injector import injector
from gumo.task.domain import GumoTask

from gumo.task.application.factory import GumoTaskFactory
from gumo.task.application.repository import GumoTaskRepository
from gumo.task.infrastructure import TaskConfiguration

logger = getLogger(__name__)


class CloudTasksEnqueueService:
    @inject
    def __init__(
            self,
            task_configuration: TaskConfiguration,
            gumo_task_factory: GumoTaskFactory,
            gumo_task_repository: GumoTaskRepository,
    ):
        self._task_configuration = task_configuration
        self._gumo_task_factory = gumo_task_factory
        self._gumo_task_repository = gumo_task_repository

    def enqueue(
            self,
            url: str,
            method: str = 'POST',
            payload: Optional[dict] = None,
            schedule_time: Optional[datetime.datetime] = None,
            in_seconds: Optional[int] = None,
            queue_name: Optional[str] = None,
    ) -> GumoTask:
        if queue_name is None:
            task_config = injector.get(TaskConfiguration)  # type: TaskConfiguration
            queue_name = task_config.default_queue_name

        if queue_name is None:
            raise ValueError(f'queue_name is not defined.')

        task = self._gumo_task_factory.build_for_new(
            relative_uri=url,
            method=method,
            payload=payload,
            schedule_time=schedule_time,
            in_seconds=in_seconds,
            queue_name=queue_name,
        )
        logger.info(f'gumo.task.enqueue called. task = {task}')

        self._gumo_task_repository.enqueue(
            task=task,
            queue_name=queue_name,
        )

        return task


def enqueue(
        url: str,
        method: str = 'POST',
        payload: Optional[dict] = None,
        schedule_time: Optional[datetime.datetime] = None,
        in_seconds: Optional[int] = None,
        queue_name: Optional[str] = None,
) -> GumoTask:
    service = injector.get(CloudTasksEnqueueService)  # type: CloudTasksEnqueueService
    return service.enqueue(
        url=url,
        method=method,
        payload=payload,
        schedule_time=schedule_time,
        in_seconds=in_seconds,
        queue_name=queue_name,
    )
