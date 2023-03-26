import openai
import json

# Set your OpenAI API key here
openai.api_key = "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"

# Set the categories to consider
CATEGORIES = [
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

# Function to get the categories and their percentages for a given query
def get_categories(query):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"What are the top categories for the query '{query}'?",
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
        frequency_penalty=0,
        presence_penalty=0
    )

    categories = []
    for choice in response.choices:
        text = choice.text.strip().split("\n")
        for t in text:
            if "-" in t:
                parts = t.split("-")
                category = parts[1].strip()
                percentage = float(parts[0].strip().replace("%", ""))
                categories.append({"category": category, "percentage": percentage})
    return categories

# Get user input and call the get_categories function
if __name__ == "__main__":
    query = input("Enter your query: ")
    categories = get_categories(query)
    output = {"query": query, "categories": categories[:4]}
    with open("output.json", "w") as f:
        json.dump(output, f, indent=4)
    print("Output saved to output.json")
