from src import *


def main():
    Logger.start_log()
    create_prompt_data("What is economic instability?")
    app.close()
    Logger.end_log()


if __name__ == "__main__":
    main()
