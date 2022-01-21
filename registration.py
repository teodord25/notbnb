import os
import hashlib
import base64
import json


def register_user(username: str, password: str) -> None:
    # 32-bits long
    salt = os.urandom(32)           # anti rainbow table and brute force

    # pbkdf2 is just some function
    key = hashlib.pbkdf2_hmac(
        'sha256',                   # the alg being used
        password.encode('utf-8'),   # encode to get bytes
        salt,                       # adding the salt
        100000)                     # number of iterations

    b64_key = base64.b64encode(key)
    b64_uname = base64.b64encode(username.encode('utf-8'))
    b64_salt = base64.b64encode(salt)
    # not sure why I used base64, but it didn't
    # work when I tried to do it without it

    with open("data/hashed_login_data", "a") as f:
        f.write(f"{b64_uname}${b64_salt}${b64_key}\n")


def save_user_details(user_dict: dict) -> None:
    user_data = user_dict

    try:
        with open("data/users.json", "r") as file:
            users = json.load(file)

    except FileNotFoundError:
        print("user data file is missing!")
        print("creating new file...")

        with open("data/users.json", "w") as file:
            json.dump(user_data, file)

        return

    with open("data/users.json", "w") as file:
        users[user_dict["username"]] = user_dict
        json.dump(users, file)

    return


def add_to_admins(username: str) -> None:
    pass

# {"username": "joeman", "first_name": "joe", "last_name": "mama", "phone": "123", "email": "123", "gender": "Musko", "ayyman": {"username": "ayyman", "first_name": "ayy", "last_name": "lmao", "phone": "123123123123", "email": "ayy@lmao.com", "gender": "Ostalo"}}


#
# if __name__ == "__main__":
#     register(input("username"), input("password"))
