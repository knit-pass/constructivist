from src import *


def main():
    Logger.start_log()
    create_prompt_data("What is economic instability?")
    # graph_test()
    Logger.end_log()


if __name__ == "__main__":
    main()
