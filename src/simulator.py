from .graph import Graph
# from .models import Hub, Drone
# from .utils import DroneStatus


class Simulator:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def run(self) -> None:

        for d in self.graph.drones:
            d.path = self.graph.find_path()
            if not d.path:
                return

        print(f"{self.graph.drones[0]}: {self.graph.drones[0].path}")

    def move(self) -> None:
        ...

    def can_move(self) -> bool:

        return False
