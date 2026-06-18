from abc import ABC
from typing import Optional, Any


class ParserError(Exception):
    ...


class Processor(ABC):
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
                raise ValueError(f"Negative Input in line: {line_index}")

        return new_value

    @staticmethod
    def process_str(value: str, line_index: int) -> str:
        if len(value.strip()) == 0:
            raise ValueError(f"Empty input in line: {line_index}")
        return value

    def process_metadata(self, value: str, line_index: int) -> dict[str, Any]:
        raw_data = value.split(" ")
        data = {}
        valid_metadata = ["zone", "color", "max_drones"]

        for raw in raw_data:
            raw = raw.strip("[]")
            if "=" not in raw:
                raise ValueError(f"Invalid metadata in line: {line_index}")
            d = raw.split("=", 1)
            if d[0] not in valid_metadata:
                raise ParserError(
                    f"Invalid metadata value in line: {line_index}")
            if d[0] == "max_drones":
                data[d[0]] = self.process_int(d[1], line_index)
            else:
                data[d[0]] = d[1]

        return data
