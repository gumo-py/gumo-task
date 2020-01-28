import json

from gumo.task.domain import GumoTask
from gumo.task.domain import TaskAppEngineRouting
from gumo.datastore.infrastructure import DatastoreMapperMixin
from gumo.datastore.infrastructure import DatastoreEntity


class DatastoreGumoTaskMapper(DatastoreMapperMixin):
    def to_datastore_entity(self, task: GumoTask) -> DatastoreEntity:
        doc = DatastoreEntity(
            key=self.entity_key_mapper.to_datastore_key(task.key),
            exclude_from_indexes=("payload_str",),
        )

        doc.update({
            'relative_uri': task.relative_uri,
            'method': task.method,
            'payload_str': json.dumps(task.payload),
            'schedule_time': task.schedule_time,
            'created_at': task.created_at,
            'queue_name': task.queue_name,
        })

        if task.app_engine_routing:
            doc.update({
                'app_engine_routing.service': task.app_engine_routing.service,
                'app_engine_routing.version': task.app_engine_routing.version,
                'app_engine_routing.instance': task.app_engine_routing.instance,
            })

        return doc

    def to_entity(self, doc: DatastoreEntity) -> GumoTask:
        key = self.entity_key_mapper.to_entity_key(doc.key)

        if 'payload_str' in doc:
            payload = json.loads(doc.get('payload_str'))
        else:
            payload = doc.get('payload', {})

        routing = TaskAppEngineRouting(
            service=doc.get('app_engine_routing.service'),
            version=doc.get('app_engine_routing.version'),
            instance=doc.get('app_engine_routing.instance'),
        )

        return GumoTask(
            key=key,
            relative_uri=doc.get('relative_uri', doc.get('url')),
            method=doc.get('method'),
            payload=payload,
            schedule_time=self.convert_datetime(doc.get('schedule_time')),
            created_at=self.convert_datetime(doc.get('created_at')),
            queue_name=doc.get('queue_name'),
            app_engine_routing=routing,
        )
