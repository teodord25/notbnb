import hashlib
import base64


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

#
# if __name__ == "__main__":
#     log_in(input("username"), input("password"))
