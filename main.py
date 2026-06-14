from sys import argv, exit
from parser import Parser, ParserError


def main() -> None:
    PURPLE = "\33[1;35m"
    GREEN = "\33[32m"
    RED = "\33[31m"
    NC = "\33[0m"

    if len(argv) < 2:
        print(RED, "Too few arguments", NC)
        exit()

    try:
        print(PURPLE, "\n===== Initiating primary Test =====\n", NC)

        parser = Parser(argv[1])
        parser.parse()

        print("nb_drones:", parser.nb_drones)
        print()
        for h in parser.hubs:
            print(f"name: {h.name} | coord: {h.coord} ",
                  f"| metadata: {h.metadata}")
        print()

        for co in parser.connections:
            print(f"hub_1: {co.hub_1} | hub_2: {co.hub_2} "
                  f"| metadata: {co.metadata}")

    except (ValueError, ParserError) as err:
        print(RED, err, NC)
        exit()

    else:
        print(GREEN, "\n=== Program tested successfully! ===\n", NC)


if __name__ == "__main__":
    main()
