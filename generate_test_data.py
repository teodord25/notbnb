import pandas as pd
import registration
import random
import convert
# from time_test import Reservation
import datetime
# import user_test
from classes_and_stuff import User
from classes_and_stuff import Reservation
from classes_and_stuff import Apartment
from classes_and_stuff import compare
from classes_and_stuff import amenity_search


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

    # .loc[] slicing includes both bounds
    hosts = user_df.iloc[0:20, 1:3]

    user_df.loc[0:20, "Uloga"] = 'Domacin'
    user_df.loc[21:22, "Uloga"] = 'Admin'
    lst_out = []

    amnt_lst = []

    # .loc[] slices include both bounds,
    # but .iloc[] slices work normally (???)

    for index in range(df.shape[0] // 2):
        tip = random.choice(["Ceo", "Soba"])

        rooms = 1
        if tip == "Ceo":
            rooms = random.randint(2, 3)

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

        price = round((1.2 ** rooms) * 18) + (2 * len(amenities))
        price = str(price)  # + " eur"

        dodaci = "da" if len(amenities) else "ne"

        row = [index, tip, rooms, guests, location, address, "24/7",
               host, price, random.choice(["aktivan", "neaktivan"]), dodaci]

        lst_out.append(row)
        amnt_lst.append([index, *amenities])

    amntdf = pd.DataFrame(amnt_lst, columns=["Sifra apartmana", "Dodatak 1", "Dodatak 2",
                                             "Dodatak 3", "Dodatak 4", "Dodatak 5"])

    convert.to_csv(amntdf, "data/amenities.csv")

    df_out = pd.DataFrame(
        lst_out,
        columns=["Sifra", "Tip", "Broj soba", "Broj gostiju", "Lokacija", "Adresa",
                 "Dostupnost", "Domacin", "Cena po noci (eur)", "Status", "Ameniti"]
    )

    convert.to_csv(df_out, "data/apartment_data.csv")


def generate_reservations():
    apt_df = convert.to_df("data/apartment_data.csv")
    usr_df = convert.to_df("data/user_data.csv")

    apt_rows = apt_df.shape[0]
    usr_rows = usr_df.shape[0]
    i = usr_rows // 3
    j = usr_rows

    # pick random apartments from all apartments, approx 1.5 times
    apt_indices = random.choices(range(apt_rows), k=apt_rows + apt_rows // 2)
    usr_indices = range(i)  # random.choices(range(usr_rows // 2), k=)
    guests_range = range(i, j)
    n = 0

    reservations = []

    for index in apt_indices:
        n += 1
        apt = Apartment(index)

        date = str(datetime.date.today())

        yr = random.randint(1970, int(date[:4]))
        mo = random.randint(1, 12)
        day = random.randint(1, 27)
        st = f"{yr}-{str(mo).zfill(2)}-{str(day).zfill(2)}"
        dur = random.randint(1, 30)

        user = User(user_id=random.choice(usr_indices))
        spots_left = int(apt.rooms) - 1

        guests = [None for _ in range(9)]
        if spots_left:
            for _ in range(spots_left):
                id = random.choice(guests_range)
                guest = User(user_id=id)
                fname = guest.fname
                lname = guest.lname
                # are getter methods necessary?

                guests.insert(0, f"{fname} {lname}")
                guests.pop()

        reservation = Reservation(reservation_id=n, start=st, duration=dur,
                                  apartment_id=index, username=user.username,
                                  guests=guests)

        if compare(reservation.end, "<", date):
            i = random.randint(1, 3)
            if i == 1:
                reservation.cancel()
            if i == 2:
                reservation.deny()
            if i == 3:
                reservation.finish()
        else:
            i = random.randint(1, 2)
            if i == 1:
                reservation.accept()

        # creating a reservation object wasn't really necessary I guess

        row = [
            reservation.res_id, reservation.apt_id, reservation.start,
            reservation.duration, reservation.end,
            f"{reservation.user.fname} {reservation.user.lname} ({reservation.user.username})",
            reservation.status,
            reservation.guests[0], reservation.guests[1], reservation.guests[2],
            reservation.guests[3], reservation.guests[4], reservation.guests[5],
            reservation.guests[6], reservation.guests[7]
        ]
        reservations.append(row)

    header = ["Sifra rezervacije", "Sifra apartmana", "Pocetak", "Broj nocenja",
              "Kraj", "Gost/Kontakt osoba", "Status", "Gost1", "Gost2", "Gost3",
              "Gost4", "Gost5", "Gost6", "Gost7", "Gost8"]

    df = pd.DataFrame(reservations, columns=header)
    convert.to_csv(df, "data/reservations.csv")


if __name__ == "__main__":
    # generate_apartments()
    # generate_users()
    generate_reservations()

# Why spend 1 hour creating testing data when you can
# spend 30 hours automating testing data generation
