import pandas as pd
import registration
import random


def generate_users():
    df = pd.read_csv("fake_people.csv", delimiter=',', usecols=range(7))

    # translate columns
    df = df.rename(columns={
        "Username": "Korisnicko ime",
        "GivenName": "Ime",
        "Surname": "Prezime",
        "TelephoneNumber": "Kontakt telefon",
        "EmailAddress": "Email adresa",
        "Gender": "Pol"
    })
    # possibly catastrophic comma removal in dict

    # set every fake users role to guest
    df["Uloga"] = ["Gost" for _ in range(df.shape[0])]

    for index in range(df.shape[0]):
        row = df.iloc[index]
        row_dict = dict(row)

        registration.register_user(row_dict["Korisnicko ime"], row_dict["Password"])

        # delete the password entry
        del row_dict["Password"]

        # translate the gender value for each row
        row_dict["Pol"] = "Musko" if row_dict["Pol"] == "male" else "Zensko"

        registration.save_user_details(row_dict)

        print(f"{index} registered: {row_dict['Korisnicko ime']}")
    print(pd.read_csv("data/user_data.csv", delimiter=','))

    # df_in = df_in.rename(columns={
    #     "Longitude": "Geografska duzina",
    #     "Latitude": "Geografska sirina",
    #     "StreetAddress": "Ulica i broj",
    #     "City": "Naseljeno Mesto",
    #     "ZipCode": "Postanski broj"
    # })

    # df_in.insert(loc=0, column="Sifra", value=[0 for _ in range(df_in.shape[0])])
    # df_in.insert(loc=1, column="Tip", value=["" for _ in range(df_in.shape[0])])
    # df_in.insert(loc=2, column="Broj soba", value=[0 for _ in range(df_in.shape[0])])
    # df_in.insert(loc=3, column="Broj gostiju", value=[0 for _ in range(df_in.shape[0])])
    # print(df_in)

def generate_apartments():
    df = pd.read_csv("fake_people.csv", usecols=range(7, 12))

    user_df = pd.read_csv("data/user_data.csv")
    print(user_df)

    # .loc[] slicing includes both bounds
    hosts = user_df.iloc[0:20, 1:3]
    # admins = user_df.iloc[21:23, 1:3]

    # print(hosts)
    # df = pd.read_csv("data/user_data.csv")
    user_df.loc[0:20, "Uloga"] = 'Domacin'
    user_df.loc[21:22, "Uloga"] = 'Admin'
    lst_out = []

    # .loc[] slices include both bounds,
    # but .iloc[] slices work normally (???)

    for index in range(df.shape[0]//2):
        tip = random.choice(["Ceo", "Soba"])

        rooms = 1
        if tip == "Ceo":
            rooms = random.randint(2, 4)

        # up to 3 people per room
        guests = random.randint(1, 3) * rooms

        i = index % random.randint(15, 20)
        host = " ".join([hosts.iat[i, 0], hosts.iat[i, 1]])
        city = df.iat[i, 3]

        lat = df.iat[index, 1]
        lon = df.iat[index, 0]
        zip = df.iat[index, 4]
        location = f"({lat}, {lon})"

        address = df.iat[index, 2].split()
        address.append(address[0])
        address.pop(0)
        address = " ".join(address)
        address = f"{address}, {city} {zip}"

        price = round((1.2**rooms) * 20)

        row = [index, tip, rooms, guests, location, address, "24/7",
               host, price, random.choice(["yes", "no"]), ["foo", "bar"]]

        lst_out.append(row)

    df_out = pd.DataFrame(
        lst_out,
        columns=["Sifra", "Tip", "Broj soba", "Broj gostiju", "Lokacija", "Adresa",
                 "Dostupnost", "Domacin", "Cena po noci", "Status", "Ameniti"]
    )

    df_out.to_csv("data/apartment_data.csv", index=False)
    print(df_out)


if __name__ == "__main__":
    generate_apartments()
    # generate_users()

# .loc[] not .loc()
#        why
