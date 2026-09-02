import pygame
from .graph import Graph
from .simulator import Simulator


class Renderer:
    def __init__(self, graph: Graph, simulator: Simulator):
        self.graph = graph
        self.history = simulator.history

    def run(self) -> None:
        pygame.init()
