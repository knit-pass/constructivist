from src import *
from .app import *
def main():
    Logger.start_log()
    # transformers_demo()
    para = """
    Virat Kohli and Gautam Gambhir are both Indian cricketers who have played for the Indian national cricket team. They have shared the field in several matches as teammates, including during India's victorious campaign in the 2011 Cricket World Cup.
    """
    fetch_category_data(para,50)
    beginFunction()
    Logger.end_log()


if __name__ == "__main__":
    main()
