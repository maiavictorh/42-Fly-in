import pygame
from .graph import Graph
from .simulator import Simulator
from .utils import Color, DroneStatus as DS
from .models import Hub, Connection


class Renderer:
    """Window that draws the graph and animates the drones' movements."""
    def __init__(self, graph: Graph, simulator: Simulator):
        """
        Initialize pygame, the color palette and the playback state.

        The coordinate scale is computed here so the whole graph fits
        inside the window.

        Args:
            graph: Graph to draw.
            simulator: Simulator whose history will be replayed; it must
                have been run already.

        Attributes:
            history: drones' state information at each simulation turn
            width: screen's width in pixels, set as an arbitrary size
            height: screen's height in pixels, set as an arbitrary size
            margin: margin between screen edge and graph drawing
            hub_colors: supported colors for hubs
            font: text font and size for information display
            current_turn: counts the simulation steps
            playing: controls whether the simulation is in automatic movement
            step_ms: controls in milliseconds (ms)
                     the speed of the drones' moves
            last_step: Time in ms (pygame ticks) of the last automatic turn
                       advance, compared against step_ms to pace the autoplay.
        """
        pygame.init()
        self.graph = graph
        self.history = simulator.history
        self.width = 1900
        self.height = 1000
        self.margin = 50
        self._compute_scale()
        self.hub_colors = {
            Color.GREEN: (0, 150, 0),
            Color.YELLOW: (180, 150, 0),
            Color.RED: (150, 0, 0),
            Color.BLUE: (0, 50, 170),
            Color.GRAY: (150, 150, 150),
            Color.ORANGE: (205, 90, 0),
            Color.CYAN: (0, 150, 150),
            Color.PURPLE: (150, 0, 150),
            Color.BROWN: (139, 19, 0),
            Color.LIME: (150, 255, 0),
            Color.MAGENTA: (205, 0, 205),
            Color.GOLD: (172, 125, 5),
            Color.BLACK: (20, 20, 20),
            Color.MAROON: (178, 0, 0),
            Color.DARKRED: (89, 0, 0),
            Color.VIOLET: (150, 100, 170),
            Color.CRIMSON: (170, 0, 10),
            Color.RAINBOW: (150, 150, 150)
        }
        self.font = pygame.font.SysFont("Arial", 14, True)
        self.current_turn = 0
        self.playing = False
        self.step_ms = 500
        self.last_step = 0

    def run(self) -> None:
        """
        Open the window and run the display loop until it is closed.

        Controls: LEFT/RIGHT step backward/forward, SPACE toggles
        autoplay, R restarts from turn 0 and ESC or closing the window
        quits.
        """
        screen = pygame.display.set_mode((self.width, self.height),
                                         pygame.SCALED)
        pygame.display.set_caption("Fly-in")

        try:
            background = pygame.image.load("assets/background.jpg").convert()
            background = pygame.transform.scale(background,
                                                (self.width, self.height))
        except FileNotFoundError:
            background = None
        try:
            drone_img = pygame.image.load("assets/drone.png")
            drone_img = pygame.transform.scale(drone_img, (45, 45))
        except FileNotFoundError:
            drone_img = None

        clock = pygame.time.Clock()
        last_turn_index = len(self.history) - 1

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.playing = False
                        self.current_turn = min(self.current_turn + 1,
                                                last_turn_index)
                    elif event.key == pygame.K_LEFT:
                        self.playing = False
                        self.current_turn = max(self.current_turn - 1, 0)
                    elif event.key == pygame.K_SPACE:
                        self.playing = not self.playing
                    elif event.key == pygame.K_r:
                        self.playing = False
                        self.current_turn = 0
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()

            now = pygame.time.get_ticks()
            if self.playing and now - self.last_step >= self.step_ms:
                if self.current_turn < last_turn_index:
                    self.current_turn += 1
                    self.last_step = now
                else:
                    self.playing = False

            if background is not None:
                screen.blit(background, (0, 0))
            else:
                screen.fill((15, 0, 0))
            self._draw_graph(screen)
            self._draw_drones(screen, drone_img)
            self._draw_hud(screen)

            pygame.display.flip()
            clock.tick(30)

        pygame.quit()

    def _draw_graph(self, screen: pygame.Surface) -> None:
        """
        Draw every connection, then every hub with its name.

        Hubs with the rainbow color cycle through the palette over time.
        Hubs without a color are drawn in light gray, and names longer
        than 10 characters are truncated.

        Args:
            screen: Surface to draw on.
        """
        for conn in self.graph.connections:
            coords = [self._get_hub_pixels(conn.hub_1.coord),
                      self._get_hub_pixels(conn.hub_2.coord)]

            conn.draw_connetion(screen, coords)

        for hub in self.graph.hubs.values():
            coord = self._get_hub_pixels(hub.coord)

            if hub.color == Color.RAINBOW:
                rainbow_colors = [color for color in self.hub_colors]
                idx = (pygame.time.get_ticks() // 180) % len(rainbow_colors)
                rgb = self.hub_colors[rainbow_colors[idx]]
                hub.draw_hub(screen, rgb, coord)
            elif hub.color is not None:
                hub.draw_hub(screen, self.hub_colors[hub.color], coord)
            else:
                hub.draw_hub(screen, (200, 200, 200), coord)

            display_name = hub.name if len(hub.name) <= 10 else hub.name[:10]
            label = self.font.render(display_name, True, (255, 255, 255))
            screen.blit(label,
                        (coord[0] - label.get_width() // 2,
                         coord[1] - label.get_height() // 2))

    def _draw_drones(self, screen: pygame.Surface,
                     drone_img: pygame.Surface | None) -> None:
        """
        Draw the drones at their positions in the current turn.

        Drones on a hub are drawn at its center and drones on a
        connection at its midpoint. Drones sharing a position are
        offset so they do not fully overlap.

        Args:
            screen: Surface to draw on.
            drone_img: Sprite used for each drone.
        """
        position_counts: dict[tuple[int, int], int] = {}
        radius = 14

        for entry in self.history[self.current_turn]:
            id = f"D{entry["id"]}"
            location = entry["location"]

            if isinstance(location, Hub):
                coord = self._get_hub_pixels(location.coord)
            elif isinstance(location, Connection):
                coord = self._get_conn_pixels(location)

            count = position_counts.get(coord, 0)
            position_counts[coord] = count + 1

            center = (coord[0] + (count % 3) * 10 - 10,
                    coord[1] + (count // 3) * 10)

            if drone_img is not None:
                screen.blit(drone_img, drone_img.get_rect(center=center))
            else:
                pygame.draw.circle(screen, (250, 250, 250), center, radius)
                pygame.draw.circle(screen, (130, 130, 130), center, radius, 2)
                label = self.font.render(id, True, (0, 0, 0))
                screen.blit(label, label.get_rect(center=center))

    def _draw_hud(self, screen: pygame.Surface) -> None:
        """
        Draw the turn counter and the drone status totals.

        Args:
            screen: Surface to draw on.
        """
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
        """
        Compute the scale and origin that fit all hubs in the window.

        The same scale is used on both axes to keep the aspect ratio,
        and a zero-width range is treated as 1 to avoid division by zero.
        Sets self.scale, self.min_x and self.min_y.
        """
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
        """
        Convert grid coordinates into screen pixels.

        Args:
            coord: Hub position on the grid as (x, y).

        Returns:
            The matching position in pixels.
        """

        x = (coord[0] - self.min_x) * self.scale + self.margin
        y = (coord[1] - self.min_y) * self.scale + self.margin
        return (int(x), int(y))

    def _get_conn_pixels(self, conn: Connection) -> tuple[int, int]:
        """
        Get the screen position of a connection's midpoint.

        Args:
            conn: Connection to locate.

        Returns:
            The midpoint between its two hubs, in pixels.
        """
        coord1 = self._get_hub_pixels(conn.hub_1.coord)

        coord2 = self._get_hub_pixels(conn.hub_2.coord)
        return ((coord1[0] + coord2[0]) // 2, (coord1[1] + coord2[1]) // 2)
