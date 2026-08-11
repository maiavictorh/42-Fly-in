from typing import Optional, Any
from .utils import DroneStatus, ZoneType, Color


class Drone:
    def __init__(self, id: int, start_hub: "Hub") -> None:
        self.id = id
        self.status = DroneStatus.WAITING
        self.path: list[Hub] = []
        self.path_index = 0
        self.turns_remaining = 0
        self.current_hub: Optional[Hub] = start_hub
        self.current_connection: Optional[Connection] = None

    def __repr__(self) -> str:
        return f"D{self.id}"


class Hub:
    def __init__(self, name: str, coord: tuple[int, int],
                 metadata: Optional[dict[str, Any]] = None) -> None:
        self.name = name
        self.coord = coord
        self.metadata = metadata
        self.zone = ZoneType.NORMAL
        self.color: Optional[Color] = None
        self.max_drones = 1
        self._define_metadata(self.metadata)

    def __repr__(self) -> str:
        return f"{self.name}"

    def _define_metadata(self, metadata: dict[str, Any] | None) -> None:

        if metadata is None:
            return

        if "zone" in metadata.keys():
            for zone in ZoneType:
                if zone.value == metadata["zone"]:
                    self.zone = zone
        if "color" in metadata.keys():
            for color in Color:
                if color.value == metadata["color"]:
                    self.color = color
        if "max_drones" in metadata.keys():
            self.max_drones = metadata["max_drones"]


class Connection:
    def __init__(self, hub_1: Hub, hub_2: Hub,
                 metadata: Optional[dict[str, int]] = None) -> None:
        self.hub_1 = hub_1
        self.hub_2 = hub_2
        self.metadata = metadata
        self.max_link_capacity = self._define_metadata(self.metadata)

    def __repr__(self) -> str:
        return f"{self.hub_1} <-> {self.hub_2}"

    def _define_metadata(self, metadata: dict[str, int] | None) -> int:

        if metadata is not None:
            if "max_link_capacity" in metadata.keys():
                return metadata["max_link_capacity"]
        return 1
