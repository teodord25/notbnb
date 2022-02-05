import convert


def amenity_search(apartment_id):
    apt_id = apartment_id

    df = convert.to_df("data/amenities.csv")
    details = df[df["Sifra apartmana"] == apt_id]
    return dict(details.squeeze())
    # sqeeze -> turns df into series


class Apartment:
    def __init__(self, apartment_id):
        self.apt_id = apartment_id

        # TODO refactor this
        df = convert.to_df("data/apartment_data.csv")
        details = df[df["Sifra"] == apartment_id]
        self.type = details.iat[0, 1]
        self.rooms = details.iat[0, 2]
        self.guests = details.iat[0, 3]
        self.location = details.iat[0, 4]
        self.address = details.iat[0, 5]

        self.avlb = details.iat[0, 6]
        # TODO this might be unnecessary
        #   (assume available for all undefined dates)

        self.host = details.iat[0, 7]
        self.price_per_night = details.iat[0, 8]
        self.status = details.iat[0, 9]

        if details.iat[0, 10] == "da":
            self.amenities = amenity_search(self.apt_id)
        else:
            self.amenities = None


class User:
    def __init__(self, user_id=None, username=None):
        if user_id is None and username is None:
            self.username = "Neregistrovan Korisnik"
            self.role = "Neregistrovan"
            self.usr_id = -1

        else:
            df = convert.to_df("data/user_data.csv")

            # select by username
            if username is not None:
                user_details = df[df["Korisnicko ime"] == username].squeeze()
                # this is probably bad -----^

            # select by id
            else:
                user_details = df.iloc[user_id]

            self.username = user_details["Korisnicko ime"]
            self.fname = user_details.iat["Ime"]
            self.lname = user_details.iat["Prezime"]
            self.phone = user_details.iat["Kontakt telefon"]
            self.email = user_details.iat["Email adresa"]
            self.gender = user_details.iat["Pol"]
            self.role = user_details.iat["Uloga"]


if __name__ == "__main__":
    usr = User(input("username: "))
