import datetime

from gumo.task.application import enqueue
from gumo.task.domain import GumoTask

from gumo.datastore.infrastructure.test_utils import DatastoreRepositoryMixinForTest
from gumo.datastore.infrastructure import DatastoreMapperMixin


class TestEnqueServiceWithEmulator(DatastoreRepositoryMixinForTest, DatastoreMapperMixin):
    KIND = GumoTask.KIND

    def setup_method(self):
        self.cleanup_entities()

    def test_enqueue_success(self):
        enqueue(
            url='/task',
            method='POST',
            payload={'body': 'message'},
            queue_name='test-queue'
        )
        assert self.count_entities() == 1

        query = self.datastore_client.query(kind=self.KIND)
        tasks = list(query.fetch())
        assert len(tasks) == 1
        assert tasks[0]['relative_uri'] == '/task'
        assert tasks[0]['method'] == 'POST'
        assert tasks[0]['payload']['body'] == 'message'
        assert tasks[0]['queue_name'] == 'test-queue'

        assert tasks[0]['schedule_time'] == tasks[0]['created_at']

    def test_enqueue_scheduled_task(self):
        schedule_time = datetime.datetime.utcnow().replace(microsecond=0) + datetime.timedelta(hours=1)
        enqueue(
            url='/scheduled-task',
            schedule_time=schedule_time,
        )
        assert self.count_entities() == 1

        query = self.datastore_client.query(kind=self.KIND)
        tasks = list(query.fetch())
        assert len(tasks) == 1
        assert tasks[0]['relative_uri'] == '/scheduled-task'
        assert self.convert_datetime(tasks[0]['schedule_time']) == schedule_time

    def test_enqueue_in_seconds_task(self):
        t = datetime.datetime.utcnow().replace(microsecond=0) + datetime.timedelta(hours=1)
        enqueue(
            url='/scheduled-task',
            in_seconds=3600
        )
        assert self.count_entities() == 1

        query = self.datastore_client.query(kind=self.KIND)
        tasks = list(query.fetch())
        assert len(tasks) == 1
        assert tasks[0]['relative_uri'] == '/scheduled-task'

        # テスト実行中の時刻のズレを考慮して、前後5秒の範囲内に収まっていればOKとする
        schedule_time = self.convert_datetime(tasks[0]['schedule_time'])
        assert t - datetime.timedelta(seconds=5) <= schedule_time <= t + datetime.timedelta(seconds=5)
