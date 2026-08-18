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
        self.conn_occupancy = \
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
        for drone in self.drones:
            drone.path = path

        turns = 0

        while self._is_delivered() is False:
            moves: list[str] = []

            for drone in self.drones:
                if drone.status == DS.IN_TRANSIT:
                    self._finish_move(drone, moves)

            for drone in self.drones:
                if drone.status == DS.DELIVERED:
                    continue
                if drone.status == DS.IN_TRANSIT:
                    continue

                next_hub = drone.path[drone.path_index + 1]
                if drone.current_hub is not None:
                    connection = self._get_connection(drone.current_hub,
                                                      next_hub)
                if connection is None:
                    continue

                if self._can_move(drone, connection, next_hub):
                    self._move(drone, connection, next_hub, moves)

            print("  ", " ".join(moves))
            turns += 1

        print("\n   Turns:", turns)

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

    def _can_move(self, drone: Drone, conn: Connection, next_hub: Hub) -> bool:

        if drone.status == DS.DELIVERED \
           or drone.current_connection is not None \
           or self.conn_occupancy[conn] >= conn.max_link_capacity \
           or self.hub_occupancy[next_hub] >= next_hub.max_drones:
            return False

        return True

    def _move(self, drone: Drone, conn: Connection, next_hub: Hub,
              moves: list[str]) -> None:
        self.conn_occupancy[conn] += 1
        self.hub_occupancy[next_hub] += 1

        if drone.current_hub is not None:
            self.hub_occupancy[drone.current_hub] -= 1

        drone.current_hub = None
        drone.current_connection = conn

        if next_hub.weight == 1:
            self.conn_occupancy[conn] -= 1
            drone.current_connection = None
            drone.path_index += 1
            drone.current_hub = next_hub
            drone.status = DS.DELIVERED \
                if drone.path_index == len(drone.path) - 1 else DS.WAITING
            moves.append(f"{drone}-{next_hub}")
        else:
            drone.turns_remaining = next_hub.weight
            drone.status = DS.IN_TRANSIT
            moves.append(f"{drone}-{conn}")

    def _finish_move(self, drone: Drone, moves: list[str]) -> None:
        drone.turns_remaining -= 1

        if drone.turns_remaining == 0:
            if drone.current_connection is not None:
                self.conn_occupancy[drone.current_connection] -= 1
            drone.current_connection = None
            drone.path_index += 1
            drone.current_hub = drone.path[drone.path_index]

            if drone.path_index == len(drone.path) - 1:
                drone.status = DS.DELIVERED
            else:
                drone.status = DS.WAITING

            moves.append(f"{drone}-{drone.current_hub}")
        else:
            moves.append(f"{drone}-{drone.current_connection}")
