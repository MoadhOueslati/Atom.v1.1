import copy

from utils import *
from PyQt5.QtWidgets import QMainWindow ,QInputDialog, QMessageBox
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtCore import Qt
from add_subject_style import Ui_MainWindow
from datetime import datetime
from pomo_settings import PomoSettings
# from plyer import notification


   
POMO_BUTTON_STYLE = """
background-color: rgb(56, 94, 168);
"""

POMO_FOCUS_WORK_PAGE_STYLE = """
border:none;
background-color: rgb(224, 75, 90)
"""

POMO_FOCUS_BREAK_PAGE_STYLE = """
border:none;
background-color: rgb(93, 192, 166)
"""


class PomoFocus(QMainWindow):
    def __init__(self, mainwindow, database, subjects):
        super().__init__()
        self.mw = mainwindow
        self.db = database

        self.subjects = subjects

        # Pomodoro durations queries
        pomodoro_duration_query = "SELECT pomodoro_duration FROM pomo_settings"
        short_break_duration_query = "SELECT short_break_duration FROM pomo_settings"
        auto_pomo_query = "SELECT auto_pomo_is_on FROM pomo_settings"
        animation_text_query = "SELECT animation_text_is_on FROM pomo_settings"

        
        # User's pomo settings
        self.pomodoro_duration = self.db.fetch_data(pomodoro_duration_query)[0]
        self.short_break_duration = self.db.fetch_data(short_break_duration_query)[0]
        self.auto_pomo_is_on = self.db.fetch_data(auto_pomo_query)[0]
        self.animation_text_is_on = self.db.fetch_data(animation_text_query)[0]

        self.pomo_status = ["pomodoro", "short_break"]

        
        self.timer = StudyTimer()

        """"Setting the default status"""
        self.reset_pomo() #initial reset
        self.current_pomo_status = self.pomo_status[0]  # Deafault pomo
        self.pomo_duration = self.pomodoro_duration # Default pomo duration
        self.current_state_index = 0

        self.total_sessions = 3
        self.current_session = 0

        # hide the progress bar and the stay fixed window button by default
        self.mw.progressBarWidget.setHidden(True) 
        self.mw.fixedWindowButton.setHidden(True) 
        self.mw.visibilitySlider.setHidden(True)


        # Set the pomodoro timer as default
        self.set_pomo_timer(self.pomodoro_duration)

        # Listen to button clicks 
        self.listen_buttons_clicks()

        # Update data 
        self.update_subjects(self.subjects)

        # Button tick sound effect
        self.button_click_sound = QSoundEffect()
        self.button_click_sound.setSource(QUrl.fromLocalFile("button_tick.wav"))

        # Alarm sound effect
        self.alarm_sound = QSoundEffect()
        self.alarm_sound.setSource(QUrl.fromLocalFile("alarm.wav"))
        self.alarm_sound.setVolume(0.1)

        self.subjects_window = SubjectsSettings(self, self.db, self.subjects)
        self.pomo_settings_window = PomoSettings(self, self.db, self.pomodoro_duration, self.short_break_duration, self.auto_pomo_is_on, self.animation_text_is_on)

        self.pomo_label = self.mw.pomoStateLabel.text()
        self.current_letter_index = len(self.pomo_label)

        self.remove_letter_timer = QTimer(self)
        self.remove_letter_timer.timeout.connect(self.remove_letter)

        self.add_letter_timer = QTimer(self)
        self.add_letter_timer.timeout.connect(self.display_letter)

        self.letter_speed = 300



    def remove_letter(self):
        self.current_text = self.mw.pomoStateLabel.text()
        if self.current_letter_index > 0:
            self.current_text = self.current_text[:-1]  # Remove the last character
            self.mw.pomoStateLabel.setText(self.current_text)
            self.current_letter_index -= 1
        else:
            self.remove_letter_timer.stop()
            self.add_letter_timer.start(self.letter_speed)

    def display_letter(self):
        self.current_text = self.mw.pomoStateLabel.text()
        if self.current_letter_index < len(self.pomo_label):
            self.current_text += self.pomo_label[self.current_letter_index]
            self.mw.pomoStateLabel.setText(self.current_text)
            self.current_letter_index += 1
        else:
            self.add_letter_timer.stop()


    def reset_pomo(self):
        self.pomo = {
            "pomodoro" : self.pomodoro_duration,
            "short_break" : self.short_break_duration,
        }


    def listen_buttons_clicks(self):
        self.mw.startStopButton.clicked.connect(self.start_stop_timer)  

        # open pomo settings window
        self.mw.pomoSettingsButton.clicked.connect(self.showSettingsWindow)

        # skip current pomo state
        self.mw.skipButton.clicked.connect(self.skip_pomo)

        # open subjects settings window
        self.mw.addSubjectButton.clicked.connect(self.showSubjectsWindow)

        # change to full screen mode
        self.mw.fullScreenButton.clicked.connect(self.change_screen_mode)


    # MIDDLE SIDE 
    def change_screen_mode(self):
        # ensuring that the window doesnt stay on top after exiting full screen mode
        self.mw.setWindowFlag(Qt.WindowStaysOnTopHint, False)
        self.mw.show()

        self.hide_widgets()
        # playing with colors 
        if self.mw.leftContainer.isHidden(): # meaning full screen mode
            self.mw.setMinimumSize(400, 415)
            self.change_pomo_focus_style()
        else:                                # meaning minimized screen 
            self.mw.setMinimumSize(1200, 800)
            self.mw.pomoFocusPage.setStyleSheet("")
            self.mw.visibilitySlider.setValue(100)


        self.mw.update_font_size()
    
    def change_pomo_focus_style(self):
        if self.mw.leftContainer.isHidden():
            if self.current_pomo_status == self.pomo_status[0]:
                self.mw.pomoFocusPage.setStyleSheet(POMO_FOCUS_WORK_PAGE_STYLE)
            elif self.current_pomo_status == self.pomo_status[1]:
                self.mw.pomoFocusPage.setStyleSheet(POMO_FOCUS_BREAK_PAGE_STYLE)

    
    def animate_pomo_label(self, speed):
        self.letter_speed = speed
        if self.current_pomo_status == self.pomo_status[0]:
            self.pomo_label = "Work"
            self.remove_letter_timer.start(self.letter_speed)
        elif self.current_pomo_status == self.pomo_status[1]:
            self.pomo_label = "Break"
            self.remove_letter_timer.start(self.letter_speed)


    def hide_widgets(self):
        current_visibility = self.mw.leftContainer.isHidden()

        self.mw.progressBarWidget.setHidden(current_visibility)
        self.mw.fixedWindowButton.setHidden(current_visibility)
        self.mw.visibilitySlider.setHidden(current_visibility)


        self.mw.leftContainer.setHidden(not current_visibility)
        self.mw.bottomWidget.setHidden(not current_visibility)
        self.mw.buttonsFrame.setHidden(not current_visibility)
        self.mw.fireBaseDataFrame.setHidden(not current_visibility)


    def change_pomo(self, pomo_duration, pomo_status):
        self.change_pomo_focus_style()
        self.stop_pomo_timer()
        self.set_pomo_timer(pomo_duration)

        # this makes sure the input buttons are enabled for breaks
        if self.current_pomo_status != "pomodoro":
            self.set_input_enabled(True)

        # to know on which timer we are right now
        self.pomo_duration = pomo_duration 
        self.current_pomo_status = pomo_status


    def update_subjects(self, subjects):
        self.subjects = subjects
        
        # update subject's combo box
        self.update_subjects_combo_box(subjects)

    def setDurationTextLabel(self, duration):
        self.mw.timerLabel.setText(f"{duration}:00")  # Pomo time 

    def update_timer(self):
        self.remaining_time -= 1
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.mw.timerLabel.setText(f"{minutes:02}:{seconds:02}")

        # updating the progress bar
        self.update_progress_bar(self.remaining_time)

        # check if time is over then reset
        if self.remaining_time <= 0:
            self.alarm_sound.play()
            self.change_pomo(self.pomo_duration ,self.current_pomo_status)  # Reset us to the current pomo duration
            if self.auto_pomo_is_on == 1:
                self.skip_pomo()
                self.start_stop_timer()
            
            if self.animation_text_is_on == 1:
                self.animate_pomo_label(300)
            else: self.animate_pomo_label(0)

            
    def skip_pomo(self):
        # clear the progress bar
        self.mw.progressBar.setValue(0)

        self.stop_pomo_timer() # to stop the previous pomo 
        self.current_state_index = (self.current_state_index + 1) % len(self.pomo_status)
        self.current_pomo_status = self.pomo_status[self.current_state_index]
        self.change_pomo(self.pomo[self.current_pomo_status], self.current_pomo_status)

        self.animate_pomo_label(0)
    

    def play_clock_tick_sound(self):
        # Play clock tick sound
        self.clock_tick_sound.play()

    def set_pomo_timer(self, duration):
        ''''
        This is responsible for decreasing the timer once the user
        hits the start button , the button handels stop/start signals.
        '''
        self.remaining_time = duration * 60

        self.pomo_timer = QTimer()
        self.pomo_timer.timeout.connect(self.update_timer)

        self.setDurationTextLabel(duration)


    def showSettingsWindow(self):
        if not self.pomo_settings_window.isVisible():
            self.pomo_settings_window.setWindowTitle("Settings")
            self.pomo_settings_window.setFixedSize(550, 650)
            self.pomo_settings_window.show()
        else:
            self.pomo_settings_window.activateWindow()

    def showSubjectsWindow(self):
        """ you need to pass subjects params from the database. """
        if not self.subjects_window.isVisible():
            self.subjects_window.setWindowTitle("Subjects")
            self.subjects_window.setFixedSize(530, 360)
            self.subjects_window.show()
            self.subjects_window.activateWindow()
        else:
            self.subjects_window.activateWindow()


    def insert_studied_hours(self, studied_hours, subject):
        today_date = datetime.now().date()
        
        # Fetch the current studied hours for the subejct
        query_fetch = f'SELECT "{subject}" FROM subject_record WHERE date = ?'
        current_hours = self.db.fetch_data(query_fetch, (today_date,))

        if not current_hours: # this means the date doesnt exists in the database
            self.mw.insert_new_hours_row(today_date) # inserts new date if doesnt exist in db
            current_hours = self.db.fetch_data(query_fetch, (today_date,))
        
        current_hours = current_hours[0]

        # Calculate the new studied hours
        new_total_hours = current_hours + studied_hours

        # Inserting the new studied hours for the subject
        query_update = f"""
        UPDATE subject_record
        SET "{subject}" = ?
        WHERE date = ?
        """
        self.db.insert_data(query_update, (new_total_hours, today_date))
    
    def insert_total_studied_hours(self, studied_hours, subject):
        
        # Fetch the current total studied hours from the subject
        query_fetch = f'SELECT "{subject}" FROM total_study_hours'
        current_total_hours = self.db.fetch_data(query_fetch,)[0]

        # Calculate the new total hours
        new_total_hours = current_total_hours + studied_hours

        # Inserting new total hours for the subject
        query_update = f"""
        UPDATE total_study_hours
        SET "{subject}" = ?
        """

        self.db.insert_data(query_update, (new_total_hours,))



    def update_progress_bar(self, remaining_time):
        total_time = self.pomo_duration * 60
        progress_value = int((total_time - remaining_time) / total_time * 100)
        self.mw.progressBar.setValue(progress_value)


    def stop_pomo_timer(self):
        if self.pomo_timer.isActive():
            # pressing stop timer
            self.mw.startStopButton.setText('Start')
            self.pomo_timer.stop()
            self.timer.stop()
            
            if self.current_pomo_status == "pomodoro":
                # Studied time 
                studied_duration = self.timer.calculate_studied_time() # only for pomodoro running

                # get the comboBox current item
                current_subject = self.mw.subjectsComboBox.currentText()  # only for pomodoro running
                
                # insert studied hours for chosen subject in mysql db
                self.insert_studied_hours(studied_duration, current_subject)   # only for pomodoro running
                # insert study hours to total study hours for chosen subject in mysql db
                self.insert_total_studied_hours(studied_duration, current_subject)
                
                self.set_input_enabled(True)   # only for pomodoro running
        

          
    def start_stop_timer(self):
        '''This makes sure the user can't use the application 
        unless he enters a subject to focus on first 
        cant focus on nothing ?!?'''
        if len(self.mw.subjectsComboBox.currentText()) != 0:                
            # Play button tick sound effect
            self.button_click_sound.play()

            # pressing stop timer
            if self.pomo_timer.isActive():
                self.stop_pomo_timer()

            #pressing  start timer
            else:
                """"Close the add subjects window incase 
                the user has opened the subjects window 
                then clicked on start button whithout closing
                the window."""
                if self.subjects_window.isVisible():
                    self.subjects_window.close()


                self.timer.start()
                self.mw.startStopButton.setText('Stop')
                self.pomo_timer.start(1000)  # timer ticks every 1 second

                if self.current_pomo_status == "pomodoro":
                    self.set_input_enabled(False)    # only for pomodoro running
        else:
            message = "You must select a subject to focus on first!"
            self.show_information_message(message)

    
    def show_information_message(self, message):
        QMessageBox.information(self, "Information", message)
        self.mw.create_instruction_dialog()
        
        

    def update_subjects_combo_box(self, subjects):
        # clear the combo box from previous data first
        self.mw.subjectsComboBox.clear()

        # adding subjects to the combo box
        for subject in subjects:
            self.mw.subjectsComboBox.addItem(subject)

    # Enable/Disable combox and add subject buttons
    def set_input_enabled(self, status):
        self.mw.subjectsComboBox.setEnabled(status)
        self.mw.addSubjectButton.setEnabled(status)
        if status == True:
            self.mw.addSubjectButton.setStyleSheet('color: white')
        else:
            self.mw.addSubjectButton.setStyleSheet('color: gray')


        
