from logging import getLogger
from injector import singleton

from typing import Union
from typing import Optional

from gumo.core.injector import injector
from gumo.task.infrastructure.configuration import TaskConfiguration
from gumo.task.bind import task_bind


logger = getLogger('gumo.task')

DEFAULT_QUEUE_NAME = 'default'


def configure(
        default_queue_name: Optional[str] = None,
        use_local_task_emulator: Union[str, bool, None] = None,
        _injector=None,
) -> TaskConfiguration:
    if _injector is None:
        _injector = injector

    config: TaskConfiguration = _injector.get(TaskConfiguration, scope=singleton)

    if default_queue_name is not None:
        config.default_queue_name = default_queue_name

    if use_local_task_emulator is not None:
        if isinstance(use_local_task_emulator, bool):
            config.use_local_task_emulator = use_local_task_emulator
        if isinstance(use_local_task_emulator, str):
            config.use_local_task_emulator = use_local_task_emulator.lower() in ['true', 'yes']

    _injector.binder.bind(TaskConfiguration, to=config, scope=singleton)
    logger.debug(f'Gumo.Task is configured, config={config}')

    _injector.binder.install(task_bind)

    return config


def get_config() -> TaskConfiguration:
    return injector.get(TaskConfiguration, scope=singleton)
