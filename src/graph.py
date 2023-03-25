from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable
from dotenv import load_dotenv, dotenv_values
from .wikipedia import *


class App:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    # ---------------- Functions to check if the category exists ---------------- #
    def __check_category(self, category):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
                self.__check_category_driver, category=category
            )
            return result

    @staticmethod
    def __check_category_driver(tx, category):
        query = "MATCH (t:Category{name : $category})" "RETURN t"
        result = tx.run(query, category=category)
        try:
            return [row for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query, exception=exception
                )
            )
            raise

    # ------ Functions to create category and link it to user profile(KNOWS) ----- #
    def __create_category(self, category):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
                self.__create_category_driver, category=category
            )
            return [row for row in result]

    @staticmethod
    def __create_category_driver(tx, category):
        global user_profile
        query = (
            "MATCH (u:Profile)"
            f"WHERE u.name = '{user_profile}'"
            "MERGE (u)-[r:KNOWS]->(t:Category {name : $category})"
            "RETURN r"
        )
        result = tx.run(query, category=category)
        try:
            return [row for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query, exception=exception
                )
            )

    def create_new_category(self, category):
        # res = self.__check_category(category)
        # if not res:
        #     self.__create_category(category)
        #     print("Category created: ", category)
        # else:
        #     print("Category already exists: ", category)
        self.__create_category(category)
        print("Category created: ", category)

    # ---- Functions to create topics and link them to categories (BELONGSTO) ---- #
    def __create_topic(self, topic, category):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
                self.__create_topic_driver, topic=topic, category=category
            )
            return [row for row in result]

    @staticmethod
    def __create_topic_driver(tx, topic, category):
        global user_profile
        # Creating a topic node with the name of the topic.
        query = (
            "MATCH (p:Profile)"
            f"WHERE p.name = '{user_profile}'"
            "MERGE (c:Category{name : $category})"
            "MERGE (t:Topic {name : $topic})"
            "MERGE (t)-[:BELONGSTO]->(c)"
            "MERGE (p)-[:KNOWS]->(c)"
            "RETURN t"
        )
        result = tx.run(query, topic=topic, category=category)
        try:
            return [row for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query, exception=exception
                )
            )

    def create_new_topic(self, topic, category):
        self.__create_topic(topic, category)
        print("Topic created: ", topic, " : ", category)

    # ------- Functions to link topics to the Categories through sub-topics ------ #
    def __create_topic_relation(self, topic, category):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
                self.__create_topic_relation_driver, topic=topic, category=category
            )
            return [row for row in result]

    @staticmethod
    def __create_topic_relation_driver(tx, topic, category):
        global user_profile
        # Creating a topic node with the name of the topic.
        result = []
        topic_wiki_page = get_nearest_wiki_links(topic)[0]
        category_wiki_page = get_nearest_wiki_links(category)[0]
        shortest_path = get_shortest_path(topic_wiki_page, category_wiki_page)
        if shortest_path[0] == 1:
            query = (
                "MATCH (c:Category {name : $category})"
                "MERGE (t:Topic {name : $topic})"
                "MERGE (c)<-[:BELONGSTO {level :1}]-(t)"
            )
            result = tx.run(query, topic=topic_wiki_page, category=category)
        elif shortest_path[0] == 2:
            query = (
                "MATCH (c:Category {name : $category})"
                "MERGE (t:Topic {name : $topic})"
                "MERGE (c)<-[:BELONGSTO {level :2}]-(t)"
            )
            result = tx.run(query, topic=topic_wiki_page, category=category)
        try:
            return [row for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query, exception=exception
                )
            )

    def create_new_topic_relation(self, topic, category):
        self.__create_topic_relation(topic, category)
        print("Topic created: ", topic, " : ", category)


creds = dotenv_values("neo4j_credentials.env")
uri = creds["NEO4J_URI"]
user = creds["NEO4J_USERNAME"]
password = creds["NEO4J_PASSWORD"]
user_profile = "user1"  # Root node of the graph
app = App(uri, user, password)

categories = [
    "Academic discipline",
    "Business",
    "Communication",
    "Concept",
    "Culture",
    "Economy",
    "Education",
    "Energy",
    "Engineering",
    "Entertainment",
    "Entity",
    "Ethics",
    "Food and drink",
    "Geography",
    "Government",
    "Health",
    "History",
    "Human behavior",
    "Humanities",
    "Information",
    "Internet",
    "Knowledge",
    "Language",
    "Law",
    "Life",
    "Mass media",
    "Mathematics",
    "Military",
    "Nature",
    "Person",
    "Philosophy",
    "Politics",
    "Religion",
    "Science",
    "Society",
    "Sport",
    "Technology",
    "Time",
    "Universe",
]


def main_graph_test():
    topic = "Alan Turing"
    for i in categories:
        app.create_new_category(i)
    for i in categories:
        app.create_new_topic_relation(topic, i)
    app.close()


if __name__ == "__main__":
    main_graph_test()
