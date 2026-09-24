import pygame
from .graph import Graph
from .simulator import Simulator
from .utils import Color


class Renderer:
    def __init__(self, graph: Graph, simulator: Simulator):
        self.graph = graph
        self.history = simulator.history
        self.width = 1280
        self.height = 620
        self.margin = 100
        self._compute_scale()
        pygame.init()
        self.font = pygame.font.SysFont("Arial", 12, True)
        self.hub_colors = {
            Color.GREEN: (0, 200, 0),
            Color.YELLOW: (230, 200, 0),
            Color.RED: (200, 0, 0),
            Color.BLUE: (0, 100, 220),
            Color.GRAY: (150, 150, 150),
            Color.ORANGE: (255, 140, 0),
            Color.CYAN: (0, 200, 200),
            Color.PURPLE: (150, 0, 200),
            Color.BROWN: (139, 69, 19),
            Color.LIME: (150, 255, 0),
            Color.MAGENTA: (255, 0, 255),
            Color.GOLD: (212, 175, 55),
            Color.BLACK: (20, 20, 20),
            Color.MAROON: (128, 0, 0),
            Color.DARKRED: (139, 0, 0),
            Color.VIOLET: (150, 100, 220),
            Color.CRIMSON: (220, 20, 60),
            Color.RAINBOW: (200, 200, 200)
        }

    def run(self) -> None:

        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fly-in")

        try:
            background = pygame.image.load("background.jpg").convert()
            background = pygame.transform.scale(background,
                                                (self.width, self.height))
        except FileNotFoundError:
            background = None

        clock = pygame.time.Clock()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            if background is not None:
                screen.blit(background, (0, 0))
            else:
                screen.fill((15, 0, 0))
            self._draw_graph(screen)

            pygame.display.flip()
            clock.tick(30)

        pygame.quit()

    def _draw_graph(self, screen: pygame.Surface) -> None:
        for conn in self.graph.connections:
            coords = [self._to_pixels(conn.hub_1.coord),
                      self._to_pixels(conn.hub_2.coord)]

            conn.draw_connetion(screen, coords)

        for hub in self.graph.hubs.values():
            coord = self._to_pixels(hub.coord)

            if hub.color == Color.RAINBOW:
                rainbow_colors = [color for color in self.hub_colors]
                idx = (pygame.time.get_ticks() // 200) % len(rainbow_colors)
                rgb = self.hub_colors[rainbow_colors[idx]]
                hub.draw_hub(screen, rgb, coord)
            elif hub.color is not None:
                hub.draw_hub(screen, self.hub_colors.get(hub.color), coord)
            else:
                hub.draw_hub(screen, (200, 200, 200), coord)

            display_name = hub.name if len(hub.name) <= 6 else hub.name[:6]
            label = self.font.render(display_name, True, (255, 255, 255))
            screen.blit(label,
                        (coord[0] - label.get_width() // 2,
                         coord[1] - label.get_height() // 2))

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
