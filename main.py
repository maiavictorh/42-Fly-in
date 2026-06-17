from sys import exit
from src import Parser, ParserError
from time import sleep


PURPLE = "\33[1;35m"
EXIT = "\33[5;31m"
YELLOW = "\33[93m"
GREEN = "\33[32m"
RED = "\33[31m"
NC = "\33[0m"
IT = "\33[3m"
BOLD = "\33[1m"
CLEAR = "\33c"


# TEST
def print_info(parser: Parser) -> None:
    print("nb_drones:", parser.nb_drones)

    print("\nHubs:")
    for h in parser.hubs:
        print(f"  name: {h.name} | coord: {h.coord} "
              f"| metadata: {h.metadata}")

    print("\nConnections:")
    for co in parser.connections:
        print(f"  hub_1: {co.hub_1} | hub_2: {co.hub_2} "
              f"| metadata: {co.metadata}")


def menu() -> str:
    maps = {
        "easy": {
            "1": "maps/easy/01_linear_path.txt",
            "2": "maps/easy/02_simple_fork.txt",
            "3": "maps/easy/03_basic_capacity.txt"
        },
        "medium": {
            "1": "maps/medium/01_dead_end_trap.txt",
            "2": "maps/medium/02_circular_loop.txt",
            "3": "maps/medium/03_priority_puzzle.txt"
        },
        "hard": {
            "1": "maps/hard/01_maze_nightmare.txt",
            "2": "maps/hard/02_capacity_hell.txt",
            "3": "maps/hard/03_ultimate_challenge.txt"
        },
        "challenger": {
            "1": "maps/challenger/01_the_impossible_dream.txt"
        }
    }

    choice = None

    print(CLEAR)
    print(f"  {PURPLE}╔══════════════════════════╗")
    print(f"  ║          {IT}Fly-in{NC}          {PURPLE}║")
    print(f"  {PURPLE}╚══════════════════════════╝{NC}")
    print("   Choose difficulty\n"
          "    1. Easy\n"
          "    2. Medium\n"
          "    3. Hard\n"
          "    4. Challenger\n"
          "    5. Custom")

    match input("\n   Choice: (1-5) or Quit: "):
        case "1":
            print(CLEAR)
            print(f"   {GREEN}{BOLD}=== Easy ==={NC}")
            print("    1. Linear_path.txt")
            print("    2. Simple_fork.txt")
            print("    3. Basic_capacity.txt")
            match input("\n   Choice: (1-3) or Quit: "):
                case "1":
                    choice = maps.get("easy").get("1")
                case "2":
                    choice = maps.get("easy").get("2")
                case "3":
                    choice = maps.get("easy").get("3")
                case "Quit" | "quit" | "q":
                    print(CLEAR)
                    menu()
                case _:
                    print(YELLOW, "   \33[5mInvalid Option...\n", NC)
                    sleep(2)
                    menu()
        case "2":
            print(CLEAR)
            print(f"   {YELLOW}{BOLD}=== Medium ==={NC}")
            print("    1. Dead_end_trap.txt")
            print("    2. Circular_loop.txt")
            print("    3. Priority_puzzle.txt")
            match input("\n   Choice: (1-3) or Quit: "):
                case "1":
                    choice = maps.get("medium").get("1")
                case "2":
                    choice = maps.get("medium").get("2")
                case "3":
                    choice = maps.get("medium").get("3")
                case "Quit" | "quit" | "q":
                    print(CLEAR)
                    menu()
                case _:
                    print(YELLOW, "   \33[5mInvalid Option...\n", NC)
                    sleep(2)
                    menu()
        case "3":
            print(CLEAR)
            print(f"   {RED}{BOLD}=== Hard ==={NC}")
            print("    1. Maze_nightmare.txt")
            print("    2. Capacity_hell.txt")
            print("    3. Priority_puzzle.txt")
            match input("\n   Choice: (1-3) or Quit: "):
                case "1":
                    choice = maps.get("hard").get("1")
                case "2":
                    choice = maps.get("hard").get("2")
                case "3":
                    choice = maps.get("hard").get("3")
                case "Quit" | "quit" | "q":
                    print(CLEAR)
                    menu()
                case _:
                    print(YELLOW, "   \33[5mInvalid Option...\n", NC)
                    sleep(2)
                    menu()
        case "4":
            choice = maps.get("challenger").get("1")
        case "5":
            choice = "config.txt"
        case "Quit" | "quit" | "q":
            print(CLEAR)
            exit()
        case _:
            print(YELLOW, "   \33[5mInvalid Option...\n", NC)
            sleep(2)
            print(CLEAR)
            menu()

    return choice


def main() -> None:

    try:
        map = menu()

        parser = Parser(map)
        parser.parse()

        print(CLEAR)
        print(PURPLE, "\n===== Initiating primary Test =====\n", NC)
        print(f"\n{map}\n")
        print_info(parser)

    except (ValueError, ParserError) as err:
        print(f"{RED}Error: {err}\n  {EXIT}Aborting...  {NC}")
        exit(1)

    else:
        print(GREEN, "\n=== Program tested successfully! ===\n", NC)


if __name__ == "__main__":
    main()
