import dataclasses
import datetime
from typing import Dict
from typing import Optional

from gumo.task.application import enqueue
from injector import inject

from gumo.task.domain import GumoTask


class Task:
    @classmethod
    def from_payload(cls, _payload):
        raise NotImplementedError()

    def payload(self) -> dict:
        raise NotImplementedError()

    def execute(self):
        raise NotImplementedError()


@dataclasses.dataclass(frozen=True)
class TaskQueueName:
    value: str

    def __post_init__(self):
        if not isinstance(self.value, str):
            raise ValueError(
                f"value must be an instance of str, but received {self.value}"
            )

        if not self.value:
            raise ValueError("value must not be empty.")


@dataclasses.dataclass(frozen=True)
class TaskServiceName:
    value: str

    def __post_init__(self):
        if not isinstance(self.value, str):
            raise ValueError(
                f"value must be an instance of str, but received {self.value}"
            )

        if not self.value:
            raise ValueError("value must not be empty.")


@dataclasses.dataclass(frozen=True)
class TaskHandlerURL:
    value: str

    def __post_init__(self):
        if not isinstance(self.value, str):
            raise ValueError(
                f"value must be an instance of str, but received {self.value}"
            )

        if not self.value:
            raise ValueError("value must not be empty.")


@dataclasses.dataclass
class TaskSetting:
    default_queue_name: TaskQueueName
    handler_url: TaskHandlerURL
    target_service: Optional[TaskServiceName] = None

    def __post_init__(self):
        errors = []
        if not isinstance(self.default_queue_name, TaskQueueName):
            errors.append(
                f"default_queue_name must be an instance of TaskQueueName, but received {self.default_queue_name}"
            )
        if not isinstance(self.handler_url, TaskHandlerURL):
            errors.append(
                f"handler_url must be an instance of TaskHandlerURL, but received {self.handler_url}"
            )
        if self.target_service is not None and not isinstance(
            self.target_service, TaskServiceName
        ):
            errors.append(
                f"target_service must be an instance of TaskServiceName or None, but received {self.target_service}"
            )

        if len(errors) > 0:
            raise ValueError(
                f"TaskSetting parameters has some invalid. errors={errors}"
            )


class TaskSettingMap:
    def setting_of(self, task: Task) -> TaskSetting:
        raise NotImplementedError()


class TaskQueue:
    @inject
    def __init__(self, setting_map: TaskSettingMap):
        self._setting_map = setting_map

    def enqueue(
        self,
        task: Task,
        queue_name: Optional[TaskQueueName] = None,
        headers: Optional[Dict[str, str]] = None,
        schedule_time: Optional[datetime.datetime] = None,
        in_seconds: Optional[int] = None,
    ) -> GumoTask:
        if headers is None:
            headers = {}

        setting = self._setting_map.setting_of(task=task)
        url = setting.handler_url.value
        payload = task.payload()

        if not queue_name:
            queue_name = setting.default_queue_name

        headers = self._append_headers(headers=headers)

        gumo_task = enqueue(
            url=url,
            queue_name=queue_name.value,
            headers=headers,
            payload=payload,
            service=setting.target_service.value if setting.target_service else None,
            schedule_time=schedule_time,
            in_seconds=in_seconds,
        )

        return gumo_task

    def _append_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        return headers
