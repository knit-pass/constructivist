# ---------------------------------------------------------------------------- #
#                                   graph.py                                   #
# ---------------------------------------------------------------------------- #
import json
import logging
from .logger import Logger
from dotenv import dotenv_values
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable


class App:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    # ---------------- Functions to check if the category exists ---------------- #
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

    def __check_category(self, category):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
                self.__check_category_driver, category=category
            )
            return result

    # ------ Functions to create category and link it to user profile(KNOWS) ----- #
    @staticmethod
    def __create_category_driver(tx, category):
        global user_profile
        query = (
            "MATCH (u:Profile)"
            f"WHERE u.name = '{user_profile}'"
            "MERGE (u)-[r:KNOWS]->(t:Category {name : $category}) "
            "ON CREATE SET t.weight = 0.0 "
            "ON CREATE SET t.normalized_weight = 0.0 "
            "MERGE (t)-[:HAS]->(l1:Level {name: 'Level1'}) "
            "ON CREATE SET l1.value = 0.0 "
            "MERGE (t)-[:HAS]->(l2:Level {name: 'Level2'}) "
            "ON CREATE SET l2.value = 0.0 "
            "MERGE (t)-[:HAS]->(l3:Level {name: 'Level3'}) "
            "ON CREATE SET l3.value = 0.0 "
            "MERGE (t)-[:HAS]->(l4:Level {name: 'Level4'}) "
            "ON CREATE SET l4.value = 0.0 "
            "RETURN r"
        )
        try:
            result = tx.run(query, category=category)

            return [row for row in result]
        # Capture any errors along with the query and data for traceability
        except ServiceUnavailable as exception:
            logging.error(
                "{query} raised an error: \n {exception}".format(
                    query=query, exception=exception
                )
            )

    def __create_category(self, category):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
                self.__create_category_driver, category=category
            )
            return [row for row in result]

    def create_new_category(self, category):
        self.__create_category(category)
        Logger.write_debug("Category created: " + str(category))

    # ------- Functions to link topics to the Categories through sub-topics ------ #
    @staticmethod
    def __create_topic_relation_driver(tx, topic, level, category_result):
        global user_profile
        result = []
        query = (
            "MATCH (p:Profile{name:$name})-[:KNOWS]->(c:Category {name : $category})-[:HAS]->(l:Level {name : $level}) "
            "MERGE (t:Topic {name : $topic}) "
            "MERGE (l)<-[b:BELONGSTO]-(t) "
            "ON CREATE SET b.value = 0 "
            "SET b.value = b.value + $value "
            "SET l.value = l.value + $value "
            "SET c.weight = c.weight + $value "
            "RETURN c,t,b"
        )

        for i in category_result:
            try:
                result = tx.run(
                    query,
                    topic=topic,
                    level=level,
                    category=i,
                    value=float(category_result[i]),
                    name=user_profile,
                )
                # Logger.write_debug(result)
            except ServiceUnavailable as exception:
                Logger.write_error(
                    "{query} raised an error: \n {exception}".format(
                        query=query, exception=exception
                    )
                )
                continue
            except Exception as e:
                Logger.write_error(e)
                continue
        return [row for row in result]

    def __create_topic_relation(self, topic, level, category_result):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
                self.__create_topic_relation_driver,
                topic=topic,
                level=level,
                category_result=category_result,
            )
            return [row for row in result]

    def create_new_topic_relation(self, topic, level, categories_result):
        self.__create_topic_relation(topic, level, categories_result)
        Logger.write_debug("Topic created: " + str(topic) + " : " + str(level))

    # ---------------------- Functions to normalize weights ---------------------- #

    @staticmethod
    def __normalize_weights_driver(tx):
        global user_profile
        result = []
        query_normalize_levels = (
            "MATCH (p:Profile {name: $name})-[:KNOWS]->(c:Category) "
            "WITH collect(c) AS categories "
            "UNWIND categories as category "
            "MATCH (category)-[:HAS]->(l:Level) "
            "WITH category, MAX(l.value) AS max_value "
            "MATCH (category)-[:HAS]->(l:Level) "
            "SET l.normalized_value = "
            "CASE "
            "WHEN max_value > 0 THEN l.value / max_value "
            "ELSE 0 "
            "END "
            "RETURN l "
        )

        query_normalize_categories = (
            "MATCH (p:Profile{name:$name})-[:KNOWS]->(c:Category) "
            "WITH MAX(c.weight) AS max_value "
            "MATCH (p:Profile)-[:KNOWS]->(c1:Category) "
            "SET c1.normalized_weight = "
            "CASE "
            "WHEN max_value > 0 THEN c1.weight / max_value "
            "ELSE 0 "
            "END "
            "RETURN c1 "
        )
        result1 = tx.run(query_normalize_levels, name=user_profile)
        result2 = tx.run(query_normalize_categories, name=user_profile)
        return [result1, result2]

    def __normalize_weights(self):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(self.__normalize_weights_driver)
            return

    def normalize_weights(self):
        self.__normalize_weights()
        Logger.write_debug("Weights Normalized")

    # ------------------------ Functions to Fetch weights ------------------------ #
    @staticmethod
    def __fetch_weights_driver(tx, category):
        global user_profile
        query = """
            MATCH (p:Profile{name:$name})-[r1:KNOWS]->(c:Category{name:$category})-[r2:HAS]->(l:Level)<-[r3:BELONGSTO]-(t:Topic)
            RETURN t.name AS Topic,r3.value as TopicValue, l.name AS Level, l.value AS LevelValue, c.weight as CategoryWeight,c.name as Category
        """
        records = tx.run(query, category=category, name=user_profile).data()
        Logger.write_debug("DATA " + str(records))
        return records

    def __fetch_weights(self, category):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
                self.__fetch_weights_driver, category=category
            )
            return result

    def fetch_weights(self, category):
        Logger.write_debug("Weights fetched : " + str(category))
        return self.__fetch_weights(category)

    # ------------------------ Functions to fetch profiles ----------------------- #
    @staticmethod
    def __fetch_profiles_driver(tx):
        global user_profile

        query = """
           MATCH (p:Profile)
           RETURN p.name as profileNames
        """
        result = tx.run(query)

        profile_names = [record["profileNames"] for record in result]
        return profile_names

    def __fetch_profiles(self):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(self.__fetch_profiles_driver)
            return result

    def fetch_profiles(self):
        return self.__fetch_profiles()

    # ----------------------- Functions to create profiles ----------------------- #
    @staticmethod
    def __create_profile_driver(tx, name):
        query = """
            MERGE (p:Profile{name:$name})
        """

        tx.run(query, name=name)

    def __create_profile(self, name):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(self.__create_profile_driver, name=name)
            return result

    def create_profile(self, name):
        self.__create_profile(name)
        Logger.write_debug("Profile created : " + name)

    # ------------------------ Functions to delete profile ----------------------- #
    @staticmethod
    def __delete_profile_driver(tx, name):
        query = """
        OPTIONAL MATCH (p:Profile{name:$name})-[r1:KNOWS]->(c:Category)-[r2:HAS]->(l:Level)<-[r3:BELONGSTO]-(t:Topic)
            DETACH DELETE p, r1, c, r2, l, r3, t
        """
        tx.run(query, name=name)

    def __delete_profile(self, name):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(self.__delete_profile_driver, name=name)
            return result

    def delete_profile(self, name):
        self.__delete_profile(name)
        Logger.write_debug("Profile Deleted :" + name)

    def set_user_profile(name):
        global user_profile
        user_profile = name


creds = dotenv_values("neo4j_credentials.env")
uri = creds["NEO4J_URI"]
user = creds["NEO4J_USERNAME"]
password = creds["NEO4J_PASSWORD"]
user_profile = "user1"
# Root node of the graph
app = App(uri, user, password)


categories = [
    "Academic discipline",
    "Business",
    "Communication",
    "Culture",
    "Economy",
    "Education",
    "Energy",
    "Engineering",
    "Entertainment",
    "Food and drink",
    "Geography",
    "Government",
    "Health",
    "History",
    "Humanities",
    "Internet",
    "Knowledge",
    "Language",
    "Law",
    "Mass media",
    "Mathematics",
    "Military",
    "Nature",
    "Philosophy",
    "Politics",
    "Religion",
    "Science",
    "Society",
    "Sport",
    "Technology",
    "Universe",
]


def init_graph():
    for i in categories:
        app.create_new_category(i)
    app.close()


def test_graph():
    for c in categories:
        app.fetch_weights(c)
    app.close()


if __name__ == "__main__":
    init_graph()
