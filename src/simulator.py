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
            ...

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
        return None
