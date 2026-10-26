from typing import Optional, Any
from .graph import Graph
from .models import Drone, Hub, Connection
from .utils import DroneStatus as DS


class Simulator:
    """Run the fleet along the shortest path, respecting all capacities."""
    def __init__(self, graph: Graph) -> None:
        """
        Initialize the simulator.

        All drones start waiting on the start hub, which holds the whole
        fleet at the beginning.

        Args:
            graph: Graph describing hubs, connections and fleet size.

        Attributes:
            drones: drones fleet, the main simulation attribute.
            hub_occupancy: counts how many drones are currently in the hub,
                           used to prevent capacity problems.
            conn_occupancy: counts how many drones are currently in the
                            connection, used to prevent capacity problems.
            history: shares information about the drones at each turn.
        """
        self.graph = graph
        self.drones = self._generate_drones()
        self.hub_occupancy = \
            {hub: 0 for hub in self.graph.hubs.values()}
        self.conn_occupancy = \
            {conn: 0 for conn in self.graph.connections}
        self.hub_occupancy[self.graph.start_hub] = self.graph.nb_drones
        self.history: list[list[dict[str, Any]]] = []

    def _generate_drones(self) -> list[Drone]:
        """
        Create the fleet, numbered from 1 and placed on the start hub.

        Returns:
            The list of drones.
        """
        drone_list = []
        for i in range(1, self.graph.nb_drones + 1):
            drone_list.append(Drone(i, self.graph.start_hub))

        return drone_list

    def run(self) -> bool:
        """
        Simulate turns until every drone is delivered.

        Each turn first finishes the moves of drones in transit, then
        moves waiting drones whenever connection and hub capacities
        allow. The moves of each turn are printed and the state of every
        drone is appended to the history.

        Returns:
            True if the simulation completed, False if there is no path
            from the start hub to the end hub.
        """
        path = self.graph.find_path()
        if not path:
            return False
        for drone in self.drones:
            drone.path = path

        turns = 0

        self.history.append([
            {"id": d.id,
             "location": d.current_hub,
             "status": d.status} for d in self.drones
        ])

        while self._is_delivered() is False:
            moves: list[str] = []
            arrived = set()
            instant_conns: set[Connection] = set()

            for drone in self.drones:
                if drone.status == DS.IN_TRANSIT:
                    self._finish_move(drone, moves)
                    arrived.add(drone)

            for drone in self.drones:
                if drone.status == DS.DELIVERED:
                    continue
                if drone.status == DS.IN_TRANSIT:
                    continue
                if drone in arrived:
                    continue

                next_hub = drone.path[drone.path_index + 1]
                if drone.current_hub is not None:
                    connection = self._get_connection(drone.current_hub,
                                                      next_hub)
                if connection is None:
                    continue

                if self._can_move(drone, connection, next_hub):
                    self._move(drone, connection, next_hub,
                               moves, instant_conns)

            for conn in instant_conns:
                self.conn_occupancy[conn] = 0

            self.history.append([
                {"id": drone.id,
                 "location": drone.current_hub or drone.current_connection,
                 "status": drone.status} for drone in self.drones
            ])

            print("  ", " ".join(moves))
            turns += 1

        print("\n   Turns:", turns)

        return True

    def _is_delivered(self) -> bool:
        """
        Check whether the whole fleet reached the end hub.

        Returns:
            True if every drone is DELIVERED.
        """
        for drone in self.drones:
            if drone.status != DS.DELIVERED:
                return False
        return True

    def _get_connection(self, current_hub: Hub,
                        next_hub: Hub) -> Optional[Connection]:
        """
        Find the connection between two hubs, in both directions.

        Args:
            current_hub: Hub where the drone is.
            next_hub: Hub the drone wants to reach.

        Returns:
            The matching Connection, or None if the hubs are not linked.
        """
        for conn in self.graph.connections:
            if current_hub == conn.hub_1 and next_hub == conn.hub_2 \
               or current_hub == conn.hub_2 and next_hub == conn.hub_1:
                return conn
        return None

    def _can_move(self, drone: Drone, conn: Connection, next_hub: Hub) -> bool:
        """
        Check whether a drone can start moving to the next hub.

        Args:
            drone: Drone that wants to move.
            conn: Connection it would use.
            next_hub: Destination hub.

        Returns:
            False if the drone is delivered or already on a connection,
            or if the connection or the destination hub is at capacity;
            True otherwise.
        """
        if drone.status == DS.DELIVERED \
           or drone.current_connection is not None \
           or self.conn_occupancy[conn] >= conn.max_link_capacity:
            return False

        return True

    def _move(self, drone: Drone, conn: Connection, next_hub: Hub,
              moves: list[str], instant_conns: set[Connection]) -> None:
        """
        Start a move, updating occupancy and the drone state.

        If the destination has weight 1 the drone arrives right away and
        the connection is queued to be released at the end of the turn.
        Otherwise the drone stays in transit on the connection.

        Args:
            drone: Drone that moves.
            conn: Connection it uses.
            next_hub: Destination hub.
            moves: Moves of the current turn, extended with this one.
            instant_conns: Connections to release at the end of the turn.
        """
        self.conn_occupancy[conn] += 1
        self.hub_occupancy[next_hub] += 1

        if drone.current_hub is not None:
            self.hub_occupancy[drone.current_hub] -= 1

        drone.current_hub = None
        drone.current_connection = conn

        if next_hub.weight == 1:
            instant_conns.add(conn)
            drone.current_connection = None
            drone.path_index += 1
            drone.current_hub = next_hub
            drone.status = DS.DELIVERED \
                if drone.path_index == len(drone.path) - 1 else DS.WAITING
        else:
            drone.turns_remaining = next_hub.weight - 1
            drone.status = DS.IN_TRANSIT

        moves.append(f"{drone}-"
                     f"{drone.current_hub or drone.current_connection}")

    def _finish_move(self, drone: Drone, moves: list[str]) -> None:
        """
        Advance a drone in transit by one turn.

        When the remaining turns reach zero, the drone leaves the
        connection, arrives at the next hub on its path and becomes
        WAITING, or DELIVERED if that hub is the end hub.

        Args:
            drone: Drone currently in transit.
            moves: Moves of the current turn, extended with this one.
        """
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
