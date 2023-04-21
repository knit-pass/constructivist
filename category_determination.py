import gensim.downloader as api
import numpy as np

# download the Word2Vec model
model = api.load("word2vec-google-news-300")

# define the categories
categories = [
    "Academic discipline",
    "Business",
    "Communication",
    "Concept",
    "Culture",
    "Economy",
    "Education",
    "Energy",
    "Engineering",
    "Entertainment",
    "Entity",
    "Ethics",
    "Food and drink",
    "Geography",
    "Government",
    "Health",
    "History",
    "Human behavior",
    "Humanities",
    "Information",
    "Internet",
    "Knowledge",
    "Language",
    "Law",
    "Life",
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
    "Time",
    "Universe",
]

# input word
input_word = "Apple"

# get the vector representation of the input word
try:
    vec = model[input_word]
except KeyError:
    print(f"{input_word} is not in the vocabulary")
    exit()

# calculate the cosine similarity between the vector representation of the input word and each category
similarity_scores = {}
for category in categories:
    category_vec = np.mean([model[word] for word in category.lower().split()], axis=0)
    similarity_scores[category] = np.dot(vec, category_vec) / (np.linalg.norm(vec) * np.linalg.norm(category_vec))

# sort the categories by their similarity scores, in descending order
sorted_categories = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)

# print the top 3 categories
print(f"The word belongs to the following categories:")
for i in range(3):
    print(f"{sorted_categories[i][0]} (similarity score: {sorted_categories[i][1]:.2f})")
