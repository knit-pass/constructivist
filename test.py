import openai
import os

# Set up your OpenAI API key
openai.api_key = "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"

# Define your query prompt
prompt = "what's the limit of queries"

# Set the parameters for your request
model_engine = "text-davinci-002"
temperature = 0.7
max_tokens = 50

# Send the request to ChatGPT
response = openai.Completion.create(
    engine=model_engine,
    prompt=prompt,
    temperature=temperature,
    max_tokens=max_tokens
)

# Print the response from ChatGPT
print(response.choices[0].text.strip())
