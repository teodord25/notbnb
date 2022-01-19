import time


class User:
    def __init__(self,
                 uname: str, fname: str, lname: str, passwd: str,
                 sex: str, phone: int, email: str, role: str):
        self.uname = uname
        self.fname = fname
        self.lname = lname
        self.passwd = passwd    # prob irrelevant
        self.sex = sex          # prob also
        self.phone = phone
        self.email = email
        self.role = role

    def promote_to_admin(self):
        self.role = "Admin"

    def promote_to_host(self):
        self.role = "Host"


class Apartment:
    def __init__(self, aprt_code: int, aprt_type: str,
                 rooms_n: int, guests_n,  # perhaps
                 location: tuple, availability: list,
                 host: object, cost: int,
                 status: bool, amenities: list):
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


# POSSIBLY UNNECESSARY (I could just use a list of tuples
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

    # inherit from QMainWindow

    # i.e. inherit its properties


from PyQt5.QtCore import Qt
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

import sys
import time
from functools import partial
import registration
import login


### TO DO ###
# change the menu from _createScreen to _showScreen
# I think this way is bad


class projekatWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("projekat_airbnb")
        self.setFixedSize(800, 600) # maybe

        self._clearScreen()
        self._createMenu()

        self._createMainPage()


    def _clearScreen(self):
        # app layout
        self.generalLayout = QVBoxLayout()

        # QWidget(self) == self as parent
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)

    def _createMenu(self):
        self.menu = self.menuBar().addMenu("&Korisnik")
        # self.menu = self.menuBar().addMenu("&Register")
        self.menu.addAction('Prijavi se', self._createLoginScreen)
        self.menu.addAction('Registruj se', self._createRegisterScreen)
        self.menu.addAction('Odjavi se')
        self.menu = self.menuBar().addMenu("&Apartmani")


    def _submitRegistration(self):
        if not (self.registerUsername.text() and
                self.registerPassword.text() and
                self.confirmPassword.text() and
                self.registerPhone.text() and
                self.registerEmail.text() and
                self.registerFName.text() and
                self.registerLName.text()
                ):

            print("field left empty")
            err = '<h3 style="background-color:Tomato;">Morate popuniti sva polja.</h3>'

            self._formMessage(msg=err)
            return

        if len(self.registerPassword.text()) < 8:
            print("password too short")
            err = '<h3 style="background-color:Tomato;">Lozinka mora biti sadrzati najmanje 8 karaktera.</h3>'

            self._formMessage(msg=err)
            return

        if self.registerPassword.text() != self.confirmPassword.text():
            print("passwords do not match")
            err = '<h3 style="background-color:Tomato;">Lozinke se ne podudaraju.</h3>'

            self._formMessage(msg=err)
            return

        print("everything checks out, registering...")
        registration.register(
            self.registerUsername.text(), self.registerPassword.text()
        )

        print("saving user details...")
        registration.save_user_details([
            self.registerUsername.text(),
            self.registerPhone.text(),
            self.registerEmail.text(),
            self.registerFName.text(),
            self.registerLName.text(),
            self.genderCBox.currentText()
        ])

        print(f"registered user: \n\t{self.registerUsername.text()}")
        success = f'<h3 style="background-color:Lime;">Uspesno ste se registrovali {self.registerUsername.text()}</h3>'

        self._formMessage(msg=success)
        return

    def _attemptLogin(self):
        if not (self.loginUsername.text() and self.loginPassword.text()):
            print("one or both fields left empty")
            err = '<h3 style="background-color:Tomato;">Popunite polja.</h3>'

            self._formMessage(msg=err)
            return

        # log_in() returns a bool
        if login.log_in(self.loginUsername.text(), self.loginPassword.text()):
            print("login successful")

            time.sleep(1)

            success = f'<h3 style="background-color:Lime;">Dobrodosao/la {self.loginUsername.text()}</h3>'

            self._formMessage(msg=success)

        ################
            return

        print("login failed")
        err = '<h3 style="background-color:Tomato;">Pogresno korisnicko ime ili lozinka.</h3>'

        self._formMessage(msg=err)
        return

    def _formMessage(self, msg):
        self.formMsg.hide()
        self.formMsg.setText(msg)
        self.formMsg.show()

    def _createMainPage(self):
        apartmentLayout = QGridLayout

        self._clearScreen()

        self.generalLayout.addWidget(QLabel("mainpage"))



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
        formLayout.addRow("Kontakt telefon:", self.registerPhone)
        formLayout.addRow("Email adresa:", self.registerEmail)
        formLayout.addRow("Ime:", self.registerFName)
        formLayout.addRow("Prezime:", self.registerLName)

        self.genderCBox = QComboBox()
        self.genderCBox.addItems(["Musko", "Zensko", "Ostalo"])
        formLayout.addRow("Pol:", self.genderCBox)

        registerLayout.addWidget(QLabel('<h1>Registruj se</h1>'))
        registerLayout.addLayout(formLayout)
        registerLayout.addWidget(self.submitRegistrationButton)

        self.formMsg = QLabel("")
        registerLayout.addWidget(self.formMsg)
        self.formMsg.hide()

        self.generalLayout.addLayout(registerLayout)

    def _createLoginScreen(self):
        loginLayout = QVBoxLayout()
        formLayout = QFormLayout()

        self._clearScreen()

        self.loginScreen = QWidget(self._centralWidget)

        self.loginUsername = QLineEdit()
        self.loginPassword = QLineEdit()
        self.loginPassword.setEchoMode(QLineEdit.Password)

        self.loginButton = QPushButton("Prijavi se")
        self.loginButton.clicked.connect(self._attemptLogin)

        formLayout.addRow("Korisnicko ime:", self.loginUsername)
        formLayout.addRow("Lozinka:", self.loginPassword)

        loginLayout.addWidget(QLabel('<h1>Prijavi se</h1>'))
        loginLayout.addLayout(formLayout)
        loginLayout.addWidget(self.loginButton)

        self.formMsg = QLabel("")
        loginLayout.addWidget(self.formMsg)
        self.formMsg.hide()

