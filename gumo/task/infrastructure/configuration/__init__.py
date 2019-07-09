import dataclasses
import os
import threading

from typing import ClassVar
from typing import Optional
from typing import Union
from typing import List
from logging import getLogger

from googleapiclient import discovery
from gumo.core import GoogleCloudProjectID
from gumo.core import get_google_oauth_credential

from google.cloud import tasks

logger = getLogger(__name__)


def _fetch_cloud_tasks_locations_by_api(google_cloud_project: GoogleCloudProjectID) -> List[dict]:
    name = 'projects/{}'.format(google_cloud_project.value)
    service = discovery.build(
        'cloudtasks', 'v2',
        credentials=get_google_oauth_credential(),
        cache_discovery=False)
    request = service.projects().locations().list(name=name)

    response = request.execute()
    locations = response.get('locations', [])
    return locations


@dataclasses.dataclass(frozen=True)
class CloudTaskLocation:
    name: str
    location_id: str
    labels: dict = dataclasses.field(default_factory=dict)

    @classmethod
    def build_local(cls):
        """
        :rtype: CloudTaskLocation
        """
        return cls(
            name='local',
            location_id='local',
            labels={
                'cloud.googleapis.com/region': 'local',
            }
        )

    @classmethod
    def build_by(cls, project_id: str, location_id: str):
        """
        :rtype: CloudTaskLocation
        """
        return cls(
            name='projects/{project_id}/locations/{location_id}'.format(
                project_id=project_id,
                location_id=location_id,
            ),
            location_id=location_id,
            labels={
                'cloud.googleapis.com/region': location_id,
            }
        )

    @classmethod
    def fetch_cloud_tasks_locations(cls, google_cloud_project: GoogleCloudProjectID):
        """
        :rtype: CloudTaskLocation
        """
        locations = _fetch_cloud_tasks_locations_by_api(google_cloud_project=google_cloud_project)
        if len(locations) == 0:
            raise RuntimeError(f'Cloud not found Cloud Tasks active locations (project={google_cloud_project.value}).')

        if len(locations) > 1:
            logger.warning(f'Cloud Tasks active locations are too many found. Use first record of results.')

        location = locations[0]  # type: dict

        return CloudTaskLocation(
            name=location.get('name'),
            location_id=location.get('locationId'),
            labels=location.get('labels')
        )


@dataclasses.dataclass()
class TaskConfiguration:
    default_queue_name: Optional[str] = None
    use_local_task_emulator: bool = False
    google_cloud_project: Union[GoogleCloudProjectID, str, None] = None
    gae_service_name: Optional[str] = None
    cloud_tasks_location: Optional[CloudTaskLocation] = None
    client: Optional[tasks.CloudTasksClient] = None

    _GOOGLE_CLOUD_PROJECT_ENV_KEY: ClassVar = 'GOOGLE_CLOUD_PROJECT'
    _GAE_SERVICE_ENV_KEY: ClassVar = 'GAE_SERVICE'
    _FALLBACK_CLOUD_TASKS_LOCATION: ClassVar = '_FALLBACK_CLOUD_TASKS_LOCATION'

    _lock: ClassVar = threading.Lock()

    def __post_init__(self):
        with self._lock:
            self._set_google_cloud_project()
            self._set_gae_service_name()
            self._set_cloud_tasks_location()
            self._set_client()

    def _has_fallback_location(self) -> bool:
        return self._FALLBACK_CLOUD_TASKS_LOCATION in os.environ

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

        if self.use_local_task_emulator:
            self.cloud_tasks_location = CloudTaskLocation.build_local()
            return

        if self._has_fallback_location():
            location_id = os.environ[self._FALLBACK_CLOUD_TASKS_LOCATION]
            logger.debug(f'Fallback to location={location_id} via env-vars "{self._FALLBACK_CLOUD_TASKS_LOCATION}"')
            self.cloud_tasks_location = CloudTaskLocation.build_by(
                project_id=self.google_cloud_project.value,
                location_id=location_id,
            )
            return

        self.cloud_tasks_location = CloudTaskLocation.fetch_cloud_tasks_locations(
            google_cloud_project=self.google_cloud_project
        )

    def _set_client(self):
        if isinstance(self.client, tasks.CloudTasksClient):
            return

        if self.use_local_task_emulator or self._has_fallback_location():
            return

        self.client = tasks.CloudTasksClient()
