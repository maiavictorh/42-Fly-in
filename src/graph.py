from typing import Optional
from heapq import heappop, heappush
from .models import Hub, Connection
from .utils import ZoneType as ZT


class Graph:
    """Network of hubs and connections used by the simulation."""
    def __init__(self, nb_drones: int,
                 start_hub: Hub,
                 end_hub: Hub,
                 hubs: dict[str, Hub],
                 connections: list[Connection]) -> None:
        """
        Initialize the graph.

        The start and end hubs have their max_drones set to nb_drones,
        so they are never limited by capacity.

        Args:
            nb_drones: Total number of drones in the fleet.
            start_hub: Hub where every drone begins.
            end_hub: Hub where every drone must arrive.
            hubs: All hubs, indexed by name.
            connections: All connections between hubs.
        """
        self.nb_drones = nb_drones
        self.start_hub = start_hub
        self.start_hub.max_drones = self.nb_drones
        self.end_hub = end_hub
        self.end_hub.max_drones = self.nb_drones
        self.hubs = hubs
        self.connections = connections

    def find_path(self) -> list[Hub]:
        """
        Find the cheapest path from the start hub to the end hub.

        Returns:
            The ordered list of hubs from start to end (both included),
            a single-element list if start and end are the same hub, or
            an empty list if the end hub is unreachable.
        """
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
        """
        Run Dijkstra's algorithm from start, stopping once end is reached.

        Blocked hubs are never entered. Ties in the heap are broken by
        insertion order through a counter.

        Args:
            start: Hub where the search begins.
            end: Hub where the search stops early.
            adjacency: Neighbors of each hub as (hub, weight) pairs.

        Returns:
            A dict mapping each hub to its predecessor on the cheapest
            known path, or None if it has none (start or unreached).
        """
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
                if neighbor.zone == ZT.BLOCKED:
                    continue
                if neighbor.zone == ZT.PRIORITY:
                    weight -= 1

                new_distance = current_distance + weight

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current_hub

                    count += 1
                    heappush(heap, (new_distance, count, neighbor))

        return previous

    def _build_adjacency(self) -> dict[Hub, list[tuple[Hub, int]]]:
        """
        Build the bidirectional adjacency list from the connections.

        The weight of each edge is the weight of the hub being entered.

        Returns:
            A dict mapping each hub to a list of (neighbor, weight) pairs.
        """
        adjacency: dict[Hub, list[tuple[Hub, int]]] = \
            {h: [] for h in self.hubs.values()}

        for conn in self.connections:
            adjacency[conn.hub_1].append((conn.hub_2, conn.hub_2.weight))
            adjacency[conn.hub_2].append((conn.hub_1, conn.hub_1.weight))

        return adjacency
