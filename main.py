from src import *


def main():
    Logger.start_log()
    data = get_categories_cap("Inflation", 50)
    main_graph_test(data)
    Logger.end_log()


if __name__ == "__main__":
    main()
