import spacy
from .graph import *
from .logger import *
from .readability import *
from .transformers import *

nlp = spacy.load("en_core_web_lg")


# Functions to process prompt
def get_prompt_categories(prompt: str, threshold=50):
    return get_categories_cap(prompt, threshold)


def get_rank(prompt: str):
    return get_readability_rank(prompt)


def get_concepts(sentence: str):
    nouns = []
    doc = nlp(sentence)
    for entity in doc.ents:
        nouns.append(entity.text.lower())
        print("Fetched: ", entity.text.lower())
    return nouns


def get_response_categories(response: str, threshold=50):
    entities = get_concepts(response)
    categories_result = {}
    level = get_rank(response)
    level_names = ["Level1", "Level2", "Level3", "Level4"]
    for i in entities:
        categories_result[i] = get_categories_cap(i, threshold)
        app.create_new_topic_relation(i, level_names[level - 1], categories_result[i])
        print(f"Created {i} : Level {level}")
    app.normalize_weights()
    return categories_result


def fetch_category_data(prompt, threshold=50):
    categories_fetched = get_prompt_categories(prompt, threshold)
    weights = []
    data = {}
    for i in categories_fetched:
        weights.extend(app.fetch_weights(i))
    for i in weights:
        data[i["Category"]] = {}
        data[i["Category"]]["confidence"] = i["CategoryWeight"]
        try:
            data[i["Category"]][i["Level"]].append([i["Topic"], i["TopicValue"]])
        except:
            data[i["Category"]][i["Level"]] = []
            data[i["Category"]][i["Level"]].append([i["Topic"], i["TopicValue"]])
    return data


def create_prompt_data(prompt, threshold=50):
    # prompt_rank = get_rank(prompt)
    prompt_rank = 4
    category_data = fetch_category_data(prompt, threshold)
    print("DATA", category_data)

    ranks = ["Level1", "Level2", "Level3", "Level4"]
    ranks = ranks[:prompt_rank]
    prompt_context = {}
    print("Category Data", category_data)
    for category in category_data:
        if category == {}:
            continue
        try:
            print("> Category", category)
            prompt_context[category] = {}
            prompt_context[category]["confidence"] = category_data[category][
                "confidence"
            ]
            prompt_context[category]["concepts"] = []
            for rank in ranks:
                try:
                    prompt_context[category]["concepts"].extend(
                        [topic_item[0] for topic_item in category_data[category][rank]]
                    )
                except Exception as e:
                    print(e)
                    continue
        except Exception as e:
            print(e)
            continue

    final_prompt = ""
    final_prompt += "[CONTEXT]: \n"
    final_prompt += str(prompt_context)
    final_prompt += "\n\n"
    final_prompt += "[PROMPT]: "
    final_prompt += prompt
    print("**************** FINAL PROMPT **********************")
    print(final_prompt)
    print("****************************************************")
    return final_prompt
