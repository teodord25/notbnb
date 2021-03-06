import pandas as pd
import registration
import random
import convert
import datetime
from classes_and_stuff import User
from classes_and_stuff import Reservation
from classes_and_stuff import Apartment
from classes_and_stuff import compare
from classes_and_stuff import amenity_search
from classes_and_stuff import check_availability


def generate_users():
    df = convert.to_df("fake_people.csv", use_cols=range(7))

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

        row = [index, tip, rooms, guests, location, address,
               host, price, random.choice(["aktivan", "neaktivan"]), dodaci]

        lst_out.append(row)
        amnt_lst.append([index, *amenities])

    amntdf = pd.DataFrame(amnt_lst, columns=["Sifra apartmana", "Dodatak 1", "Dodatak 2",
                                             "Dodatak 3", "Dodatak 4", "Dodatak 5"])

    convert.to_csv(amntdf, "data/amenities.csv")

    df_out = pd.DataFrame(
        lst_out,
        columns=["Sifra", "Tip", "Broj soba", "Broj gostiju", "Lokacija", "Adresa",
                 "Domacin", "Cena po noci (eur)", "Status", "Ameniti"]
    )

    convert.to_csv(df_out, "data/apartment_data.csv")


def generate_reservations():
    apt_df = convert.to_df("data/apartment_data.csv")
    usr_df = convert.to_df("data/user_data.csv")

    apt_rows = apt_df.shape[0]
    usr_rows = usr_df.shape[0]
    i = usr_rows // 3
    j = usr_rows

    # pick random apartments from all apartments, 4 times as many times (?)
    apt_indices = random.choices(range(apt_rows), k=apt_rows*4)
    usr_indices = range(i)
    guests_range = range(i, j)
    n = 0

    reservations = []

    for index in apt_indices:
        n += 1
        apt = Apartment(index)

        date = str(datetime.date.today())

        yr = random.randint(2020, int(date[:4]))
        mo = random.randint(1, 12)
        day = random.randint(1, 27)
        st = f"{yr}-{str(mo).zfill(2)}-{str(day).zfill(2)}"
        dur = random.randint(1, 15)

        user = User(user_id=random.choice(usr_indices))

        guests = []
        for _ in range(8):
            guest = User(random.choice(guests_range))
            guest = " ".join([guest.fname, guest.lname])
            guests.append(guest)

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

        row = reservation.row_data()
        header = reservation.header

        # not the most efficient way of doing this, but it's whatever now
        temp_df = pd.DataFrame(reservations, columns=header)
        if check_availability(
            reservation.start, reservation.end, reservation.apt_id, df=temp_df
        ):
            print(f"{n} {reservation.apt_id} {reservation.apartment.host} "
                  f"{reservation.apartment.rooms} {len([i for i in guests if i != 'ne postoji'])}")
            reservations.append(row)

    df = pd.DataFrame(reservations, columns=header)
    convert.to_csv(df, "data/reservations.csv")


def update_users():
    hosts = list(convert.to_df("data/apartment_data.csv", use_cols=[7]).squeeze())
    df = convert.to_df("data/user_data.csv")

    for i in range(df.shape[0]):
        host = " ".join([df.iat[i, 1], df.iat[i, 2]])
        if host in hosts:
            df.iat[i, 6] = "Domacin"

    convert.to_csv(df, "data/user_data.csv")


if __name__ == "__main__":
    # generate_apartments()
    # generate_users()
    # generate_reservations()
    update_users()

# Why spend 1 hour creating testing data when you can
# spend 40 hours automating testing data generation
