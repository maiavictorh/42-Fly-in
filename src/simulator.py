from typing import Optional
from .graph import Graph
from .models import Drone, Hub, Connection
from .utils import DroneStatus as DS


class Simulator:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.drones = self._generate_drones()
        self.hub_occupancy = \
            {hub: 0 for hub in self.graph.hubs.values()}
        self.connection_occupancy = \
            {conn: 0 for conn in self.graph.connections}

    def _generate_drones(self) -> list[Drone]:
        drone_list = []
        for i in range(1, self.graph.nb_drones + 1):
            drone_list.append(Drone(i, self.graph.start_hub))

        return drone_list

    def run(self) -> None:
        path = self.graph.find_path()
        if not path:
            return
        for d in self.drones:
            d.path = path

        while self._is_delivered() is False:
            for d in self.drones:

                if d.status == DS.IN_TRANSIT:
                    d.turns_remaining -= 1

                    if d.turns_remaining == 0:
                        self.connection_occupancy[d.current_connection] -= 1
                        d.current_connection = None
                        d.path_index += 1
                        d.current_hub = d.path[d.path_index]
                        d.status = DS.WAITING

                        if d.path_index == len(d.path) - 1:
                            d.status = DS.DELIVERED

                elif d.status == DS.WAITING:
                    if d.path_index == len(d.path) - 1:
                        d.status = DS.DELIVERED
                        continue

                    next_hub = d.path[d.path_index + 1]
                    connection = self._get_connection(d.current_hub, next_hub)

                    if self._can_move(d, connection, next_hub):
                        self.hub_occupancy[d.current_hub] -= 1
                        self.hub_occupancy[next_hub] += 1
                        self.connection_occupancy[connection] += 1
                        d.current_connection = connection
                        d.turns_remaining = next_hub.weight
                        d.status = DS.IN_TRANSIT

    def _is_delivered(self) -> bool:
        for drone in self.drones:
            if drone.status != DS.DELIVERED:
                return False
        return True

    def _get_connection(self, current_hub: Hub,
                        next_hub: Hub) -> Optional[Connection]:

        for conn in self.graph.connections:
            if current_hub == conn.hub_1 and next_hub == conn.hub_2 \
               or current_hub == conn.hub_2 and next_hub == conn.hub_1:
                return conn

    def _can_move(self, drone: Drone,
                  connection: Connection, next_hub: Hub) -> bool:
        ...
