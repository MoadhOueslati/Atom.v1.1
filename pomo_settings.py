from PyQt5.QtWidgets import QMainWindow
from pomo_settings_style import Ui_MainWindow 
import os


class PomoSettings(QMainWindow, Ui_MainWindow):
    def __init__(self, pomoFocusWindow, database, pomodoro_duration, short_break_duration, auto_pomo_is_on, animation_text_is_on):
        super().__init__()
        self.setupUi(self)

        self.pomo_window = pomoFocusWindow
        self.db = database

        # Attributes you get from the database 
        # User's pomo durations attributes
        self.pomodoro_duration = pomodoro_duration
        self.short_break_duration = short_break_duration
        self.auto_pomo_is_on = auto_pomo_is_on
        self.animation_text_is_on = animation_text_is_on

        # place the data inside widgets
        self.insert_data()

    
        # save & cancel Buttons
        self.cancelButton.clicked.connect(self.cancelAll)
        self.saveButton.clicked.connect(self.saveAll)

        

    def saveAll(self):
        self.pomodoro_duration = self.pomodoroSpinBox.value()
        self.short_break_duration = self.shortBreakSpinBox.value()

        self.auto_pomo_is_on = 1 if self.loopCheckBox.isChecked() else 0
        self.animation_text_is_on = 1 if self.animationCheckBox.isChecked() else 0


        update_query = "UPDATE pomo_settings SET pomodoro_duration = ?, short_break_duration = ?, auto_pomo_is_on = ?, animation_text_is_on = ?"
        self.db.insert_data(update_query, (self.pomodoro_duration, self.short_break_duration, self.auto_pomo_is_on, self.animation_text_is_on))

        # For resetting the pomodoro duration for pomo_focus window
        self.pomo_window.pomodoro_duration = self.pomodoro_duration
        # For resetting the short break duration for pomo_focus window
        self.pomo_window.short_break_duration = self.short_break_duration

        # For resetting the auto pomo check box state for pomo_focus window
        self.pomo_window.auto_pomo_is_on = self.auto_pomo_is_on
        # For resetting the animation text check box state for pomo_focus window
        self.pomo_window.animation_text_is_on = self.animation_text_is_on

        # Final reset pomo 
        self.pomo_window.reset_pomo()


        # For setting current study mode window in pomo_focus
        if self.pomo_window.current_pomo_status == "pomodoro":
            self.pomo_window.change_pomo(self.pomodoro_duration, "pomodoro") 
        if self.pomo_window.current_pomo_status == "short_break":
            self.pomo_window.change_pomo(self.short_break_duration, "short_break") 



        update_query_2 = f"""
        UPDATE daily_study_hours 
        SET 
        Sun = {self.SunDoubleSpinBox.value()},
        Mon = {self.MonDoubleSpinBox.value()},
        Tue = {self.TueDoubleSpinBox.value()},
        Wed = {self.WedDoubleSpinBox.value()},
        Thu = {self.ThuDoubleSpinBox.value()},
        Fri = {self.FriDoubleSpinBox.value()},
        Sat = {self.SatDoubleSpinBox.value()}
        """

        self.db.insert_data(update_query_2,)

        self.close()
    
    def cancelAll(self):
        self.insert_data()
        self.close()
    
    def closeEvent(self, event):
        self.insert_data()
        event.accept()

    def insert_data(self):
        # Show the durations 
        self.pomodoroSpinBox.setValue(self.pomodoro_duration)
        self.shortBreakSpinBox.setValue(self.short_break_duration)

        # Show the loop check box
        self.loopCheckBox.setChecked(True) if self.auto_pomo_is_on == 1 else self.loopCheckBox.setChecked(False)

        # Show the animation text check box
        self.animationCheckBox.setChecked(True) if self.animation_text_is_on == 1 else self.animationCheckBox.setChecked(False)

        # Show daily hours
        query_check = "SELECT * FROM daily_study_hours"
        daily_study_hours = self.db.fetch_data(query_check,)
        self.SunDoubleSpinBox.setValue(daily_study_hours[0])
        self.MonDoubleSpinBox.setValue(daily_study_hours[1])
        self.TueDoubleSpinBox.setValue(daily_study_hours[2])
        self.WedDoubleSpinBox.setValue(daily_study_hours[3])
        self.ThuDoubleSpinBox.setValue(daily_study_hours[4])
        self.FriDoubleSpinBox.setValue(daily_study_hours[5])
        self.SatDoubleSpinBox.setValue(daily_study_hours[6])
