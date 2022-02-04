import PyQt5.QtWidgets
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
        return df[df[x] == qr]

    except ValueError:
        print("not int... doing comparison filter")

    try:
        qr = qr.replace(" ", "")
        for ch in qr:
            if ch not in "<>0123456789x":
                print("invalid input, illegal char")
                return df

        i = qr.index("x")

        if qr[i-1:i] == qr[i+1:i+2]:
            qr1 = qr[i:]
            qr1 = qr1.replace("x", f'df["{x}"]')
            qr1 = f"df[{qr1}]"

            df = eval(qr1)

            qr2 = qr[:i+1]
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

    except TypeError:
        print("type error")
        print("invalid input")


class User:
    def __init__(self, username="Neregistrovan Korisnik", role="Neregistrovan"):
        self.username = username
        self.role = role

    def log_out(self):
        self.username = "Neregistrovan Korisnik"
        self.role = "Neregistrovan"


class Apartment:
    def __init__(self, aprt_code: int, aprt_type: str, rooms_n: int, guests_n, location: tuple,
                 availability: list, host: object, cost: int, status: bool, amenities: list):
        self.aprt_code = aprt_code
        self.aprt_type = aprt_type
        self.rooms_n = rooms_n
        self.guests_n = guests_n
        self.location = location
        self.availability = availability
        self.host = host
        self.cost = cost
        self.status = status
        self.amenities = amenities


class Amenitiy:
    def __init__(self, amnt_code, name):
        self.amnt_code = amnt_code
        self.name = name


