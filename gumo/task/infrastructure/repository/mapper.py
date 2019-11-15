from gumo.core import EntityKey
from gumo.task.domain import GumoTask
from gumo.datastore.infrastructure import DatastoreMapperMixin


class DatastoreGumoTaskMapper(DatastoreMapperMixin):
    def to_datastore_entity(self, task: GumoTask) -> dict:
        j = {
            'relative_uri': task.relative_uri,
            'method': task.method,
            'payload': task.payload,
            'schedule_time': task.schedule_time,
            'created_at': task.created_at,
            'queue_name': task.queue_name,
        }

        return j

    def to_entity(self, key: EntityKey, doc: dict) -> GumoTask:
        return GumoTask(
            key=key,
            relative_uri=doc.get('relative_uri', doc.get('url')),
            method=doc.get('method'),
            payload=doc.get('payload'),
            schedule_time=self.convert_datetime(doc.get('schedule_time')),
            created_at=self.convert_datetime(doc.get('created_at')),
            queue_name=doc.get('queue_name'),
        )
