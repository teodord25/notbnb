import convert
import datetime
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
import pandas as pd


class Error(Exception):
    pass


class InvalidDateError(Error):
    """Raised when a TimeFrame object (or child) recieve an invalid date"""
    pass


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
        self.spots = details["Broj gostiju"]
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
        if user_id is None and username is None:
            self.username = "Neregistrovan Korisnik"
            self.role = "Neregistrovan"

            # why??
            self.usr_id = -1

            self.fname = ""
            self.lname = ""

        else:
            df = convert.to_df("data/user_data.csv")

            # select by username
            if username is not None:
                user_details = df[df["Korisnicko ime"] == username].squeeze()
                # this is probably bad -----^

            # select by id
            else:
                # why did I ever add this???
                user_details = df.iloc[user_id]

            self.username = user_details["Korisnicko ime"]
            self.fname = user_details["Ime"]
            self.lname = user_details["Prezime"]
            self.phone = user_details["Kontakt telefon"]
            self.email = user_details["Email adresa"]
            self.gender = user_details["Pol"]
            self.role = user_details["Uloga"]

    def log_out(self):
        self.username = "Neregistrovan Korisnik"
        self.role = "Neregistrovan"


# pls tell me I didn't mess something up by setting a default duration
class TimeFrame:
    def __init__(self, start: str, duration=1, end=""):
        self.start = start
        self.duration = duration
        self.end = end

        self.date_check()

        self.year, self.month, self.day = [int(i) for i in start.split("-")]

        if self.end == "":
            self.compute_end()

    def date_check(self, start=""):
        if start == "":
            _start = self.start.split("-")
        else:
            _start = start

        if len(_start) != 3:
            print("invalid start date")
            raise InvalidDateError

        try:
            y, m, d = _start
            y = int(y)
            m = int(m)
            d = int(d)

            if y < 0:
                raise InvalidDateError
            if not 1 <= m <= 12:
                raise InvalidDateError

            if m == 2:
                leap = self.leap_check(y)
                if leap:
                    if not 1 <= d <= 29:
                        raise InvalidDateError
                else:
                    if not 1 <= d <= 28:
                        raise InvalidDateError
            else:
                lookup = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                if not 1 <= d <= lookup[m - 1]:
                    raise InvalidDateError

            return 0

        except ValueError:
            print("invalid start date")
            raise InvalidDateError

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
    def __init__(self, start, duration, apartment_id, username, status="Kreirana", guests=None, reservation_id=None):
        super().__init__(start, duration)

        self.date_check()

        self.df = convert.to_df("data/reservations.csv")

        if reservation_id is None:
            # last reservation id in reservations.csv + 1
            self.res_id = int(self.df.iat[-1, 0]) + 1

        self.apt_id = apartment_id
        self.user = User(username=username)
        self.apartment = Apartment(self.apt_id)
        self.status = status
        self.guests = guests

        self.city = " ".join(self.apartment.address.split(" | ")[1].split()[:-1])

        spots_left = int(self.apartment.spots) - 1
        guests = ["ne postoji" for _ in range(spots_left)]

        if spots_left:
            for guest in self.guests:
                guests.insert(0, f"{guest[0]} {guest[1]}")
                guests.pop()

        self.guests = guests

        self.header = [
            "Sifra rezervacije", "Sifra apartmana", "Pocetak", "Broj nocenja",
            "Kraj", "Ukupna cena", "Gost/Kontakt osoba", "Status", "Gost1",
            "Gost2", "Gost3", "Gost4", "Gost5", "Gost6", "Gost7", "Gost8", "Grad"
        ]

    def cancel(self):
        self.status = "Odustanak"

    def deny(self):
        self.status = "Odbijena"

    def accept(self):
        self.status = "Prihvacena"

    # manual
    def finish(self):
        self.status = "Zavrsena"

    def row_data(self):
        row = [
            self.res_id, self.apt_id, self.start, self.duration, self.end,

            int(self.apartment.price_per_night) * self.duration,

            f"{self.user.fname} {self.user.lname} ({self.user.username})",

            self.status
        ]

        row = row.append(self.guests)
        return row

    def reserve(self):
        self.df = self.df.append(pd.DataFrame([self.row_data()]), ignore_index=True)
        convert.to_csv(self.df, "data/reservations.csv")

    # TODO check if current date is past the end date for
    #   every active reservation on startup?


# spots = ["ne postoji" for _ in range(9)]
# if spots_left:
#     for _ in range(spots_left):
#         id = random.choice(guests_range)
#         guest = User(user_id=id)
#         fname = guest.fname
#         lname = guest.lname
#
#         spots.insert(0, f"{fname} {lname}")
#         spots.pop()

