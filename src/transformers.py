from transformers import pipeline
import nltk
import os

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


def get_categories_cap(entity: str):
    result = pipe(entity, candidate_labels=categories_refined)
    result_c = result["labels"]
    result_p = result["scores"]
    threshold = 0.1 * result_p[0]
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
    result_dictionary = {}
    for idx, i in enumerate(result_p):
        result_p[idx] += i * balance
        result_dictionary[result_c[idx]] = result_p[idx]
    return result_dictionary


    # entity = "Narendra Modi"
    # result = pipe(entity, candidate_labels=cats)
    # result_c = result["labels"]
    # result_p = result["scores"]
    # threshold = 0.3 * result_p[0]
    # # print(result_c,result_p)
    # j = 0
    # for i in result_p:
    #     if i < threshold:
    #         break
    #     j += 1
    # result_p = result_p[0:j]
    # result_c = result_c[0:j]
    # print(result_c, result_p)




def get_entities_of_paragraph(para : str):
    sentences = nltk.sent_tokenize(para)
    Entities = []
    for sentence in sentences:
        print(sentence)
    



