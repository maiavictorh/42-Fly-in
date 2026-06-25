from typing import Optional, Any


class Graph:
    def __init__(self) -> None:
        pass


class Drone:
    def __init__(self) -> None:
        pass


class Hub:
    def __init__(self, name: str, coord: tuple[int, int],
                 metadata: Optional[dict[str, Any]] = None) -> None:
        self.name = name
        self.coord = coord
        self.metadata = metadata

    # @staticmethod
    # def validate_metadata


class Connection:
    def __init__(self, hub_1: str, hub_2: str,
                 metadata: Optional[dict[str, Any]] = None) -> None:
        self.hub_1 = hub_1
        self.hub_2 = hub_2
        self.metadata = metadata
