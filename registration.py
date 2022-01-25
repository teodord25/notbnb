import os
import hashlib
import base64
import pandas as pd
import json


def register_user(username: str, password: str, admin_target_file=False) -> None:
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

    try:
        with open("data/hashed_login_data", "a") as f:
            f.write(f"{b64_uname}${b64_salt}${b64_key}\n")

    except FileNotFoundError:
        print("login data file is missing!")
        print("creating new file...")

        with open("data/hashed_login_data", "w") as f:
            f.write(f"{b64_uname}${b64_salt}${b64_key}\n")

    return


# changing json to csv
def save_user_details(user_dict: dict) -> None:
    data = pd.DataFrame({i: [j] for i, j in user_dict.items()})

    try:
        df = pd.read_csv(filepath_or_buffer="data/user_data.csv", delimiter=",")
        df = df.append(data, ignore_index=True)
        df.to_csv("data/user_data.csv", index=False)

    except FileNotFoundError:
        print("user data file is missing!")
        print("creating new file...")

        df = pd.DataFrame(data)
       # print(df)
        df.to_csv("data/user_data.csv", index=False)

    return


def add_to_admins(username: str) -> None:
    pass

# {"username": "joeman", "first_name": "joe", "last_name": "mama", "phone": "123", "email": "123", "gender": "Musko", "ayyman": {"username": "ayyman", "first_name": "ayy", "last_name": "lmao", "phone": "123123123123", "email": "ayy@lmao.com", "gender": "Ostalo"}}


#
# if __name__ == "__main__":
#     register(input("username"), input("password"))
#     save_user_details()