# guests = ["ne postoji" for i in range(self.apartment.spots)]
#
# Long explanation of the check_availability() function
#

# Checks every reservation and determines if the passed time frame
# is overlapping with any existing reservation.
#
# The function does this by returning False,
# if the date being checked doesn't either:
#   - start after or at the end of each reservation
#   - end before or at the start of each reservation
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
#     if not (s_n >= e_i  or  e_n <= s_i):
#          return False
# return True
#
# occupied (at least one conflict)
# case 1:  s_n-------e_n            not(False  or  False) -> not(False) -> True
#               s_i------e_i        s_n >= e_i  or  e_n <= s_i -> return False
#
# occupied (at least one conflict)
# case 2:       s_n-------e_n       not(False  or  False) -> not(False) -> True
#          s_i------e_i             s_n >= e_i  or  e_n <= s_i -> return False
#
# occupied (at least one conflict)
# case 3:       s_n----e_n          not(False  or  False) -> not(False) -> True
#          s_i--------------e_i     s_n >= e_i  or  e_n <= s_i -> return False
#
# occupied (at least one conflict)
# case 4:  s_n--------------e_n     not(False  or  False) -> not(False) -> True
#               s_i----e_i          s_n >= e_i  or  e_n <= s_i -> return False
#
# not occupied (no conflict found anywhere) == available
# case 5:  s_n----e_n               not(False  or  True) -> not(True) -> False
#                       s_i----e_i  s_n >= e_i  or  e_n <= s_i -> do nothing
#
# not occupied (no conflict found anywhere) == available
# case 6:               s_n----e_n  not(True  or  False) -> not(True) -> True
#          s_i----e_i               s_n >= e_i  or  e_n <= s_i -> do nothing


def check_availability(start, end, apt_id, df=None, normal_mode=True):
    if not compare(start, "<", end):
        print("invalid date")
        return

    if df is None:
        try:
            df = convert.to_df("data/reservations.csv", use_cols=[1, 2, 4])
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


