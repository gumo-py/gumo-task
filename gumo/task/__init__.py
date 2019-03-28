from logging import getLogger

from gumo.task._configuration import configure
from gumo.task.domain.configuration import TaskConfiguration


__all__ = [
    configure.__name__,

    TaskConfiguration.__name__,
]

logger = getLogger('gumo.task')
