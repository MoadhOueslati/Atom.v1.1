

'''
compiling : 
pyrcc5 resources_from_qt.qrc -o resources_from_qt.py

'''

# 🟢👤

import time

import os
import resources_from_qt
from pomo_focus_style import Ui_MainWindow 
from usage_dialog_style import Usage_Dialog
from version_dialog_style import Version_Dialog
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QLabel
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer, QCoreApplication, QThread, pyqtSignal
from database import DatabaseManager
from pomo_focus import PomoFocus
from reports import Reports
from ranking import Ranking
from datetime import datetime
import pyrebase

from data_modules import DataModules

from PyQt5 import uic


# Style constants
NAV_BAR_BUTTON_STYLE = '''
background-color: rgb(29, 35, 44);
color: rgb(209, 209, 209);
padding: 15px;
font-size: 20px;
border-top-left-radius: 30px;
text-align: left
'''


OK_PUSH_BUTTON_STYLE = '''
border: 1px solid rgb(75, 114, 255);
background-color: rgb(23, 77, 143);
color: white
'''


FILE_PATH = 'protocol.txt'
CURRENT_VERSION = 1.0

IS_REGISTERED_ONLINE = False



class WorkerThread(QThread):
    completed_counting_fetch_online = pyqtSignal()
    completed_counting_update_online = pyqtSignal()
    completed_counting_fetch_users = pyqtSignal()
    completed_counting_update_users = pyqtSignal()

    def run(self):
        while True:
            time.sleep(300)
            self.completed_counting_fetch_online.emit()
            time.sleep(300)
            self.completed_counting_update_online.emit()
            time.sleep(300)
            self.completed_counting_fetch_users.emit()
            time.sleep(300)
            self.completed_counting_update_users.emit()

    def stop(self):
        self.terminate()

class InstructionDialog(QDialog, Usage_Dialog):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.okPushButton.setEnabled(False)
        self.okPushButton.clicked.connect(self.close_dialog)
    
        # Connect the clicked signal of the next button
        self.nextPushButton.clicked.connect(self.show_next_image)
        self.image_index =  0  # Initialize the index of the displayed image
        self.image_paths = ["images/icons/first.png", "images/icons/second.png", "images/icons/third.png", "images/icons/fourth.png"]

        # Load and display the initial image
        self.load_image()

    def show_next_image(self):
        self.image_index = (self.image_index + 1) % 4
        # Load and display the next image
        self.load_image()
        self.display_paragraph()

    def load_image(self):
        image_label = self.findChild(QLabel, "imageLabel")

        # Check if the QLabel exists
        if image_label:
            # Load the image using QPixmap
            pixmap = QPixmap(self.image_paths[self.image_index])
            # Set the pixmap to the QLabel
            image_label.setPixmap(pixmap)
            # Adjust the size of the QLabel to fit the image
            image_label.adjustSize()
        

    def display_paragraph(self):
        text = ''
        if self.image_index == 0:
            text = '1. Click on the plus button to add a subject first.'
        if self.image_index == 1:
            text = '2. Click on the plus button, enter the subject name, press save.'
        if self.image_index == 2:
            text = '3. Press start to start your pomodoro session.'
        if self.image_index == 3:
            text = '4. Your studying data will appear here, GOOD LUCK! 🤩'
            self.okPushButton.setEnabled(True)
            self.okPushButton.setStyleSheet(OK_PUSH_BUTTON_STYLE)
        
        self.paragraphLabel.setText(text)
        
    
    def close_dialog(self):
        self.accept()


class VersionDialog(QDialog, Version_Dialog):
    def __init__(self, app_version):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Atom Update")
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setWindowIcon(QIcon('Atom.png'))
        self.updateMessage.setText(f"🎉 New Update Available! Atom Pomodoro {app_version} 🎉")


