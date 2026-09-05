import pygame
from .graph import Graph
from .simulator import Simulator


class Renderer:
    def __init__(self, graph: Graph, simulator: Simulator):
        self.graph = graph
        self.history = simulator.history
        self.width = 1280
        self.height = 720
        self.margin = 100
        self._compute_scale()

    def run(self) -> None:
        pygame.init()

        screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Fly-in")

        background = pygame.image.load("background.jpg")
        background = pygame.transform.scale(screen, (1280, 720))

        clock = pygame.time.Clock()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            screen.blit(background, (0, 0))
            self._draw_graph(screen)

            pygame.display.flip()
            clock.tick(30)

        pygame.quit()

    def _draw_graph(self, screen: pygame.Surface) -> None:
        for conn in self.graph.connections:
            pygame.draw.line(screen, (100, 100, 100),
                             self._to_pixels(conn.hub_1.coord),
                             self._to_pixels(conn.hub_2.coord), 2)

        for hub in self.graph.hubs.values():
            pygame.draw.circle(screen, (200, 200, 200),
                               self._to_pixels(hub.coord), 20)

    def _compute_scale(self) -> None:
        xs = [hub.coord[0] for hub in self.graph.hubs.values()]
        ys = [hub.coord[1] for hub in self.graph.hubs.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        range_x = max_x - min_x or 1
        range_y = max_y - min_y or 1

        scale_x = (self.width - 2 * self.margin) / range_x
        scale_y = (self.height - 2 * self.margin) / range_y
        self.scale = min(scale_x, scale_y)

        self.min_x = min_x
        self.min_y = min_y

    def _to_pixels(self, coord: tuple[int, int]) -> tuple[int, int]:
        x = (coord[0] - self.min_x) * self.scale + self.margin
        y = (coord[1] - self.min_y) * self.scale + self.margin
        return (int(x), int(y))
