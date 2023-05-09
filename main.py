from src import *
from .app import *


def main():
    Logger.start_log()
    beginFunction()
    app.close()
    Logger.end_log()


if __name__ == "__main__":
    main()
