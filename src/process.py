import nltk
from .graph import *
from .logger import *
from .readability import *
from .transformers import *


# Functions to process prompt
def get_prompt_categories(prompt: str, threshold=50):
    return get_categories_cap(prompt, threshold)


def get_rank(prompt: str):
    return get_readability_rank(prompt)


def get_concepts(sentence: str):
    nouns = []
    for word, pos in nltk.pos_tag(nltk.word_tokenize(str(sentence))):
        if pos == "NN" or pos == "NNP" or pos == "NNS" or pos == "NNPS":
            nouns.append(word)
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
    return categories_result


def fetch_category_data(prompt, threshold=50):
    categories_fetched = get_prompt_categories(prompt, threshold)
    weights = []
    for i in categories_fetched:
        weights.append(app.fetch_weights(i))
    return weights


def create_prompt_data(prompt, threshold=50):
    prompt_rank = get_rank(prompt)
    category_data = fetch_category_data(prompt, threshold)
    print("DATA", category_data)
    ranks = ["topics_level1", "topics_level2", "topics_level3", "topics_level4"]
    ranks = ranks[:prompt_rank]
    prompt_context = {}
    empty_flag = True
    for category in category_data:
        if category == {}:
            continue
        try:
            print("> Category", category)
            category_name = category["category"]
            prompt_context[category_name] = {}
            prompt_context[category_name]["confidence"] = category["weight"]
            prompt_context[category_name]["concepts"] = []
            for rank in ranks:
                for concepts_of_rank in category[rank]:
                    concepts = []
                    for c in concepts_of_rank:
                        concepts.append(c)
                    prompt_context[category_name]["concepts"].extend(concepts)
            empty_flag = False
        except:
            continue

    final_prompt = ""
    final_prompt += "[CONTEXT]: \n"
    if not empty_flag:
        final_prompt += str(prompt_context)
        final_prompt += "\n\n"
    final_prompt += "[PROMPT]: "
    final_prompt += prompt
    print("**************** FINAL PROMPT **********************")
    print(final_prompt)
    print("****************************************************")
    return final_prompt
