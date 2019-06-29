import dataclasses

from typing import Optional


@dataclasses.dataclass(frozen=True)
class TaskConfiguration:
    default_queue_name: Optional[str] = None
    use_local_task_emulator: bool = False