# What a terrible day to have eyes
class ReservationLayout(QGridLayout): #QFormLayout):
    def __init__(self, user):
        super().__init__()

        self.reservationUser = user

        self._createWidgets()
        self._addToLayout()
        self.hideInfo()
        self.hideForm()

    def _showGuests(self, guests_n):
        guests = [
            self.reservationGuest1,
            self.reservationGuest2,
            self.reservationGuest3,
            self.reservationGuest4,
            self.reservationGuest5,
            self.reservationGuest6,
            self.reservationGuest7,
            self.reservationGuest8
        ]

        labels = [
            self.label5,
            self.label6,
            self.label7,
            self.label8,
            self.label9,
            self.label10,
            self.label11,
            self.label12
        ]

        # is this even legal
        for i in range(guests_n):
            guests[i].show()
            labels[i].show()

    def _createWidgets(self):
        self.info0 = QLabel("")
        self.info1 = QLabel("")
        self.info2 = QLabel("")
        self.info3 = QLabel("")
        self.info4 = QLabel("")
        self.info5 = QLabel("")
        self.info6 = QLabel("")
        self.info7 = QLabel("")
        self.info8 = QLabel("")
        self.info9 = QLabel("")

        self.reservationStart = QLineEdit()
        self.reservationDuration = QLineEdit()
        self.reservationGuest1 = QLineEdit()
        self.reservationGuest2 = QLineEdit()
        self.reservationGuest3 = QLineEdit()
        self.reservationGuest4 = QLineEdit()
        self.reservationGuest5 = QLineEdit()
        self.reservationGuest6 = QLineEdit()
        self.reservationGuest7 = QLineEdit()
        self.reservationGuest8 = QLineEdit()

        self.label0 = QLabel("Pocetak rezervacije: ")
        self.label1 = QLabel("Broj nocenja: ")

        self.label2 = QLabel("Sifra apartmana: ")

        fname = self.reservationUser.fname
        lname = self.reservationUser.lname
        uname = self.reservationUser.username

        user = f"{fname} {lname} ({uname})"
        self.label3 = QLabel(f"Prijavljeni ste kao: {user}")

        self.label4 = QLabel("Ako zakazujete za sebe, polja ispod ostavite prazno.")
        self.label5 = QLabel("Dodatni gost 1: ")
        self.label6 = QLabel("Dodatni gost 2: ")
        self.label7 = QLabel("Dodatni gost 3: ")
        self.label8 = QLabel("Dodatni gost 4: ")
        self.label9 = QLabel("Dodatni gost 5: ")
        self.label10 = QLabel("Dodatni gost 6: ")
        self.label11 = QLabel("Dodatni gost 7: ")
        self.label12 = QLabel("Dodatni gost 8: ")
        self.label13 = QLabel("Nema vise mesta za dodatne goste.")

    def _addToLayout(self):
        self.addWidget(self.info0, 0, 0)
        self.addWidget(self.info1, 1, 0)
        self.addWidget(self.info2, 2, 0)
        self.addWidget(self.info3, 3, 0)
        self.addWidget(self.info4, 4, 0)
        self.addWidget(self.info5, 5, 0)
        self.addWidget(self.info6, 6, 0, 3, 1)  # dostupnost
        self.addWidget(self.info7, 10, 0)
        self.addWidget(self.info8, 11, 0)
        self.addWidget(self.info9, 12, 0)
        self.addWidget(self.label0, 0, 1)
        self.addWidget(self.label1, 1, 1)
        self.addWidget(self.label2, 2, 1, 1, 2)
        self.addWidget(self.label3, 3, 1, 1, 2)
        self.addWidget(self.label4, 4, 1, 1, 2)
        self.addWidget(self.label5, 5, 1)
        self.addWidget(self.label6, 6, 1)
        self.addWidget(self.label7, 7, 1)
        self.addWidget(self.label8, 8, 1)
        self.addWidget(self.label9, 9, 1)
        self.addWidget(self.label10, 10, 1)
        self.addWidget(self.label11, 11, 1)
        self.addWidget(self.label12, 12, 1)
        self.addWidget(self.label13, 13, 1, 1, 2)
        self.addWidget(self.reservationStart, 0, 2)
        self.addWidget(self.reservationDuration, 1, 2)
        self.addWidget(self.reservationGuest1, 5, 2)
        self.addWidget(self.reservationGuest2, 6, 2)
        self.addWidget(self.reservationGuest3, 7, 2)
        self.addWidget(self.reservationGuest4, 8, 2)
        self.addWidget(self.reservationGuest5, 9, 2)
        self.addWidget(self.reservationGuest6, 10, 2)
        self.addWidget(self.reservationGuest7, 11, 2)
        self.addWidget(self.reservationGuest8, 12, 2)

    def hideInfo(self):
        return
        # self.info0.hide()
        # self.info1.hide()
        # self.info2.hide()
        # self.info3.hide()
        # self.info4.hide()
        # self.info5.hide()
        # self.info6.hide()
        # self.info7.hide()
        # self.info8.hide()
        # self.info9.hide()

    def hideForm(self):
        self.label0.hide()
        self.label1.hide()
        self.label2.hide()
        self.label3.hide()
        self.label4.hide()
        self.label5.hide()
        self.label6.hide()
        self.label7.hide()
        self.label8.hide()
        self.label9.hide()
        self.label10.hide()
        self.label11.hide()
        self.label12.hide()
        self.label13.hide()

        self.reservationStart.hide()
        self.reservationDuration.hide()
        self.reservationGuest1.hide()
        self.reservationGuest2.hide()
        self.reservationGuest3.hide()
        self.reservationGuest4.hide()
        self.reservationGuest5.hide()
        self.reservationGuest6.hide()
        self.reservationGuest7.hide()
        self.reservationGuest8.hide()

    def showInfo(self):
        self.info0.show()
        self.info1.show()
        self.info2.show()
        self.info3.show()
        self.info4.show()
        self.info5.show()
        self.info6.show()
        self.info7.show()
        self.info8.show()
        self.info9.show()

    def showForm(self, n):
        self._showGuests(n)
        self.label0.show()
        self.label1.show()
        self.label2.show()
        self.label3.show()
        self.label4.show()
        self.label13.show()

        self.reservationStart.show()
        self.reservationDuration.show()

        # self.label5.show()
        # self.label6.show()
        # self.label7.show()
        # self.label8.show()
        # self.label9.show()
        # self.label10.show()
        # self.label11.show()
        # self.label12.show()
        # self.reservationAptId.show()
        # self.reservationGuest1.show()
        # self.reservationGuest2.show()
        # self.reservationGuest3.show()
        # self.reservationGuest4.show()
        # self.reservationGuest5.show()
        # self.reservationGuest6.show()
        # self.reservationGuest7.show()
        # self.reservationGuest8.show()

    # self.addWidget(self.info0, 0, 0)
    # self.addWidget(self.info1, 1, 0)
    # self.addWidget(self.info2, 2, 0)
    # self.addWidget(self.info3, 3, 0)
    # self.addWidget(self.info4, 4, 0)
    # self.addWidget(self.info5, 5, 0)
    # self.addWidget(self.info6, 6, 0)
    # self.addWidget(self.info7, 7, 0)
    # self.addWidget(self.info8, 8, 0)
    # self.addWidget(self.info9, 9, 0)
    # self.addWidget(self.label0, 10, 0)
    # self.addWidget(self.label1, 11, 0)
    # self.addWidget(self.label2, 12, 0)
    # self.addWidget(self.label3, 13, 0)
    # self.addWidget(self.label4, 14, 0)
    # self.addWidget(self.label5, 15, 0)
    # self.addWidget(self.label6, 16, 0)
    # self.addWidget(self.label7, 17, 0)
    # self.addWidget(self.label8, 18, 0)
    # self.addWidget(self.label9, 19, 0)
    # self.addWidget(self.label10, 20, 0)
    # self.addWidget(self.label11, 21, 0)
    # self.addWidget(self.label12, 22, 0)
    # self.addWidget(self.reservationStart, 10, 1)
    # self.addWidget(self.reservationDuration, 11, 1)
    # self.addWidget(self.reservationAptId, 12, 1)
    # self.addWidget(self.reservationGuest1, 15, 1)
    # self.addWidget(self.reservationGuest2, 16, 1)
    # self.addWidget(self.reservationGuest3, 17, 1)
    # self.addWidget(self.reservationGuest4, 18, 1)
    # self.addWidget(self.reservationGuest5, 19, 1)
    # self.addWidget(self.reservationGuest6, 20, 1)
    # self.addWidget(self.reservationGuest7, 21, 1)
    # self.addWidget(self.reservationGuest8, 22, 1)
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


