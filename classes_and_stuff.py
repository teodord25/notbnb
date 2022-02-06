import convert
import datetime


def compare(date1, sign, date2) -> bool:
    y1, m1, d1 = [int(i) for i in date1.split("-")]
    y2, m2, d2 = [int(i) for i in date2.split("-")]

    if "=" in sign:
        if y1 == y2 and m1 == m2 and d1 == d2:
            return True
        else:
            sign = sign.replace("=", "")
            # str.replace returns a copy!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

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
    def __init__(self, apartment_id, compute_avlb=False):
        self.apt_id = apartment_id

        df = convert.to_df("data/apartment_data.csv")
        details = df[df["Sifra"] == str(apartment_id)].squeeze()
        self.type = details["Tip"]
        self.rooms = details["Broj soba"]
        self.guests = details["Broj gostiju"]
        self.location = details["Lokacija"]
        self.address = details["Adresa"]

        if compute_avlb:
            self.avlb = free_time(self.apt_id)

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


# pls tell me I didn't mess something up by setting a default duration
class TimeFrame:
    def __init__(self, start: str, duration=1, end=""):
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

    def header(self, header=None):
        header = [
            "Sifra rezervacije", "Sifra apartmana", "Pocetak", "Broj nocenja",
            "Kraj", "Ukupna cena", "Gost/Kontakt osoba", "Status", "Gost1",
            "Gost2", "Gost3", "Gost4", "Gost5", "Gost6", "Gost7", "Gost8", "Grad"
        ]

        return header

    def list(self):
        # mfw
        city = " ".join(self.apartment.address.split(" | ")[1].split()[:-1])

        row = [
            self.res_id, self.apt_id, self.start, self.duration, self.end,

            int(self.apartment.price_per_night) * self.duration,

            f"{self.user.fname} {self.user.lname} ({self.user.username})",

            self.status,

            self.guests[0], self.guests[1], self.guests[2],
            self.guests[3], self.guests[4], self.guests[5],
            self.guests[6], self.guests[7], city
        ]

        return row

    # TODO check if current date is past the end date for
    #   every active reservation on startup?

#
# Long explanation of the check_availability() function
#

# Check every reservation and determines if the passed time frame
# is overlapping with any existing reservation
#
# The function does this by returning False,
# if the date being checked doesn't either:
#   start after the end of each reservation
#   end before the start of each reservation
#
# It's a little difficult to comprehend like this, so here's a visual proof:
#
# s_n - start of date being checked
# e_n - end of date being checked
#
# s_i - start of an existing reservation
# e_i - end of an existing reservation
#
# # checking every (start, end) pair of the existing reservations
# for (s_i, e_i) in existing_reservations:
#     if not (s_n > e_i  or  e_n < s_i):
#          return False
# return True
#
# occupied
# case 1:  s_n-------e_n            not(False  or  False) => not(False) => True
#               s_i------e_i        s_n > e_i  or  e_n < s_i => return False
#
# occupied
# case 2:       s_n-------e_n       not(False  or  False) => not(False) => True
#          s_i------e_i             s_n > e_i  or  e_n < s_i => return False
#
# occupied
# case 3:       s_n----e_n          not(False  or  False) => not(False) => True
#          s_i--------------e_i     s_n > e_i  or  e_n < s_i => return False
#
# occupied
# case 4:  s_n--------------e_n     not(False  or  False) => not(False) => True
#               s_i----e_i          s_n > e_i  or  e_n < s_i => return False
#
# not occupied (anywhere) == available
# case 5:  s_n----e_n               not(False  or  True) => not(True) => False
#                       s_i----e_i  s_n > e_i  or  e_n < s_i => do nothing
#
# not occupied (anywhere) == available
# case 6:               s_n----e_n  not(True  or  False) => not(True) => True
#          s_i----e_i               s_n > e_i  or  e_n < s_i => do nothing


def check_availability(start, end, apt_id, df=None, normal_mode=True):
    if not compare(start, "<", end):
        print("invalid date")
        return

    if df is None:
        try:
            df = convert.to_df("data/reservations.csv", use_cols=[2, 4])
        except FileNotFoundError:
            return True

    # filter for reservations only at this apartment
    df = df[df["Sifra apartmana"] == apt_id]
    # am I doing this twice??

    # start and end of the potential date that was passed as an argument
    s_n = start
    e_n = end

    for index in range(df.shape[0]):
        res = df.iloc[index]

        # start and end of each reservation in "reservations.csv"
        s_i = res["Pocetak"]
        e_i = res["Kraj"]

        # is sn >= ei
        if not (compare(s_n, ">=", e_i) or compare(e_n, "<=", s_i)):
            print(f"conflict with {s_i}, {e_i}")
            if normal_mode:
                return False
            else:
                return TimeFrame(s_i, end=e_i)
    return True


def free_time(apt_id):
    res_df = convert.to_df("data/reservations.csv", use_cols=[1, 2, 3, 4])
    df = res_df[res_df["Sifra apartmana"] == apt_id]
    # only the reservations for this apartment

    date = str(datetime.date.today())

    tf = TimeFrame(date, 30)
    ctf = False
    pairs = []

    s = tf.start
    e = tf.end

    while ctf is not True:
        ctf = check_availability(start=s, end=e, df=df, apt_id=apt_id, normal_mode=False)

        if ctf is True:
            pairs.append([s, e])
            return pairs

        cs = ctf.start
        ce = ctf.end

        # case 1
        if compare(cs, "<=", s) and compare(ce, ">=", e):
            return [[0, 0]]

        # case 2
        elif compare(cs, ">", s) and compare(ce, ">=", e):
            pairs.append([s, cs])
            return pairs
            # return pairs

        # case 3
        elif compare(cs, "<=", s) and compare(ce, "<", e):
            s = ce
            # pairs.append([ce, e])
            # return pairs

        # case 4
        elif compare(cs, ">", s) and compare(ce, "<", e):
            pairs.append([s, cs])
            s = ce
    #
    #
    # if not isinstance(ctf, TimeFrame):
    #     break
    #
    # free = False
    # if free:
    #     return pairs
    #
    # s = start
    # e = end
    #
        # s = tf.start
        # e = tf.end
        # id = apt_id
        #
        # pairs = []
        # free = False

    # def check_tf(tf, df, apt_id): #start, end, df, id, p, free):

    # # conflicting time frame
    # # conf_tf = check_availability(s, e, df=res_df, apt_id=id, normal_mode=False)
    # pair = [s, ctf.start]
    # pairs.append(pair)
    # s = ctf.end
    # if compare()
    #
    # ctf =
    #
    # check_tf()
    # return True
    #
    # if check_availability(s, e, df=res_df, apt_id=id) is True:
    #     return [tf.start[-5:], tf.end[-5:]]
    # else:
    #     while True:
    #
    #     # while isinstance((check_availability(s, e, df=res_df, apt_id=id, normal_mode=False)), TimeFrame):
    #     #     # conflicting time frame
    #     #     conf_tf = check_availability(s, e, df=res_df, apt_id=id, normal_mode=False)
    #     #     pair = [s, conf_tf.start]
    #     #     pairs.append(pair)
    #     #     s = conf_tf.end
    #     pairs.append(pair)
    #
    # self.avlb = pairs
    #
    # self.avlb = details["Dostupnost"]
    # # TODO change to only apply to the next 30 days
