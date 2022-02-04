import pandas as pd
import registration
import random
import convert


def generate_users():
    df = convert.to_df("fake_people.csv", use_cols=range(7))
    # df = pd.read_csv("fake_people.csv", delimiter=',', usecols=range(7))

    # translate columns
    df = df.rename(columns={
        "Username": "Korisnicko ime",
        "GivenName": "Ime",
        "Surname": "Prezime",
        "TelephoneNumber": "Kontakt telefon",
        "EmailAddress": "Email adresa",
        "Gender": "Pol"
    })

    # add an "uloga" column and set all values to gost
    df["Uloga"] = "Gost"

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


def generate_apartments():
    df = convert.to_df("fake_people.csv", use_cols=range(7, 12))

    user_df = pd.read_csv("data/user_data.csv")
    # print(user_df)

    # .loc[] slicing includes both bounds
    hosts = user_df.iloc[0:20, 1:3]

    user_df.loc[0:20, "Uloga"] = 'Domacin'
    user_df.loc[21:22, "Uloga"] = 'Admin'
    lst_out = []

    amnt_lst = []

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
        location = f"({lat} | {lon})"

        address = df.iat[index, 2].split()
        address.append(address[0])
        address.pop(0)
        address = " ".join(address)
        address = f"{address} | {city} {zip}"

        k = random.randint(0, 5)
        amenities = random.sample(["parking", "kuhinja", "pegla", "ves masina", "klima uredjaj"], k=k)

        price = round((1.2**rooms) * 18) + (2 * len(amenities))
        price = str(price)# + " eur"

        dodaci = "da" if len(amenities) else "ne"

        row = [index, tip, rooms, guests, location, address, "24/7",
               host, price, random.choice(["aktivan", "neaktivan"]), dodaci]

        lst_out.append(row)
        amnt_lst.append([index, *amenities])

    amntdf = pd.DataFrame(amnt_lst, columns=["Sifra apartmana", "Dodatak 1", "Dodatak 2",
                                              "Dodatak 3", "Dodatak 4", "Dodatak 5"])

    convert.to_csv(amntdf, "data/amenities.csv")
    # amntdf.to_csv("data/amenities.csv", index=False)

    df_out = pd.DataFrame(
        lst_out,
        columns=["Sifra", "Tip", "Broj soba", "Broj gostiju", "Lokacija", "Adresa",
                 "Dostupnost", "Domacin", "Cena po noci (eur)", "Status", "Ameniti"]
    )

    convert.to_csv(df_out, "data/apartment_data.csv")
    # df_out.to_csv("data/apartment_data.csv", index=False)
    # print(df_out)


def generate_reservations():
    header = ["Sifra apartmana", "Pocetni datum rezervacije",
              "Broj nocenja", "Ukupna cena", "Gost", "Status"]

    aprt_df = convert.to_df("data/apartment_data.csv")
    aprt_df = aprt_df[aprt_df["Status"] == "aktivan"]
    print(aprt_df)


if __name__ == "__main__":
    generate_apartments()
    # generate_users()
    # generate_reservations()

# .loc[] not .loc()
#        why
