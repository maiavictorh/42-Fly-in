from typing import Optional, Any
from enum import Enum

PURPLE = "\33[1;35m"
YELLOW = "\33[93m"
GREEN = "\33[32m"
RED = "\33[31m"
EXIT = "\33[5;31m"
NC = "\33[0m"
IT = "\33[3m"
BOLD = "\33[1m"
CLEAR = "\33c"


class ParserError(Exception):
    """Raised when a map file contains invalid or inconsistent data."""
    ...


class ZoneType(Enum):
    """Type of a hub zone, which affects how drones can traverse it."""
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class DroneStatus(Enum):
    """Current state of a drone during the simulation."""
    WAITING = "waiting"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"


class Color(Enum):
    """Colors available for rendering hubs."""
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


class Processor:
    """Validation helpers used by the Parser to convert raw values."""
    def __init__(self) -> None:
        """Initialize the processor (no state is required)."""
        pass

    @staticmethod
    def process_int(value: str, line_index: int,
                    validate_negative: Optional[bool] = False) -> int:
        """
        Convert a raw string into an integer.

        Args:
            value: Raw string, which must not contain spaces.
            line_index: Line number, used in error messages.
            validate_negative: If True, negative values are rejected.

        Returns:
            The converted integer.

        Raises:
            ParserError: If the value is not a valid integer, or is
                negative while validate_negative is True.
        """
        try:
            if " " in value:
                raise ValueError
            new_value = int(value)
        except ValueError:
            raise ParserError(f"Expected integer in line: {line_index}")

        if validate_negative is True:
            if new_value < 0:
                raise ParserError(f"Negative Input in line: {line_index}")

        return new_value

    @staticmethod
    def process_str(value: str, line_index: int) -> str:
        """
        Strip a raw string and ensure it is not empty.

        Args:
            value: Raw string.
            line_index: Line number, used in error messages.

        Returns:
            The stripped string.

        Raises:
            ParserError: If the stripped string is empty.
        """
        new_value = value.strip()

        if len(new_value) == 0:
            raise ParserError(f"Empty input in line: {line_index}")

        return new_value

    def process_metadata(self, value: str, line_index: int) -> dict[str, Any]:
        """
        Parse hub metadata such as "[zone=normal color=blue]".

        Accepted keys are "zone" (must be a ZoneType value), "color"
        (alphabetic only) and "max_drones" (integer >= 1).

        Args:
            value: Raw metadata string, enclosed in square brackets.
            line_index: Line number, used in error messages.

        Returns:
            A dict mapping each metadata key to its value; "max_drones"
            is converted to int, the others are kept as strings.

        Raises:
            ParserError: If the brackets are missing, a key=value pair is
                malformed, a key is unknown, or a value is invalid.
        """
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
