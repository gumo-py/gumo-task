import dataclasses


@dataclasses.dataclass(frozen=True)
class CloudTaskLocation:
    name: str
    location_id: str
    labels: dict = dataclasses.field(default_factory=dict)
