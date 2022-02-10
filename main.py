import PyQt5.QtWidgets
import datetime
from classes_and_stuff import InvalidSearchError
from classes_and_stuff import InvalidDateError
from classes_and_stuff import TimeFrame
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QTableView
from PyQt5.QtWidgets import QMenuBar
from PyQt5.QtWidgets import QCheckBox
from PyQt5 import QtCore

from functools import partial
import pandas as pd
import time
import sys
import json
import registration
import login
import convert
import time_test
from classes_and_stuff import User
from classes_and_stuff import Apartment
from classes_and_stuff import compare
from classes_and_stuff import ReservationLayout
from classes_and_stuff import check_availability
from classes_and_stuff import Reservation
from collections import Counter


# date = start.split("-")
# self.year = date[0]
# self.month = date[1]
# self.day = date[2]


# format 2022-06-09
# MAX DAYS TO BOOK 30
# no need to check validity of date as it is picked from a drop-down menu
# class TimeFrame:
#     def __init__(self, start:str, duration:int, end=""):
#         self.start = start
#         self.duration = duration
#         self.end = end
#
#         self.year, self.month, self.day = start.split("-")
#
#         if self.end == "":
#             self.compute_end()
#
#     def leap_check(self, year=None):
#         leap_year = False
#
#         year = int(self.year) if year is None else year
#
#         if year % 4 == 0:
#             leap_year = True
#
#             if year % 100 == 0:
#                 if year % 400 == 0:
#                     leap_year = True
#                 else:
#                     leap_year = False
#
#         return leap_year
#
#     def compute_end(self, start="", duration=0):
#         if not duration:
#             duration = self.duration
#
#         if start:
#             start_year, start_month, start_day = [int(i) for i in start.split("-")]
#         else:
#             start_year = self.year
#             start_month = self.month
#             start_day = self.day
#
#         leap = self.leap_check(start_year)
#
#         lookup = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
#
#         lookup[1] += leap
#
#         if start_day + duration <= lookup[start_month - 1]:
#             end_month = start_month
#             end_day = start_day + duration
#             return f"{start_year}-{end_month}-{end_day}"
#
#         remaining = lookup[start_month - 1] - start_day
#         duration -= remaining
#
#         curr_month = start_month + 1
#         while duration > lookup[curr_month - 1]:
#             duration -= lookup[curr_month]
#
#         end_month = curr_month
#         end_day = duration
#
#         print(f"{start_year}-{end_month}-{end_day}")
#
#         #
#         # if start_month <= 7:
#         #     days = 30 + (start_month % 2)
#         # else:
#         #     days = 31 - (start_month % 2)
#         #
#         # end_day = (start_day + length) % days

def filter_df(dataframe, query, x):
    df = dataframe
    qr = query

    try:
        qr = int(qr)
        return df[df[x] == str(qr)]

    except ValueError:
        print("not int... doing comparison filter")

    try:
        qr = qr.replace(" ", "")
        for ch in qr:
            if ch not in "<>0123456789x":
                print("invalid input, illegal char")
                raise InvalidSearchError

        # put "" around every number
        s = []

        i = 0
        while i < len(qr):
            if qr[i].isnumeric():
                s.append('"')
                while qr[i].isnumeric():
                    s.append(qr[i])
                    i += 1
                    if i == len(qr):
                        break
                s.append('"')
            else:
                s.append(qr[i])
                i += 1

        qr = "".join(s)

        i = qr.index("x")

        if qr[i - 1:i] == qr[i + 1:i + 2]:
            qr1 = qr[i:]
            qr1 = qr1.replace("x", f'df["{x}"]')
            qr1 = f"df[{qr1}]"

            # df = eval(qr1)

            qr2 = qr[:i + 1]
            qr2 = qr2.replace("x", f'df["{x}"]')
            qr2 = f"df[{qr2}]"

            df = eval(qr2)

        else:
            qr = qr.replace("x", f'df["{x}"]')
            qr = f"df[{qr}]"
            df = eval(qr)

        return df

    except ValueError:
        print("value error")
        print("invalid input")
        raise InvalidSearchError

    except TypeError:
        print("type error")
        print("invalid input")
        raise InvalidSearchError

    except SyntaxError:
        print("syntax error")
        print("invalid input")
        raise InvalidSearchError


