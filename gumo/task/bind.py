from gumo.task.application.repository import GumoTaskRepository
from gumo.task.infrastructure.repository import GumoTaskRepositoryImpl


def task_bind(binder):
    binder.bind(GumoTaskRepository, to=GumoTaskRepositoryImpl)
