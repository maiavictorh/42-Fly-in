from typing import Any, Optional


class ParserError(Exception):
    ...


class Hub:
    def __init__(self, name: str, coord: tuple[int, int],
                 metadata: Optional[dict[str, Any]] = None) -> None:
        self.name = name
        self.coord = coord
        self.metadata = metadata


class Connection:
    def __init__(self, hub_1: str, hub_2: str,
                 metadata: Optional[dict[str, Any]] = None) -> None:
        self.hub_1 = hub_1
        self.hub_2 = hub_2
        self.metadata = metadata


class Parser:
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.nb_drones: int | None = None
        self.start_hub: Hub | None = None
        self.end_hub: Connection | None = None
        self.hubs: list[Hub] = []
        self.connections: list[Connection] = []

    def parse(self) -> None:
        with open(self.file_name, "r") as file:

            for index, line in enumerate(start=1, iterable=file):

                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                elif ":" not in line:
                    raise ParserError(f"Invalid line: {index}")

                self._handle_line(line, index)

                hub_names = []
                for hub in self.hubs:
                    hub_names.append(hub.name)

                for connection in self.connections:
                    if connection.hub_1 not in hub_names:
                        raise ParserError("Invalid connection (First hub "
                                          f"not defined) in line: {index}")
                    if connection.hub_2 not in hub_names:
                        raise ParserError("Invalid connection (Second hub "
                                          f"not defined) in line: {index}")

    def _handle_line(self, line: str, index: int) -> None:
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()

        handlers = {
            "nb_drones": self._parse_nb_drones,
            "start_hub": self._parse_hub,
            "end_hub": self._parse_hub,
            "hub": self._parse_hub,
            "connection": self._parse_connection
        }

        handler = handlers.get(key)

        if not handler:
            raise ParserError(f"Invalid directive in line {index}")

        handler(value, index)

    def _parse_nb_drones(self, value: str, line_index: int) -> None:
        nb_drones = self.validate_int(value, line_index)

        if nb_drones < 1:
            raise ParserError("Must contain at least one drone")

        if self.nb_drones is not None:
            raise ParserError(
                f"Duplicated number of drones on line: {line_index}"
                )
        self.nb_drones = nb_drones

    def _parse_hub(self, value: str, line_index: int) -> None:
        values = value.split(" ", 3)
        metadata = None

        if len(values) < 3:
            raise ParserError(f"Invalid hub in line: {line_index}")

        name = self.validate_str(values[0], line_index)

        for hub in self.hubs:
            if name == hub.name:
                raise ParserError(f"Duplicated hub name in line: {line_index}")

        x = self.validate_int(values[1], line_index)
        y = self.validate_int(values[2], line_index)

        if len(values) > 3:
            metadata = self.validate_metadata(values[3], line_index)

            self.hubs.append(Hub(name, (x, y), metadata))

        else:
            self.hubs.append(Hub(name, (x, y)))

    def _parse_connection(self, value: str, line_index: int) -> None:
        connections = value.split("-", 1)
        data = None
        metadata = {}

        for hub in connections:
            if "[" in hub:
                raw_data = hub.split(" ", 1)
                connections[1] = raw_data[0]
                data = raw_data[1].strip("[]")

        if "-" in connections[0] or "-" in connections[1]:
            raise ParserError(f"Invalid connection name in line: {line_index}")

        if data is not None:
            raw_metadata = data.split("=", 1)
            metadata[raw_metadata[0]] = \
                self.validate_int(raw_metadata[1], line_index)

            self.connections.append(
                Connection(connections[0], connections[1], metadata))

        elif data is None:
            self.connections.append(
                Connection(connections[0], connections[1]))

    @staticmethod
    def validate_int(value: str, line_index: int) -> int:
        try:
            new_value = int(value)
        except ValueError:
            raise ParserError(f"Expected integer in line: {line_index}")

        if new_value < 0:
            raise ValueError(f"Negative Input in line: {line_index}")
        return new_value

    @staticmethod
    def validate_str(value: str, line_index: int) -> str:
        if len(value.strip()) == 0:
            raise ValueError(f"Empty input in line: {line_index}")
        return value

    @staticmethod
    def validate_metadata(value: str, line_index: int) -> dict[str, Any]:
        raw_data = value.split(" ")
        data = {}

        for raw in raw_data:
            raw = raw.strip("[]")
            if "=" not in raw:
                raise ValueError(f"Invalid metadata in line: {line_index}")
            d = raw.split("=", 1)
            data[d[0]] = d[1]

        return data
