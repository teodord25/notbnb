import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QVBoxLayout
from functools import partial


ERROR_MSG = 'ERROR'


class PyCalcUi(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('AyoCalc')
        self.setFixedSize(235, 235)

        self.generalLayout = QVBoxLayout()

        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)

        self._centralWidget.setLayout(self.generalLayout)

        self._createDisplay()
        self._createButtons()

    def _createDisplay(self):
        self.display = QLineEdit()

        self.display.setFixedHeight(35)

        # text is left aligned?
        self.display.setAlignment(Qt.AlignRight)

        # read only so no direct editing
        self.display.setReadOnly(True)

        self.generalLayout.addWidget(self.display)

    def _createButtons(self):
        self.buttons = {}
        buttonsLayout = QGridLayout()

        # text | position

        buttons = {'7': (0, 0),
                   '8': (0, 1),
                   '9': (0, 2),
                   '/': (0, 3),
                   'C': (0, 4),
                   '4': (1, 0),
                   '5': (1, 1),
                   '6': (1, 2),
                   '*': (1, 3),
                   '(': (1, 4),
                   '1': (2, 0),
                   '2': (2, 1),
                   '3': (2, 2),
                   '-': (2, 3),
                   ')': (2, 4),
                   '0': (3, 0),
                   '00': (3, 1),
                   '.': (3, 2),
                   '+': (3, 3),
                   '=': (3, 4),
                   }

        for btnText, pos in buttons.items():
            self.buttons[btnText] = QPushButton(btnText)
            self.buttons[btnText].setFixedSize(40, 40)
            buttonsLayout.addWidget(self.buttons[btnText], pos[0], pos[1])

        self.generalLayout.addLayout(buttonsLayout)

    def setDisplayText(self, text):
        self.display.setText(text)
        self.display.setFocus()

    def displayText(self):
        return self.display.text()

    def clearDisplay(self):
        self.setDisplayText('')

class PyCalcCtrl:
    def __init__(self, model, view):
        self._evaluate = model
        self._view = view
        self._connectSignals()

    def _calculateResult(self):
        result = self._evaluate(expression=self._view.displayText())
        self._view.setDisplayText(result)

    def _buildExpression(self, sub_exp):
        if self._view.displayText() == ERROR_MSG:
            self._view.clearDisplay()

        expression = self._view.displayText() + sub_exp
        self._view.setDisplayText(expression)
            # _view = view = PyCalcUi
            # thats why i can use setDisplayText

    def _connectSignals(self):
        for btnText, btn in self._view.buttons.items():
            if btnText not in {'=', 'C'}:
                btn.clicked.connect(partial(self._buildExpression, btnText))

        self._view.buttons['C'].clicked.connect(self._view.clearDisplay)
        self._view.buttons['='].clicked.connect(self._calculateResult)

        # returnPressed = "Enter key (return key)"
        self._view.display.returnPressed.connect(self._calculateResult)




def evaluateExpression(expression):
    try:
        result = str(eval(expression, {}, {}))
    except Exception:
        result = ERROR_MSG

    return result


def main():
    pycalc = QApplication(sys.argv)

    view = PyCalcUi()
    view.show()

    # model is just a reference to evalexpr..
    model = evaluateExpression
    PyCalcCtrl(model=model, view=view)

    sys.exit(pycalc.exec_())


if __name__ == '__main__':
    main()


#
# class Window(QMainWindow):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self._initUi()
#
#     def _initUi(self):
#         self.setWindowTitle('QMAINWINDOW')
#
#         self.msg = QLabel('')
#
#         self.btn1 = QPushButton("ayo")
#         self.btn1.clicked.connect(self._greeting)
#
#         layout = QGridLayout()
#         layout.addWidget(self.btn1)
#         layout.addWidget(self.btn1, 0, 0)
#         layout.addWidget(self.msg, 1, 0)
#
#
#         self.setCentralWidget(QLabel("ima da central widget"))
#
#         self._createMenu()
#         self._createToolBar()
#         self._createStatusBar()
#
#         self.setLayout(layout)
#
#     def _greeting(self):
#         if self.msg.text():
#             self.msg.setText("")
#         else:
#             self.msg.setText("Ayo world!")
#
#
#     def _createMenu(self):
#         self.menu = self.menuBar().addMenu("&Menu")
#         self.menu.addAction('&Exit', self.close)
#
#     def _createToolBar(self):
#         tools = QToolBar()
#         self.addToolBar(tools)
#         tools.addAction('Exit', self.close)
#
#     def _createStatusBar(self):
#         status = QStatusBar()
#         status.showMessage("status bar")
#         self.setStatusBar(status)
#
#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     win = Window()
#     win.show()
#     sys.exit(app.exec_())

# class Dialog(QDialog):
    # def __init__(self, parent=None):
        # super().__init__(parent)
        # self.setWindowTitle('QDialog')
        # dlgLayout = QVBoxLayout()
        # formLayout = QFormLayout()
        # formLayout.addRow("Name:", QLineEdit())
        # formLayout.addRow("Age:", QLineEdit())
        # formLayout.addRow("Job:", QLineEdit())
        # formLayout.addRow("Hobbies:", QLineEdit())
        # dlgLayout.addLayout(formLayout)

        # btns = QDialogButtonBox()
        # btns.setStandardButtons(
            # QDialogButtonBox.Cancel | QDialogButtonBox.Ok
        # )
        # dlgLayout.addWidget(btns)
        # self.setLayout(dlgLayout)

# if __name__ == "__main__":
    # app = QApplication([])
    # dlg = Dialog()
    # dlg.show()
    # sys.exit(app.exec_())

# create an instance of QApp
# app = QApplication([])  # replace [] with sys.argv if using CL arguments


# window = QWidget()
# window.setWindowTitle("pyqt app")
# window.setGeometry(100, 100, 280, 280)
# window.move(50, 15)

# A widget with no parent is a main window
# or top-level window

# a widget that has a parent (another widget)
# is contained within its parent

# The familial relationship also implies
# ownership, which ensures that if
# you delete a parent the child is also deleted


# helloMsg = QLabel('<h1>Hello World!</h1>', parent=window)
# helloMsg.move(50, 15)

#         HorizontalBoxLayout
# layout = QHBoxLayout()
# layout.addWidget(QPushButton('Left'))
# layout.addWidget(QPushButton('Center'))
# layout.addWidget(QPushButton('Right'))
# window.setLayout(layout)

# layout = QGridLayout()
# layout.addWidget(QPushButton("Joe"), 0, 0, 1, 2)
# layout.addWidget(QPushButton("Mama"), 1, 1, 1, 2)
# layout.addWidget(QPushButton("yo"), 1, 0, 1, 1)
# layout.addWidget(QPushButton("yo"), 0, 2, 1, 1)
# window.setLayout(layout)

# layout = QFormLayout()
# layout.addRow("Joe:", QLineEdit())
# layout.addRow("Mama:", QLineEdit())
# layout.addRow("Broman:", QLineEdit())
# layout.addRow("ding:", QLineEdit())
# layout.addRow("dong:", QLineEdit())
# layout.addRow("ayo the pizzas here:", QLineEdit())
# window.setLayout(layout)

# show GUI ( schedule a paint event )
# window.show()

# run apps event loop
# sys.exit(app.exec_())
