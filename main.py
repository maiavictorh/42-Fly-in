from sys import exit, argv
from src import Menu, Parser, Simulator, Renderer, ParserError, \
                RED, EXIT, NC, CLEAR, PURPLE, IT, YELLOW


def main() -> None:
    flag = False

    try:
        if len(argv) == 2:
            map = argv[1]
        elif len(argv) == 3:
            if argv[1] != "--capacity-info":
                print(CLEAR, "Invalid flag")
                return
            map = argv[2]
            flag = True
        else:
            menu = Menu()
            map = menu.run()

        parser = Parser(map)
        graph = parser.parse()

        print(CLEAR)
        print(f" {PURPLE}┌──────────────────────────────┐")
        print(f" │            {IT}Fly-in{NC}            {PURPLE}│")
        print(f" {PURPLE}└──────────────────────────────┘{NC}\n")

        simulator = Simulator(graph, flag)
        if simulator.run() is False:
            print(f"{RED}  No valid path found!{NC}")

        renderer = Renderer(graph, simulator)
        renderer.run()

    except ParserError as err:
        print(CLEAR)
        print(f"{RED}Error: {err}\n  {EXIT}Aborting...  {NC}")
    except KeyboardInterrupt:
        print(CLEAR)
        print(f"  {YELLOW}Program Interrupted!{NC}")
    finally:
        exit()


if __name__ == "__main__":
    main()
