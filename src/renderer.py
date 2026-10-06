import pygame
from .graph import Graph
from .simulator import Simulator
from .utils import Color, DroneStatus as DS
from .models import Hub, Connection


class Renderer:
    def __init__(self, graph: Graph, simulator: Simulator):
        pygame.init()
        self.graph = graph
        self.history = simulator.history
        self.width = 1600
        self.height = 900
        self.margin = 50
        self._compute_scale()
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
        self.font = pygame.font.SysFont("Arial", 12, True)
        self.current_turn = 0
        self.playing = False
        self.step_ms = 500
        self.last_step = 0

    def run(self) -> None:

        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fly-in")

        background = pygame.image.load("background.jpg").convert()
        background = pygame.transform.scale(background,
                                            (self.width, self.height))
        drone_img = pygame.image.load("drone.png")
        drone_img = pygame.transform.scale(drone_img, (20, 20))

        clock = pygame.time.Clock()
        last_turn_index = len(self.history) - 1

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.current_turn = min(self.current_turn + 1,
                                                last_turn_index)
                    elif event.key == pygame.K_LEFT:
                        self.current_turn = max(self.current_turn - 1, 0)
                    elif event.key == pygame.K_SPACE:
                        self.playing = not self.playing

            now = pygame.time.get_ticks()
            if self.playing and now - self.last_step >= self.step_ms:
                if self.current_turn < last_turn_index:
                    self.current_turn += 1
                    self.last_step = now
                else:
                    self.playing = False

            screen.blit(background, (0, 0))
            self._draw_graph(screen)
            self._draw_drones(screen, drone_img)
            self._draw_hud(screen)

            pygame.display.flip()
            clock.tick(30)

        pygame.quit()

    def _draw_graph(self, screen: pygame.Surface) -> None:
        for conn in self.graph.connections:
            coords = [self._get_hub_pixels(conn.hub_1.coord),
                      self._get_hub_pixels(conn.hub_2.coord)]

            conn.draw_connetion(screen, coords)

        for hub in self.graph.hubs.values():
            coord = self._get_hub_pixels(hub.coord)

            if hub.color == Color.RAINBOW:
                rainbow_colors = [color for color in self.hub_colors]
                idx = (pygame.time.get_ticks() // 200) % len(rainbow_colors)
                rgb = self.hub_colors[rainbow_colors[idx]]
                hub.draw_hub(screen, rgb, coord)
            elif hub.color is not None:
                hub.draw_hub(screen, self.hub_colors.get(hub.color), coord)
            else:
                hub.draw_hub(screen, (200, 200, 200), coord)

            display_name = hub.name if len(hub.name) <= 8 else hub.name[:8]
            label = self.font.render(display_name, True, (255, 255, 255))
            screen.blit(label,
                        (coord[0] - label.get_width() // 2,
                         coord[1] - label.get_height() // 2))

    def _draw_drones(self, screen: pygame.Surface,
                     drone_img: pygame.Surface) -> None:
        position_counts: dict[tuple[int, int], int] = {}

        for entry in self.history[self.current_turn]:
            location = entry["location"]

            if isinstance(location, Hub):
                coord = self._get_hub_pixels(location.coord)
            elif isinstance(location, Connection):
                coord = self._get_conn_pixels(location)

            count = position_counts.get(coord, 0)
            position_counts[coord] = count + 1

            offset_x = (count % 3) * 10 - 10
            offset_y = (count // 3) * 10
            rect = drone_img.get_rect(center=(coord[0] + offset_x,
                                              coord[1] + offset_y))
            screen.blit(drone_img, rect)

    def _draw_hud(self, screen: pygame.Surface) -> None:
        statuses = [entry["status"]
                    for entry in self.history[self.current_turn]]
        waiting = statuses.count(DS.WAITING)
        in_transit = statuses.count(DS.IN_TRANSIT)
        delivered = statuses.count(DS.DELIVERED)

        info = [f"Turn: {self.current_turn}/{len(self.history) - 1}",
                f"Waiting: {waiting}  "
                f"In transit: {in_transit}  "
                f"Delivered: {delivered}",]

        start_y = self.height - len(info) * 18 - 10
        for i, line in enumerate(info):
            label = self.font.render(line, True, (255, 255, 255))
            screen.blit(label, (10, start_y + i * 18))

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

    def _get_hub_pixels(self, coord: tuple[int, int]) -> tuple[int, int]:
        x = (coord[0] - self.min_x) * self.scale + self.margin
        y = (coord[1] - self.min_y) * self.scale + self.margin
        return (int(x), int(y))

    def _get_conn_pixels(self, conn: Connection) -> tuple[int, int]:
        coord1 = self._get_hub_pixels(conn.hub_1.coord)
        coord2 = self._get_hub_pixels(conn.hub_2.coord)
        return ((coord1[0] + coord2[0]) // 2, (coord1[1] + coord2[1]) // 2)
