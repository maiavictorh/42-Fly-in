import pygame
from typing import Optional, Any
from .utils import DroneStatus, ZoneType, Color


class Drone:
    """A drone that travels along a path from the start hub to the end hub."""
    def __init__(self, id: int, start_hub: "Hub") -> None:
        """
        Initialize a waiting drone placed on the start hub.

        Args:
            id: Unique drone identifier.
            status: current drone movement status, defaults to "waiting".
            path: path to follow set by the algorithm.
            path_index: current position in the path.
            turns_remaining: turns left to move or to finish move.
            current_hub: drone's location, when in a hub,
                         beginning at start_hub.
            current_connection: drone's location when in a connetion.
        """
        self.id = id
        self.status = DroneStatus.WAITING
        self.path: list[Hub] = []
        self.path_index = 0
        self.turns_remaining = 0
        self.current_hub: Optional[Hub] = start_hub
        self.current_connection: Optional[Connection] = None

    def __repr__(self) -> str:
        """Return the drone label, ex: "D1"."""
        return f"D{self.id}"


class Hub:
    """A zone of the map where drones can stay or pass through."""
    def __init__(self, name: str, coord: tuple[int, int],
                 metadata: Optional[dict[str, Any]] = None) -> None:
        """
        Initialize a hub.

        Defaults are a normal zone, no color and capacity of one drone.
        The weight is 2 for restricted zones and 1 otherwise.

        Args:
            name: Unique hub name.
            coord: Grid position as (x, y).
            metadata: Optional parsed values for "zone", "color" and
                      "max_drones".
            zone: zone type, directly impacts the chosen path.
            color: hub color, for enhanced visual representation.
            max_drones: number of drones that can occupy the hub.
            weight: hub's movement cost for drones,
                    different types mean different costs.
        """
        self.name = name
        self.coord = coord
        self.metadata = metadata
        self.zone = ZoneType.NORMAL
        self.color: Optional[Color] = None
        self.max_drones = 1
        self._define_metadata(self.metadata)
        self.weight = 2 if self.zone == ZoneType.RESTRICTED else 1

    def __repr__(self) -> str:
        """Returns the hub name."""
        return f"{self.name}"

    def _define_metadata(self, metadata: dict[str, Any] | None) -> None:
        """
        Apply zone, color and max_drones from the metadata, if present.

        Args:
            metadata: Parsed metadata, or None to keep the defaults.
        """
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

    def draw_hub(self, screen: pygame.Surface,
                 rgb: tuple[int, int, int],
                 coord: tuple[int, int]) -> None:
        """
        Draw the hub as a filled circle.

        Args:
            screen: Surface to draw on.
            rgb: Fill color.
            coord: Center of the circle in screen pixels.
        """
        pygame.draw.circle(screen, rgb, coord, 40)


class Connection:
    """A bidirectional link between two hubs."""
    def __init__(self, hub_1: Hub, hub_2: Hub,
                 metadata: Optional[dict[str, int]] = None) -> None:
        """
        Initialize a connection.

        Args:
            hub_1: First end of the connection.
            hub_2: Second end of the connection.
            metadata: Optional parsed values; supports "max_link_capacity".
            max_link_capacity: number of drones that can occupy the connection.
        """
        self.hub_1 = hub_1
        self.hub_2 = hub_2
        self.metadata = metadata
        self.max_link_capacity = self._define_metadata(self.metadata)

    def __repr__(self) -> str:
        """Return the connection label, ex: "A<->B"."""
        return f"{self.hub_1}<->{self.hub_2}"

    def _define_metadata(self, metadata: dict[str, int] | None) -> int:
        """
        Resolve the link capacity from the metadata.

        Args:
            metadata: Parsed metadata, or None.

        Returns:
            The max_link_capacity value, or 1 if it was not provided.
        """
        if metadata is not None:
            if "max_link_capacity" in metadata.keys():
                return metadata["max_link_capacity"]
        return 1

    def draw_connetion(self, screen: pygame.Surface,
                       coords: list[tuple[int, int]]) -> None:
        """
        Draw the connection as a gray line between its two hubs.

        Args:
            screen: Surface to draw on.
            coords: Screen positions of the two ends, as [start, end].
        """
        pygame.draw.line(screen, (150, 150, 150), coords[0], coords[1], 2)
