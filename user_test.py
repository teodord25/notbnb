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

        df = convert.to_df("data/apartment_data.csv")
        details = df[df["Sifra"] == apartment_id]
        self.type = details.iat[0, 1]
        self.rooms = details.iat[0, 2]
        self.guests = details.iat[0, 3]
        self.location = details.iat[0, 4]
        self.address = details.iat[0, 5]
        self.avlb = details.iat[0, 6]
        self.host = details.iat[0, 7]
        self.price_per_night = details.iat[0, 8]
        self.status = details.iat[0, 9]

        if details.iat[0, 10] == "da":
            self.amenities = amenity_search(self.apt_id)
        else:
            self.amenities = None


class User:
    def __init__(self, username="Neregistrovan Korisnik", role="Neregistrovan"):
        if username == "Neregistrovan Korisnik":
            self.username = username
            self.role = role

        else:
            df = convert.to_df("data/user_data.csv")
            user_details = df[df["Korisnicko ime"] == username]
            # this is bad ------------^
            self.username = user_details.iat[0, 0]
            self.fname = user_details.iat[0, 1]
            self.lname = user_details.iat[0, 2]
            self.phone = user_details.iat[0, 3]
            self.email = user_details.iat[0, 4]
            self.gender = user_details.iat[0, 5]
            self.role = user_details.iat[0, 6]
            # this is also bad probably -^


if __name__ == "__main__":
    usr = User(input("username: "))