class Reservation:  # apartment
    def __init__(self, aprt_code: int, start_date: str, duration_of_stay: int,
                 total_cost: int, guest: object, status: str):
        self.aprt_code = aprt_code
        self.start_date = start_date
        self.duration_of_stay = duration_of_stay
        self.total_cost = total_cost
        self.guest = guest
        self.status = status

    def cancel(self):
        self.status = False


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
        self.currentDF = convert.to_df("data/apartment_data.csv", use_cols=[0, 1, 2, 3, 5, 6, 8])

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

        userMenu.addAction('Prijavi se', self._createLoginScreen)
        userMenu.addAction('Registruj se', self._createRegisterScreen)
        userMenu.addAction('Odjavi se', self.logOut)

        apartmentMenu.addAction(
            'Pretraga apartmana', self._createTable
        )
        apartmentMenu.addAction('Pregled i rezervacija apartmana', self._createTable)
        # apartmentMenu.addAction('Rezervacija', self.apartmentReservation)
        #
        # if self.currentUser.role == "Domacin":
        #     apartmentMenu.addAction('Registracija', self.apartmentRegistration)

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

            self.currentUser.username = username
            self.currentUser.role = role

            print("login successful")

            # success = f'<h3 style="background-color:Lime;">Dobrodosao/la {username}</h3>'
            succ = color_msg(f"Dobrodosao/la {username}", "Lime")

            self._formMessage(msg=succ)
            self._createMenu()
            return

        print("login failed")
        # TODO ayo
        # err = '<h3 style="background-color:Tomato;">Pogresno korisnicko ime ili lozinka.</h3>'
        err = color_msg("Pogresno korisnicko ime ili lozinka.", "Tomato")

        self._formMessage(msg=err)
        return

    def _formMessage(self, msg):
        self.formMsg.hide()
        self.formMsg.setText(msg)
        self.formMsg.show()

    def _submitSearch(self, mode="search", aprt_id=0):
        # if mode == "review":
        #     df = pd.read_csv("data/apartment_data.csv").iloc[[aprt_id]]
        #     amenity_df = pd.read_csv("data/amenities.csv").iloc[[aprt_id]]
        # elif mode == "search":
        df_base = convert.to_df("data/apartment_data.csv")
        df = df_base.loc[:, ["Sifra", "Tip", "Broj soba", "Broj gostiju",
                         "Adresa", "Dostupnost", "Cena po noci (eur)"]]

        # TODO 10 most pop na osnovu broja izdatih apartmana u tom gradu
        # u poslednjih godinu dana

        # TODO case insensitive search
        # current is sensitive
        df = df[df["Adresa"].str.contains(self.searchLocation.text())]

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
            df = df_base[df_base["Status"] == "aktivan"]
            df = df.loc[:, ["Sifra", "Tip", "Broj soba", "Broj gostiju",
                            "Adresa", "Dostupnost", "Cena po noci (eur)"]]
            # [:, [cols]]
            # : -> all rows
            # [cols] -> only "cols" columns

        self.currentDF = df
        self._createTable()

        # TODO be able to explain why df[df[]] works

    def _createReview(self):
        reviewLayout = QVBoxLayout

        self._clearScreen()

        self.generalLayout.addLayout(reviewLayout)

    def _createTopRow(self):
        topLayout = QGridLayout()
        textLayout = QGridLayout()

        self.searchLocation = QLineEdit()
        self.searchAvailability = QLineEdit()
        self.searchRooms = QLineEdit()
        self.searchPersons = QLineEdit()
        self.searchPrice = QLineEdit()
        self.popularCities = QCheckBox()
        self.showActive = QCheckBox()
        # TODO show active

        # TODO fix shishana latinica
        self.searchButton = QPushButton("Pretrazi")
        self.searchButton.clicked.connect(
            partial(self._submitSearch, mode="search", aprt_id=20)
        )

        topLayout.addWidget(QLabel(f"<h4>Vi ste: {self.currentUser.username}</h4>"), 0, 0)
        topLayout.addWidget(QLabel(f"<h4>Uloga: {self.currentUser.role}</h4>"), 1, 0)

        # (widget, y, x)
        topLayout.addWidget(QLabel("Mesto"), 0, 1)
        topLayout.addWidget(self.searchLocation, 0, 2, 1, 7)
        topLayout.addWidget(QLabel("Dostupnost"), 1, 1)
        topLayout.addWidget(self.searchAvailability, 1, 2)
        topLayout.addWidget(QLabel("Broj soba"), 1, 3)
        topLayout.addWidget(self.searchRooms, 1, 4)
        topLayout.addWidget(QLabel("Broj osoba"), 1, 5)
        topLayout.addWidget(self.searchPersons, 1, 6)
        topLayout.addWidget(QLabel("Cena po noci"), 1, 7)
        topLayout.addWidget(self.searchPrice, 1, 8)
        topLayout.addWidget(self.searchButton, 0, 9, 2, 1)
        topLayout.addWidget(QLabel("Prikazi 10 najpopularnijih gradova"), 2, 1)
        topLayout.addWidget(self.popularCities, 2, 2)
        topLayout.addWidget(QLabel("Prikazi samo aktivne apartmane"), 3, 1)
        topLayout.addWidget(self.showActive, 3, 2)
        # topLayout.addWidget(PyQt5.QtWidgets.QCheckBox, 2, 1)
        textLayout.addWidget(QLabel("Primeri koriscenja pretrage:"))
        textLayout.addWidget(QLabel("Vrednost manja od: x < 3 je isto sto i 3 > x, isto vazi i za vece."))
        textLayout.addWidget(QLabel("Vrednost izmedju: 2 < x < 5, ili samo unesite tacnu vrednost koju trazite."))

        topLayout.addLayout(textLayout, 3, 3, 1, 6)
        self.generalLayout.addLayout(topLayout, 1)

    def _createRegisterScreen(self):
        registerLayout = QVBoxLayout()
        formLayout = QFormLayout()

        self._clearScreen()

        self.registerScreen = QWidget(self._centralWidget)

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

        self.loginScreen = QWidget(self._centralWidget)

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

    # TODO I could literally return the relevant details in each method

    def apartmentReview(self):
        tableLayout = QVBoxLayout()

    def _createTable(self):
        tableLayout = QHBoxLayout()

        self._clearScreen()
        self._createTopRow()

        df = self.currentDF

        self.model = tableModel(df)
        self.table = QTableView()
        self.table.setModel(self.model)

        # TODO .clearScreen might be redundant
        # TODO instance attribute defined outside __init__

        # set the top row to fit the data
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(df.shape[1] - 1, QHeaderView.Stretch)
        for i in range(df.shape[1] - 1):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        tableLayout.addWidget(self.table, 2)
        tableLayout.addWidget(QPushButton("AYO"), 1)
        # tableLayout.addWidget(self.table2)

        self.generalLayout.addLayout(tableLayout)
        # so apparently _clearScreen is redundant
        # self.setCentralWidget(self.table)

    def logOut(self):
        # self._createLoginScreen()

        if self.currentUser.role == "Neregistrovan":
            self.setCentralWidget(QLabel(color_msg("Niste prijavljeni", "OrangeRed", 1)))
            return

        self.currentUser.log_out()
        self._clearScreen()
        self.setCentralWidget(QLabel(color_msg("Odjavili ste se", "OrangeRed", 1)))
        return

# TODO explicit return or just let be

# Sooo, I need to make a custom table model (whatever that is?)

# OK that was a little too easy

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


# you can change the ratios by passing a number in .addWidget or .addLayout
# e.g. .addWidget(widget_one, 1) .addWidget(widget_two, 9)
#   this will make widget_two take up 9 times as much space as widget_one
