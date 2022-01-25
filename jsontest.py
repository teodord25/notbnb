import json


# so I can store the entire userbase in a single json
# or split it into many small files

# opening lots of files for the info table
# is kinda bad tho

# open(, "r") read the entire file anyway



def main():
    # user_data = {
    #     "user1": {
    #         "username": "joeman",
    #         "fname": "joe",
    #         "lname": "mama"
    #     },
    #
    #     "user2": {
    #         "username": "ayyman",
    #         "fname": "ayy",
    #         "lname": "lmao",
    #     }
    # }
    #

    # user_data = {
    #     input("username"): {
    #         "fname": input("fname"),
    #         "lname": input("lname")
    #     }
    # }

    user_data = {
        input("ayo man add a new user: "): {
            "fname": input("f: "),
            "lname": input("l: ")
            }
    }

    try:
        with open("jsonuser_data.json", "r") as file:
            users = json.load(file)

    except FileNotFoundError:
        print("user data file missing!")
        print("creating user data file...")

        with open("jsonuser_data.json", "w") as file:
            json.dump(user_data, file)

        print("created user data file.")

        quit()


    with open("jsonuser_data.json", "w") as file:
        json.dump(users, file)



if __name__ == "__main__":
    main()