#        loginLayout.addWidget(QLabel("Prijavite se"), 0, 0)
#        loginLayout.addWidget(QLabel("Korisnicko ime"), 1, 0)
#        loginLayout.addWidget(self.loginUsername, 2, 0)
#        loginLayout.addWidget(QLabel("Lozinka"), 3, 0)
#        loginLayout.addWidget(self.loginPassword, 4, 0)

        self.generalLayout.addLayout(loginLayout)


#class projekat_controller:
 #   def __init__(self):


def main():
    app = QApplication([])

    view = projekatWindow()
    view.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

#
#         if self.registerPassword.text():
#             if self.registerPassword.text() == self.confirmPassword.text():
#                 print("passwords match, registering...")
#
#                 registration.register(
#                     self.registerUsername.text(), self.registerPassword.text()
#                 )
#
#                 print(f"Registered user: \n\t{self.registerUsername.text()}")
#             else:
#                 print("passwords do not match.")
#                 err = '<h3 style="background-color:Tomato;">Passwords must match.</h3>'
#                 self._formMessage(msg=err)
#         else:
#             print("password too short")
#             err = '<h3 style="background-color:Tomato;">Please enter a password.</h3>'
#             self._formMessage(msg=err)
#   def _clearScreen(self):
  #       # app layout
  #       self.generalLayout = QVBoxLayout()

  #       # QWidget(self) == self as parent
  #       self._centralWidget = QWidget(self)
  #       self.setCentralWidget(self._centralWidget)
  #       self._centralWidget.setLayout(self.generalLayout)

# class MyWindow(QMainWindow):
#     def __init__(self):
#         # call the parent constructor (its init)
#         super(MyWindow, self).__init__()
#         self.setGeometry(99, 100, 800, 600)
#         self.setWindowTitle("joe mama")
#         self.initUI()
#
#     # this is where all the stuff that shows up
#     # will be loaded
#     def initUI(self):
#         self.label = QtWidgets.QLabel(self)
#         self.label.setText("bruh moment")
#         self.label.move(49, 50)
#
#         self.btn_0 = QtWidgets.QPushButton(self)
#         self.btn_0.setText("click me")
#         self.btn_0.clicked.connect(self.clicked)
#
#         self.layout = QGridLayout()
#         self.setLayout(self.layout)
#
#     def clicked(self):
#         self.label.setText("i fucked ur momasdsdasdjahgsdfuyasgf")
#         self.label.adjustSize()
#
#     def login_screen(self):
#         screen = login_test_1
#
#         self.layout.addWidget(screen, -1, 1)
#
#
# def window():
#     app = QApplication(sys.argv)  # just some config?
#     win = MyWindow()  # window
#     win.show()  # show the window
#
#     widget
#
#     # "clean exit"
#     sys.exit(app.exec_())
#
#

