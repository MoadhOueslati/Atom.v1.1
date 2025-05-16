from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem
from data_modules import DataModules

class Ranking(QMainWindow):
    def __init__(self, mainwindow, database, datamodules):
        super().__init__()
        self.mw = mainwindow
        self.db = database
        self.dm = datamodules

        self.total_studied_hours = datamodules.get_total_studied_hours()
        

        self.mw.rankingButton.clicked.connect(self.display_ranks)


    def display_ranks(self):
        row_position = self.mw.rankingsTable.rowCount()
        print(row_position)
        self.mw.rankingsTable.insertRow(row_position)
        self.mw.rankingsTable.setItem(0, 0, QTableWidgetItem("moadh"))
        self.mw.rankingsTable.setItem(0, 1, QTableWidgetItem(str(self.total_studied_hours)))


    


        