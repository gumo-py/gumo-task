from typing import Optional

from gumo.task.domain import GumoTask


class GumoTaskRepository:
    def enqueue(
            self,
            task: GumoTask,
            queue_name: Optional[str] = None
    ):
        raise NotImplementedError()
