import dataclasses


@dataclasses.dataclass(frozen=True)
class CloudTaskLocation:
    name: str
    locationID: str
    labels: dict = dataclasses.field(default_factory=dict)
