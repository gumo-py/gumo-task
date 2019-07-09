import dataclasses
import datetime

from typing import Optional

from gumo.core import EntityKey


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

    def _clone(self, **changes):
        """
        :rtype: GumoTask
        """
        return dataclasses.replace(self, **changes)

    def with_queue_name(self, queue_name: str):
        return self._clone(queue_name=queue_name)
