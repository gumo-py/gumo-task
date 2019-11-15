from gumo.task.domain import GumoTask
from gumo.task.domain import TaskAppEngineRouting
from gumo.datastore.infrastructure import DatastoreMapperMixin
from gumo.datastore.infrastructure import DatastoreEntity


class DatastoreGumoTaskMapper(DatastoreMapperMixin):
    def to_datastore_entity(self, task: GumoTask) -> DatastoreEntity:
        doc = DatastoreEntity(key=self.entity_key_mapper.to_datastore_key(task.key))

        routing = {}
        if task.app_engine_routing:
            routing = {
                'service': task.app_engine_routing.service,
                'version': task.app_engine_routing.version,
                'instance': task.app_engine_routing.instance,
            }

        doc.update({
            'relative_uri': task.relative_uri,
            'method': task.method,
            'payload': task.payload,
            'schedule_time': task.schedule_time,
            'created_at': task.created_at,
            'queue_name': task.queue_name,
            'app_engine_routing': routing,
        })

        return doc

    def to_entity(self, doc: DatastoreEntity) -> GumoTask:
        key = self.entity_key_mapper.to_entity_key(doc.key)

        routing = None
        if 'app_engine_routing' in doc:
            routing = TaskAppEngineRouting(
                service=doc['app_engine_routing'].get('service'),
                version=doc['app_engine_routing'].get('version'),
                instance=doc['app_engine_routing'].get('instance'),
            )

        return GumoTask(
            key=key,
            relative_uri=doc.get('relative_uri', doc.get('url')),
            method=doc.get('method'),
            payload=doc.get('payload'),
            schedule_time=self.convert_datetime(doc.get('schedule_time')),
            created_at=self.convert_datetime(doc.get('created_at')),
            queue_name=doc.get('queue_name'),
            app_engine_routing=routing,
        )
