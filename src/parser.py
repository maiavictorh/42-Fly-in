from .utils import Processor, ParserError
from .models import Hub, Connection
from .graph import Graph


class Parser(Processor):
    """Parse a map file into a Graph, validating every directive."""
    def __init__(self, file_name: str) -> None:
        """Initialize the parser.

        Args:
            file_name: Path of the map file to parse.

        Attributes:
            nb_drones: Number of drones stored by the parser.
            start_hub: start_hub stored by the parser.
            end_hub: end_hub stored by the parser.
            hubs: dict of hubs_names and hubs stored by the parser.
            connections: list of connections stored by the parser.
            end_conn_flag: flag for checking end_hub connectivity.
        """
        super().__init__()
        self.file_name = file_name
        self.nb_drones: int | None = None
        self.start_hub: Hub | None = None
        self.end_hub: Hub | None = None
        self.hubs: dict[str, Hub] = {}
        self.connections: list[Connection] = []
        self.end_conn_flag = False

    def parse(self) -> Graph:
        """
        Read the map file and build the corresponding Graph.

        This method takes into account several parsing constraints,
        for example:
            - Blank lines and lines starting with "#" are ignored.
            - After each directive, hub coordinates and connections
              are checked for duplicates.
            - Once the file is read, the mandatory directives and
            the end hub connectivity are verified.

        Returns:
            The Graph built from the parsed directives.

        Raises:
            ParserError: If the file has invalid syntax, duplicated
                coordinates or connections, missing mandatory directives,
                blocked start/end zones, or no connection to the end hub etc.
        """
        with open(self.file_name, "r") as file:

            for line_index, line in enumerate(start=1, iterable=file):

                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                elif ":" not in line:
                    raise ParserError(
                        f"Invalid syntax (missing ':') in line: {line_index}")

                self._handle_line(line, line_index)

                hub_names = []
                hub_coords = []
                for hub in self.hubs.values():
                    hub_names.append(hub.name)
                    if hub.coord in hub_coords:
                        raise ParserError("Duplicated coordinates for hub "
                                          f"in line: {line_index}")
                    hub_coords.append(hub.coord)

                checked_pairs: set[frozenset[Hub | None]] = set()
                for connection in self.connections:
                    if self.end_hub == connection.hub_1 \
                       or self.end_hub == connection.hub_2:
                        self.end_conn_flag = True

                    conn_pair = frozenset((connection.hub_1, connection.hub_2))
                    if conn_pair in checked_pairs:
                        raise ParserError(
                            f"Duplicated connection in line: {line_index}")
                    checked_pairs.add(conn_pair)

            if self.end_conn_flag is False:
                raise ParserError("Missing connection with end_hub")

        if self.nb_drones is None:
            raise ParserError("Missing nb_drones directive")
        if self.start_hub is None:
            raise ParserError("Missing start_hub directive")
        elif self.start_hub.zone.value == "blocked":
            raise ParserError("Invalid zone type for start hub")
        if self.end_hub is None:
            raise ParserError("Missing end_hub directive")
        elif self.end_hub.zone.value == "blocked":
            raise ParserError("Invalid zone type for end hub")

        return Graph(self.nb_drones, self.start_hub,
                     self.end_hub, self.hubs, self.connections)

    def _handle_line(self, line: str, line_index: int) -> None:
        """
        Dispatch a "key: value" line to the matching directive handler.

        Args:
            line: Stripped line containing a ":" separator.
            line_index: Line number, used in error messages.

        Raises:
            ParserError: If the directive key is not recognized.
        """
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()

        handlers = {
            "nb_drones": self._parse_nb_drones,
            "start_hub": self._parse_start_hub,
            "end_hub": self._parse_end_hub,
            "hub": self._create_hub,
            "connection": self._parse_connection
        }

        handler = handlers.get(key)

        if not handler:
            raise ParserError(
                f"Invalid directive \"{key}\" in line {line_index}")

        handler(value, line_index)

    def _parse_nb_drones(self, value: str, line_index: int) -> None:
        """
        Parse the nb_drones directive and store the drone count.

        Args:
            value: Raw directive value.
            line_index: Line number, used in error messages.

        Raises:
            ParserError: If the value is lower than 1 or the directive
                was already defined.
        """
        nb_drones = self.process_int(value, line_index, True)

        if nb_drones < 1:
            raise ParserError("Must contain at least one drone")

        if self.nb_drones is not None:
            raise ParserError(
                f"Duplicated number of drones on line: {line_index}")

        self.nb_drones = nb_drones

    def _parse_start_hub(self, value: str, line_index: int) -> None:
        """
        Parse the start_hub directive and register the start hub.

        Args:
            value: Raw hub definition.
            line_index: Line number, used in error messages.

        Raises:
            ParserError: If the start hub was already defined or the hub
                definition is invalid.
        """
        if self.start_hub is not None:
            raise ParserError(f"Duplicated start hub in line: {line_index}")

        self.start_hub = self._create_hub(value, line_index)

    def _parse_end_hub(self, value: str, line_index: int) -> None:
        """
        Parse the end_hub directive and register the end hub.

        Args:
            value: Raw hub definition.
            line_index: Line number, used in error messages.

        Raises:
            ParserError: If the end hub was already defined or the hub
                definition is invalid.
        """
        if self.end_hub is not None:
            raise ParserError(f"Duplicated end hub in line: {line_index}")

        self.end_hub = self._create_hub(value, line_index)

    def _create_hub(self, value: str, line_index: int) -> Hub:
        """
        Create a Hub from "name x y [metadata]" and register it.

        Args:
            value: Raw hub definition.
            line_index: Line number, used in error messages.

        Returns:
            The newly created Hub, already added to self.hubs.

        Raises:
            ParserError: If nb_drones is not defined yet, parameters are
                missing, the name has invalid characters or is duplicated,
                or the coordinates/metadata are invalid.
        """
        if self.nb_drones is None:
            raise ParserError(
                "nb_drones must be defined first")

        values = value.split(" ", 3)
        metadata = None
        hub = None
        invalid_chars = ['-', '=', '[', ']', ' ']

        if len(values) < 3:
            raise ParserError(
                f"Missing parameter for hub in line: {line_index}")

        name = self.process_str(values[0], line_index)
        for char in invalid_chars:
            if char in name:
                raise ParserError(
                    f"Invalid character for hub name in line: {line_index}")

        for h in self.hubs.values():
            if name == h.name:
                raise ParserError(f"Duplicated hub name in line: {line_index}")

        x = self.process_int(values[1], line_index)
        y = self.process_int(values[2], line_index)

        if len(values) > 3:
            metadata = self.process_metadata(values[3], line_index)

            hub = Hub(name, (x, y), metadata)

        else:
            hub = Hub(name, (x, y))

        self.hubs[hub.name] = hub
        return hub

    def _parse_connection(self, value: str, line_index: int) -> None:
        """
        Parse "hub1-hub2 [max_link_capacity=N]" and register it.

        Args:
            value: Raw connection definition.
            line_index: Line number, used in error messages.

        Raises:
            ParserError: If nb_drones is not defined yet, the syntax or
                metadata is invalid, both ends are the same hub, a hub is
                undefined, or max_link_capacity is lower than 1.
        """
        if self.nb_drones is None:
            raise ParserError(
                "nb_drones must be defined first")

        if "-" not in value:
            raise ParserError(
                f"Invalid connection syntax in line: {line_index}")

        hubs = value.split("-", 1)
        data = None
        metadata = {}

        if "[" in hubs[1]:
            if " " not in hubs[1]:
                raise ParserError(
                    f"Invalid connection syntax in line: {line_index}")
            raw_data = hubs[1].split(" ", 1)
            hubs[1] = raw_data[0]
            if "[" not in raw_data[1] or "]" not in raw_data[1]:
                raise ParserError("Invalid metadata syntax "
                                  f"for connection in line: {line_index}")
            data = raw_data[1].strip("[]")

        if len(hubs) < 2:
            raise ParserError(
                f"Invalid connection syntax in line: {line_index}")

        if hubs[0] == hubs[1]:
            raise ParserError("Invalid connection (same hub on both ends)"
                              f" in line: {line_index}")
        if hubs[0] not in self.hubs or hubs[1] not in self.hubs:
            raise ParserError(
                f"Connection references undefined hub in line: {line_index}")

        if data is not None:
            if "=" not in data:
                raise ParserError(f"Invalid metadata in line: {line_index}")
            raw_metadata = data.split("=", 1)
            if raw_metadata[0] != "max_link_capacity":
                raise ParserError(
                    f"Invalid metadata for connection in line: {line_index}")
            metadata[raw_metadata[0]] = \
                self.process_int(raw_metadata[1], line_index)
            if metadata["max_link_capacity"] < 1:
                raise ParserError(
                    f"Invalid metadata value in line: {line_index}")

            self.connections.append(
                Connection(self.hubs[hubs[0]], self.hubs[hubs[1]], metadata))

        else:
            self.connections.append(
                Connection(self.hubs[hubs[0]], self.hubs[hubs[1]]))
