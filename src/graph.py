from heapq import heappop, heappush
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
        path: list[Hub] = []

        self.dijkstra(self.start_hub, self.end_hub, adjacency)

        # for k, v in adjacency.items():
        #     print(f"{k} -> {v}")
        # print()

        return path

    def dijkstra(self, start: Hub, end: Hub,
                 adjacency: dict[Hub, list[tuple[Hub, int]]]):

        distances = {hub: float("inf") for hub in adjacency}
        distances[start] = 0
        previous = {hub: None for hub in adjacency}
        visited: set[Hub] = set()
        count = 0

        heap: list[tuple[float, int, Hub]] = [(0, count, start)]

        while heap:
            current_distance, _, current_hub = heappop(heap)

            if current_hub in visited:
                continue
            visited.add(current_hub)

            if current_hub == end:
                break

            for neighbor, weight in adjacency[current_hub]:

                new_distance = current_distance + weight

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current_hub

                    count += 1
                    heappush(heap, (new_distance, count, neighbor))

                # print(distances)
                # print(previous)
                print(heap)

        return previous

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
