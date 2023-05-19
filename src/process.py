import spacy
from tqdm import tqdm
from .graph import *
from .logger import *
from .readability import *
from .transformers import *

nlp = spacy.load("en_core_web_sm")


# Functions to process prompt
def get_prompt_categories(prompt: str, threshold=50):
    return get_categories_cap(prompt, threshold)


def get_rank(prompt: str):
    return get_readability_rank(prompt)


def get_concepts(sentence):
    doc = nlp(sentence)
    noun_chunks = []
    for chunk in doc.noun_chunks:
        if chunk.root.pos_ == "NOUN":
            filtered_chunk = " ".join(
                token.text for token in chunk if token.pos_ != "DET"
            )
            noun_chunks.append(filtered_chunk.lower())
    return noun_chunks


def get_response_categories(response: str, threshold=50):
    entities = get_concepts(response)
    categories_result = {}
    level = get_rank(response)
    level_names = ["Level1", "Level2", "Level3", "Level4"]
    Logger.write_print_debug("Updating your knowledge base..")
    for i in tqdm(entities, colour="yellow"):
        categories_result[i] = get_categories_cap(i, threshold)
        app.create_new_topic_relation(i, level_names[level - 1], categories_result[i])
    app.normalize_weights()
    return categories_result


def fetch_category_data(prompt, threshold=50):
    categories_fetched = get_prompt_categories(prompt, threshold)
    weights = []
    data = {}
    Logger.write_print_debug("\nCreating your prompt.")
    for i in tqdm(categories_fetched, colour="green"):
        weights.extend(app.fetch_weights(i))
    for i in weights:
        try:
            data[i["Category"]]["confidence"] = i["CategoryWeight"]
        except:
            data[i["Category"]] = {}
            data[i["Category"]]["confidence"] = i["CategoryWeight"]
        try:
            data[i["Category"]][i["Level"]].append([i["Topic"], i["TopicValue"]])
        except:
            data[i["Category"]][i["Level"]] = []
            data[i["Category"]][i["Level"]].append([i["Topic"], i["TopicValue"]])
    # print("Data:: ", data)
    return data


def create_prompt_data(prompt, threshold=50):
    # prompt_rank = get_rank(prompt)
    prompt_rank = 4
    category_data = fetch_category_data(prompt, threshold)
    ranks = ["Level1", "Level2", "Level3", "Level4"]
    ranks = ranks[:prompt_rank]
    prompt_context = {}
    Logger.write_debug("Category Data " + str(category_data))
    for category in category_data:
        if category == {}:
            continue
        try:
            Logger.write_debug("> Category " + str(category))
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
                    Logger.write_error(e)
                    continue
        except Exception as e:
            print(e)
            continue

    final_prompt = ""
    final_prompt += "[CONTEXT]: \n"
    # final_prompt += str(prompt_context)
    final_prompt += json.dumps(prompt_context, indent=4)
    final_prompt += "\n\n"
    final_prompt += "[PROMPT]: "
    final_prompt += prompt
    print("**************** FINAL PROMPT **********************")
    print(final_prompt)
    print("****************************************************")
    return final_prompt
