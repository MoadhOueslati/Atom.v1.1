import sys
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5 import uic
from PyQt5.QtCore import QTimer
import os

FILE_PATH = 'protocol.txt'

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('styles/login.ui', self)

        self.credentials_are_correct = True

        self.progressTimer = QTimer()
        self.progressTimer.timeout.connect(self.update_progress)
        self.progress_value = 0

        self.loginPushButton.clicked.connect(self.login)

    def login(self):
        if self.credentials_are_correct:
            self.loginPushButton.setEnabled(False)
            self.start_progress_timer()

    def start_progress_timer(self):
        self.progressTimer.start(30)

    def load_main_window(self):
        import main
        main.main()
        self.close()

    def update_progress(self):
        self.progress_bar.setValue(self.progress_value)
        self.progress_value += 1

        if self.progress_value == 90:
            self.progress_bar.setFormat("Loading your data...")

        if self.progress_value >= 100:
            self.progressTimer.stop()
            self.load_main_window()

    def closeEvent(self, event):
        delete_file()
        event.accept()  

def single_window_protocol():
    return os.path.exists(FILE_PATH)

def create_file():
    with open(FILE_PATH, 'w'):
        pass

def delete_file():
    if os.path.exists(FILE_PATH):
        os.remove(FILE_PATH)

if not single_window_protocol():
    create_file()
    app = QApplication(sys.argv)
    window = MyWidget()
    window.show()
    sys.exit(app.exec_())



        