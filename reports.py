from PyQt5.QtWidgets import QMainWindow
import matplotlib.pyplot as plt
from matplotlib import dates as mpl_dates
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QFileDialog
import seaborn as sns 
from data_modules import DataModules


class Reports(QMainWindow):
    def __init__(self, mainwindow, database, subjects, datamodules):
        super().__init__()
        self.mw = mainwindow
        self.db = database
        self.subjects = subjects
        self.dm = datamodules

        self.first_day = self.get_first_day()

        # get how many hours the user must study per day
        # self.total_hours_per_day = self.get_daily_study_hours()


        self.studied_hours = self.get_studied_hours_by_date(datetime.now().date())

        self.pie_figure = plt.Figure(facecolor='None')
        
        self.pie_canvas = FigureCanvas(self.pie_figure)
        self.pie_figure.tight_layout()

        self.total_study_hours = datamodules.get_total_study_hours()
        self.pie_chart_graph(self.total_study_hours)

        
        # Bar chart graph
        self.bars_figure = plt.Figure(figsize=(8, 6), facecolor="#1D232C")
        self.bars_canvas = FigureCanvas(self.bars_figure)
        self.bars_figure.tight_layout()
 

        today_date = datetime.now().date()
        self.current_week = today_date
        self.bars_chart_graph(self.current_week)

        #for changing bars graph
        self.mw.barComboBox.currentIndexChanged.connect(lambda: self.changeBarGraph(self.current_week))

        self.mw.leftWeekButton.clicked.connect(self.show_previous_week)
        self.mw.rightWeekButton.clicked.connect(self.show_next_week)

        self.mw.todayButton.clicked.connect(self.show_today_data)
        self.mw.overAllButton.clicked.connect(self.show_overall_data)

        self.mw.saveBarChartButton.clicked.connect(self.save_bar_graph)


    def changeBarGraph(self, today_date):
        if self.mw.barComboBox.currentText() == "Hour":
            self.bars_chart_graph(today_date)
        if self.mw.barComboBox.currentText() == "Percentage":
            self.bars_chart_graph_2(today_date)
        #this updates user bar graph settings
        self.change_bar_settings()
    
    def change_bar_settings(self):
        bar_type = self.mw.barComboBox.currentText()
        query_update = f"UPDATE bar_settings SET bar_type = ?"
        self.db.insert_data(query_update, (bar_type,))

    def bars_chart_graph(self, chosen_day):
        self.current_bar_graph = "bar1"
        # Clear earlier figure
        self.bars_figure.clear()

        self.mw.barChartWidget.layout().addWidget(self.bars_canvas)

        # today_date = datetime.now().date()
        week_days = 7

        # Generate a list of dates
        dates = [chosen_day - timedelta(days=i) for i in range(week_days)]


        # Get studied hours of each day in 1 week
        studied_by_date = [self.get_studied_hours_by_date(x) for x in dates]


        # Get total studied hours in 1 week
        total_studied_hours = [round(sum(study_hours), 2) for study_hours in studied_by_date]


        # Convert date objects to numeric values
        x = mpl_dates.date2num(dates)

        # Create a custom date formatter
        date_format = mpl_dates.DateFormatter("(%a) %d-%b")

        # Create a subplot for the bar chart
        ax = self.bars_figure.add_subplot(111)

        '''figure styling'''
        ax.set_facecolor('#2C343C')
        ax.grid(color='lightgray', alpha=0.2, linewidth=0.5)
        # Set title
        ax.set_title("Study Hours Over Time\n", color="white", fontsize=12, fontweight='bold')
        # Set x-axis label color
        ax.xaxis.label.set_color('white')  # Set the color to white or any desired color

        # Set y-axis label color
        ax.yaxis.label.set_color('white')  # Set the color to white or any desired color


        # Adjust subplot parameters for better layout
        self.bars_figure.subplots_adjust(bottom=0.15)

        # Create the bar chart
        ax.bar(x, total_studied_hours, color='#ef5959', edgecolor='#e32d2d', linewidth=2, alpha=0.9)

        # Set the x-axis label format
        ax.xaxis.set_major_formatter(date_format)
        # Rotate the x-axis date labels for better readability (e.g., 45 degrees)
        ax.tick_params(axis='x', rotation=45)

        # Setting header for each bar (TOTAL HOURS)
        for i , (_, hour) in enumerate(zip(dates, total_studied_hours)):
            # place text only if user have studied that day
            if hour != 0 : 
                ax.annotate(f'{hour} H', (dates[i], total_studied_hours[i]), textcoords="offset points", xytext=(0, 5), ha='center', fontweight='bold', color="white", fontsize=12)


        # Disable showing previous week if the first day date is in dates list
        first_day_date = datetime.strptime(self.first_day, "%Y-%m-%d").date()
        if first_day_date in dates:
            self.mw.leftWeekButton.setEnabled(False)
        else:
            self.mw.leftWeekButton.setEnabled(True)

        # Disable showing next week if today's date in dates list
        if (datetime.now().date()) in dates:
            self.mw.rightWeekButton.setEnabled(False)
        else:
            self.mw.rightWeekButton.setEnabled(True)



        plt.style.use("ggplot")
        # Refresh the canvas
        self.bars_canvas.draw()


    def bars_chart_graph_2(self, chosen_day):

        #Test 
        self.total_hours_per_day = self.get_daily_study_hours()

        self.current_bar_graph = "bar2"
        # Clear earlier figure
        self.bars_figure.clear()

        self.mw.barChartWidget.layout().addWidget(self.bars_canvas)

        # today_date = datetime.now().date()
        week_days = 7

        # Generate a list of dates
        dates = [chosen_day - timedelta(days=i) for i in range(week_days)]

        # Convert date objects to numeric values
        x = mpl_dates.date2num(dates)

        # Get studied hours of each day in 1 week
        studied_by_date = [self.get_studied_hours_by_date(x) for x in dates]


        # Get total studied hours in 1 week
        total_studied_hours = [round(sum(study_hours), 2) for study_hours in studied_by_date]


        # Create a subplot for the bar chart
        ax1 = self.bars_figure.add_subplot(111)

        '''figure styling'''
        ax1.set_facecolor('#2C343C')
        ax1.grid(color='lightgray', alpha=0.2, linewidth=0.5)
        # Set title
        ax1.set_title("Study Percentage Over Time\n", color="white", fontsize=12, fontweight='bold')
        
        # Set x-axis label color
        ax1.xaxis.label.set_color('white')  # Set the color to white or any desired color

        # Set y-axis label color
        ax1.yaxis.label.set_color('white')  # Set the color to white or any desired color


        # Adjust subplot parameters for better layout
        self.bars_figure.subplots_adjust(bottom=0.15)


        # Create a custom date formatter
        date_format = mpl_dates.DateFormatter("(%a) %d-%b")

        # Adjust subplot parameters for better layout
        self.bars_figure.subplots_adjust(bottom=0.15)

        # Set the x-axis label format
        ax1.xaxis.set_major_formatter(date_format)
        # Rotate the x-axis date labels for better readability (e.g., 45 degrees)
        ax1.tick_params(axis='x', rotation=45)


        # Calculate remaining hours and percentage completion
        remaining_hours = [max(0, total - studied) for total, studied in zip(self.total_hours_per_day, total_studied_hours)]
        percentage_completion = [0 if total==0 else (studied / total) * 100 for studied, total in zip(total_studied_hours, self.total_hours_per_day)]

        bars_studied = ax1.bar(x, total_studied_hours, color='#ef5959', edgecolor='#e32d2d', linewidth=2, alpha=0.9)
        ax1.bar(x, remaining_hours, bottom=total_studied_hours, color='lightgrey', alpha=0.1, linewidth=5, edgecolor='black', linestyle='dashed')

        # Adding percentage labels on top of the bars
        for bar, percent in zip(bars_studied, percentage_completion):
            if percent != 0: 
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width() / 2, height, f'{percent:.1f}%', ha='center', va='bottom', fontweight='bold', color="white", fontsize=12)

        # Disable showing previous week if the first day date is in dates list
        first_day_date = datetime.strptime(self.first_day, "%Y-%m-%d").date()
        if first_day_date in dates:
            self.mw.leftWeekButton.setEnabled(False)
        else:
            self.mw.leftWeekButton.setEnabled(True)

        # Disable showing next week if today's date in dates list
        if (datetime.now().date()) in dates:
            self.mw.rightWeekButton.setEnabled(False)
        else:
            self.mw.rightWeekButton.setEnabled(True)



        plt.style.use("ggplot")

        # Refresh the canvas
        self.bars_canvas.draw()


    def pie_chart_graph(self, total_subject_hours):
        subjects = list(total_subject_hours.keys()) 
        studied_hours_data = list(total_subject_hours.values())
        total_studied_hours = sum(studied_hours_data)
        
        # Pie chart layout
        layout = self.mw.pieChartWidget2.layout()

        # Create a matplotlib figure only if total_studied_hours is not zero
        if total_studied_hours != 0:
            # Remove the 'haven't studied yet label' if he have studied.
            try:
                layout.removeWidget(self.mw.noStudyLabel)
                self.mw.noStudyLabel.deleteLater()
            except:
                pass

            # Create a Matplotlib figure
            if len(self.mw.pieChartWidget2.layout()) !=29:
                self.mw.pieChartWidget2.layout().addWidget(self.pie_canvas)

            # Clearing the last graph to start fresh
            self.pie_figure.clear()

            # self.pie_figure.set_facecolor('#ff0000')  

            # create an axis
            ax = self.pie_figure.add_subplot(111)
            # Adjust subplot parameters for better layout
            self.pie_figure.subplots_adjust(bottom=0.50)  # You can adjust the top value accordingly

            # Setting the pie chart graph
            handles = ax.pie(studied_hours_data, autopct="%1.1f%%", wedgeprops={'edgecolor': 'white'}, colors=sns.color_palette('Set2'))            # Setting the pie chart legend
            studied_hours_percentages_data = [p / total_studied_hours * 100 for p in studied_hours_data]
            studied_hours_percentages_data_formatted = self.round_numbers(studied_hours_percentages_data)

            studied_hours_data_formatted = self.round_numbers(studied_hours_data)
            # here you re-order everything including handle color, subject, percentage
            studied_subjects = list(zip(handles[0], subjects, studied_hours_percentages_data_formatted, studied_hours_data_formatted))
            sorted_studied_subjects = sorted(studied_subjects, key= lambda pair: pair[3], reverse= True)
            sorted_colors = [item[0] for item in sorted_studied_subjects]
            subjects_legend = [item[1] for item in sorted_studied_subjects]
            percentage_legend = [item[2] for item in sorted_studied_subjects]
            hours_legend = [item[3] for item in sorted_studied_subjects]
            total_hours = f"TOTAL :{round(sum(hours_legend), 1)} h"
            legend_labels = [f'{s} {p}% || {h}h' for s, p, h in zip(subjects_legend, percentage_legend, hours_legend)]
            ax.legend(handles=sorted_colors, bbox_to_anchor=(0.5, 0) ,loc='upper center', labels=legend_labels, title=total_hours, fontsize=12)

            # Title of the pie chart graph
            ax.set_title("Study Hours Distribution\n", color="white", fontsize=12, fontweight='bold', y=1.02)

            # refresh canvas
            self.pie_canvas.draw()

        else:
            return
    
    def round_numbers(self, numbers_list):
        return [round(p, 1) for p in numbers_list]



    def save_bar_graph(self):
        # Ask the user for the file path to save the PNG
        file_path, _ = QFileDialog.getSaveFileName(self, 'Save Bar Graph', '', 'PNG Files (*.png)')

        if file_path:
            # Save the figure to the specified file path
            self.bars_figure.savefig(file_path)

    def show_today_data(self):
        print('showing todays data')

    def show_overall_data(self):
        print('showing overall data')


    def show_previous_week(self):
        self.current_week -= timedelta(weeks = 1)
        if self.current_bar_graph == "bar1":
            self.bars_chart_graph(self.current_week)
        else:
            self.bars_chart_graph_2(self.current_week)

    def show_next_week(self):
        self.current_week += timedelta(weeks = 1)
        if self.current_bar_graph == "bar1":
            self.bars_chart_graph(self.current_week)
        else:
            self.bars_chart_graph_2(self.current_week)

    def get_daily_study_hours(self):
        ''''this treat the how many hours i must study per day'''
        query_check = "SELECT * FROM daily_study_hours"
        daily_study_hours = self.db.fetch_data(query_check,)

        hours_per_day = {'Sun': 0, 'Mon': 0, 'Tue': 0, 'Wed': 0, 'Thu' :0, 'Fri' :0, 'Sat': 0}
        for day, hours  in zip(hours_per_day, daily_study_hours):
            hours_per_day[day] = hours

        # Get the current day of the week (e.g., 'Mon')
        current_day = datetime.now().strftime('%a')

        # Create a new dictionary with the specified logic
        ordered_hours_per_day = {current_day: hours_per_day[current_day]}
        for i in range(6):
                previous_day = (datetime.now() - timedelta(days=i + 1)).strftime('%a')
                ordered_hours_per_day[previous_day] = hours_per_day[previous_day]

        ordered_hours_per_day = list(ordered_hours_per_day.values())

        return ordered_hours_per_day


    def get_studied_hours_by_date(self, date):
        query_check = "SELECT * FROM subject_record WHERE date = ?"
        studied_hours_row = self.db.fetch_data(query_check, (date,))

        if not studied_hours_row :
            self.mw.insert_new_hours_row(date)

        query_fetch = "SELECT * FROM subject_record WHERE date = ?"
        studied_hours_row = self.db.fetch_data(query_fetch, (date,))

        studied_hours_row = list(studied_hours_row)
        studied_hours_row.pop(0)

        return studied_hours_row


    def get_first_day(self):
        query = "SELECT date FROM first_day_date"
        return self.db.fetch_data(query)[0]
        