# class User:
#     def __init__(self, username="Neregistrovan Korisnik", role="Neregistrovan"):
#         if username == "Neregistrovan Korisnik":
#             self.username = username
#
#         if role == "Neregistrovan":
#             self.role = role
#
#         user_details = convert.to_df("data/user_data.csv").loc[[""]]
#

#
# class Apartment:
#     def __init__(self, aprt_code: int, aprt_type: str, rooms_n: int, guests_n, location: tuple,
#                  availability: list, host: object, cost: int, status: bool, amenities: list):
#         self.aprt_code = aprt_code
#         self.aprt_type = aprt_type
#         self.rooms_n = rooms_n
#         self.guests_n = guests_n
#         self.location = location
#         self.availability = availability
#         self.host = host
#         self.cost = cost
#         self.status = status
#         self.amenities = amenities
#
#
# class Amenitiy:
#     def __init__(self, amnt_code, name):
#         self.amnt_code = amnt_code
#         self.name = name
#
#
# class Reservation:  # apartment
#     def __init__(self, aprt_code: int, start_date: str, duration_of_stay: int,
#                  total_cost: int, guest: object, status: str):
#         self.aprt_code = aprt_code
#         self.start_date = start_date
#         self.duration_of_stay = duration_of_stay
#         self.total_cost = total_cost
#         self.guest = guest
#         self.status = status
#
#     def cancel(self):
#         self.status = False


# when the admin requests a table,
#   only show the usernames,
#   but when clicked,
#   open a combo box with their details


class ProjekatWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("projekat_airbnb")

        # fixed size forces bspwm to make the window floating
        # but it's still resizable (???)
        self.setFixedSize(1280, 720)

        self.currentUser = User()

        self.baseDF = convert.to_df("data/apartment_data.csv")
        self.currentDF = self.baseDF.copy().loc[:, ["Sifra", "Tip", "Broj soba", "Broj gostiju",
                                                    "Adresa", "Cena po noci (eur)"]]

        # self.currentDF = convert.to_df("data/reservations.csv")

        self._clearScreen()
        self._createMenu()

    def _clearScreen(self):
        # app layout
        self.generalLayout = QVBoxLayout()

        # QWidget(self) == self as parent
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)

        self._createMenu()

    def _createMenu(self):
        menu = QMenuBar()
        self.setMenuBar(menu)

        userMenu = menu.addMenu("&Korisnik")
        apartmentMenu = menu.addMenu("&Apartmani")
        resMenu = menu.addMenu("&Rezervacije")

        userMenu.addAction('Prijavi se', self._createLoginScreen)
        userMenu.addAction('Registruj se', self._createRegisterScreen)
        userMenu.addAction('Odjavi se', self.logOut)

        apartmentMenu.addAction('Pretraga i rezervacija apartmana', self._createBrowsingScreen)

        if self.currentUser.role == "Domacin":
            apartmentMenu.addAction('Registracija apartmana', self.apartmentRegistration)

        resMenu.addAction('Vase rezervacije', self._createResReviewScreen)

    def _createResReviewScreen(self):
        resReviewLayout = QVBoxLayout()
        subLayout = QGridLayout()

        self._clearScreen()

        df = convert.to_df("data/reservations.csv", use_cols=range(8))

        self.model = tableModel(df)
        self.table = QTableView()
        self.table.setModel(self.model)

        # set the top row to fit the data
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(df.shape[1] - 1, QHeaderView.Stretch)
        for i in range(df.shape[1] - 1):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        subLayout.addWidget(QPushButton("bing bong"))

        resReviewLayout.addLayout(subLayout)
        resReviewLayout.addWidget(self.table)
        self.generalLayout.addLayout(resReviewLayout)

    def _submitRegistration(self):
        if not (self.registerUsername.text() and
                self.registerPassword.text() and
                self.confirmPassword.text() and
                self.registerFName.text() and
                self.registerLName.text() and
                self.registerPhone.text() and
                self.registerEmail.text() and
                self.genderCBox.currentText()
        ):
            print("field left empty")
            err = color_msg("Morate popuniti sva polja.", "Tomato")

            self._formMessage(msg=err)
            return

        if len(self.registerPassword.text()) < 8:
            print("password too short")
            err = color_msg("Lozinka mora sadrzati najmanje 8 karaktera.", "Tomato")

            self._formMessage(msg=err)
            return

        if self.registerPassword.text() != self.confirmPassword.text():
            print("passwords do not match")
            err = color_msg("Lozinke se ne podudaraju", "Tomato")

            self._formMessage(msg=err)
            return

        print("everything checks out, registering...")

        registration.register_user(
            self.registerUsername.text(), self.registerPassword.text()
        )

        print("saving user details...")
        registration.save_user_details({
            "Korisnicko ime": self.registerUsername.text(),
            "Ime": self.registerFName.text(),
            "Prezime": self.registerLName.text(),
            "Kontakt telefon": self.registerPhone.text(),
            "Email adresa": self.registerEmail.text(),
            "Pol": self.genderCBox.currentText(),
            "Uloga": "Gost"
        })

        print(f"registered user: \n\t{self.registerUsername.text()}")
        success = color_msg(
            f"Uspesno ste se registrovali. {self.registerUsername.text()}", "Lime"
        )

        self._formMessage(msg=success)
        return

    def _attemptLogin(self):
        username = self.loginUsername.text()
        password = self.loginPassword.text()

        if not (username and password):
            print("one or both fields left empty")
            err = color_msg("Popunite polja.", "Tomato")

            self._formMessage(msg=err)
            return

        # log_in() returns a bool
        if login.log_in(username, password):

            role = login.get_role(username)
            if role == "Error":
                print("no such user in data/user_data.csv")
                err = color_msg("Korisnik ne postoji u bazi podataka.", "Tomato")

                self._formMessage(err)
                return

            self.currentUser = User(username=username)
            # self.currentUser.username = username
            # self.currentUser.role = role

            print("login successful")

            succ = color_msg(f"Dobrodosao/la {username}", "Lime")

            self._formMessage(msg=succ)
            self._createMenu()
            return

        print("login failed")
        err = color_msg("Pogresno korisnicko ime ili lozinka.", "Tomato")

        self._formMessage(msg=err)
        return

    def _formMessage(self, msg):
        self.formMsg.hide()
        self.formMsg.setText(msg)
        self.formMsg.show()

    def _showPopularCities(self):
        df = convert.to_df("data/reservations.csv", use_cols=[2, 7, 16])
        # df = self.baseDF.copy()
        # df = df.loc[:, ["Pocetak", "Status", "Grad"]]

        date = str(datetime.date.today()).split("-")
        date[0] = str(int(date[0]) - 1)
        date = "-".join(date)

        lst = []
        for i in range(df.shape[0]):
            row = list(df.iloc[i])
            if compare(row[0], ">", date):
                lst.append(row)

        df = pd.DataFrame(lst, columns=["Pocetak", "Status", "Grad"])

        # df = df[compare(df["Pocetak"], ">", date)]
        # a =
        # a = convert.to_df("data/reservations.csv", use_cols=[8, 16])
        # b = convert.to_df("data/reservations.csv", use_cols=[8, 16])

        a = df[df["Status"] == "Zavrsena"]
        b = df[df["Status"] == "Prihvacena"]

        df = pd.concat([a, b])

        df = df.loc[:, "Grad"]
        cities = Counter(list(df))

        # lst = sorted(list({j: i for i, j in cities.items()}.items()))[-10:]

        rvrs_dct = {j: i for i, j in cities.items()}
        lst = list(rvrs_dct.items())
        lst = sorted(lst)
        pop_cities = reversed(lst[-10:])

        df = pd.DataFrame(pop_cities, columns=["Broj ostvarenih rezervacija", "Grad"])
        self.currentDF = df
        self._createBrowsingScreen()
        # self.currentDF = convert.to_df("data/apartment_data.csv")

    def _submitSearch(self, mode="search", aprt_id=0):
        # if mode == "review":
        #     df = pd.read_csv("data/apartment_data.csv").iloc[[aprt_id]]
        #     amenity_df = pd.read_csv("data/amenities.csv").iloc[[aprt_id]]
        # elif mode == "search":
        # df_base = convert.to_df("data/apartment_data.csv")
        df = self.baseDF.copy()

        # df = df.loc[:, ["Sifra", "Tip", "Broj soba", "Broj gostiju",
        #                  "Adresa", "Cena po noci (eur)"]]

        # TODO case insensitive search
        # current is sensitive
        df = df[df["Adresa"].str.contains(self.searchLocation.text())]

        # Example usage of multivariable search below:
        #
        # Explanation of how this could be done manually using nested lists,
        # but it's analogous to doing it with dataframes.
        #
        # This could be done manually by just accessing values in every nested \
        # list at the same index (the column index) and then \
        # rejecting or appending the current "row" (nested list) to a new list,
        # but that's just more unnecessary conversions of which I already have enough...
        #
        # search one
        # df = filter_df(df, query="x > 2", x="C")
        # filter_df -> return only rows of df \
        # that have a value larger than 2 in the "C" column
        #
        #                 search one
        # df = [[A, B, C], -> df = [[A, B, C],
        #       [1, 1, 4],          [1, 1, 4],
        #       [3, 0, 2],          [2, 3, 8],
        #       [2, 3, 8],          [2, 2, 3]]
        #       [2, 2, 3]]
        #
        # search two
        # df = filter_df(df, query="x <= 2", x="B")
        # filter_df -> return only rows of df \
        # that have a value less than or equal to 2 in the "B" column
        #
        #                 search one          search two
        # df = [[A, B, C], -> df = [[A, B, C], -> df = [[A, B, C],
        #       [1, 1, 4],          [1, 1, 4],          [1, 1, 4],
        #       [3, 0, 2],          [2, 3, 8],          [2, 2, 3]]
        #       [2, 3, 8],          [2, 2, 3]]
        #       [2, 2, 3]]

        try:
            rooms = self.searchRooms.text()
            if rooms:
                df = filter_df(df, query=rooms, x="Broj soba")

            persons = self.searchPersons.text()
            if persons:
                df = filter_df(df, query=persons, x="Broj gostiju")

            price = self.searchPrice.text()
            if price:
                df = filter_df(df, query=price, x="Cena po noci (eur)")

            if self.showActive.isChecked():
                df = df[df["Status"] == "aktivan"]

            df = df.loc[:, ["Sifra", "Tip", "Broj soba", "Broj gostiju",
                            "Adresa", "Cena po noci (eur)"]]

            # [:, [cols]]
            # : -> all rows
            # [cols] -> only "cols" columns

        except InvalidSearchError:
            print("invalid search")
            err = color_msg("Pogresan unos!", "Tomato")

            self.currentDF = df.loc[:, ["Sifra", "Tip", "Broj soba", "Broj gostiju", "Adresa", "Cena po noci (eur)"]]
            self._createBrowsingScreen()
            self.searchMsg.setText(err)
            return

        # if self.popularCities.isChecked():
        #     df = convert.to_df("data/reservations.csv", use_cols=[16])
        #
        #     df = df_base[df_base[""]]

        self.currentDF = df.loc[:, ["Sifra", "Tip", "Broj soba", "Broj gostiju", "Adresa", "Cena po noci (eur)"]]
        self._createBrowsingScreen()

        # I'm not sure how df[df[]] works

    # def _createReview(self):
    #     reviewLayout = QVBoxLayout
    #
    #     self._clearScreen()
    #
    #     self.generalLayout.addLayout(reviewLayout)

    def _createTopRow(self):
        topLayout = QGridLayout()
        textLayout = QGridLayout()

        self.searchLocation = QLineEdit()
        # self.searchAvailability = QLineEdit()
        self.searchRooms = QLineEdit()
        self.searchPersons = QLineEdit()
        self.searchPrice = QLineEdit()
        self.popularCities = QPushButton("Prikazi 10 najpopularnijih gradova")
        self.showActive = QCheckBox()
        self.searchMsg = QLabel("")

        # TODO fix shishana latinica
        self.searchButton = QPushButton("Pretrazi")
        self.searchButton.clicked.connect(
            partial(self._submitSearch, mode="search", aprt_id=20)
        )

        self.popularCities.clicked.connect(self._showPopularCities)

        topLayout.addWidget(QLabel(f"<h4>Vi ste: {self.currentUser.username}</h4>"), 0, 0)
        topLayout.addWidget(QLabel(f"<h4>Uloga: {self.currentUser.role}</h4>"), 1, 0)

        # TODO do something about the lack of dostupnost searching
        # (widget, y, x)
        topLayout.addWidget(self.searchMsg, 0, 1)
        topLayout.addWidget(QLabel("Mesto"), 0, 3)
        topLayout.addWidget(self.searchLocation, 0, 4, 1, 5)
        # topLayout.addWidget(QLabel("Dostupnost"), 1, 1)
        # topLayout.addWidget(self.searchAvailability, 1, 2)
        topLayout.addWidget(QLabel("Broj soba"), 1, 3)
        topLayout.addWidget(self.searchRooms, 1, 4)
        topLayout.addWidget(QLabel("Broj gostiju"), 1, 5)
        topLayout.addWidget(self.searchPersons, 1, 6)
        topLayout.addWidget(QLabel("Cena po noci"), 1, 7)
        topLayout.addWidget(self.searchPrice, 1, 8)
        topLayout.addWidget(self.searchButton, 0, 9, 2, 1)
        topLayout.addWidget(self.popularCities, 0, 1, 1, 2)
        topLayout.addWidget(QLabel(f"Potvrdite/osvezite pretragu pritiskom na dugme 'Pretrazi',\n"
                                   f"Mozete vratiti tabelu u prvobitno stanje (svi apartmani), "
                                   f"ako polja ostavite prazno kada pritisnete dugme."), 2, 0, 1, 8)

        # topLayout.addWidget(self.popularCities, 2, 2)
        topLayout.addWidget(QLabel("Prikazi samo aktivne apartmane"), 1, 1)
        topLayout.addWidget(self.showActive, 1, 2)
        topLayout.addWidget(QLabel(f"Primeri koriscenja pretrage: \n"
                                   f"Vrednost manja od: x < 3 je isto sto i 3 > x, isto vazi i za vece.\n"
                                   f"Vrednost izmedju: 2 < x < 5, ili samo unesite tacnu vrednost koju trazite."), 3, 0, 1, 8)
        topLayout.addWidget(QLabel("Dostupnost se racuna/proverava kad izaberete apartman!"), 3, 4, 1, 5)

        # textLayout.addWidget(QLabel("Primeri koriscenja pretrage:"))
        # textLayout.addWidget(QLabel("Vrednost manja od: x < 3 je isto sto i 3 > x, isto vazi i za vece."))
        # textLayout.addWidget(QLabel("Vrednost izmedju: 2 < x < 5, ili samo unesite tacnu vrednost koju trazite."))
        # textLayout.addWidget(QLabel("Dostupnost se racuna kad prikazete detalje apartmana"))
        #
        # topLayout.addLayout(textLayout, 3, 3, 1, 6)
        self.generalLayout.addLayout(topLayout)

    def _createRegisterScreen(self):
        registerLayout = QVBoxLayout()
        formLayout = QFormLayout()

        self._clearScreen()

        # self.registerScreen = QWidget(self._centralWidget)

        self.registerUsername = QLineEdit()
        self.registerPassword = QLineEdit()
        self.confirmPassword = QLineEdit()
        self.registerPhone = QLineEdit()
        self.registerEmail = QLineEdit()
        self.registerFName = QLineEdit()
        self.registerLName = QLineEdit()

        # Echo mode = hide characters "****"
        self.registerPassword.setEchoMode(QLineEdit.Password)
        self.confirmPassword.setEchoMode(QLineEdit.Password)

        # connect the "activated" signal to the self._submitRegistration slot (?)
        self.submitRegistrationButton = QPushButton("Registruj se")
        self.submitRegistrationButton.clicked.connect(
            self._submitRegistration
        )

        formLayout.addRow("Korisnicko ime:", self.registerUsername)
        formLayout.addRow("Lozinka:", self.registerPassword)
        formLayout.addRow("Potvrda lozinke:", self.confirmPassword)
        formLayout.addRow("Ime:", self.registerFName)
        formLayout.addRow("Prezime:", self.registerLName)
        formLayout.addRow("Kontakt telefon:", self.registerPhone)
        formLayout.addRow("Email adresa:", self.registerEmail)

        self.genderCBox = QComboBox()
        self.genderCBox.addItems(["", "Musko", "Zensko", "Ostalo"])
        formLayout.addRow("Pol:", self.genderCBox)

        registerLayout.addWidget(QLabel('<h1>Registruj se</h1>'))
        registerLayout.addLayout(formLayout)
        registerLayout.addWidget(self.submitRegistrationButton)

        self.formMsg = QLabel("")
        registerLayout.addWidget(self.formMsg)

        self.generalLayout.addLayout(registerLayout, 9)

    def _createLoginScreen(self):
        loginLayout = QVBoxLayout()
        formLayout = QFormLayout()

        self._clearScreen()

        # self.loginScreen = QWidget(self._centralWidget)

        self.loginUsername = QLineEdit()
        self.loginPassword = QLineEdit()

        self.loginUsername.returnPressed.connect(self._attemptLogin)
        self.loginPassword.returnPressed.connect(self._attemptLogin)

        self.loginPassword.setEchoMode(QLineEdit.Password)

        self.loginButton = QPushButton("Prijavi se")
        self.loginButton.clicked.connect(self._attemptLogin)

        formLayout.addRow("Korisnicko ime:", self.loginUsername)
        formLayout.addRow("Lozinka:", self.loginPassword)

        loginLayout.addWidget(QLabel('<h1>Prijavi se</h1>'), 3)
        loginLayout.addLayout(formLayout)
        loginLayout.addWidget(self.loginButton)

        self.formMsg = QLabel("")
        loginLayout.addWidget(self.formMsg, 1)

        self.generalLayout.addLayout(loginLayout, 9)

    def _createReview(self):
        try:
            # self.widget0.show()
            # self.widget1.show()
            # self.widget2.show()
            # self.widget3.show()
            # self.widget4.show()
            # self.widget5.show()
            # self.widget6.show()
            # self.widget7.show()
            # self.widget8.show()
            # self.widget9.show()

            self.resLayout.showInfo()
            self.resLayout.hideForm()
            int(self.requestApt.text())

            self.reviewWarning.setText("")

            # TODO make recovery functions (i.e. create_empty_reservations.csv with header)

            try:
                apt = Apartment(self.requestApt.text(), compute_avlb=True)
            # except IndexError:
            #     print("reservations.csv empty")
            #     err = color_msg("Fajl za rezervacije je prazan!", "Tomato")
            #
            #     self.reviewWarning.setText(err)
            #     return
            except FileNotFoundError:
                print("reservations.csv missing")
                err = color_msg("Fajl za rezervacije ne postoji!", "Tomato")

                self.reviewWarning.setText(err)
                return

            self.resLayout.info0.setText(f"Sifra: {apt.apt_id}")
            self.resLayout.info1.setText(f"Tip: {apt.type}")
            self.resLayout.info2.setText(f"Broj soba: {apt.rooms}")
            self.resLayout.info3.setText(f"Broj gostiju: {apt.spots}")
            self.resLayout.info4.setText(f"Lokacija: {apt.location}")
            self.resLayout.info5.setText(f"Adresa: {apt.address}")

            self.currentApt = apt

            # yeah idk even know anymore
            self.resLayout.apt = apt

            self.reviewMessage.setText(
                f"Ako Vam se dopada ovaj apartman, kliknite na dugme 'dalje' da predjete na rezervaciju.\n"
                f"Ako zelite pregledati neki drugi apartman ili sakriti polja za rezervaciju,\n"
                f"upisite neku drugu sifru (ili ostavite ovu) i pritisnite dugme 'prikazi apartman'."
            )

            self.goNext.show()

            tf = TimeFrame(str(datetime.date.today()), 30)
            ts = tf.start
            te = tf.end

            dostupnost = []
            for pair in apt.avlb:
                s, e = pair[0], pair[1]
                dostupnost.append(f"od {s}, do {e}")

            if ts == s and te == e:
                dostupnost.append("Slobodno je svih sledecih 30 dana.")

            dostupnost = "\n".join(dostupnost)

            self.resLayout.info6.setText(f"Dostupnost za sledecih 30 dana:\n{dostupnost}")

            self.resLayout.info7.setText(f"Domacin: {apt.host}")
            self.resLayout.info8.setText(f"Cena po noci (eur): {apt.price_per_night}")
            self.resLayout.info9.setText(f"Status: {apt.status}")


        except ValueError:
            print("value error")
            msg = color_msg("Pogresan unos", "Tomato")
            self.reviewWarning.setText(msg)

    # TODO updateReservations
    def updateReservations(self):
        pass

    def _reservationForm(self):
        self.resLayout.showForm(int(self.currentApt.spots) - 1)
        self.resLayout.label2.setText(f"Sifra apartmana: {self.currentApt.apt_id}")
        self.resLayout.reservationDuration.clear()
        self.resLayout.label14.setText("Ukupna cena: ")

    def _bookApt(self):
        # df = convert.to_df("data/reservations.csv")
        # n = df.iloc[-1, 0]["Sifra rezervacije"]

        # self.resLayout.label2.setText(f"Sifra apartmana: {self.requestApt.text()}")
        s = self.resLayout.reservationStart.text()

        dur = self.resLayout.reservationDuration.text()
        guests = [
            self.resLayout.reservationGuest1.text(),
            self.resLayout.reservationGuest2.text(),
            self.resLayout.reservationGuest3.text(),
            self.resLayout.reservationGuest4.text(),
            self.resLayout.reservationGuest5.text(),
            self.resLayout.reservationGuest6.text(),
            self.resLayout.reservationGuest7.text(),
            self.resLayout.reservationGuest8.text()
        ]
        guests = [i for i in guests if i != ""]

        try:
            dur = int(dur)
        except ValueError:
            err = color_msg("Pogresan broj nocenja.", "Tomato")
            self.reviewWarning.setText(err)
            self._reservationForm()
            return

        apt_id = self.requestApt.text()
        uname = self.resLayout.reservationUser.username

        # TODO email validation

        try:
            df = self.baseDF.copy()
            apt = df[df["Sifra"] == apt_id].squeeze()

            tf = TimeFrame(s, dur)
            tf.date_check()

            date = str(datetime.date.today())
            if compare(s, "<", date):
                print("tried to reserve a date in the past")

                err = color_msg("Ne mozete napraviti rezervaciju koja pocinje u proslosti!", "Tomato")

                self.reviewWarning.setText(err)
                self._reservationForm()
                return

            if self.currentUser.role == "Neregistrovan":
                print("not logged in")
                err = color_msg("Morate se prijaviti!", "Tomato")

                self.reviewWarning.setText(err)
                self._reservationForm()
                return

            if apt["Status"] == "neaktivan":
                print("inactive apt")
                err = color_msg("Ovaj apartman trenutno nije aktivan!", "Tomato")

                self.reviewWarning.setText(err)
                self._reservationForm()
                return

            foo = check_availability(s, tf.end, apt_id, normal_mode=False)
            if foo is not True:
                cs = foo[0]
                ce = foo[1]
                err = color_msg(f"Apartman je zauzet od {cs} do {ce}!", "Tomato")

                self.reviewWarning.setText(err)
                self._reservationForm()
                return

            reservation = Reservation(start=s, duration=dur, apartment_id=apt_id, username=uname, guests=guests)

            reservation.reserve()
            res_id = reservation.res_id
            succ = color_msg(f"Uspesno ste rezervisali apartman, sifra ove rezervacije je: {res_id}", "Lime")
            self.reviewMessage.setText(succ)

        except InvalidDateError:
            print("invalid date")
            err = color_msg("Nepravilan datum.", "Tomato")

            self.reviewWarning.setText(err)
            self._reservationForm()
            return

        # TODO USPESNO STE REZERVISALI BRALE

    def _createBrowsingScreen(self):
        tableLayout = QHBoxLayout()
        reviewLayout = QVBoxLayout()
        self.resLayout = ReservationLayout(self.currentUser)

        self._clearScreen()
        self._createTopRow()

        df = self.currentDF

        self.model = tableModel(df)
        self.table = QTableView()
        self.table.setModel(self.model)

        # set the top row to fit the data
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(df.shape[1] - 1, QHeaderView.Stretch)
        for i in range(df.shape[1] - 1):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        tableLayout.addWidget(self.table, 5)

        self.reviewWarning = QLabel("")
        self.reviewMessage = QLabel("")
        self.requestApt = QLineEdit()
        self.goNext = QPushButton("Dalje")
        self.goNext.hide()

        self.bookBtn = QPushButton("Rezervisi ovaj apartman")
        self.bookBtn.clicked.connect(self._bookApt)

        self.goNext.clicked.connect(self._reservationForm)

        showApt = QPushButton("Prikazi apartman")
        showApt.clicked.connect(self._createReview)

        reviewLayout.addWidget(self.reviewWarning)
        reviewLayout.addWidget(
            QLabel("Unesite sifru apartmana koji bi detaljnije da pregledate i/ili da rezervisete.")
        )

        # requestApt is the input field
        reviewLayout.addWidget(self.requestApt)
        reviewLayout.addWidget(showApt)

        reviewLayout.addWidget(self.reviewMessage)
        reviewLayout.addWidget(self.goNext)

        reviewLayout.addLayout(self.resLayout, 1)
        reviewLayout.addWidget(self.bookBtn)
        tableLayout.addLayout(reviewLayout, 4)
        self.generalLayout.addLayout(tableLayout)

    def logOut(self):
        if self.currentUser.role == "Neregistrovan":
            self.setCentralWidget(QLabel(color_msg("Niste prijavljeni", "OrangeRed", 1)))
            return

        self.currentUser.log_out()
        self._clearScreen()
        self.setCentralWidget(QLabel(color_msg("Odjavili ste se", "OrangeRed", 1)))
        return


