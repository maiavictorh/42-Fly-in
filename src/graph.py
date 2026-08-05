from .models import Hub, Connection, Drone
from .utils import ZoneType


class Graph:
    def __init__(self, nb_drones: int,
                 start_hub: Hub,
                 end_hub: Hub,
                 hubs: dict[str, Hub],
                 connections: list[Connection]) -> None:
        self.nb_drones = nb_drones
        self.start_hub = start_hub
        self.end_hub = end_hub
        self.hubs = hubs
        self.connections = connections
        self.drones = self._generate_drones()

    def _generate_drones(self) -> list[Drone]:
        drone_list = []
        for i in range(1, self.nb_drones + 1):
            drone_list.append(Drone(i, self.start_hub))

        return drone_list

    def find_path(self) -> list[Hub]:
        adjacency = self._build_adjacency()
        print(adjacency)

    def _build_adjacency(self) -> dict[Hub, list[tuple[Hub, int]]]:
        adjacency: dict[Hub, list[tuple[Hub, int]]] = \
            {h: [] for h in self.hubs.values()}

        for conn in self.connections:
            weight = self._connection_weight(conn)
            adjacency[conn.hub_1].append((conn.hub_2, weight))
            adjacency[conn.hub_2].append((conn.hub_1, weight))

        return adjacency

    @staticmethod
    def _connection_weight(conn: Connection) -> int:
        if conn.hub_1.zone == ZoneType.RESTRICTED \
           or conn.hub_2.zone == ZoneType.RESTRICTED:
            return 2
        return 1
