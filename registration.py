import os
import hashlib
import base64
import pandas as pd
import convert


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

    try:
        with open("data/hashed_login_data", "a") as f:
            f.write(f"{b64_uname}${b64_salt}${b64_key}\n")

    except FileNotFoundError:
        print("login data file is missing!")
        print("creating new file...")

        with open("data/hashed_login_data", "w") as f:
            f.write(f"{b64_uname}${b64_salt}${b64_key}\n")

    return


def save_user_details(user_dict: dict) -> None:
    data = pd.DataFrame({i: [j] for i, j in user_dict.items()})

    try:
        # df = pd.read_csv(filepath_or_buffer="data/user_data.csv", delimiter=",")
        df = convert.to_df("data/user_data.csv")

        # df = df.append(data, ignore_index=True)
        df = pd.concat([df, data], ignore_index=True)

        convert.to_csv(df, "data/user_data.csv")

    except FileNotFoundError:
        print("user data file is missing!")
        print("creating new file...")

        df = pd.DataFrame(data)
        convert.to_csv(df, "data/user_data.csv")

    return


# if __name__ == "__main__":
#     register(input("username"), input("password"))
#     save_user_details()
