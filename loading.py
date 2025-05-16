from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QDialog
import sys
from PyQt5.QtGui import QIcon
import os 
FILE_PATH = 'protocol.txt'

class LoadScreen(QThread):
    progress_update = pyqtSignal(int)
    finished_signal = pyqtSignal()

    def run(self):
        # Simulate your initialization tasks here
        for i in range(100):
            self.progress_update.emit(i + 1)
            self.msleep(30)  # Simulate work (adjust as needed)

        self.finished_signal.emit()


class MainForm(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('styles/loading_screen.ui', self)

        self.progress_value = 0

        # Connect signals and slots
        self.LoadScreen = LoadScreen()
        self.LoadScreen.progress_update.connect(self.update_progress)
        self.LoadScreen.finished_signal.connect(self.on_worker_finished)

        # Start the loading screen thread
        self.LoadScreen.start()

        # Delay the initialization of MainWindow to let the loading screen continue smoothly
        self.main_window = None

    def update_progress(self, value):
        # Update the progress bar
        self.progress_value = value
        self.progressBar.setValue(self.progress_value)

        # Create and show the main window once the loading is complete
        if self.progress_value == 99 and not self.main_window:
            import main
            main.create_file()
            self.main_window = main.MainWindow()
            self.main_window.setWindowTitle('Atom By Moadh v1.1')
            self.main_window.show()

    def on_worker_finished(self):
        # Hide the progress bar
        self.close()


def start():
    app = QApplication(sys.argv)

    # Create the main window
    window = MainForm()
    window.setWindowTitle('Atom By Moadh v1.1')
    window.setWindowIcon(QIcon('Atom.png'))
    window.show()

    sys.exit(app.exec_())

def single_window_protocol():
    return os.path.exists(FILE_PATH)
      

if __name__ == "__main__":
    if not single_window_protocol():
        start()