# So, I need to make a custom table model (whatever that is?)

# so, every item has a "role",
# e.g. items with the DisplayRole role are to be displayed as text
#  https://doc.qt.io/archives/qt-4.8/qt.html#ItemDataRole-enum 
#

# pycharm complains that I'm overriding methods,
# but according to the internet this is what I'm supposed to do
class tableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(tableModel, self).__init__()
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                # iloc is a pandas method for locating values
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == QtCore.Qt.Vertical:
                return str(self._data.index[section])


# returns a html heading of the desired color and size
def color_msg(msg, color, size=3):
    colored_msg = f'<h{size} style="background-color:{color};">{msg}</h{size}>'

    return colored_msg


def main():
    app = QApplication([])

    view = ProjekatWindow()
    view.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

# the option is called stretch
# you can change the ratios by passing a number in .addWidget or .addLayout
# e.g. .addWidget(widget_one, 1) .addWidget(widget_two, 9)
#   this will make widget_two take up 9 times as much space as widget_one

# self.widget0.hide()
# self.widget1.hide()
# self.widget2.hide()
# self.widget3.hide()
# self.widget4.hide()
# self.widget5.hide()
# self.widget6.hide()
# self.widget7.hide()
# self.widget8.hide()
# self.widget9.hide()

# self.resLayout.hideInfo()
# form = QFormLayout()

# form.addRow("Ayo", QLineEdit())

# self.reservation = Reservation(n, s, d, apt_id, uname, guests)

# self.infoLayout.setParent(None)
# self.infoLayout = QVBoxLayout()
# for i in reversed(range(self.infoLayout.count())):
#     self.infoLayout.itemAt(i).widget().setParent(None)
# self.infoLayout.addWidget(QPushButton())
# self.infoLayout.addLayout(form)
# self.form = QFormLayout()
# self.form.addRow("Ayo: ", QPushButton("jodjifoisjdoifjsoidjfosd"))
# self.form.addRow("Ayo: ", QPushButton("jodjifoisjdoifjsoidjfosd"))
# self.form.addRow("Ayo: ", QPushButton("jodjifoisjdoifjsoidjfosd"))
# self.form.addRow("Ayo: ", QPushButton("jodjifoisjdoifjsoidjfosd"))
# self.form.addRow("Ayo: ", QPushButton("jodjifoisjdoifjsoidjfosd"))
# self.infoLayout.addLayout(self.form)
# self.form.hide()
# self.form.setItem(0, PyQt5.QtWidgets.QFormLayout.ItemRole, "BINGONG")
