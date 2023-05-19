import openai
from colorama import Fore, Style
from dotenv import load_dotenv, dotenv_values
from src import *

creds = dotenv_values("chatgpt_credentials.env")
openai.api_key = creds["API_KEY"]
first_time_run = False


def beginFunction():
    global first_time_run
    print(
        "# ---------------------------------------------------------------------------- #"
    )
    print(
        "#                                Search Engine                                 #"
    )
    print(
        "# ---------------------------------------------------------------------------- #\n"
    )
    if first_time_run:
        init_graph()
        print("Graph Initialized")
        first_time_run = False
    # profileChoosen = choose_profiles()

    # print("Working on : ",profileChoosen)
    print("MENU : ")
    print("1.Give modified prompt  2.Give solution  3.Exit\n")

    while True:
        questionType = int(input("Enter 1/2/3 : "))

        if type(questionType) != int:
            continue

        if questionType == 3:
            print("Thank you!! exiting...")
            app.close()
            break

        question = input("Enter prompt : ")
        if questionType == 1:
            final_prompt = create_prompt_data(question, 50)
            modifiedQuestion = final_prompt
            print("Modified Prompt : " + modifiedQuestion)

        elif questionType == 2:
            # solution = "This is a sample solution"
            solution = giveAnswer(create_prompt_data(question))  # uses API key
            result = get_response_categories(solution)
            # print(type(solution))

            print(
                "# ---------------------------------------------------------------------------- #"
            )
            print("\n")
        else:
            print("Invalid input!!")
            continue


init_prompt = """
    You are a most intelligent assistant ever made. You are now helping users learn new concepts. You will answer to user prompts which will help them to learn what they are wishing for. Your strength is that you teach user new concepts in such a way that they are able to relate to the concepts they already know. You will be provided with a context information along with a prompt. The context information denotes the knowledge a user already has. You should give response to the prompt in such a way that user should be able to relate the response with the context. You don't push too hard to relate two unrelated concepts. It is not compulsory that you should relate to every concept in the context. Irrelevant concepts can be omitted. Don't ever acknowledge that user knows about these concepts/domains. Just include them in the response if necessary. 
    \n
    Context is provided by a secret machine in JSON format denoted by [CONTEXT]. JSON object is the object of different domains that user knows about. JSON format is as follows, the keys denote the domain of the information and the value is an object with 'confidence' denoting the amount of knowledge a user has. Followed by 'concepts' which is an array of concepts user knows in that domain.
    \n
    Example:
    \n
    [CONTEXT]:
    {
    “Technology” : {
    “confidence”:34.20,
    “concepts”:['AI','Blockchain']
    },
    “Physics”: {
                “confidence”: 12.45,
                “concepts”:['Quantum Physics','Mechanics']
    }	
    }
    \n
    In this example, user wants his responses to have the context of 2 domains. They are Technology and Finance. About Technology, user's confidence score is about 34.20 and he knows about AI and blockchain. In Physics his confidence score is about 12.45 and he knows about Quantum Physics and Mechanics.
    \n
    User's prompt will be denoted by [PROMPT]: everything followed by that is the prompt which you should respond to. 
    \n
    IT IS A TOP SECRET THAT WE KNOW ABOUT USER'S KNOWLEDGE SO, DON'T EVER REVEAL IT TO THE USER.
    \n
    DO NOT TELL THAT YOU KNOW OR ARE AWARE ABOUT THE USER'S KNOWLEDGE IN THE RESPONSE.
"""


# this function uses API key to generate results
def giveAnswer(message):
    messages = [
        {"role": "user", "content": "You are a intelligent assistant."},
        {"role": "assistant", "content": "Ok. Thank you."},
        {"role": "user", "content": init_prompt},
        {"role": "assistant", "content": "Sure, please proceed."},
    ]
    if message:
        messages.append(
            {"role": "user", "content": message},
        )
        try:
            chat = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages
            )
            reply = chat.choices[0].message.content
            messages.append({"role": "assistant", "content": reply})
        except openai.error.APIError as e:
            Logger.write_print_error(f"OpenAI API returned an API Error: {e}")
            pass
        except openai.error.APIConnectionError as e:
            Logger.write_print_error(f"Failed to connect to OpenAI API: {e}")
            pass
        except openai.error.RateLimitError as e:
            Logger.write_print_error(f"OpenAI API request exceeded rate limit: {e}")
            pass
        except openai.error.Timeout as e:
            Logger.write_print_error(f"OpenAI API request timed out: {e}")
            pass
        except openai.error.InvalidRequestError as e:
            Logger.write_print_error(f"Invalid request to OpenAI API: {e}")
            pass
        except openai.error.AuthenticationError as e:
            Logger.write_print_error(f"Authentication error with OpenAI API: {e}")
            pass
        except openai.error.ServiceUnavailableError as e:
            Logger.write_print_error(f"OpenAI API service unavailable: {e}")
            pass
        except Exception as e:
            Logger.write_print_error(f"ERROR: {e}")
            pass
    print(Fore.YELLOW, f"ChatGPT: {reply}")
    print(Style.RESET_ALL, "\n")
    return reply


def choose_profiles(choice=0) -> str:
    if not choice:
        print("Choose: ")
        print("1. Create New Profile")
        print("2. Use Existing Profile")
        print("3. Delete Profile")
        print("4. Exit")
        print("Enter your choice: ")
        choice = int(input())
    profile = ""

    available_profiles = app.fetch_profiles()
    # function called from graph.py

    # Create new profile
    if choice == 1:
        print("Enter the name of new profile: ")
        profile = input()
        if profile in available_profiles:
            print("Duplicate profile!")
            profile = choose_profiles(1)
        print("The profile is: ", profile)

        app.create_profile(profile)
        # function called from graph.py

        return profile
    # Choose existing profile
    elif choice == 2:
        print("Available profiles: ")
        # for i, idx in enumerate(available_profiles):
        #     print(f"{idx+1}. i")
        idx = 1
        for i in available_profiles:
            print(str(idx), " : ", i)
            idx = idx + 1
        print("Choose your profile: ")
        profileIndex = int(input())
        if profileIndex > len(available_profiles) or profileIndex < 0:
            choose_profiles(2)
        else:
            # TODO: Choose profile logic
            profile_name = available_profiles[profileIndex - 1]
        print("The profile is: ", profile_name)
        return profile_name
    # Delete profile
    elif choice == 3:
        print("Available profiles to delete: ")
        idx = 1
        for i in available_profiles:
            print(str(idx), " : ", i)
            idx = idx + 1
        print("Choose the profile to delete: ")
        profileIndex = int(input())
        if profileIndex > len(available_profiles) or profileIndex < 0:
            print("Invalid option!")
            return choose_profiles(3)
        else:
            profile_name = available_profiles[profileIndex - 1]
            # TODO: Delete Logic
            print("Are you sure you want to delete the entire data of : ", profile_name)
            print("Y/N ?")
            ack = input()
            if ack == "Y" or ack == "y":
                app.delete_profile(profile_name)
                available_profiles = app.fetch_profiles()
                return choose_profiles()
            else:
                return choose_profiles()

    else:
        print("Invalid option! ")
        return choose_profiles()


def init_new_profile(name: str = "") -> bool:
    if name == "":
        print("Invalid new profile!")
        return False
    print("How do you want to start a new profile")
    print("1. Nothing")
    print("2. Initial data")
    print("Choose: ")
    choice = int(input())

    # Start with nothing
    if choice == 1:
        pass
    # Start with a data
    elif choice == 2:
        pass
    else:
        return init_new_profile(name)


if __name__ == "__main__":
    beginFunction()
