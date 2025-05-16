import sqlite3
import sys 
import os
import shutil
from PyQt5.QtWidgets import QMessageBox

class DatabaseManager:
    def __init__(self):
        self.database_filename = 'save_atom.db'
        self.documents_folder = os.path.expanduser('~/Documents')
        self.database_path_initial = os.path.join(os.path.dirname(sys.argv[0]), self.database_filename)
        self.database_path_final = os.path.join(self.documents_folder, self.database_filename)

        self.move_file_if_needed()
        self.connect_to_file()


    def connect_to_file(self):
        try:
            self.conn = sqlite3.connect(self.database_path_final)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Error connecting to the database: {e}")
            sys.exit(1)  # Exit the application on a database connection error

    def move_file_if_needed(self):
        if not os.path.exists(self.database_path_final):
            try:
                shutil.move(self.database_path_initial, self.database_path_final)
            except Exception as e:
                print(f"Error moving the database file: {e}")



    def _handle_query_error(self):
        QMessageBox.warning(None, "ERROR 306", "Something went wrong with fetching data")

    def fetch_data(self, query, params=None):
        try:
            if params is None:
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, params)

            result = self.cursor.fetchone()

            # If no data is found, return an empty list
            return [] if result is None else result
        
        except sqlite3.Error as e:
            print(e)
            self._handle_query_error()
    
    def fetch_all_data(self, query, params=None): 
        try:
            if params is None:
                self.cursor.execute(query)
            else:
                self.cursor.execute(query, params)
                
            return self.cursor.fetchall()
        
        except sqlite3.Error as e:
            print(e)
            self._handle_query_error()
    

    def insert_data(self, query, params=None):
        if params is None:
            self.cursor.execute(query)
            self.conn.commit()
        else:
            try:
                self.cursor.execute(query, params)
                self.conn.commit()
            except Exception as e:
                print(f'Error executing query: {e}')

    def delete_data(self, query, params=None):
        try:
            if params is None:
                self.cursor.execute(query)
                self.conn.commit()
            else:
                self.cursor.execute(query, params)
                self.conn.commit()
        except sqlite3.Error as e:
            print(e)
            self._handle_query_error()

    def close_connection(self):
        self.cursor.close()
        self.conn.close()