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
            for hub in d.path:
                d.turns_remaining += 2 if hub.zone == ZT.RESTRICTED else 1

        while not self._is_delivered():

            for drone in self.drones:
                if drone.path_index == len(drone.path) - 1:
                    drone.status = DS.DELIVERED

                print(drone, drone.path_index, drone.current_hub)

                if self._can_move(drone):
                    self._move(drone)

    def _is_delivered(self) -> bool:
        for drone in self.drones:
            if drone.status != DS.DELIVERED:
                return False
        return True

    def _move(self, drone: Drone) -> None:
        drone.path_index += 1
        drone.current_hub = drone.path[drone.path_index]
        self.hub_occupancy[drone.current_hub] += 1

    def _can_move(self, drone: Drone) -> bool:

        if drone.status == DS.DELIVERED:
            return False

        return True
