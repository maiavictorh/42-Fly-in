from .graph import Graph
# from .models import Hub, Drone
# from .utils import DroneStatus


class Simulator:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def run(self) -> None:
        ...

    def move(self) -> None:
        ...

    def can_move(self) -> bool:

        return False
