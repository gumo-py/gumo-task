from logging import getLogger

from typing import Union

from gumo.core.injector import injector
from gumo.task.domain.configuration import TaskConfiguration
from gumo.task.bind import task_bind


logger = getLogger('gumo.task')


class ConfigurationFactory:
    @classmethod
    def build(
            cls,
            default_queue_name: str,
            use_local_task_emulator: Union[str, bool, None] = False
    ) -> TaskConfiguration:
        use_emulator = False

        if isinstance(use_local_task_emulator, bool):
            use_emulator = use_local_task_emulator
        elif isinstance(use_local_task_emulator, str):
            use_emulator = use_local_task_emulator.lower() in ['true', 'yes']

        return TaskConfiguration(
            default_queue_name=default_queue_name,
            use_local_task_emulator=use_emulator,
        )


def configure(
        default_queue_name: str,
        use_local_task_emulator: Union[str, bool, None] = False
) -> TaskConfiguration:
    config = ConfigurationFactory.build(
        default_queue_name=default_queue_name,
        use_local_task_emulator=use_local_task_emulator,
    )
    logger.debug(f'Gumo.Task is configured, config={config}')

    injector.binder.bind(TaskConfiguration, to=config)
    injector.binder.install(task_bind)

    return config
