from sys import exit
from time import sleep
from typing import Any


class Menu:
    def __init__(self):
        pass

    @staticmethod
    def run() -> Any:

        PURPLE = "\33[1;35m"
        YELLOW = "\33[93m"
        GREEN = "\33[32m"
        RED = "\33[31m"
        NC = "\33[0m"
        IT = "\33[3m"
        BOLD = "\33[1m"
        CLEAR = "\33c"

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

        while True:
            print(CLEAR)
            print(f" {PURPLE}┌──────────────────────────┐")
            print(f" │          {IT}Fly-in{NC}          {PURPLE}│")
            print(f" {PURPLE}└──────────────────────────┘{NC}")
            print(f"   {BOLD}{GREEN}Choose difficulty:{NC}\n"
                "    1. Easy\n"
                "    2. Medium\n"
                "    3. Hard\n"
                "    4. Challenger\n"
                "    5. Custom")

            choice = input("\n   Choice: (1-5) or Quit: ")

            if choice in ("Quit", "quit", "q"):
                print(CLEAR)
                exit()

            if choice == "4":
                return maps["challenger"]["1"]

            if choice == "5":
                return "config.txt"

            if choice not in ("1", "2", "3"):
                print(YELLOW, "   \33[5mInvalid Option...\n", NC)
                sleep(2)
                continue

            difficulty = {"1": "easy", "2": "medium", "3": "hard"}[choice]
            labels = {
                "easy": (GREEN, ["Linear_path.txt",
                                "Simple_fork.txt",
                                "Basic_capacity.txt"]),
                "medium": (YELLOW, ["Dead_end_trap.txt",
                                    "Circular_loop.txt",
                                    "Priority_puzzle.txt"]),
                "hard": (RED, ["Maze_nightmare.txt",
                            "Capacity_hell.txt",
                            "Ultimate_challenge.txt"]),
            }
            color, files = labels[difficulty]

            print(CLEAR)
            print(f" {PURPLE}┌──────────────────────────┐")
            print(f" │          {IT}Fly-in{NC}          {PURPLE}│")
            print(f" {PURPLE}└──────────────────────────┘{NC}")
            print(f"   {BOLD}{color}{difficulty.capitalize()}:{NC}")
            for i, f in enumerate(files, start=1):
                print(f"    {i}. {f}")

            sub_choice = input("\n   Choice: (1-3) or Quit: ")

            if sub_choice in ("Quit", "quit", "q"):
                continue

            if sub_choice in maps[difficulty]:
                return maps[difficulty][sub_choice]

            print(YELLOW, "   \33[5mInvalid Option...\n", NC)
            sleep(2)
