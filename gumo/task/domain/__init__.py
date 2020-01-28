import dataclasses
import datetime
import json

from typing import Optional

from gumo.core import EntityKey


@dataclasses.dataclass(frozen=True)
class TaskAppEngineRouting:
    service: Optional[str] = None
    version: Optional[str] = None
    instance: Optional[str] = None


@dataclasses.dataclass(frozen=True)
class GumoTask:
    KIND = 'GumoTask'

    key: EntityKey
    relative_uri: str
    method: str = 'POST'
    payload: Optional[dict] = dataclasses.field(default_factory=dict)
    schedule_time: datetime.datetime = dataclasses.field(default_factory=datetime.datetime.utcnow)
    created_at: datetime.datetime = dataclasses.field(default_factory=datetime.datetime.utcnow)
    queue_name: Optional[str] = None
    app_engine_routing: Optional[TaskAppEngineRouting] = None

    PAYLOAD_MAX_SIZE = 100 * 1024  # 100KB

    def __post_init__(self):
        self._payload_length_check()

    def _payload_length_check(self):
        if not isinstance(self.payload, dict):
            return
        j = json.dumps(self.payload)
        if len(j) > self.PAYLOAD_MAX_SIZE:
            raise ValueError(
                f"Too large payload (actual size={len(j)}bytes, maximum size is 100KB)"
            )

    def _clone(self, **changes) -> "GumoTask":
        return dataclasses.replace(self, **changes)

    def with_queue_name(self, queue_name: str) -> "GumoTask":
        return self._clone(queue_name=queue_name)

    def with_routing(self, routing: TaskAppEngineRouting) -> "GumoTask":
        return self._clone(app_engine_routing=routing)
