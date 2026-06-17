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

    @staticmethod
    def process_metadata(value: str, line_index: int) -> dict[str, Any]:
        raw_data = value.split(" ")
        data = {}

        for raw in raw_data:
            raw = raw.strip("[]")
            if "=" not in raw:
                raise ValueError(f"Invalid metadata in line: {line_index}")
            d = raw.split("=", 1)
            data[d[0]] = d[1]

        return data
