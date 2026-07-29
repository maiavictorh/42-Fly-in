from .models import Hub, Connection, Drone


class Graph:
    def __init__(self, nb_drones: int,
                 start_hub: Hub,
                 end_hub: Hub,
                 hubs: list[Hub],
                 connections: list[Connection]) -> None:
        self.nb_drones = nb_drones
        self.start_hub = start_hub
        self.end_hub = end_hub
        self.hubs = hubs
        self.connections = connections
        self.start_hub.max_drones = nb_drones
        self.end_hub.max_drones = nb_drones
        self.drones = self._generate_drones()

    def _generate_drones(self) -> list[Drone]:
        drone_list = []
        for i in range(1, self.nb_drones):
            drone_list.append(Drone(f"D{i}", self.start_hub))

        return drone_list
