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


def _detect_suitable_version_name(hostname: str, service_name: Optional[str]) -> Optional[str]:
    if hostname.find('.appspot.com') < 0:
        # custom domain url
        return

    subdomain = hostname.replace('.appspot.com', '').replace('-dot-', '.')
    if subdomain.find('.') < 0:
        # <app-id>.appspot.com style.
        return

    split = subdomain.split('.')
    if len(split) == 2 and service_name == split[0]:
        # <service>.<app-id>.appspot.com style.
        return

    if len(split) == 3 and service_name == split[1]:
        # <version>.<service>.<app-id>.appspot.com style.
        return split[0]

    return split[0]


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
    gae_version_name: Optional[str] = None
    cloud_tasks_location: Optional[CloudTaskLocation] = None
    client: Optional[tasks.CloudTasksClient] = None

    _ENV_KEY_GOOGLE_CLOUD_PROJECT: ClassVar = 'GOOGLE_CLOUD_PROJECT'
    _ENV_KEY_GAE_SERVICE: ClassVar = 'GAE_SERVICE'
    _ENV_KEY_GAE_DEPLOYMENT_ID: ClassVar = 'GAE_DEPLOYMENT_ID'
    _ENV_KEY_GAE_INSTANCE: ClassVar = 'GAE_INSTANCE'
    _ENV_KEY_CLOUD_TASKS_EMULATOR_ENABLED: ClassVar = 'CLOUD_TASKS_EMULATOR_ENABLED'

    _lock: ClassVar = threading.Lock()

    def __post_init__(self):
        with self._lock:
            self._set_google_cloud_project()
            self._set_gae_service_name()
            self._set_use_local_task_emulator()
            self._set_cloud_tasks_location()
            self._set_client()

    def _cloud_tasks_emulator_enabled(self) -> bool:
        return os.environ.get(self._ENV_KEY_CLOUD_TASKS_EMULATOR_ENABLED, '').lower() == 'true'

    def _is_google_platform(self) -> bool:
        return self._ENV_KEY_GAE_DEPLOYMENT_ID in os.environ and self._ENV_KEY_GAE_INSTANCE in os.environ

    def _set_google_cloud_project(self):
        if isinstance(self.google_cloud_project, str):
            self.google_cloud_project = GoogleCloudProjectID(self.google_cloud_project)
        if isinstance(self.google_cloud_project, GoogleCloudProjectID):
            if self.google_cloud_project.value != os.environ.get(self._ENV_KEY_GOOGLE_CLOUD_PROJECT):
                raise RuntimeError(f'Env-var "{self._ENV_KEY_GOOGLE_CLOUD_PROJECT}" is invalid or undefined.'
                                   f'Please set value "{self.google_cloud_project.value}" to env-vars.')

        if self.google_cloud_project is None and self._ENV_KEY_GOOGLE_CLOUD_PROJECT in os.environ:
            self.google_cloud_project = GoogleCloudProjectID(os.environ[self._ENV_KEY_GOOGLE_CLOUD_PROJECT])

    def _set_gae_service_name(self):
        if self.gae_service_name is None and self._ENV_KEY_GAE_SERVICE in os.environ:
            self.gae_service_name = os.environ[self._ENV_KEY_GAE_SERVICE]

    def _set_use_local_task_emulator(self):
        if isinstance(self.use_local_task_emulator, bool):
            return

        if self._is_google_platform():
            self.use_local_task_emulator = False
            return

        if self._cloud_tasks_emulator_enabled():
            self.use_local_task_emulator = True
            return

    def _set_cloud_tasks_location(self):
        if isinstance(self.cloud_tasks_location, CloudTaskLocation):
            return

        if self.use_local_task_emulator:
            self.cloud_tasks_location = CloudTaskLocation.build_local()
            return

        self.cloud_tasks_location = CloudTaskLocation.fetch_cloud_tasks_locations(
            google_cloud_project=self.google_cloud_project
        )

    def _set_client(self):
        if isinstance(self.client, tasks.CloudTasksClient):
            return

        if self.use_local_task_emulator:
            return

        self.client = tasks.CloudTasksClient()

    def suitable_version_name(self, hostname: str) -> Optional[str]:
        return _detect_suitable_version_name(
            hostname=hostname,
            service_name=self.gae_service_name,
        )
