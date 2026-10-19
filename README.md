*This project has been created as part of the 42 curriculum by <your_login>.*

# Fly-in

## Description

**Fly-in** is a drone delivery simulator written in Python. A fleet of drones starts on a `start_hub` and must reach an `end_hub` through a network of zones (hubs) and connections, in as few turns as possible, while respecting the capacity limits of every hub and every connection.

The map is described in a custom text file, parsed and validated by the program, turned into a graph, solved with a hand-written Dijkstra, simulated turn by turn, and finally replayed in a `pygame` window.

### Features

- Strict map parser with detailed error messages (line number included).
- Dijkstra's algorithm implemented from scratch (no graph libraries).
- Turn-based simulation engine with hub capacity (`max_drones`) and connection capacity (`max_link_capacity`).
- Zone types: `normal`, `blocked`, `restricted`, `priority`.
- Interactive terminal menu to pick a map by difficulty.
- `pygame` visualization with turn-by-turn navigation, autoplay and dynamic scaling to any map size.

## Instructions

### Requirements

- Python 3.10+
- `pygame` (installed through `requirements.txt`)

### Installation and execution

```bash
make install   # creates .venv and installs the dependencies
make run       # launches the program
```

Other Makefile rules:

| Rule | Description |
|---|---|
| `make debug` | Runs the program under `pdb` |
| `make lint` | Runs `flake8` and `mypy` with the standard flags |
| `make lint-strict` | Runs `flake8` and `mypy --strict` |
| `make clean` | Removes caches (`__pycache__`, `.mypy_cache`, ...) |
| `make fclean` | `clean` + removes the virtual environment |
| `make re` | `fclean` + `install` + `run` |

### Usage

1. Run `make run`. The menu offers:
   - **1. Easy / 2. Medium / 3. Hard**: opens a second screen with the maps of that difficulty;
   - **4. Challenger**: loads the challenger map;
   - **5. Custom**: loads `config.txt` from the project root.
   - `q` / `quit` leaves the program (or goes back from a difficulty submenu).
2. The simulation runs and prints each turn's moves to the terminal, followed by the total number of turns.
3. The `pygame` window opens to replay the simulation.

### Visualizer controls

| Key | Action |
|---|---|
| `→` | Next turn |
| `←` | Previous turn |
| `SPACE` | Toggle autoplay |
| `R` | Restart from turn 0 |
| `ESC` / close window | Quit |

The HUD shows the current turn and how many drones are waiting, in transit and delivered.

### Map file format

```
nb_drones: 5
start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [zone=restricted color=orange max_drones=2]
hub: waypoint2 2 0 [zone=priority color=blue]
end_hub: goal 3 0 [color=red]

connection: start-waypoint1
connection: waypoint1-waypoint2 [max_link_capacity=2]
connection: waypoint2-goal
```

Rules enforced by the parser:

- Blank lines and lines starting with `#` are ignored.
- Every line follows the `key: value` syntax. Valid keys: `nb_drones`, `start_hub`, `end_hub`, `hub`, `connection`.
- `nb_drones` must be defined first and be at least 1.
- Hub syntax: `name x y [metadata]`. Names cannot contain `-`, `=`, `[`, `]` or spaces, and must be unique. Two hubs cannot share the same coordinates.
- Hub metadata: `zone` (`normal`, `blocked`, `restricted`, `priority`), `color` (alphabetic) and `max_drones` (integer ≥ 1).
- Connection syntax: `hub1-hub2 [max_link_capacity=N]` with `N ≥ 1`. Both hubs must already exist, they must be different, and the same pair cannot be declared twice.
- `start_hub` and `end_hub` are mandatory, unique, cannot be `blocked`, and the end hub must have at least one connection.

Defaults: `zone=normal`, no color, `max_drones=1`, `max_link_capacity=1`.

### Project structure

```
.
├── main.py              # entry point
├── Makefile
├── requirements.txt
├── config.txt           # custom map (menu option 5)
├── maps/                # easy / medium / hard / challenger maps
├── assets/              # optional: background.jpg and drone.png
└── src/
    ├── menu.py          # terminal menu
    ├── parser.py        # map parsing and validation
    ├── models.py        # Drone, Hub, Connection
    ├── graph.py         # graph + Dijkstra
    ├── simulator.py     # turn engine
    ├── renderer.py      # pygame visualization
    └── utils.py         # enums, colors, ParserError, Processor
```

The `assets/` files are optional: without them the renderer falls back to a plain background and drawn circles for the drones.

## Algorithm and design choices

### Pathfinding

The map is converted into a bidirectional adjacency list where the weight of an edge is the **cost of entering the destination hub**, stored as a tuple `(turns, -priority)`:

- `turns` is `2` for `restricted` zones and `1` otherwise;
- `-priority` is `-1` when the destination is a `priority` zone and `0` otherwise.

Dijkstra (with a binary heap and an insertion counter as heap tie-breaker) compares these costs lexicographically, so it first minimizes the number of turns and, between paths with the same number of turns, prefers the one crossing more `priority` zones. It never enters `blocked` hubs. If the end hub is unreachable, the program reports that no valid path was found.

Pathfinding ignores capacities on purpose: it only decides *where* to go. Capacities are enforced by the simulation engine, which decides *when* each drone can move.

### Simulation

All drones follow the computed path. Each turn has two phases:

1. **Finish transits**: drones travelling towards a restricted zone advance one turn and, when done, arrive at the next hub (or become `DELIVERED` if it is the end hub).
2. **Start moves**: every waiting drone tries to move to the next hub of the path. The move is allowed only if the connection has free capacity and the destination hub is not full. The drone list order decides priority in case of conflicts.

Movement rules:

- Moves into `normal` / `priority` hubs take **1 turn** and resolve immediately.
- Moves into `restricted` hubs take **2 turns**: the drone stays `IN_TRANSIT` on the connection and cannot be interrupted.
- `start_hub` and `end_hub` have `max_drones = nb_drones`, so they are never limited by capacity.
- Connections used by instant moves are released at the end of the turn, so the capacity applies per turn.

After each turn, the state of every drone is saved in a history that the renderer replays, which is why the visualization can go backwards and forwards freely.

### Visualization

The `Renderer` computes one scale for both axes so the whole graph fits in the window while keeping the aspect ratio (with a guard against zero-width ranges). Drones on a hub are drawn on its center, drones in transit are drawn at the middle of the connection, and drones sharing a position are offset so they stay visible. Hubs with `color=rainbow` cycle through the palette over time.

## Resources

- [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Python `heapq` documentation](https://docs.python.org/3/library/heapq.html)
- [Pygame documentation](https://www.pygame.org/docs/)
- [PEP 484 – Type Hints](https://peps.python.org/pep-0484/)
- [PEP 257 – Docstring Conventions](https://peps.python.org/pep-0257/)
- 42 project subject (`en_subject.pdf`)

### Use of AI

<!-- Describe honestly which tasks AI helped with (e.g. design discussions, code review, README writing) and which parts you wrote and validated yourself. -->