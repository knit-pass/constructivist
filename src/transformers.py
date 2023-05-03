from transformers import pipeline
import json
from .logger import *

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
        Logger.write_debug(f"Categories fetched for(cap): {entity}")
        Logger.write_debug(str(result_dictionary))
    except Exception as e:
        Logger.write_error(str(e))
    return result_dictionary


def get_categories(entity: str):
    result_dictionary = {}
    try:
        result = pipe(entity, candidate_labels=categories_refined)
        result_c = result["labels"]
        result_p = result["scores"]
        for idx, i in enumerate(result_p):
            result_dictionary[result_c[idx]] = result_p[idx]
        Logger.write_debug(f"Categories fetched for: {entity}")
        Logger.write_debug(str(result_dictionary))
    except Exception as e:
        Logger.write_error(str(e))
    return result_dictionary


def transformers_demo():
    result = get_categories("Inflation")
    with open ("data/category.json") as f:
        json.dump(result,f)
    get_categories_cap("Inflation")


