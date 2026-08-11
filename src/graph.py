from typing import Optional
from heapq import heappop, heappush
from .models import Hub, Connection
from .utils import ZoneType


class Graph:
    def __init__(self, nb_drones: int,
                 start_hub: Hub,
                 end_hub: Hub,
                 hubs: dict[str, Hub],
                 connections: list[Connection]) -> None:
        self.nb_drones = nb_drones
        self.start_hub = start_hub
        self.start_hub.max_drones = self.nb_drones
        self.end_hub = end_hub
        self.end_hub.max_drones = self.nb_drones
        self.hubs = hubs
        self.connections = connections

    def find_path(self) -> list[Hub]:
        path: list[Hub] = []

        adjacency = self._build_adjacency()
        previous_dict = self.dijkstra(self.start_hub, self.end_hub, adjacency)

        if self.end_hub == self.start_hub:
            return [self.start_hub]
        if previous_dict[self.end_hub] is None:
            return []

        path.append(self.end_hub)
        current = previous_dict[self.end_hub]

        while current is not None:
            path.append(current)
            current = previous_dict[current]

        return list(reversed(path))

    def dijkstra(
            self, start: Hub, end: Hub,
            adjacency: dict[Hub, list[tuple[Hub, int]]]
            ) -> dict[Hub, Optional[Hub]]:

        distances = {hub: float("inf") for hub in adjacency}
        distances[start] = 0
        previous: dict[Hub, Optional[Hub]] = {hub: None for hub in adjacency}
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

        return previous

    def _build_adjacency(self) -> dict[Hub, list[tuple[Hub, int]]]:
        adjacency: dict[Hub, list[tuple[Hub, int]]] = \
            {h: [] for h in self.hubs.values()}

        for conn in self.connections:
            weight = 2 if conn.hub_1.zone == ZoneType.RESTRICTED \
                        or conn.hub_2.zone == ZoneType.RESTRICTED else 1
            adjacency[conn.hub_1].append((conn.hub_2, weight))
            adjacency[conn.hub_2].append((conn.hub_1, weight))

        return adjacency
