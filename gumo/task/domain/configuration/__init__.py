import dataclasses


@dataclasses.dataclass(frozen=True)
class TaskConfiguration:
    default_queue_name: str
    use_local_task_emulator: bool = False
