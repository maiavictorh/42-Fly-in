from .graph import Graph
from .models import Drone
from .utils import DroneStatus as DS, ZoneType as ZT


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

        while self._is_delivered():
            for d in self.drones:

                if d.status == DS.DELIVERED:
                    continue

                elif d.status == DS.WAITING:
                    ...

                elif d.status == DS.IN_TRANSIT:
                    print(f"{d}-{d.current_connection}")
                

    def _is_delivered(self) -> bool:
        for drone in self.drones:
            if drone.status != DS.DELIVERED:
                return False
        return True

    def _move(self, drone: Drone) -> None:
        ...

    def _can_move(self, drone: Drone) -> bool:

        if drone.status == DS.DELIVERED:
            return False

        return True