# self.widget0 = QLabel("")
# self.widget1 = QLabel("")
# self.widget2 = QLabel("")
# self.widget3 = QLabel("")
# self.widget4 = QLabel("")
# self.widget5 = QLabel("")
# self.widget6 = QLabel("")
# self.widget7 = QLabel("")
# self.widget8 = QLabel("")
# self.widget9 = QLabel("")
#
# self.infoLayout.addWidget(self.widget0)
# self.infoLayout.addWidget(self.widget1)
# self.infoLayout.addWidget(self.widget2)
# self.infoLayout.addWidget(self.widget3)
# self.infoLayout.addWidget(self.widget4)
# self.infoLayout.addWidget(self.widget5)
# self.infoLayout.addWidget(self.widget6)
# self.infoLayout.addWidget(self.widget7)
# self.infoLayout.addWidget(self.widget8)
# self.infoLayout.addWidget(self.widget9)
#
# self.reservationStart = QLineEdit()
# self.reservationDuration = QLineEdit()
# self.reservationAptId = QLineEdit()
# self.reservationUser = self.currentUser
# self.reservationGuest1 = QLineEdit()
# self.reservationGuest2 = QLineEdit()
# self.reservationGuest3 = QLineEdit()
# self.reservationGuest4 = QLineEdit()
# self.reservationGuest5 = QLineEdit()
# self.reservationGuest6 = QLineEdit()
# self.reservationGuest7 = QLineEdit()
# self.reservationGuest8 = QLineEdit()
#
# self.infoLayout.addWidget(self.reservationStart)
# self.infoLayout.addWidget(self.reservationDuration)
# self.infoLayout.addWidget(self.reservationAptId)
# # self.infoLayout.addWidget(self.reservationUser)
# self.infoLayout.addWidget(self.reservationGuest1)
# self.infoLayout.addWidget(self.reservationGuest2)
# self.infoLayout.addWidget(self.reservationGuest3)
# self.infoLayout.addWidget(self.reservationGuest4)
# self.infoLayout.addWidget(self.reservationGuest5)
# self.infoLayout.addWidget(self.reservationGuest6)
# self.infoLayout.addWidget(self.reservationGuest7)
# self.infoLayout.addWidget(self.reservationGuest8)
#
# self.infoLayout.addWidget(QLabel("Pocetak rezervacije: "))
# self.infoLayout.addWidget(QLabel("Broj nocenja: "))
# self.infoLayout.addWidget(QLabel("Sifra apartmana: "))
# self.infoLayout.addWidget(QLabel("Prijavljeni ste kao: "))
# self.infoLayout.addWidget(QLabel("Ako zakazujete za sebe, polja ispod ostavite prazno."))
# self.infoLayout.addWidget(QLabel("Dodatni gost 1"))
# self.infoLayout.addWidget(QLabel("Dodatni gost 2"))
# self.infoLayout.addWidget(QLabel("Dodatni gost 3"))
# self.infoLayout.addWidget(QLabel("Dodatni gost 4"))
# self.infoLayout.addWidget(QLabel("Dodatni gost 5"))
# self.infoLayout.addWidget(QLabel("Dodatni gost 6"))
# self.infoLayout.addWidget(QLabel("Dodatni gost 7"))
# self.infoLayout.addWidget(QLabel("Dodatni gost 8"))
