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

def transformers_demo():
    entity = "Leonardo DiCaprio"
    result = pipe(entity, candidate_labels=categories_refined)
    result_c = result["labels"]
    result_p = result["scores"]
    threshold = 0.1 * result_p[0]
    # print(result_c,result_p)
    j = 0
    for i in result_p:
        if i < threshold:
            break
        j += 1
    result_p = result_p[0:j]
    result_c = result_c[0:j]
    print(result_c, result_p)

    cats = ["Person", "Non Person"]

    entity = "Narendra Modi"
    result = pipe(entity, candidate_labels=cats)
    result_c = result["labels"]
    result_p = result["scores"]
    threshold = 0.3 * result_p[0]
    # print(result_c,result_p)
    j = 0
    for i in result_p:
        if i < threshold:
            break
        j += 1
    result_p = result_p[0:j]
    result_c = result_c[0:j]
    print(result_c, result_p)

if __name__ == "__main__":
    transformers_demo()