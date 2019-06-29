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
