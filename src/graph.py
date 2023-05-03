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
            "MERGE (t)-[:HAS]->(:Level {name: 'Level1'})"
            "MERGE (t)-[:HAS]->(:Level {name: 'Level2'})"
            "MERGE (t)-[:HAS]->(:Level {name: 'Level3'})"
            "MERGE (t)-[:HAS]->(:Level {name: 'Level4'})"
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
    def __create_topic_relation(self, topic, level):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
                self.__create_topic_relation_driver, topic=topic, level=level
            )
            return [row for row in result]

    def __assign_weights(self):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(self.__assign_weights_driver)
            return

    def __normalize_weights(self):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(self.__normalize_weights_driver)
            return

    def __fetch_weights(self, category):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
                self.__fetch_weights_driver, category=category
            )
            return result

    @staticmethod
    def __assign_weights_driver(tx):
        global user_profile
        result = []
        query1 = (
            "MATCH (c:Category)-[:HAS]->(l:Level{name:'Level1'})<-[r:BELONGSTO]-(otherNode)"
            "WITH c, l, SUM(r.value) AS weight "
            "SET l.weight = weight, c.weight_level1 = weight "
            "RETURN weight"
        )
        query2 = (
            "MATCH (c:Category)-[:HAS]->(l:Level{name:'Level2'})<-[r:BELONGSTO]-(otherNode)"
            "WITH c, l, SUM(r.value) AS weight "
            "SET l.weight = weight, c.weight_level2 = weight "
            "RETURN weight"
        )
        query3 = (
            "MATCH (c:Category)-[:HAS]->(l:Level{name:'Level3'})<-[r:BELONGSTO]-(otherNode)"
            "WITH c, l, SUM(r.value) AS weight "
            "SET l.weight = weight, c.weight_level3 = weight "
            "RETURN weight"
        )
        query4 = (
            "MATCH (c:Category)-[:HAS]->(l:Level{name:'Level4'})<-[r:BELONGSTO]-(otherNode)"
            "WITH c, l, SUM(r.value) AS weight "
            "SET l.weight = weight, c.weight_level4 = weight "
            "RETURN weight"
        )

        # "MATCH (n:Category)<-[r:BELONGSTO]-(otherNode) "
        # "WITH n,SUM(r.value) AS weight "
        # "SET n.weight = weight "
        # "RETURN weight"
        result = tx.run(query1)
        result = tx.run(query2)
        result = tx.run(query3)
        result = tx.run(query4)

        return result

    @staticmethod
    def __normalize_weights_driver(tx):
        global user_profile
        result = []

        # query = (
        #     "MATCH (n:Profile)-[r:KNOWS]->(Category) "
        #     "WITH n,max(Category.weight) as max_weight "
        #     "SET c.normalized_weight =(c.weight)/max_weight "
        #     "RETURN c.normalized_weight"
        # )
        # match(c:Category)
        # WITH max(c.weight_level1) as max_weight
        # match (c:Category)
        # SET c.normalized_weight_level1 = c.weight_level1 / max_weight
        # RETURN c.weight_level1, max_weight, c.normalized_weight_level1

        query = (
            "MATCH (c:Category) "
            "WITH MAX(c.weight_level1) as max_weight1, max(c.weight_level2) as max_weight2, "
            "MAX(c.weight_level3) as max_weight3, max(c.weight_level4) as max_weight4 "
            "MATCH (c:Category) "
            "SET c.normalized_weight_level1 = c.weight_level1 / max_weight1, "
            "c.normalized_weight_level2 = c.weight_level2 / max_weight2, "
            "c.normalized_weight_level3 = c.weight_level3 / max_weight3, "
            "c.normalized_weight_level4 = c.weight_level4 / max_weight4"
        )

        # "RETURN c.name, c.weight_level1, c.weight_level2, c.weight_level3, c.weight_level4,"
        #     "max_weight1, max_weight2, max_weight3, max_weight4,"
        #     "c.normalized_weight_level1, c.normalized_weight_level2,"
        #     "c.normalized_weight_level3, c.normalized_weight_level4"

        result = tx.run(query)
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
                COALESCE(c.weight_level1,'null') as weight_level1, 
                COALESCE(c.weight_level2,'null') as weight_level2, 
                COALESCE(c.weight_level3,'null') as weight_level3, 
                COALESCE(c.weight_level4,'null') as weight_level4, 
                COALESCE(c.normalized_weight_level1,'null') as normalized_weight_level1, 
                COALESCE(c.normalized_weight_level2,'null') as normalized_weight_level2, 
                COALESCE(c.normalized_weight_level3,'null') as normalized_weight_level3, 
                COALESCE(c.normalized_weight_level4,'null') as normalized_weight_level4,
                COALESCE(COLLECT(DISTINCT {topic: t1, value: rel1.value}),[]) as topics_level1,
                COALESCE(COLLECT(DISTINCT {topic: t2, value: rel2.value}),[]) as topics_level2,
                COALESCE(COLLECT(DISTINCT {topic: t3, value: rel3.value}),[]) as topics_level3,
                COALESCE(COLLECT(DISTINCT {topic: t4, value: rel4.value}),[]) as topics_level4
            """

        #         MATCH (c:Category{name:"Technology"})-[:HAS]->(l:Level{name:"Level1"})<-[:BELONGSTO]-(t:Topic)
        # RETURN COALESCE(c.name) as name,
        # COALESCE(c.weight_level1,'null') as weight_level1,
        # COALESCE(c.weight_level2,'null') as weight_level2,
        # COALESCE(c.weight_level3,'null') as weight_level3,
        # COALESCE(c.weight_level4,'null') as weight_level4,
        # COALESCE(c.normalized_weight_level1,'null') as normalized_weight_level1,
        # COALESCE(c.normalized_weight_level2,'null') as normalized_weight_level2,
        # COALESCE(c.normalized_weight_level3,'null') as normalized_weight_level3,
        # COALESCE(c.normalized_weight_level4,'null') as normalized_weight_level4

        record = tx.run(query, category=category).single()
        # data = {
        #     "category": record["c"].get("name"),
        #     "weight_level1": record["c"].get("weight_level1"),
        #     "weight_level2": record["c"].get("weight_level2"),
        #     "weight_level3": record["c"].get("weight_level3"),
        #     "weight_level4": record["c"].get("weight_level4"),
        #     "normalized_weight_level1": record["c"].get("normalized_weight_level1"),
        #     "normalized_weight_level2": record["c"].get("normalized_weight_level2"),
        #     "normalized_weight_level3": record["c"].get("normalized_weight_level3"),
        #     "normalized_weight_level4": record["c"].get("normalized_weight_level4")
        # }
        data = {
            "category": record["name"],
            "weight_level1": record["weight_level1"],
            "weight_level2": record["weight_level2"],
            "weight_level3": record["weight_level3"],
            "weight_level4": record["weight_level4"],
            "normalized_weight_level1": record["normalized_weight_level1"],
            "normalized_weight_level2": record["normalized_weight_level2"],
            "normalized_weight_level3": record["normalized_weight_level3"],
            "normalized_weight_level4": record["normalized_weight_level4"],
            "topics_level1":[],
            "topics_level2": [],
            "topics_level3": [],
            "topics_level4": []
        }
        for instance in record["topics_level1"]:
            if(instance["topic"] != None and instance["value"]!=None):
                data["topics_level1"].append({str(instance["topic"]["name"]): float(instance["value"])})
            else:
                continue
        for instance in record["topics_level2"]:
            if(instance["topic"] != None and instance["value"]!=None):
                data["topics_level1"].append({str(instance["topic"]["name"]): float(instance["value"])})
            else:
                continue
        for instance in record["topics_level3"]:
            if(instance["topic"] != None and instance["value"]!=None):
                data["topics_level1"].append({str(instance["topic"]["name"]): float(instance["value"])})
            else:
                continue
        for instance in record["topics_level4"]:
            if(instance["topic"] != None and instance["value"]!=None):
                data["topics_level1"].append({str(instance["topic"]["name"]): float(instance["value"])})
            else:
                continue

        fileName = "data/" + category + ".json"
        with open(fileName, "w") as f:
            json.dump(data, f)

        return result

    @staticmethod
    def __create_topic_relation_driver(tx, topic, level):
        global user_profile
        # Creating a topic node with the name of the topic.
        result = []
        # topic_wiki_page = get_nearest_wiki_links(topic)[0]
        # category_wiki_page = get_nearest_wiki_links(category)[0]
        # shortest_path = get_shortest_path(topic_wiki_page, category_wiki_page)
        query = (
            "MATCH (c:Category {name : $category})-[:HAS]->(l:Level {name : $level})"
            "MERGE (t:Topic {name : $topic})"
            "MERGE (l)<-[:BELONGSTO {value : $value}]-(t)"
        )
        # query = (
        #     "MATCH (c:Category {name : $category})"
        #     "MERGE (t:Topic {name : $topic})"
        #     "MERGE (c)<-[:BELONGSTO {value : $value}]-(t)"
        # )
        category_file_path = "data/category.json"
        if __name__ == "__main__":
            category_file_path = "./data/category.json"

        with open(category_file_path, "r") as file:
            categories_fetched_with_percentage = json.load(file)

        print(categories_fetched_with_percentage)
        categories_fetched = []

        for i in categories_fetched_with_percentage:
            categories_fetched.append(i)
        print(categories_fetched)

        for i in categories_fetched:
            print(i)
            result = tx.run(
                query,
                topic=topic,
                level=level,
                category=i["category"],
                value=float(i["percentage"]),
            )
            try:
                print(result)
            except ServiceUnavailable as exception:
                logging.error(
                    "{query} raised an error: \n {exception}".format(
                        query=query, exception=exception
                    )
                )

        return [row for row in result]

    def create_new_topic_relation(self, topic, level):
        self.__create_topic_relation(topic, level)
        print("Topic created: ", topic, " : ", level)

    def assign_weights(self):
        self.__assign_weights()
        print("Weights Assigned")

    def normalize_weights(self):
        self.__normalize_weights()
        print("Weights Normalized")

    def fetch_weights(self, category):
        self.__fetch_weights(category)
        print("Weights fetched : ", category)


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


def main_graph_test():
    topic = "Inflation"
    level = "Level1"
    category = "Economy"
    # for i in categories:
    #     app.create_new_category(i)
    # app.create_new_topic_relation(topic,level)
    # app.assign_weights()
    # app.normalize_weights()
    app.fetch_weights(category)
    app.close()


if __name__ == "__main__":
    main_graph_test()

# match (c:Category{name:"Entertainment"})-[:HAS]->(l:Level1)
# create (t:Topic {name:"Tom Cruise"})
# create (l)<-[:BELONGSTO {value : 10}]-(t)
