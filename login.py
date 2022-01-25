import hashlib
import base64
import pandas as pd


# ',' is default delimiter?
def get_role(username):
    df = pd.read_csv("data/user_data.csv", delimiter=',', usecols=[0, 6])

    try:
        result_df = df[df["Korisnicko ime"].isin([username])]
        result_df.reset_index(drop=True, inplace=True)
        # reset the index to start from zero,
        # without this, the result dataframe keeps the rows index
        #
        # e.g.  print(result_df)
        #
        #       Korisnicko ime  Uloga
        # 200   test            Gost

        return result_df.at[0, "Uloga"]

    except KeyError:
        return "Error"

    # result = df[df["Korisnicko ime"].str.contains(username)]

def is_admin(username: str) -> None:
    pass


def log_in(username: str, password: str) -> bool:
    with open("data/hashed_login_data", "r") as f:
        lines = f.readlines()

        for line in lines:
            items = [n for n in line.split('$')]
            _uname = items[0]
            _uname = eval(_uname).decode('utf-8')
            # can this eval() be exploited?

            _uname = base64.b64decode(_uname).decode('utf-8')

    #        _uname = base64.b64decode(
    #            eval(items[0]).decode('utf-8').decode('utf-8')
    #        )

            if username == _uname:
                _salt = items[1]
                _key = items[2]

                _salt = eval(_salt).decode('utf-8')
                _key = eval(_key).decode('utf-8')

                _salt = base64.b64decode(_salt)
                _key = base64.b64decode(_key)

                key = hashlib.pbkdf2_hmac(
                    'sha256', password.encode('utf-8'), _salt, 100000
                )

                if key == _key:
                    return True

                return False


if __name__ == "__main__":
    # log_in(input("username"), input("password"))
    get_role(input("username: "))
