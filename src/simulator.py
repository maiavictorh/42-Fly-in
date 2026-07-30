from .graph import Graph
from .models import Hub
from .drone import Drone, DroneStatus


class Simulator:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def run(self) -> None:
        ...

    def move(self) -> None:
        ...

    def can_move(self, drone: Drone, next_hub: Hub) -> bool:

        return (drone.status != DroneStatus.DELIVERED
                and drone.path[drone.path_index + 1])
