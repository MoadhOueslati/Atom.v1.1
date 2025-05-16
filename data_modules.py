from PyQt5.QtWidgets import QMainWindow


class DataModules(QMainWindow):
    def __init__(self, mainwindow, database, subjects):
        super().__init__()
        self.mw = mainwindow
        self.db = database
        self.subjects = subjects


    def get_total_study_hours(self):
        """"for the pie chart"""
        subjects_total_hours = {}
        for subject in self.subjects:
            query_check = f'SELECT "{subject}" FROM total_study_hours'
            total_study_hours = self.db.fetch_data(query_check, )[0]
            subjects_total_hours[subject] = total_study_hours

        return subjects_total_hours



    def get_total_studied_hours(self):
        total_subject_hours = self.get_total_study_hours()
        studied_hours_data = list(total_subject_hours.values())
        total_studied_hours = sum(studied_hours_data)

        return total_studied_hours