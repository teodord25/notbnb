import csv
import registration

import pandas as pd
# this is redundant now, # pandas is fucking awesome #
# def read():
#     with open("fake_people.csv", "r") as csv_file:
#         csv_reader = csv.reader(csv_file, delimiter=',')
#         line_count = 0
#         for row in csv_reader:
#             if line_count == 0:
#                 print(f"{'|'.join([w.ljust(12) for w in row])}")
#                 print("-"*100)
#                 line_count += 1
#             else:
#                 print(f"{'|'.join([w.ljust(12) for w in row])}")
#                 line_count += 1
#         print(f"processed {line_count} lines")
import registration


def panda():
    joe = pd.read_csv(filepath_or_buffer="fake_people.csv", delimiter=',', usecols=range(7))
    print(joe)

def autoregister():
    df = pd.read_csv("fake_people.csv", delimiter=',', usecols=range(7))

    df = df.rename(columns={
        "Username": "Korisnicko ime",
        "GivenName": "Ime",
        "Surname": "Prezime",
        "TelephoneNumber": "Kontakt telefon",
        "EmailAddress": "Email adresa",
        "Gender": "Pol",
    })

    df["Uloga"] = ["Gost" for _ in range(df.shape[0])]

    for index in range(df.shape[0]):
        row = df.iloc[index]
        row_dict = dict(row)

        registration.register_user(row_dict["Korisnicko ime"], row_dict["Password"])

        del row_dict["Password"]

        row_dict["Pol"] = "Musko" if row_dict["Pol"] == "male" else "Zensko"

        registration.save_user_details(row_dict)

        print(f"{index} registered: {row_dict['Korisnicko ime']}")

    print(pd.read_csv("data/user_data.csv", delimiter=','))

    # df1 = pd.DataFrame({"Username": ["uname"],
    #                     "Password": ["pwd"],
    #                     "GivenName": ["joe"],
    #                     "Surname": ["mama"],
    #                     "TelephoneNumber": ["03993939"],
    #                     "EmailAddress": ["joe@mama.com"],
    #                     "Gender": ["ayylien"],
    #                    })
    # df2 = df1
    # print(df1)
    # print(df2)
    # df3 = df1.append(df2, ignore_index=True)
    # print(df3)
# #     joe.append(df, ignore_index=True)

    # [registration.register_user() for ]
    # row = joe.iloc[1]
   #  print(joe)
    # this is redundant now, # pandas is fucking awesome #


# when converting a dict to a dataframe you must have lists as the values

def generate_apartments():
    pass


def write():
    pass


if __name__ == "__main__":
    # generate_apartments()
    autoregister()