class StudyTimer:
    def __init__(self):
        self.start_time = None
        self.stop_time = None
    
    def start(self):
        self.start_time = datetime.now()

    def stop(self):
        self.stop_time = datetime.now()

    
    def calculate_studied_time(self):
        if self.start_time is not None and self.stop_time is not None:
            duration = self.stop_time - self.start_time  
            minutes = duration.seconds // 60

            total_duration = minutes / 60

            formatted_duration = float("{:.2f}".format(total_duration))  # formated the duration to be in this format (0.00 hours)

            return formatted_duration
        else:
            return  # maybe an error message here ? 


class SubjectsSettings(QMainWindow, Ui_MainWindow):
    def __init__(self, pomoFocusWindow, db_manager, subjects):
        super().__init__()
        self.setupUi(self)
        self.init_ui(pomoFocusWindow, db_manager, subjects)

    def init_ui(self, pomoFocusWindow, db_manager, subjects):
        self.pomo_window = pomoFocusWindow
        self.db = db_manager
        
        self.original_subjects = subjects
        self.subjects = copy.deepcopy(self.original_subjects)

        self.to_remove_subjects = []

        self.display_subjects()

        self.addSubjectButton.clicked.connect(self.add_subject)
        self.removeSubjectButton.clicked.connect(self.remove_subject)
        
        self.cancelButton.clicked.connect(self.cancel_changes)
        self.saveButton.clicked.connect(self.save_changes)


    def display_subjects(self):
        self.listWidget.clear()
        for subject in self.subjects:
            self.listWidget.addItem(subject)

    def add_subject(self):
        subject, ok = QInputDialog.getText(self, "Add subject", "Subject")
        subject = add_spaces(subject).lower()

        try:
            # this makes sure to remove the subject from the bin(self.to_remove_subjects) incase user changes his mind by entering it again after removing it at the same time
            if subject in self.to_remove_subjects:
                self.to_remove_subjects.remove(subject)

            if ok and self.subject_input_verification(subject):
                self.listWidget.addItem(subject)
                self.subjects.append(subject)
        except Exception as e:
            self.show_error_message(f"Error adding subject: {e}")

    def subject_input_verification(self, subject):
        condition_1 = 0 < len(subject) < 20
        condition_2 = subject not in self.subjects
        condition_3 = True
        x = 0
        while condition_3 == True and x < len(subject):
            condition_3 = 'a' <= subject[x] <= 'z' or 'A' <= subject[x] <= 'Z' or subject[x] == ' '
            x += 1

        return condition_1 and condition_2 and condition_3
    
    def remove_subject(self):
        selcted_subject = self.listWidget.currentItem()
        try:
            if selcted_subject != None:
                if selcted_subject.text() in self.original_subjects:
                    warning_message = f'Are you sure you want to delete "{selcted_subject.text()}" from subjects ?\nAny related data to "{selcted_subject.text()}" will be deleted.\n(not recommended)'
                    reply = QMessageBox.question(
                    self,
                    "Remove Subject",
                    warning_message,
                    QMessageBox.Ok | QMessageBox.Cancel,  # <-- Corrected line
                    QMessageBox.Cancel
                    )
                    if reply == QMessageBox.Ok:
                        self.listWidget.takeItem(self.listWidget.row(selcted_subject))
                        # add the subject to the trash can
                        self.to_remove_subjects.append(selcted_subject.text())
                        self.subjects.remove(selcted_subject.text())
                    else:
                        pass

                # Remove the subject if he has just insert it (there is no actual data for it.)
                else:
                    self.listWidget.takeItem(self.listWidget.row(selcted_subject))
                    self.subjects.remove(selcted_subject.text())
        except Exception as e:
            self.show_error_message(f"Error removing subject: {e}")



    def save_changes(self):
        # inserting new subjects to the database
        for subject in self.subjects:
            if subject not in self.original_subjects:
                subject_column_query = f'ALTER TABLE subject_record ADD COLUMN "{subject}" NUMERIC DEFAULT 0'
                subject_column_query_2 = f'ALTER TABLE total_study_hours ADD COLUMN "{subject}" NUMERIC DEFAULT 0'
                self.db.insert_data(subject_column_query)
                self.db.insert_data(subject_column_query_2)

        # deleting subjects from the database
        for subject in self.to_remove_subjects:
            deleting_subject_query = f'ALTER TABLE subject_record DROP COLUMN "{subject}"'
            deleting_subject_query_2 = f'ALTER TABLE total_study_hours DROP COLUMN "{subject}"'
            self.db.insert_data(deleting_subject_query)
            self.db.insert_data(deleting_subject_query_2)


        # updating user's subjects
        self.original_subjects = copy.deepcopy(self.subjects) # this is responsible for making self.original_subjects identical with self.subjects in case of adding a new subject to database
        self.pomo_window.update_subjects(self.original_subjects) 
        self.to_remove_subjects.clear()
        self.close()
    
    def cancel_changes(self):
        self.to_remove_subjects.clear()
        self.subjects = copy.deepcopy(self.original_subjects)
        self.display_subjects()
        self.close()

    def closeEvent(self, event):
        self.cancel_changes()
        event.accept()
        
        

    # For handling errors
    def show_error_message(self, message):
        error_box = QMessageBox()
        error_box.setIcon(QMessageBox.Critical)
        error_box.setWindowTitle("Error")
        error_box.setText(message)
        error_box.exec_()
    



