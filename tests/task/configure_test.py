from injector import Injector
from injector import singleton

from gumo.task._configuration import ConfigurationFactory
from gumo.task.infrastructure import TaskConfiguration


def test_configuration_factory_build():
    o = ConfigurationFactory.build(
        default_queue_name='gumo-default-queue',
        use_local_task_emulator='yes',
    )

    assert o == TaskConfiguration(
        default_queue_name='gumo-default-queue',
        use_local_task_emulator=True,
    )

    assert ConfigurationFactory.build(
        default_queue_name='gumo-default-queue',
        use_local_task_emulator='yes',
    ).use_local_task_emulator
    assert ConfigurationFactory.build(
        default_queue_name='gumo-default-queue',
        use_local_task_emulator='true',
    ).use_local_task_emulator
    assert not ConfigurationFactory.build(
        default_queue_name='gumo-default-queue',
        use_local_task_emulator='no',
    ).use_local_task_emulator


def test_singleton_task_configuration():
    injector = Injector()
    config = TaskConfiguration()
    injector.binder.bind(TaskConfiguration, to=config, scope=singleton)
    fetched_config = injector.get(TaskConfiguration)

    assert id(config) == id(fetched_config)
    assert fetched_config.default_queue_name is None

    fetched_config.default_queue_name = 'default-queue'
    retry_fetched_config = injector.get(TaskConfiguration)
    assert id(config) == id(retry_fetched_config)
    assert retry_fetched_config.default_queue_name == 'default-queue'
