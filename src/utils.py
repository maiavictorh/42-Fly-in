from typing import Optional, Any
from enum import Enum


class ParserError(Exception):
    ...


class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Color(Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"
    BLUE = "blue"
    GRAY = "gray"
    ORANGE = "orange"
    CYAN = "cyan"
    PURPLE = "purple"
    BROWN = "brown"
    LIME = "lime"
    MAGENTA = "magenta"
    GOLD = "gold"
    BLACK = "black"
    MAROON = "maroon"
    DARKRED = "darkred"
    VIOLET = "violet"
    CRIMSON = "crimson"
    RAINBOW = "rainbow"


class DroneStatus(Enum):
    WAITING = "waiting"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"


class Processor:
    def __init__(self) -> None:
        pass

    @staticmethod
    def process_int(value: str, line_index: int,
                    validate_negative: Optional[bool] = False) -> int:
        try:
            new_value = int(value)
        except ValueError:
            raise ParserError(f"Expected integer in line: {line_index}")

        if validate_negative is True:
            if new_value < 0:
                raise ParserError(f"Negative Input in line: {line_index}")

        return new_value

    @staticmethod
    def process_str(value: str, line_index: int) -> str:
        new_value = value.strip()

        if len(new_value) == 0:
            raise ParserError(f"Empty input in line: {line_index}")

        return new_value

    def process_metadata(self, value: str, line_index: int) -> dict[str, Any]:
        raw_data = value.split(" ")
        data: dict[str, Any] = {}
        valid_metadata = ["zone", "color", "max_drones"]
        valid_zones = [zone.value for zone in ZoneType]

        if "[" not in value or "]" not in value:
            raise ParserError(
                f"Invalid metadata syntax for hub in line: {line_index}")

        for raw in raw_data:
            raw = raw.strip("[]")

            if "=" not in raw:
                raise ParserError(f"Invalid metadata in line: {line_index}")

            d = raw.split("=", 1)

            if d[0] not in valid_metadata:
                raise ParserError(
                    f"Invalid metadata value in line: {line_index}")
            if d[0] == "zone":
                if d[1] not in valid_zones:
                    raise ParserError(
                        f"Invalid metadata zone in line: {line_index}")
            if d[0] == "color":
                if not d[1].isalpha():
                    raise ParserError(
                        f"Invalid metadata color in line: {line_index}")
            if d[0] == "max_drones":
                data[d[0]] = self.process_int(d[1], line_index)
                if data[d[0]] < 1:
                    raise ParserError(
                        f"Minimun max_drones must be 1 in line: {line_index}")
            else:
                data[d[0]] = d[1]

        return data
