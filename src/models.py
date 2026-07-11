from typing import Optional, Any
from .utils import ZoneType


class Drone:
    def __init__(self) -> None:
        pass


class Hub:
    def __init__(self, name: str, coord: tuple[int, int],
                 metadata: Optional[dict[str, Any]] = None) -> None:
        self.name = name
        self.coord = coord
        self.metadata = metadata
        self.zone = ZoneType.NORMAL.value
        self.color = None
        self.max_drones = 1
        self._define_metadata(self.metadata)

    def _define_metadata(self, metadata: dict[str, Any] | None) -> None:

        if metadata is None:
            return

        if "zone" in metadata.keys():
            self.zone = metadata["zone"]
        if "color" in metadata.keys():
            self.color = metadata["color"]
        if "max_drones" in metadata.keys():
            self.max_drones = metadata["max_drones"]


class Connection:
    def __init__(self, hub_1: str, hub_2: str,
                 metadata: Optional[dict[str, int]] = None) -> None:
        self.hub_1 = hub_1
        self.hub_2 = hub_2
        self.metadata = metadata
        self.max_link_capacity = self._define_metadata(self.metadata)

    def _define_metadata(self, metadata: dict[str, int] | None) -> int:

        if metadata is not None:
            if "max_link_capacity" in metadata.keys():
                return metadata["max_link_capacity"]
        return 1
