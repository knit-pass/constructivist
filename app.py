import openai
from dotenv import load_dotenv, dotenv_values

creds = dotenv_values("chatgpt_credentials.env")
openai.api_key = creds['API_KEY']
def beginFunction():
    print("# ---------------------------------------------------------------------------- #")
    print("#                                Search Engine                                 #")
    print("# ---------------------------------------------------------------------------- #\n")
    
    print("MENU : ")
    print("1.Give modified prompt  2.Give solution  3.Exit\n")
    
    while True:
        questionType = int(input("Enter 1/2/3 : "))

        if(questionType == 3):
            print("Thank you!! exiting...")
            break

        question = input("Enter prompt : ")

        #call function to modify question using graph and store in newQuestion
        modifiedQuestion = "This is a new sample prompt"
        if(questionType == 1):
            print("New Prompt : " + modifiedQuestion)
        else :
            solution = "This is a sample solution"
            # solution = giveAnswer(modifiedQuestion) # uses API key
            print("Solution : " + solution)
        print("# ---------------------------------------------------------------------------- #")
        print("\n")


# this function uses API key to generate results
def giveAnswer(message):
    messages = [ {"role": "system", "content": 
              "You are a intelligent assistant."} ]
    if message:
        messages.append(
            {"role": "user", "content": message},
        )
        chat = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=messages
        )
    reply = chat.choices[0].message.content
    print(f"ChatGPT: {reply}")
    messages.append({"role": "assistant", "content": reply})


def choose_profiles(choice=0) -> str:
    if not choice:
        print("Choose: ")
        print("1. Create New Profile")
        print("2. Use Existing Profile")
        print("3. Delete Profile")
        print("Enter your choice: ")
        choice = int(input())
    profile = ""
    # TODO: Fetch users from graph DB
    available_profiles = ["user1", "user2", "user3"]

    # Create new profile
    if choice == 1:
        print("Enter the name of new profile: ")
        profile = input()
        if profile in available_profiles:
            print("Duplicate profile!")
            profile = choose_profiles(1)
        print("The profile is: ", profile)
        # TODO: Profile creation in DB
        return profile
    # Choose existing profile
    elif choice == 2:
        print("Available profiles: ")
        for i, idx in enumerate(available_profiles):
            print(f"{idx+1}. i")
        print("Choose your profile: ")
        profile = int(input())
        if profile > len(available_profiles) or profile < 0:
            profile_name = choose_profiles(2)
            return profile
        else:
            # TODO: Choose profile logic
            profile_name = available_profiles[profile - 1]
        print("The profile is: ", profile_name)
        return profile_name
    # Delete profile
    elif choice == 3:
        print("Available profiles to delete: ")
        for i, idx in enumerate(available_profiles):
            print(f"{idx+1}. i")
        print("Choose the profile to delete: ")
        profile = int(input())
        if profile > len(available_profiles) or profile < 0:
            print("Invalid option!")
            return choose_profiles(3)
        else:
            profile_name = available_profiles[profile - 1]
            # TODO: Delete Logic
        print("The profile is: ", profile_name)
        print("The following profile will be deleted: ", profile_name)
        return ""
    else:
        print("Invalid option! ")
        return choose_profiles()


def init_new_profile(name: str = "") -> bool:
    if name == "":
        print("Invalid new profile!")
        return False
    print("How you want to start a new profile")
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
    # print("Chosen Profile: ", choose_profiles())
    # print(giveAnswer("who is narendra modi")) # function uses API key
    beginFunction()
