import json
import logging
from dotenv import dotenv_values
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable


class App:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    #!--------------------------------------------------------------------------------------------------
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
            "MERGE (u)-[r:KNOWS]->(t:Category {name : $category}) "
            "ON CREATE SET t.weight = 0.0 "
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

    def create_new_category(self, category):
        # res = self.__check_category(category)
        # if not res:
        #     self.__create_category(category)
        #     print("Category created: ", category)
        # else:
        #     print("Category already exists: ", category)
        self.__create_category(category)
        print("Category created: ", category)

    #!--------------------------------------------------------------------------------------------------

    # ------- Functions to link topics to the Categories through sub-topics ------ #
    def __create_topic_relation(self, topic, level, category_result):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
                self.__create_topic_relation_driver,
                topic=topic,
                level=level,
                category_result=category_result,
            )
            return [row for row in result]

    @staticmethod
    def __create_topic_relation_driver(tx, topic, level, category_result):
        global user_profile
        result = []
        query = (
            "MATCH (c:Category {name : $category})-[:HAS]->(l:Level {name : $level}) "
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
                )
                print(result)
            except ServiceUnavailable as exception:
                logging.error(
                    "{query} raised an error: \n {exception}".format(
                        query=query, exception=exception
                    )
                )
                continue
            except Exception as e:
                logging.error(e)
                continue
        return [row for row in result]

    def create_new_topic_relation(self, topic, level, categories_result):
        self.__create_topic_relation(topic, level, categories_result)
        print("Topic created: ", topic, " : ", level)

    #!-------------------------------------------------------------------------------------------------

    def __normalize_weights(self):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(self.__normalize_weights_driver)
            return

    @staticmethod
    def __normalize_weights_driver(tx):
        global user_profile
        result = []

        query_normalize_levels = (
            "MATCH (p:Profile)-[:KNOWS]->(c:Category)"
            "WITH collect(c) AS categories"
            "UNWIND categories as category"
            "MATCH (category)-[:HAS]->(l:Level)"
            "WITH category,MAX(l.value) AS max_value"
            "MATCH (category)-[:HAS]->(l:Level)"
            "SET l.normalized_value ="
            "CASE"
            "WHEN max_value > 0 THEN l.value / max_value "
            "ELSE 0"
            "END"
            "RETURN l"
        )

        query_normalize_categories = (
            "MATCH (p:Profile)-[:KNOWS]->(c:Category)"
            "WITH MAX(c.weight) AS max_value"
            "MATCH (p:Profile)-[:KNOWS]->(c1:Category)"
            "SET c1.normalized_weight="
            "CASE"
            "WHEN max_value > 0 THEN c1.weight / max_value"
            "ELSE 0"
            "END"
            "RETURN c1"
        )
        result1 = tx.run(query_normalize_levels)
        result2 = tx.run(query_normalize_categories)
        return [result1, result2]

    def normalize_weights(self):
        self.__normalize_weights()
        print("Weights Normalized")

    #!-------------------------------------------------------------------------------------------------

    def __fetch_weights(self, category):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
                self.__fetch_weights_driver, category=category
            )
            return result

    @staticmethod
    def __fetch_weights_driver(tx, category):
        global user_profile

        result = []
        # query = (
        #     "MATCH (c:Category)-[:HAS]->(l1:Level {name:'Level1'}) "
        #     "MATCH (c:Category)-[:HAS]->(l2:Level {name:'Level2'}) "
        #     "MATCH (c:Category)-[:HAS]->(l3:Level {name:'Level3'}) "
        #     "MATCH (c:Category)-[:HAS]->(l4:Level {name:'Level4'}) "
        #     "WHERE c.name = $category "
        #     "RETURN c, l1, l2, l3, l4"
        # )
        query = """
            MATCH (c:Category{name:$category})-[:HAS]->(l:Level{name:'Level1'})<-[rel1:BELONGSTO]-(t1:Topic)
            OPTIONAL MATCH (c)-[:HAS]->(l2:Level{name:'Level2'})<-[rel2:BELONGSTO]-(t2:Topic)
            OPTIONAL MATCH (c)-[:HAS]->(l3:Level{name:'Level3'})<-[rel3:BELONGSTO]-(t3:Topic)
            OPTIONAL MATCH (c)-[:HAS]->(l4:Level{name:'Level4'})<-[rel4:BELONGSTO]-(t4:Topic)
            RETURN COALESCE(c.name) as name, 
                COALESCE(c.weight,'null') as weight, 
                COALESCE(c.normalized_weight,'null') as normalized_weight, 
                COALESCE(COLLECT(DISTINCT {topic: t1, value: rel1.value}),[]) as topics_level1,
                COALESCE(COLLECT(DISTINCT {topic: t2, value: rel2.value}),[]) as topics_level2,
                COALESCE(COLLECT(DISTINCT {topic: t3, value: rel3.value}),[]) as topics_level3,
                COALESCE(COLLECT(DISTINCT {topic: t4, value: rel4.value}),[]) as topics_level4
            """

        record = tx.run(query, category=category).single()
        data = {
            "category": record["name"],
            "weight": record["weight"],
            "normalized_weight": record["normalized_weight"],
            "topics_level1": [],
            "topics_level2": [],
            "topics_level3": [],
            "topics_level4": [],
        }
        for instance in record["topics_level1"]:
            if instance["topic"] != None and instance["value"] != None:
                data["topics_level1"].append(
                    {str(instance["topic"]["name"]): float(instance["value"])}
                )
            else:
                continue
        for instance in record["topics_level2"]:
            if instance["topic"] != None and instance["value"] != None:
                data["topics_level1"].append(
                    {str(instance["topic"]["name"]): float(instance["value"])}
                )
            else:
                continue
        for instance in record["topics_level3"]:
            if instance["topic"] != None and instance["value"] != None:
                data["topics_level1"].append(
                    {str(instance["topic"]["name"]): float(instance["value"])}
                )
            else:
                continue
        for instance in record["topics_level4"]:
            if instance["topic"] != None and instance["value"] != None:
                data["topics_level1"].append(
                    {str(instance["topic"]["name"]): float(instance["value"])}
                )
            else:
                continue

        fileName = "data/" + category + ".json"
        with open(fileName, "w") as f:
            json.dump(data, f)

        return result

    def fetch_weights(self, category):
        self.__fetch_weights(category)
        print("Weights fetched : ", category)

    #!-------------------------------------------------------------------------------------------------


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


def main_graph_test(categories_data):
    topic = "Inflation"
    level = "Level1"
    category = "Economy"
    for i in categories:
        app.create_new_category(i)
    app.create_new_topic_relation(topic, level, categories_data)
    app.fetch_weights(category)
    app.close()
