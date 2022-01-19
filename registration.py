import os
import hashlib
import base64


def register(username: str, password: str):
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


def save_user_details(detail_list):
    user_data = "$".join(detail_list)

    with open("data/user_details.txt", "a") as f:
        f.write(user_data + '\n')


if __name__ == "__main__":
    register(input("username"), input("password"))
