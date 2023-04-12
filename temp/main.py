import preprocessor


query = input("Enter query : ")
words = preprocessor.get_concepts(query)
print(words)