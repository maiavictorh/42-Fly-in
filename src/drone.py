from typing import Optional
from .models import Hub, Connection
from .utils import DroneStatus


class Drone:
    def __init__(self, id: int, start_hub: Hub) -> None:
        self.id = id
        self.current_hub: Optional[Hub] = start_hub
        self.status = DroneStatus.WAITING
        self.path: list[Hub] = []
        self.path_index = 0
        self.turns_remaining = 0
        self.current_connection: Optional[Connection] = None
