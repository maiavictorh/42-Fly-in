from .graph import Graph
# from .models import Hub, Drone
# from .utils import DroneStatus


class Simulator:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def run(self) -> None:

        for d in self.graph.drones:
            d.path = self.graph.find_path()

            # # ========= TEST ========= #
            # print(f"Drone {d.id}:", end=" ")
            # for h in d.path:
            #     print(h.name, end=" ")
            # print("\n")
            # # ======================== #

    def move(self) -> None:
        ...

    def can_move(self) -> bool:

        return False
