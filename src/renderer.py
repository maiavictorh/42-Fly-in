import pygame
from .graph import Graph


class Renderer:
    def __init__(self, graph: Graph):
        self.graph = graph

    def render(self) -> None:
        pygame.init()
