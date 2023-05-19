# ---------------------------------------------------------------------------- #
#                                    main.py                                   #
# ---------------------------------------------------------------------------- #
from app import *
from src import Logger


def main():
    Logger.start_log()
    begin_app()
    Logger.end_log()


if __name__ == "__main__":
    main()
