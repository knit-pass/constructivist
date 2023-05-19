import json
from .logger import *
from transformers import pipeline

pipe = pipeline(model="facebook/bart-large-mnli")

categories_refined = [
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


def get_categories_cap(entity: str, tp=10):
    """
    This function takes an entity and returns a dictionary of its top predicted categories along with
    their corresponding scores, with an optional parameter to adjust the threshold for category
    selection.

    :param entity: The input entity for which we want to get the categories
    :type entity: str
    :param tp: tp stands for "threshold percentage". It is a parameter that determines the threshold
    score for selecting the categories. The default value is 10, which means that the function will
    select categories with a score higher than 10% of the highest score, defaults to 10 (optional)
    :return: a dictionary containing the categories related to the input entity and their corresponding
    scores. The number of categories returned is determined by the "tp" parameter, which defaults to 10.
    """
    result_dictionary = {}
    try:
        result = pipe(entity, candidate_labels=categories_refined)
        result_c = result["labels"]
        result_p = result["scores"]
        p = tp / 100
        threshold = p * result_p[0]
        j = 0
        score_sum = 0
        for i in result_p:
            if i < threshold:
                break
            score_sum += i
            j += 1
        result_p = result_p[0:j]
        result_c = result_c[0:j]
        balance = 1 - score_sum
        for idx, i in enumerate(result_p):
            result_p[idx] += i * balance
            result_dictionary[result_c[idx]] = result_p[idx]
        Logger.write_debug(f"Categories fetched for: {entity}")
        Logger.write_debug(str(result_dictionary))
    except Exception as e:
        Logger.write_error(str(e))
    return result_dictionary


def get_categories(entity: str):
    """
    The function takes an entity as input, uses a pre-trained model to predict its categories, and
    returns a dictionary of category labels and their corresponding scores.

    :param entity: a string representing the entity for which categories need to be fetched
    :type entity: str
    :return: The function `get_categories` returns a dictionary containing the categories related to the
    input `entity` and their corresponding scores.
    """
    result_dictionary = {}
    try:
        result = pipe(entity, candidate_labels=categories_refined)
        result_c = result["labels"]
        result_p = result["scores"]
        for idx, i in enumerate(result_p):
            result_dictionary[result_c[idx]] = result_p[idx]
        Logger.write_debug(str(result_dictionary))
        Logger.write_debug(f"Categories fetched for: {entity}")
    except Exception as e:
        Logger.write_error(str(e))
    return result_dictionary
