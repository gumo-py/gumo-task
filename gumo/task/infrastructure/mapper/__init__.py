from injector import inject

from gumo.core import EntityKey
from gumo.task.domain import GumoTask
from gumo.datastore.infrastructure import EntityKeyMapper


class DatastoreGumoTaskMapper:
    @inject
    def __init__(
            self,
            entity_key_mapper: EntityKeyMapper
    ):
        self._entity_key_mapper = entity_key_mapper

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
            schedule_time=doc.get('schedule_time'),
            created_at=doc.get('created_at'),
            queue_name=doc.get('queue_name'),
        )
