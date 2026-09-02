from sys import exit
from src import Menu, Parser, Simulator, Renderer, ParserError, \
                RED, EXIT, NC, CLEAR, PURPLE, IT


def main() -> None:

    try:
        menu = Menu()
        map = menu.run()

        parser = Parser(map)
        graph = parser.parse()

        print(CLEAR)

        # =================== TEST =================== #
        # print("nb_drones:", graph.nb_drones)
        # print("\nHubs:")
        # for h in graph.hubs.values():
        #     print(f"  name: {h.name} | coord: {h.coord} "
        #           f"| zone: {h.zone.value}, color: "
        #           f"{h.color.value if h.color is not None else 'none'}, "
        #           f"max_drones: {h.max_drones}")

        # print("\nConnections:")
        # for c in graph.connections:
        #     print("  ", end="")
        #     print("hub_1:", c.hub_1.name if c.hub_1 else 'none',
        #           "| hub_2:", c.hub_2.name if c.hub_2 else 'none',
        #           f"| max_link_capacity: {c.max_link_capacity}")
        # print()
        # print("=" * 80)
        # ============================================ #
        print(f" {PURPLE}┌──────────────────────────────┐")
        print(f" │            {IT}Fly-in{NC}            {PURPLE}│")
        print(f" {PURPLE}└──────────────────────────────┘{NC}\n")

        simulator = Simulator(graph)
        simulator.run()

        renderer = Renderer(graph, simulator)
        renderer.run()

    except ParserError as err:
        print(f"{RED}Error: {err}\n  {EXIT}Aborting...  {NC}")
        exit(1)


if __name__ == "__main__":
    main()
