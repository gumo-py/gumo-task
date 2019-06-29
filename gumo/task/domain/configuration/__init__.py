import dataclasses
import os

from typing import Optional
from typing import Union
from typing import ClassVar

from logging import getLogger

from gumo.core import get_google_oauth_credential
from gumo.core.domain.configuration import GoogleCloudProjectID
from googleapiclient import discovery

logger = getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class CloudTaskLocation:
    name: str
    locationID: str
    labels: dict = dataclasses.field(default_factory=dict)


def _get_cloud_tasks_locations(google_cloud_project: GoogleCloudProjectID) -> Optional[CloudTaskLocation]:
    name = 'projects/{}'.format(google_cloud_project.value)
    service = discovery.build('cloudtasks', 'v2', credentials=get_google_oauth_credential())
    request = service.projects().locations().list(name=name)

    response = request.execute()
    locations = response.get('locations', [])

    if len(locations) == 0:
        logger.warning(f'Cloud not found Cloud Tasks active locations ({name}).')
        return

    if len(locations) > 1:
        logger.warning(f'Cloud Tasks active locations are too many found. Use first record of results.')

    location = locations[0]  # type: dict

    return CloudTaskLocation(
        name=location.get('name'),
        locationID=location.get('locationId'),
        labels=location.get('labels')
    )


@dataclasses.dataclass()
class TaskConfiguration:
    default_queue_name: Optional[str] = None
    use_local_task_emulator: bool = False
    google_cloud_project: Union[GoogleCloudProjectID, str, None] = None
    gae_service_name: Optional[str] = None
    cloud_tasks_location: Optional[CloudTaskLocation] = None

    _GOOGLE_CLOUD_PROJECT_ENV_KEY: ClassVar = 'GOOGLE_CLOUD_PROJECT'
    _GAE_SERVICE_ENV_KEY: ClassVar = 'GAE_SERVICE'

    def __post_init__(self):
        self._set_google_cloud_project()
        self._set_gae_service_name()
        self._set_cloud_tasks_location()

    def _set_google_cloud_project(self):
        if isinstance(self.google_cloud_project, str):
            self.google_cloud_project = GoogleCloudProjectID(self.google_cloud_project)
        if isinstance(self.google_cloud_project, GoogleCloudProjectID):
            if self.google_cloud_project.value != os.environ.get(self._GOOGLE_CLOUD_PROJECT_ENV_KEY):
                raise RuntimeError(f'Env-var "{self._GOOGLE_CLOUD_PROJECT_ENV_KEY}" is invalid or undefined.'
                                   f'Please set value "{self.google_cloud_project.value}" to env-vars.')

        if self.google_cloud_project is None and self._GOOGLE_CLOUD_PROJECT_ENV_KEY in os.environ:
            self.google_cloud_project = GoogleCloudProjectID(os.environ[self._GOOGLE_CLOUD_PROJECT_ENV_KEY])

    def _set_gae_service_name(self):
        if self.gae_service_name is None and self._GAE_SERVICE_ENV_KEY in os.environ:
            self.gae_service_name = os.environ[self._GAE_SERVICE_ENV_KEY]

    def _set_cloud_tasks_location(self):
        if isinstance(self.cloud_tasks_location, CloudTaskLocation):
            return

        self.cloud_tasks_location = _get_cloud_tasks_locations(google_cloud_project=self.google_cloud_project)
