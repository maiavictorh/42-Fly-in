class ParserError(Exception):
    ...


class Parser:
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.handlers = {
            "nb_drones": self._parse_nb_drones,
            "start_hub": self._parse_start_end_hub,
            "end_hub": self._parse_start_end_hub,
            "hub": self._parse_hub,
            "connection": self._parse_connection
        }

    def parse(self) -> None:
        with open(self.file_name, "r") as file:
            lines = []

            for index, line in enumerate(file, 1):
                line = line.strip()

                if not line or line.startswith("#"):
                    continue
                elif ":" not in line:
                    raise ParserError(f"Invalid line: {index}")

                lines.append((index, line))
                self._handle_line(line, index)

    def _handle_line(self, line: str, index: int) -> None:
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        # print(f"{key} = {value}")

        if key not in self.handlers.keys():
            raise ParserError(f"Invalid directive in line: {index}")

        handler = self.handlers.get(key)
        handler(value, index)

    def _parse_nb_drones(self, value: str, line_index: int) -> None:
        new_value = self.validate_int(value, line_index)

        if new_value < 1:
            raise ParserError("Must contain at least one drone")

    def _parse_start_end_hub(self, value: str, line_index: int) -> None:
        values = value.split(" ", 3)
        name = self.validate_str(values[0], line_index)
        x = self.validate_int(values[1], line_index)
        y = self.validate_int(values[2], line_index)
        if len(values) > 3:
            metadata = self.validate_metadata(values[3], line_index)

        print(name)
        print(x)
        print(y)
        print(metadata, "\n")

    def _parse_hub(self, value: str, line_index: int) -> None:
        ...

    def _parse_connection(self, value: str, line_index: int) -> None:
        ...

    @staticmethod
    def validate_int(value: str, line_index: int) -> int:
        new_value = int(value)

        if new_value < 0:
            raise ValueError(f"Negative Input in line: {line_index}")
        return new_value

    @staticmethod
    def validate_str(value: str, line_index: int) -> str:
        if len(value.strip()) == 0:
            raise ValueError(f"Empty input in line: {line_index}")
        return value

    @staticmethod
    def validate_metadata(value: str, line_index: int) -> dict[str]:
        raw_data = value.split(" ")
        data = {}

        for r in raw_data:
            if "=" not in r:
                raise ValueError(f"Invalid metadata in line: {line_index}")
            d = r.split("=", 1)
            data[d[0]] = d[1]

        return data
