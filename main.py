from collections import Counter
from functools import partial
import datetime
import random
import sys
import re

from PyQt5.QtCore import QAbstractTableModel
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QFormLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QTableView
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QMenuBar
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt
import pandas as pd

from classes_and_stuff import update_reservations
from classes_and_stuff import check_availability
from classes_and_stuff import InvalidSearchError
from classes_and_stuff import ReservationLayout
from classes_and_stuff import InvalidDateError
from classes_and_stuff import Reservation
from classes_and_stuff import TimeFrame
from classes_and_stuff import Apartment
from classes_and_stuff import compare
from classes_and_stuff import User
import registration
import convert
import invert
import login


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

            # this seems like it's not important but it is
            df = eval(qr1)

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


class ProjekatWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Airbnb (not)")

        # fixed size forces bspwm to make the window floating
        # but it's still resizable (???)
        # TODO should I keep it fixed?
        self.setFixedSize(1280, 720)

        # TODO TESTING
        self.currentUser = User(username="Otibitepar")

        self.baseDF = convert.to_df("data/apartment_data.csv")
        self.currentDF = self.baseDF.copy().loc[:, ["Sifra", "Tip", "Broj soba", "Broj gostiju",
                                                    "Adresa", "Cena po noci (eur)"]]

        update_reservations()

        self._clearScreen()
        self._createMenu()

        welcome = QVBoxLayout()
        welcome.addWidget(QLabel("<h1>Airbnb (not)</h1>\n<h2>Za navigaciju koristite meni na vrhu prozora.</h2>"))
        self.generalLayout.addLayout(welcome)

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

        apartmentMenu.addAction('Pretraga i rezervacija apartmana', self._createBrowsingScreen)

        if self.currentUser.role != "Neregistrovan":
            resMenu = menu.addMenu("&Rezervacije")
            resMenu.addAction('Vase rezervacije', self._createResReviewScreen)

            if self.currentUser.role == "Domacin":
                apartmentMenu.addAction('Vasi apartmani', self._createAptEdit)
                resMenu.addAction('Rezervacije Vasih apartmana', self._createHostRes)

            if self.currentUser.role == "Admin":
                adminMenu = menu.addMenu("&Admin")
                adminMenu.addAction("Pretraga rezervacija", self._resSearch)
                adminMenu.addAction("Registracija novih domacina", self._hostReg)
                adminMenu.addAction("Kreiranje i brisanje dodatne opreme", self._editAmnt)
                adminMenu.addAction("Blokiranje korisnika", self._blockUsr)
                adminMenu.addAction("Izvestavanje", self._reviewData)

    def _submitResSearch(self, btn, txt, df):
        # TODO exclude special reservations!
        #   2/4 buttons work properly
        #   maybe just add the relevant data as columns...
        if btn == "accp":
            df = df[df["Status"] == "Prihvacena"]

        elif btn == "deny":
            df = df[df["Status"] == "Odbijena"]

        elif btn == "addr":
            df = df[df["Adresa"].str.contains(txt)]

        elif btn == "uname":
            adf = convert.to_df("data/apartment_data.csv")
            udf = convert.to_df("data/user_data.csv")
            rdf = convert.to_df("data/reservations.csv")

            if udf.empty:
                # TODO ERROR
                print("")

            host = udf[udf["Korisnicko ime"] == txt].squeeze()
            host = " ".join([host["Ime"], host["Prezime"]])

            adf = adf[adf["Domacin"] == host]
            ids = list(adf.loc["Sifra"].squeeze())
            lst = []
            for i in range(rdf.shape[0]):
                aptid = rdf.at[i, "Sifra apartmana"]
                if aptid in ids:
                    lst.append(list(rdf.iloc[i].squeeze()))
            header = convert.headers("data/reservations")
            df = pd.DataFrame(lst, columns=header)

        self._resSearch(df=df)

    def _resSearch(self, df=convert.to_df("data/reservations.csv")):
        layout = QGridLayout()

        self._clearScreen()

        self.model = tableModel(df)
        self.table = QTableView()
        self.table.setModel(self.model)

        # set the top row to fit the data
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(df.shape[1] - 1, QHeaderView.Stretch)
        for i in range(df.shape[1] - 1):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)


        # self.resInput.setPlaceholderText()
        resInput = QLineEdit()
        accp = QPushButton("Prikazi prihvacene")
        deny = QPushButton("Prikazi odbijene")
        addr = QPushButton("Pretrazi po adresi")
        uname = QPushButton("Pretrazi po korisnickom imenu")

        accp.clicked.connect(partial(self._submitResSearch, "accp", accp.text(), df))
        deny.clicked.connect(partial(self._submitResSearch, "deny", deny.text(), df))
        addr.clicked.connect(partial(self._submitResSearch, "addr", addr.text(), df))
        uname.clicked.connect(partial(self._submitResSearch, "uname", uname.text(), df))

        layout.addWidget(QLabel("<h2>Pretrazujte rezervacije po statusu, adresi ili korisnickom imenu domacina</h2>"), 0, 0, 1, 4)
        layout.addWidget(resInput, 1, 0, 1, 4)
        layout.addWidget(accp, 2, 0)
        layout.addWidget(deny, 2, 1)
        layout.addWidget(addr, 2, 2)
        layout.addWidget(uname, 2, 3)

        layout.addWidget(self.table, 3, 0, 1, 4)
        self.generalLayout.addLayout(layout)
        pass

    def _hostReg(self):
        pass

    def _editAmnt(self):
        pass

    def _blockUsr(self):
        pass

    def _reviewData(self):
        pass

    def _createHostRes(self):
        layout = QGridLayout()
        self._clearScreen()

        host = " ".join([self.currentUser.fname, self.currentUser.lname])

        dfa = convert.to_df("data/apartment_data.csv")
        ids = dfa[dfa["Domacin"] == host]
        ids = ids.loc[:, "Sifra"]
        ids = ids.squeeze()
        ids = list(ids)

        dfr = convert.to_df("data/reservations.csv")

        header = convert.headers("data/reservations.csv")
        res_df = pd.DataFrame([], columns=header)

        for i in range(dfr.shape[0]):
            apt_id = dfr.iat[i, 1]
            if apt_id in ids:
                row = pd.DataFrame([list(dfr.iloc[i])], columns=header)
                # res_df = res_df.append(row, ignore_index=True)
                res_df = pd.concat([res_df, row], ignore_index=True)

        df = res_df[res_df["Status"] == "Kreirana"]

        self.model = tableModel(df)
        self.table = QTableView()
        self.table.setModel(self.model)

        header = self.table.horizontalHeader()
        for i in range(df.shape[1]):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(df.shape[1] - 1, QHeaderView.Stretch)

        self.editRes = QLineEdit()
        accept = QPushButton("Potvrdi")
        deny = QPushButton("Odbij")
        self.resLabel = QLabel("")

        if df.empty:
            sad = color_msg("Ne postoje rezervacije za Vase apartmane :(", "Purple")
            self.resLabel.setText(sad)

        accept.clicked.connect(self._acceptRes)
        deny.clicked.connect(self._denyRes)

        layout.addWidget(self.resLabel, 0, 0, 1, 2)
        layout.addWidget(QLabel("Unesite sifru rezervacije, pa je odbijte ili potvrdite"), 1, 0, 1, 2)
        layout.addWidget(self.editRes, 2, 0, 1, 2)
        layout.addWidget(accept, 3, 0)
        layout.addWidget(deny, 3, 1)
        layout.addWidget(self.table, 4, 0, 1, 2)

        self.generalLayout.addLayout(layout)

    def _acceptRes(self):
        resId = self.editRes.text()
        if not resId.isnumeric():
            err = color_msg("Pogresan unos!", "Tomato")

            self._createHostRes()
            self.resLabel.setText(err)
            return

        df = convert.to_df("data/reservations.csv")
        if df[df["Sifra rezervacije"] == str(resId)].empty:
            err = color_msg("Pogresna sifra/rezervacija ne postoji!", "Tomato")

            self._createHostRes()
            self.resLabel.setText(err)
            return

        for i in range(df.shape[0]):
            if df.at[i, "Sifra rezervacije"] == str(resId):
                df.at[i, "Status"] = "Prihvacena"
                break

        convert.to_csv(df, "data/reservations.csv")
        self._createHostRes()

        succ = color_msg(f"Uspesno ste prihvatili rezervaciju {resId}!", "Lime")
        self.resLabel.setText(succ)

    def _denyRes(self):
        resId = self.editRes.text()
        if not resId.isnumeric():
            err = color_msg("Pogresan unos!", "Tomato")

            self._createHostRes()
            self.resLabel.setText(err)
            return

        df = convert.to_df("data/reservations.csv")
        if df[df["Sifra rezervacije"] == str(resId)].empty:
            err = color_msg("Pogresna sifra/rezervacija ne postoji!", "Tomato")

            self._createHostRes()
            self.resLabel.setText(err)
            return

        for i in range(df.shape[0]):
            if df.at[i, "Sifra rezervacije"] == str(resId):
                df.at[i, "Status"] = "Odbijena"
                break

        convert.to_csv(df, "data/reservations.csv")
        self._createHostRes()

        succ = color_msg(f"Uspesno ste odbili rezervaciju {resId}!", "Lime")
        self.resLabel.setText(succ)

    def _checkEdit(self, a=0):
        try:
            int(self.editRooms.text())
            int(self.editGuests.text())
            int(self.editPrice.text())

        except ValueError:
            err = color_msg("Broj soba, broj gostiju, sifra apartmana, i cena moraju biti brojevi!", "Tomato")

            self.editLabel.setText(err)
            return True

        if not (
            self.editRooms.text() and
            self.editGuests.text() and
            self.editPrice.text() and
            self.editAmnt.text()
        ):

            if a == 0:
                self.editAddr.text()

            err = color_msg("Popunite sva polja!", "Tomato")

            self.editLabel.setText(err)
            return True

        if len(self.editAmnt.text().split()) > 5:
            err = color_msg("Sadrzaj apartmana razdvajate zarezima, najvise 5 dodataka.", "Tomato")

            self.editLabel.setText(err)
            return True

        if a == 1 or a == 2:
            df = convert.to_df("data/apartment_data.csv", use_cols=[0, 5, 7])
            df = df[df["Domacin"] == " ".join([self.currentUser.fname, self.currentUser.lname])]
            if not df.empty:
                for i in range(df.shape[0]):
                    if a == 1 and df[df["Sifra"] == self.editId.text()].empty:
                        err = color_msg("Pogresna sifra/apartman ne postoji!", "Tomato")
                        self.editLabel.setText(err)
                        return True

                    if a == 2 and df[df["Sifra"] == self.rmId.text()].empty:
                        err = color_msg("Pogresna sifra/apartman ne postoji!", "Tomato")
                        self.editLabel.setText(err)
                        return True

                    if a == 0 and df.iat[i, 1] == self.editAddr.text():
                        err = color_msg("Taj apartman je vec registrovan!", "Tomato")
                        self.editLabel.setText(err)
                        return True
            else:
                err = color_msg("Nemate apartmane!", "Tomato")
                self.editLabel.setText(err)
                return True

    def _addApt(self):
        if self._checkEdit(a=0):
            return

        apt = Apartment(self.aptId, save=True)
        apt.type = "Soba" if self.editRooms.text() == "1" else "Ceo"
        apt.rooms = self.editRooms.text()
        apt.spots = self.editGuests.text()
        apt.address = self.editAddr.text()

        if "," in apt.address:
            err = color_msg("Ne mozete koristiti zarez u adresi, koristite '|' ili samo razmak", "Tomato")

            self._createAptEdit()
            self.editLabel.setText(err)
            return

        # apt.avlb = self.editAvlb.text()
        invert.finish(self.aptId, self.dates)

        apt.host = " ".join([self.currentUser.fname, self.currentUser.lname])
        apt.price_per_night = self.editPrice.text()

        amnts = self.editAmnt.text().split(",")
        amnts = [i.strip() for i in amnts]

        # check if every element of amnts is a number
        if eval(" and ".join([str(i) for i in [i.isnumeric() for i in amnts]])):
            with open("data/sadrzaj.txt", "r") as f:
                dct = {i: j[:-1] for i, j in [k.split(":") for k in f.readlines()]}

            for i in range(len(amnts)):
                amnts[i] = dct[amnts[i]]

        # check if mixed
        elif eval(" or ".join([str(i) for i in [i.isnumeric() for i in amnts]])):
            err = color_msg("Pogresan unos!", "Tomato")

            self._createAptEdit()
            self.editLabel.setText(err)
            return

        # lst = [i.strip() for i in self.editAmnt.text().split(",")]

        apt.amenities = amnts + ["None" for _ in range(5)][len(amnts):]

        apt.append()

        succ = color_msg("Uspesno ste registrovali apartman!", "Lime")

        self._createAptEdit()
        self.editLabel.setText(succ)

    def _rmApt(self):
        if not self.rmId.text().isnumeric():
            err = color_msg("Sifra mora biti broj!", "Tomato")

            self.editLabel.setText(err)
            return

        dfa = convert.to_df("data/apartment_data.csv")
        dfr = convert.to_df("data/reservations.csv")
        dfm = convert.to_df("data/amenities.csv")

        for i in range(dfa.shape[0]):
            if dfa.iat[i, 0] == self.rmId.text():
                dfa = dfa.drop(i)
                break

        for i in range(dfm.shape[0]):
            if dfm.iat[i, 0] == self.rmId.text():
                dfm = dfm.drop(i)
                break

        i = 0
        while i < dfr.shape[0]:
            if dfr.iat[i, 1] == self.rmId.text():
                dfr = dfr.drop(i)

            i += 1

        convert.to_csv(dfa, "data/apartment_data.csv")
        convert.to_csv(dfr, "data/reservations.csv")
        convert.to_csv(dfm, "data/amenities.csv")

        self._createAptEdit()

        msg = color_msg(f"Obrisali ste apartman {self.rmId}", "Tomato")
        self.editLabel.setText(msg)

    def _addTF(self):
        s = self.editAvlb.text()
        try:
            self.dates = invert.add(s, self.dates)
            self.editAvlb.clear()

            succ = color_msg("Datumi zabelezeni!", "Lime")

            # self._createAptEdit()
            self.editLabel.setText(succ)

        except InvalidDateError:
            err = color_msg("Pogresan datum!", "Tomato")

            self._createAptEdit()
            self.editLabel.setText(err)
            return

    def _actApt(self):
        try:
            int(self.actId.text())
        except ValueError:
            err = color_msg("Pogresna sifra!", "Tomato")

            self._createAptEdit()
            self.editLabel.setText(err)
            return

        df = self.apt_df.copy()

        df = df[df["Sifra"] == self.actId.text()]
        if df.empty:
            err = color_msg("Pogresna sifra/apartman ne postoji!", "Tomato")

            self._createAptEdit()
            self.editLabel.setText(err)
            return

        df = df[df["Status"] == "neaktivan"]
        if df.empty:
            err = color_msg("Apartman je vec aktivan!", "Tomato")

            self._createAptEdit()
            self.editLabel.setText(err)
            return

        df = convert.to_df("data/apartment_data.csv")
        for i in range(df.shape[0]):
            if df.iat[i, 0] == self.actId.text():
                df.at[i, "Status"] = "aktivan"
                break

        convert.to_csv(df, "data/apartment_data.csv")
        self._createAptEdit()

        err = color_msg("Uspesno ste aktivirali apartman!", "Lime")

        self._createAptEdit()
        self.editLabel.setText(err)
        return

    def _editApt(self):
        if self._checkEdit(a=1):
            return

        if not self.editId.text().isnumeric():
            err = color_msg("Sifra mora biti broj!", "Tomato")

            self.editLabel.setText(err)
            return

        apt = Apartment(self.aptId, save=True)
        apt.type = "Soba" if self.editRooms.text() == "1" else "Ceo"
        apt.rooms = self.editRooms.text()
        apt.spots = self.editGuests.text()

        apt.address = self.showAddr.text()[8:]

        apt.host = " ".join([self.currentUser.fname, self.currentUser.lname])
        apt.price_per_night = self.editPrice.text()

        amnts = self.editAmnt.text().split(",")
        amnts = [i.strip() for i in amnts]

        # check if every element of amnts is a number
        if eval(" and ".join([str(i) for i in [i.isnumeric() for i in amnts]])):
            with open("data/sadrzaj.txt", "r") as f:
                dct = {i: j[:-1] for i, j in [k.split(":") for k in f.readlines()]}

            for i in range(len(amnts)):
                amnts[i] = dct[amnts[i]]

        # check if mixed
        elif eval(" or ".join([str(i) for i in [i.isnumeric() for i in amnts]])):
            err = color_msg("Pogresan unos!", "Tomato")

            self._createAptEdit()
            self.editLabel.setText(err)
            return

        apt.amenities = [self.aptId] + amnts + ["None" for _ in range(5)][len(amnts):]

        apt.save_changes()

        succ = color_msg(f"Uspesno ste promenili podatke apartmana {self.aptId}!", "Lime")

        self._createAptEdit()
        self.editLabel.setText(succ)

    def _idChanged(self, n):
        df = convert.to_df("data/apartment_data.csv", use_cols=[0, 5, 7])

        self.editAddr.hide()
        self.showAddr.show()

        if n:
            self.aptId = self.editId.text()

        else:
            self.aptId = self.rmId.text()

        self.idLabel.setText(f"Sifra apartmana: {self.aptId}")
        df = df[df["Sifra"] == self.aptId]
        df = df[df["Domacin"] == " ".join([self.currentUser.fname, self.currentUser.lname])]
        if df.empty:
            self.editLabel.setText(color_msg("To nije Vas apartman!", "Tomato"))
            addr = ""
            self.editAddr.show()
            return
        else:
            self.editLabel.setText("")
            addr = df.squeeze()["Adresa"]

        self.showAddr.setText(f"Adresa: {addr}")

    def _createAptEdit(self):
        aptEditLayout = QVBoxLayout()
        formLayout = QFormLayout()

        self._clearScreen()

        df = convert.to_df("data/apartment_data.csv")
        name = " ".join([self.currentUser.fname, self.currentUser.lname])
        apt_df = df[df["Domacin"] == name]
        apt_df = apt_df.iloc[:, [0,1,2,3,5,8,9,10]]

        apt_df = apt_df.rename(columns={"Ameniti": "Sadrzaj"})
        self.apt_df = apt_df.copy()
        amt_df = convert.to_df("data/amenities.csv")

        for i in range(apt_df.shape[0]):
            if apt_df.iat[i, 7] == "da":
                amt = dict(amt_df[amt_df["Sifra apartmana"] == apt_df.iat[i, 0]].squeeze())
                del amt["Sifra apartmana"]
                amt = list(amt.values())
                try:
                    amt = [i for i in amt if i != "None"]
                except ValueError:
                    print("multiple ids in amenities.csv probably")
                    return

                amt = ", ".join(amt)
                apt_df.iat[i, 7] = amt

        self.model = tableModel(apt_df)
        self.table = QTableView()
        self.table.setModel(self.model)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(apt_df.shape[1] - 1, QHeaderView.Stretch)

        self.editLabel = QLabel("")

        self.aptId = int(df.iat[-1, 0]) + 1
        self.editRooms = QLineEdit()
        self.editGuests = QLineEdit()
        self.editAddr = QLineEdit()
        self.showAddr = QLabel("Adresa: ")
        self.showAddr.hide()
        self.editAddr.setPlaceholderText("Ulica i broj, Naseljeno mesto, Postanski broj mesta (npr. Sutjeska 3, Novi Sad 21000)")

        self.editAvlb = QLineEdit()
        self.addTF = QPushButton("dodaj")
        self.addTF.clicked.connect(self._addTF)
        self.dates = []

        self.editPrice = QLineEdit()
        self.editAmnt = QLineEdit()
        self.editAmnt.setPlaceholderText("Dodatnu opremu mozete uneti po nazivu, razdvojenu zarezima, ili preko 'sifre' opreme (npr. 1,3,5), morate jedno ili drugo ne mozete kombinovati!")

        dodaj = QPushButton("Dodaj apartman")
        promeni = QPushButton("Promeni podatke")
        obrisi = QPushButton("Obrisi apartman")
        activate = QPushButton("Aktiviraj apartman")

        self.editId = QLineEdit()
        self.editId.setPlaceholderText("Ovde upisite sifru apartmana koji bi da menjate")

        self.idLabel = QLabel(f"Sifra apartmana: {self.aptId}")

        self.rmId = QLineEdit()
        self.rmId.setPlaceholderText("Ovde upisite sifru apartmana koji bi da obrisete")

        self.actId = QLineEdit()
        self.actId.setPlaceholderText("Ovde upisite sifru apartmana koji bi da aktivirate")

        self.editId.textChanged.connect(partial(self._idChanged, 1))
        self.rmId.textChanged.connect(partial(self._idChanged, 0))

        dodaj.clicked.connect(self._addApt)
        promeni.clicked.connect(self._editApt)
        obrisi.clicked.connect(self._rmApt)
        activate.clicked.connect(self._actApt)

        formLayout.addRow(dodaj)
        formLayout.addRow(obrisi, self.rmId)
        formLayout.addRow(promeni, self.editId)
        formLayout.addRow(activate, self.actId)

        formLayout.addRow(self.editLabel)

        f = self.currentUser.fname
        l = self.currentUser.lname
        nm = " ".join([f, l])

        formLayout.addRow(QLabel(f"Domacin: {nm} (Vi)"))
        formLayout.addRow(self.idLabel)
        formLayout.addRow(self.showAddr)
        formLayout.addRow("Broj soba: ", self.editRooms)
        formLayout.addRow("Broj gostiju: ", self.editGuests)
        formLayout.addRow("Adresa: ", self.editAddr)
        self.editAddr.show()

        formLayout.addRow(QLabel("Dostupnost: Unesite termine (pocetak i kraj) u formatu: 'pocetak, kraj' i pritisnete dugme dodaj, tako ponavljate dok ne unesete sve termine koje zelite"))
        formLayout.addRow(self.addTF, self.editAvlb)

        formLayout.addRow("Cena po noci: ", self.editPrice)
        formLayout.addRow("Sadrzaj: ", self.editAmnt)

        aptEditLayout.addWidget(self.table)
        aptEditLayout.addLayout(formLayout)

        self.generalLayout.addLayout(aptEditLayout)

    def _check(self):
        msg = color_msg("Da li sigurno zelite otkazati ovu rezervaciju?", "Tomato")

        try:
            int(self.cancelId.text())
        except ValueError:
            print("invalid res id")
            err = color_msg("Pogresan unos!", "Tomato")

            self.checkLabel.setText(err)
            return

        self.checkLabel.setText(msg)
        self.checkLabel.show()
        self.cancelRes.show()

    def _cancelReservation(self):
        df = convert.to_df("data/reservations.csv")

        cancelId = str(self.cancelId.text())
        resdf = df[df["Sifra rezervacije"] == cancelId]

        # ...
        usr = self.currentUser
        u, f, l = usr.username, usr.fname, usr.lname
        foo = f"{f} {l} ({u})"
        usrdf = df[df["Gost/Kontakt osoba"] == foo]

        if resdf.empty:
            err = color_msg("Ne postoji rezervacija sa tom sifrom na Vase ime!", "Tomato")

            # self._createResReviewScreen()
            self.checkLabel.setText(err)
            self.cancelRes.hide()
            return

        elif usrdf[usrdf["Status"] == "Kreirana"].empty and usrdf[usrdf["Status"] == "Prihvacena"].empty:
            err = color_msg("Nemate aktivne rezervacije!", "Tomato")

            self.checkLabel.setText(err)
            self.cancelRes.hide()
            return

        for i in range(df.shape[0]):
            sifra = df.iat[i, 0]
            status = df.iat[i, 7]

            if sifra == cancelId:
                if status == "Odustanak" or status == "Odbijena" or status == "Zavrsena":
                    err = color_msg("Ova rezervacija nije aktivna!", "Tomato")

                    self.checkLabel.setText(err)
                    self.cancelRes.hide()
                    return
                else:
                    df.iat[i, 7] = "Odustanak"

                    convert.to_csv(df, "data/reservations.csv")

                    self._createResReviewScreen()
                    self.checkLabel.show()
                    succ = color_msg(f"Otkazali ste rezervaciju {sifra}", "Tomato")
                    self.checkLabel.setText(succ)

    def _createResReviewScreen(self):
        resReviewLayout = QVBoxLayout()

        self._clearScreen()

        df = convert.to_df("data/reservations.csv", use_cols=range(8))
        df = df[df["Gost/Kontakt osoba"].str.contains(self.currentUser.username)]

        self.model = tableModel(df)
        self.table = QTableView()
        self.table.setModel(self.model)

        # set the top row to fit the data
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(df.shape[1] - 1, QHeaderView.Stretch)
        for i in range(df.shape[1] - 1):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        self.topLabel = QLabel("<h2>Vase rezervacije</h2>")
        self.cancelId = QLineEdit()
        self.makeSure = QPushButton("Otkazi")
        self.cancelRes = QPushButton("Da, zelim.")
        self.checkLabel = QLabel("")

        if df.empty:
            self.topLabel.setText("<h2>Nemate rezervacije.</h2>")

        self.makeSure.clicked.connect(self._check)
        self.cancelRes.clicked.connect(self._cancelReservation)

        resReviewLayout.addWidget(self.topLabel)
        resReviewLayout.addWidget(QLabel("Za otkazivanje, unesite sifru rezervacije koju bi da otkazete ispod."))
        resReviewLayout.addWidget(self.cancelId)
        resReviewLayout.addWidget(self.checkLabel)
        self.checkLabel.hide()

        resReviewLayout.addWidget(self.makeSure)
        resReviewLayout.addWidget(self.cancelRes)
        self.cancelRes.hide()

        resReviewLayout.addWidget(QLabel(""))
        resReviewLayout.addWidget(QLabel(""))

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

        regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        if not re.fullmatch(regex, self.registerEmail.text()):
            print("invalid email")
            err = color_msg("Nepravilan email", "Tomato")

            self._formMessage(msg=err)
            return

        for ch in self.registerPhone.text():
            if not ch.isnumeric():
                if ch not in ["-", " ", "+", "/"]:
                    print("invalid phone")
                    err = color_msg("Nepravilan broj", "Tomato")

                    self._formMessage(msg=err)
                    return

        unames = list(convert.to_df("data/user_data.csv", use_cols=[0]).squeeze())
        if self.registerUsername.text() in unames:
            print("user exists")
            err = color_msg("Korisnicko ime je zauzeto!", "Tomato")

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

        date = str(datetime.date.today()).split("-")
        date[0] = str(int(date[0]) - 1)
        date = "-".join(date)

        lst = []
        for i in range(df.shape[0]):
            row = list(df.iloc[i])
            if compare(row[0], ">", date):
                lst.append(row)

        df = pd.DataFrame(lst, columns=["Pocetak", "Status", "Grad"])

        a = df[df["Status"] == "Zavrsena"]
        b = df[df["Status"] == "Prihvacena"]

        df = pd.concat([a, b])

        df = df.loc[:, "Grad"]
        cities = Counter(list(df))

        rvrs_dct = {j: i for i, j in cities.items()}
        lst = list(rvrs_dct.items())
        lst = sorted(lst)
        pop_cities = reversed(lst[-10:])

        df = pd.DataFrame(pop_cities, columns=["Broj ostvarenih rezervacija", "Grad"])
        self.currentDF = df
        self._createBrowsingScreen()
        # self.currentDF = convert.to_df("data/apartment_data.csv")

    def _submitSearch(self):
        df = self.baseDF.copy()

        df = df[df["Adresa"].str.contains(self.searchLocation.text())]
        # case-sensitive
        # I honestly can't be bothered to make the search case-insensitive right now

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

        self.currentDF = df.loc[:, ["Sifra", "Tip", "Broj soba", "Broj gostiju", "Adresa", "Cena po noci (eur)"]]
        self._createBrowsingScreen()

        # I'm not sure how df[df[]] works

    def _createTopRow(self):
        topLayout = QGridLayout()

        self.searchLocation = QLineEdit()
        self.searchRooms = QLineEdit()
        self.searchPersons = QLineEdit()
        self.searchPrice = QLineEdit()
        self.popularCities = QPushButton("Prikazi 10 najpopularnijih gradova")
        self.showActive = QCheckBox()
        self.searchMsg = QLabel("")

        # TODO fix shishana latinica
        self.searchButton = QPushButton("Pretrazi")
        self.searchButton.clicked.connect(self._submitSearch)

        self.popularCities.clicked.connect(self._showPopularCities)

        topLayout.addWidget(QLabel(f"<h4>Vi ste: {self.currentUser.username}</h4>"), 0, 0)
        topLayout.addWidget(QLabel(f"<h4>Uloga: {self.currentUser.role}</h4>"), 1, 0)

        # (widget, y, x)
        topLayout.addWidget(self.searchMsg, 0, 1)
        topLayout.addWidget(QLabel("Mesto"), 0, 3)
        topLayout.addWidget(self.searchLocation, 0, 4, 1, 5)
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

        topLayout.addWidget(QLabel("Prikazi samo aktivne apartmane"), 1, 1)
        topLayout.addWidget(self.showActive, 1, 2)
        topLayout.addWidget(QLabel(f"Primeri koriscenja pretrage: \n"
                                   f"Vrednost manja od: x < 3 je isto sto i 3 > x, isto vazi i za vece.\n"
                                   f"Vrednost izmedju: 2 < x < 5, ili samo unesite tacnu vrednost koju trazite."), 3, 0, 1, 8)
        topLayout.addWidget(QLabel("Dostupnost se racuna/proverava kad izaberete apartman!"), 3, 4, 1, 5)

        self.generalLayout.addLayout(topLayout)

    def _createRegisterScreen(self):
        registerLayout = QVBoxLayout()
        formLayout = QFormLayout()

        self._clearScreen()

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
            self.resLayout.showInfo()
            self.resLayout.hideForm()
            int(self.requestApt.text())

            self.reviewWarning.setText("")

            try:
                apt = Apartment(self.requestApt.text(), compute_avlb=True)
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
            dct = apt.amenities
            if dct:
                del dct["Sifra apartmana"]

                sadrzaj = ", ".join([i for i in dct.values() if i != "None"])

                self.resLayout.info10.setText(f"Sadrzaj: \n{sadrzaj}")
            else:
                self.resLayout.info10.setText(f"Sadrzaj: Apartman nema dodatne opreme")

        except ValueError:
            print("value error")
            msg = color_msg("Pogresan unos", "Tomato")
            self.reviewWarning.setText(msg)

    def _reservationForm(self):
        self.resLayout.showForm(int(self.currentApt.spots) - 1)
        self.resLayout.label2.setText(f"Sifra apartmana: {self.currentApt.apt_id}")
        self.resLayout.reservationDuration.clear()
        self.resLayout.loadRes()
        self.resLayout.label14.setText("Ukupna cena: ")

    def _bookApt(self):
        s = self.resLayout.reservationStart.text()

        try:
            tf = TimeFrame(s)
        except ValueError:
            print("invalid date")
            err = color_msg("Nepravilan datum.", "Tomato")

            self.reviewWarning.setText(err)
            self._reservationForm()
            return

        except InvalidDateError:
            print("invalid date")
            err = color_msg("Nepravilan datum.", "Tomato")

            self.reviewWarning.setText(err)
            self._reservationForm()
            return

        dur = self.resLayout.reservationDuration.text()

        try:
            dur = int(dur)
            if not (0 < dur < 1000):
                print("bad dur")
                err = color_msg("Nedozvoljen broj nocenja", "Tomato")

                self.reviewWarning.setText(err)
                self._reservationForm()
                return

        except ValueError:
            print("invalid duration")
            err = color_msg("Nepravilan broj nocenja", "Tomato")

            self.reviewWarning.setText(err)
            self._reservationForm()
            return

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
class tableModel(QAbstractTableModel):
    def __init__(self, data):
        super(tableModel, self).__init__()
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                # iloc is a pandas method for locating values
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Vertical:
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

# assuming non reserved apartments are always available may have been the wrong move in this case
