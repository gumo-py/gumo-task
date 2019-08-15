import os

from injector import Injector
from injector import singleton

from gumo.task._configuration import configure
from gumo.task.infrastructure.configuration import TaskConfiguration
from gumo.task.infrastructure.configuration import _detect_suitable_version_name


def test_singleton_task_configuration():
    injector = Injector()
    config = configure(_injector=injector)
    fetched_config = injector.get(TaskConfiguration)

    assert id(config) == id(fetched_config)
    assert fetched_config.default_queue_name == 'default'

    fetched_config.default_queue_name = 'default-queue'
    retry_fetched_config = injector.get(TaskConfiguration)
    assert id(config) == id(retry_fetched_config)
    assert retry_fetched_config.default_queue_name == 'default-queue'

    configure(default_queue_name='another-queue', _injector=injector)
    another_fetched_config = injector.get(TaskConfiguration)
    assert id(config) == id(another_fetched_config)
    assert another_fetched_config.default_queue_name == 'another-queue'


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
