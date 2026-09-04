import pygame
from .graph import Graph
from .simulator import Simulator


class Renderer:
    def __init__(self, graph: Graph, simulator: Simulator):
        self.graph = graph
        self.history = simulator.history

    def run(self) -> None:
        pygame.init()
        screen = pygame.display.set_mode((1280, 720))
        clock = pygame.time.Clock()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.fill((30, 30, 30))
            self._draw_graph(screen)

            pygame.display.flip()
            clock.tick(30)

        pygame.quit()