class MainWindow(QMainWindow): # add Uimainwindow later in arguments
    def __init__(self):
        super().__init__()
        # self.setupUi(self)   
        uic.loadUi('styles/main.ui', self)     
        self.db = DatabaseManager()

        self.user_count = ""
        self.online_users = ""

        self.init_firebase()
        self.set_online()
        self.init_ui()
        self.check_for_updates()
        self.closed_app = False

        self.worker_thread = WorkerThread()
        self.worker_thread.completed_counting_fetch_online.connect(self.fetch_online_users)
        self.worker_thread.completed_counting_update_online.connect(self.update_online_users_label)
        self.worker_thread.completed_counting_fetch_users.connect(self.fetch_user_count)
        self.worker_thread.completed_counting_update_users.connect(self.update_user_count_label)
        self.worker_thread.start()

    def init_ui(self):
        # check first day existance
        self.check_first_day_existance()


        self.subjects = self.get_user_subjects()

        # Prepare modules workshop
        self.dataModules = DataModules(self, self.db ,self.subjects)

        # Create page instances
        self.pomo_focus = PomoFocus(self, self.db, self.subjects)

        self.reports =  None
        self.rankings = None

        self.reportsButton.clicked.connect(self.show_reports)
        self.rankingButton.clicked.connect(self.show_rankings)

        # Instructions window
        self.instructions_dialog = None
        self.instructionsButton.clicked.connect(self.create_instruction_dialog)

        # Version window
        self.version_dialog = None

        # Connect signals
        self.connect_nav_bar_buttons()

        self.resize_timer = QTimer(self)
        self.resize_timer.setSingleShot(True)
        self.resize_timer.timeout.connect(self.update_font_size)

        self.fixedWindowButton.clicked.connect(self.toggle_always_on_top)
        self.visibilitySlider.valueChanged.connect(self.set_window_alpha)
    

    def check_for_updates(self):
        app_version = self.get_version()
        if app_version is not None:
            if CURRENT_VERSION != app_version:
                self.create_version_dialog(app_version)
                QTimer.singleShot(10000, self.show_version_dialog)
    
    def create_version_dialog(self, app_version):
        if self.version_dialog == None:
            self.version_dialog = VersionDialog(app_version)

    def show_version_dialog(self):
        self.version_dialog.exec_()


    def create_instruction_dialog(self):
        if self.instructions_dialog == None:
            self.instructions_dialog = InstructionDialog()
        self.show_instruction_dialog()
    
    
    def show_instruction_dialog(self):
        self.instructions_dialog.exec_()
    
    def show_rankings(self):
        if self.rankings == None:
            self.rankings = Ranking(self, self.db, self.dataModules)

    def show_reports(self):
        if self.reports == None:
            self.reports= Reports(self, self.db, self.subjects, self.dataModules)
        today_date = datetime.now().date()
        subjects = self.get_user_subjects()
        total_subject_hours = self.reports.get_total_study_hours(subjects)
        self.reports.pie_chart_graph(total_subject_hours)
        
        # this checks user's bar type settings (h or %)
        self.current_bar_type = self.check_current_bar_type()
        if self.current_bar_type == "Percentage":
            self.barComboBox.setCurrentIndex(1)
            self.reports.bars_chart_graph_2(today_date)
        if self.current_bar_type == "Hour":
            self.barComboBox.setCurrentIndex(0)
            self.reports.bars_chart_graph(today_date)

        #this fixes the showing weeks bug buttons
        self.reports.current_week = today_date
    
    def insert_new_hours_row(self, today_date):
        # Check if self.subjects is empty
        if not self.subjects:
            # If it's empty, insert only the date
            query = "INSERT INTO subject_record (date) VALUES (?)"
            values = [today_date]
        else:
            # If not empty, insert the date and zeros for each subject
            place_holders = ", ".join(["?" for _ in self.subjects])
            columns = ', '.join(f'"{subject}"' for subject in self.subjects)
            query = f"INSERT INTO subject_record (date, {columns}) VALUES (?, {place_holders})"
            values = [today_date] + [0 for _ in self.subjects]
        

        self.db.insert_data(query, tuple(values))

    def check_current_bar_type(self):
        query = "SELECT * FROM bar_settings"
        current_bar_type = self.db.fetch_data(query,)[0]
        return current_bar_type

    def connect_nav_bar_buttons(self):
        self.buttons = [
            self.pomoFocusButton,
            self.reportsButton,
            self.rankingButton
        ]

        for button in self.buttons:
            button.clicked.connect(self.nav_bar_buttons)


    def nav_bar_buttons(self):
        sender = self.sender()
        index = self.buttons.index(sender)
        self.pagesStackedWidget.setCurrentIndex(index)

        # Style Button
        for button in self.buttons:
            button.setStyleSheet(NAV_BAR_BUTTON_STYLE if button is sender else "")


    def resizeEvent(self, event):
        self.resize_timer.start(200)
  
    def update_font_size(self):
        # Calculate a dynamic font size based on the window width
        adjusted_width = self.pomoContainer.width() / 5
        adjusted_height = self.pomoContainer.height() / 5
        font_size = int(min(adjusted_width, adjusted_height))
        # Set the calculated font size to the label
        self.timerLabel.setStyleSheet(f"""
                                    font: {font_size}pt 'MS Shell Dlg 2';
                                    color:white
                                    """
                                    )


    def toggle_always_on_top(self):
        # Toggle the "always on top" status
        is_always_on_top = self.windowFlags() & Qt.WindowStaysOnTopHint
        self.setWindowFlag(Qt.WindowStaysOnTopHint, not is_always_on_top)
        self.resize(400, 415)
        self.move(0,0)
        self.show()

    def set_window_alpha(self, value):
        alpha_value = value / 100.0
        self.setWindowOpacity(alpha_value)


    def closeEvent(self, event):
        self.hide()
        delete_file() # deleting the single window file protocol
        self.pomo_focus.stop_pomo_timer()  # for saving data incase he didnt click stop button


        # making sure to close the other windows 
        if self.pomo_focus.subjects_window.isVisible():
            self.pomo_focus.subjects_window.close()
        if self.pomo_focus.pomo_settings_window.isVisible():
            self.pomo_focus.pomo_settings_window.close()
        try:self.db.close_connection()
        except: pass
        try:
            if IS_REGISTERED_ONLINE:
                self.set_offline()
        except:
            pass
        self.closed_app = True
        if self.worker_thread.isRunning():
            self.worker_thread.stop()
            self.worker_thread.wait()
        QCoreApplication.processEvents()

        event.accept()
     

    def get_user_subjects(self):
        # User's subjects
        table_query = f"PRAGMA table_info({'subject_record'})"
        table_data_query = self.db.fetch_all_data(table_query)
        columns = [column[1] for column in table_data_query]
        # removing 'date' column from the subjects list
        columns.pop(0)

        return columns
    
    def check_first_day_existance(self):
        query = "SELECT date FROM first_day_date"
        first_day = self.db.fetch_data(query)
        if not first_day:
            try:
                self.insert_today_date()
                # add a new user to the firebase database user-count
                self.insert_new_user()
            except:
                pass
        else:
            try:
                self.get_user_count()
            except:
                pass

        self.usersCountLabel.setText(self.user_count)
        self.usersOnlineLabel.setText(self.online_users)
            
    # Insert first day date since application was used
    def insert_today_date(self):
        query = "INSERT INTO first_day_date (date) VALUES (?)"
        self.db.insert_data(query, (datetime.now().date(),))

    def get_user_count(self):
        try:
            data_key = 'user_count'
            self.user_count = self.get_firebase_data(data_key)
        except: 
            pass

    def insert_new_user(self):
        try:
            self.get_user_count()
            data_key = 'user_count'
            data = str(int(self.user_count) + 1)
            self.insert_firebase_data(data_key, data)
        except:
            pass

    def get_firebase_data(self, data_key):
        try:
            result = self.fdb.child('your_data_node').child(data_key).get()
            data = result.val()
            return data
        except:
            pass

    def insert_firebase_data(self, data_key, data):
        try:
            self.fdb.child("your_data_node").child(data_key).set(data)
        except:
            pass

    def get_online_users(self):
        try:
            data_key = 'online_users' 
            self.online_users = self.get_firebase_data(data_key)
        except:
            pass

    def set_online(self):
        global IS_REGISTERED_ONLINE
        try:
            self.get_online_users()
            data_key = 'online_users'
            data = str(int(self.online_users) + 1)
            self.insert_firebase_data(data_key, data)
            IS_REGISTERED_ONLINE = True
        except:
            pass

    def set_offline(self):
        try:
            self.get_online_users()
            if int(self.online_users) > 0 and not self.closed_app:
                data_key = 'online_users'
                data = str(int(self.online_users) - 1)
                self.insert_firebase_data(data_key, data)
        except:
            pass

    # Version Control 
    def get_version(self):
        try:
            data_key = 'app_version'
            app_version = self.get_firebase_data(data_key)
            return app_version
        except:
            return None
    
    def init_firebase(self):
        try: 
            firebase_config = {
                "apiKey": "AIzaSyCI4WkhrIZQ-z-8OdkDKt1Rt6w9SC5ZUlY",
                "authDomain": "sick-1ea39.firebaseapp.com",
                "databaseURL": "https://sick-1ea39-default-rtdb.firebaseio.com/",
                "projectId": "sick-1ea39",
                "storageBucket": "sick-1ea39.appspot.com",
                "messagingSenderId": "441026160301",
                "appId": "1:441026160301:web:668c9ba356acbb41a54824",
                "measurementId": "G-HR6S3F65YD"
            }

            self.firebase = pyrebase.initialize_app(firebase_config)
            self.fdb = self.firebase.database()
        except:
            pass
        
    def fetch_online_users(self):
        try:
            self.get_online_users()
        except:
            pass

    def update_online_users_label(self):
        try:
            self.usersOnlineLabel.setText(self.online_users)
        except:
            pass

    def fetch_user_count(self):
        try:
            self.get_user_count()
        except:
            pass

    def update_user_count_label(self):
        try:
            self.usersCountLabel.setText(self.user_count)
        except:
            pass

# def create_file():
#     with open(FILE_PATH, 'w'):
#         pass

def delete_file():
    if os.path.exists(FILE_PATH):
        os.remove(FILE_PATH)
        

def main():
    # Create the main window
    window = MainWindow()
    window.setWindowTitle(f'Atom By Moadh v{CURRENT_VERSION}')
    window.setWindowIcon(QIcon('Atom.png'))
    window.show()





        