import dataclasses
import os

from typing import Optional


@dataclasses.dataclass()
class TaskConfiguration:
    default_queue_name: Optional[str] = None
    use_local_task_emulator: bool = False
    gae_service_name: Optional[str] = None

    def __post_init__(self):
        if self.gae_service_name is None and 'GAE_SERVICE' in os.environ:
            self.gae_service_name = os.environ['GAE_SERVICE']
