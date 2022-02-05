import convert


def compare(date1, sign, date2) -> bool:
    y1, m1, d1 = [int(i) for i in date1.split("-")]
    y2, m2, d2 = [int(i) for i in date2.split("-")]

    if eval(f"{y1}{sign}{y2}"):
        return True

    elif y1 == y2:
        if eval(f"{m1}{sign}{m2}"):
            return True

        elif m1 == m2:
            if eval(f"{d1}{sign}{d2}"):
                return True

            else:
                return False
        else:
            return False
    else:
        return False


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
        details = df[df["Sifra"] == str(apartment_id)].squeeze()
        self.type = details["Tip"]
        self.rooms = details["Broj soba"]
        self.guests = details["Broj gostiju"]
        self.location = details["Lokacija"]
        self.address = details["Adresa"]

        self.avlb = details["Dostupnost"]
        # TODO this might be unnecessary
        #   (assume available for all undefined dates)

        self.host = details["Domacin"]
        self.price_per_night = details["Cena po noci (eur)"]
        self.status = details["Status"]

        if details["Ameniti"] == "da":
            self.amenities = amenity_search(self.apt_id)
        else:
            self.amenities = None


class User:
    def __init__(self, user_id=None, username=None):
        if (user_id is None and username is None):
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
            self.fname = user_details["Ime"]
            self.lname = user_details["Prezime"]
            self.phone = user_details["Kontakt telefon"]
            self.email = user_details["Email adresa"]
            self.gender = user_details["Pol"]
            self.role = user_details["Uloga"]


class TimeFrame:
    def __init__(self, start: str, duration: int, end=""):
        self.start = start
        self.duration = duration
        self.end = end

        self.year, self.month, self.day = [int(i) for i in start.split("-")]

        if self.end == "":
            self.compute_end()

    def leap_check(self, year=None):
        leap_year = False

        year = self.year if year is None else year

        if year % 4 == 0:
            leap_year = True

            if year % 100 == 0:
                if year % 400 == 0:
                    leap_year = True
                else:
                    leap_year = False

        return leap_year

    # I could probably use this logic to compute
    # a date backwards, but I can't be bothered
    def compute_end(self, start="", duration=0):
        if not duration:
            duration = self.duration

        if start:
            start_year, start_month, start_day = [int(i) for i in start.split("-")]
        else:
            start_year = self.year
            start_month = self.month
            start_day = self.day

        leap = self.leap_check(start_year)

        lookup = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        lookup[1] += leap

        if start_day + duration <= lookup[start_month - 1]:
            end_month = str(start_month).zfill(2)
            end_day = str(start_day + duration).zfill(2)
            self.end = f"{start_year}-{end_month}-{end_day}"

            # print(f"computed end {self.end}")
            return

        remaining = lookup[start_month - 1] - start_day
        duration -= remaining

        end_year = start_year
        # curr_month = start_month + 1
        curr_month = start_month + 1
        if curr_month >= 12:
            curr_month = 0
            end_year += 1

        while duration > lookup[curr_month - 1]:
            duration -= lookup[curr_month - 1]
            curr_month += 1

        end_month = str(curr_month).zfill(2)
        end_day = str(duration).zfill(2)

        self.end = f"{end_year}-{end_month}-{end_day}"

        # print(f"computed end {self.end}")
        return


class Reservation(TimeFrame):
    def __init__(self, reservation_id, start, duration, apartment_id, username, status="Kreirana", guests=None):
        super().__init__(start, duration)

        self.res_id = reservation_id

        self.apt_id = apartment_id
        self.user = User(username=username)
        self.apartment = Apartment(self.apt_id)
        self.status = status
        self.guests = guests

    def cancel(self):
        self.status = "Odustanak"

    def deny(self):
        self.status = "Odbijena"

    def accept(self):
        self.status = "Prihvacena"

    # manual
    def finish(self):
        self.status = "Zavrsena"

    # TODO check if current date is past the end date for
    #   every active reservation on startup?

