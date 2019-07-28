import os

from injector import Injector
from injector import singleton

from gumo.task._configuration import ConfigurationFactory
from gumo.task.infrastructure.configuration import TaskConfiguration
from gumo.task.infrastructure.configuration import _detect_suitable_version_name


def test_configuration_factory_build():
    o = ConfigurationFactory.build(
        default_queue_name='gumo-default-queue',
        use_local_task_emulator='yes',
    )

    assert o == TaskConfiguration(
        default_queue_name='gumo-default-queue',
        use_local_task_emulator=True,
    )


def test_singleton_task_configuration():
    injector = Injector()
    config = TaskConfiguration(use_local_task_emulator=True)
    injector.binder.bind(TaskConfiguration, to=config, scope=singleton)
    fetched_config = injector.get(TaskConfiguration)

    assert id(config) == id(fetched_config)
    assert fetched_config.default_queue_name is None

    fetched_config.default_queue_name = 'default-queue'
    retry_fetched_config = injector.get(TaskConfiguration)
    assert id(config) == id(retry_fetched_config)
    assert retry_fetched_config.default_queue_name == 'default-queue'


class TestConfiguration:
    def setup_method(self, method):
        self.env_vars = {}
        for k, v in os.environ.items():
            self.env_vars[k] = v

    def teardown_method(self, method):
        for k in os.environ.keys():
            if k not in self.env_vars:
                del os.environ[k]

        for k, v in self.env_vars.items():
            os.environ[k] = v

    def test_use_emulator(self):
        del os.environ['CLOUD_TASKS_EMULATOR_ENABLED']

        o = ConfigurationFactory.build(
            default_queue_name='default',
            use_local_task_emulator='yes'
        )

        assert o.cloud_tasks_location.name == 'local'
        assert o.cloud_tasks_location.location_id == 'local'


class TestSuitableVersionName:
    def test_default_url(self):
        assert _detect_suitable_version_name(
            hostname='gumo-sample.appspot.com',
            service_name=None
        ) is None

    def test_custom_domain_url(self):
        assert _detect_suitable_version_name(
            hostname='app.balus.me',
            service_name=None
        ) is None

    def test_with_version_url(self):
        assert _detect_suitable_version_name(
            hostname='version-dot-gumo-sample.appspot.com',
            service_name=None
        ) == 'version'

        assert _detect_suitable_version_name(
            hostname='version.gumo-sample.appspot.com',
            service_name=None
        ) == 'version'

    def test_with_service_default_url(self):
        assert _detect_suitable_version_name(
            hostname='service-dot-gumo-sample.appspot.com',
            service_name='service'
        ) is None

        assert _detect_suitable_version_name(
            hostname='service.gumo-sample.appspot.com',
            service_name='service'
        ) is None

    def test_with_service_specific_version_url(self):
        assert _detect_suitable_version_name(
            hostname='version-dot-service-dot-gumo-sample.appspot.com',
            service_name='service'
        ) == 'version'

        assert _detect_suitable_version_name(
            hostname='version.service.gumo-sample.appspot.com',
            service_name='service'
        ) == 'version'

