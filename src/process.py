import spacy
from tqdm import tqdm
from .graph import *
from .logger import *
from .readability import *
from .transformers import *

nlp = spacy.load("en_core_web_sm")


def get_prompt_categories(prompt: str, threshold=50):
    return get_categories_cap(prompt, threshold)


def get_rank(prompt: str):
    return get_readability_rank(prompt)


def get_concepts(sentence):
    """
    The function takes a sentence as input, extracts noun phrases from it, filters out determiners, and
    returns a list of lowercase noun phrases.

    :param sentence: a string containing a sentence or text from which the function will extract noun
    phrases as concepts
    :return: The function `get_concepts` returns a list of noun phrases (concepts) extracted from the
    input sentence, where each concept is represented as a string in lowercase.
    """
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
    """
    This function updates a knowledge base with categories related to entities in a given response and
    returns the categories.

    :param response: The input response string for which we want to get the response categories
    :type response: str
    :param threshold: The threshold is a value used to filter out categories with low confidence scores.
    Categories with confidence scores below the threshold percentage of the highest will not be included in the final prompt(optional)
    :return: The function `get_response_categories` returns a dictionary `categories_result` which
    contains the categories for each entity in the input `response` text, after updating the knowledge
    base and normalizing weights.
    """
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
    """
    This function fetches category data based on a given prompt and threshold, and returns a dictionary
    containing the confidence level and topic values for each category.

    :param prompt: The prompt for which category data needs to be fetched
    :param threshold: The threshold is a value used to filter out categories with low confidence scores.
    Categories with confidence scores below the threshold percentage of the highest will not be included in the final prompt
    :return: The function `fetch_category_data` returns a dictionary `data` containing the confidence
    level and topic values for each category fetched from the prompt.
    """
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
    return data


def create_prompt_data(prompt, threshold=50):
    """
    This function creates a final prompt by fetching category data and concepts based on a given prompt
    and threshold.

    :param prompt: The text prompt for which we want to create context data
    :param threshold: The threshold is a value used to filter out categories with low confidence scores.
    Categories with confidence scores below the threshold percentage of the highest will not be included in the final prompt
    context. The default value is 50, defaults to 50 (optional)
    :return: The function `create_prompt_data` returns a string that contains the context and prompt
    data.
    """
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
    final_prompt += json.dumps(prompt_context, indent=4)
    final_prompt += "\n\n"
    final_prompt += "[PROMPT]: "
    final_prompt += prompt
    print("**************** FINAL PROMPT **********************")
    print(final_prompt)
    print("****************************************************")
    return final_prompt
