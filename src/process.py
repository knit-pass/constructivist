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
    for i in entities:
        categories_result[i] = get_categories_cap(i, threshold)
    return categories_result

def fetch_category_data(prompt,threshold):
    categories_fetched = get_prompt_categories(prompt,threshold)
    for i in categories_fetched:
        app.fetch_weights(i)