from typing import Any
import mysql.connector
import psycopg2
import sqlite3  
# import locale

  
class MySQLDatabase:  
    def __init__(self, host, username, password, database, port, sslmode, time_out=30):  
        self.host = host  
        self.username = username  
        self.password = password  
        self.database = database
        self.port = port
        self.sslmode = sslmode
        self.time_out = time_out  
        self.conn = None  
  
    def connect(self):  
        try:  
            self.conn = psycopg2.connect(  
                host=self.host,  
                user=self.username,  
                password=self.password,  
                database=self.database,
                port = self.port  
            )  
            # print("Connected to MySQL database")  
        except psycopg2.DatabaseError as e:  
            # print(f"Error connecting to MySQL database: {e}") 
            self.conn = None  
  
    def close(self):  
        if self.conn is not None:  
            self.conn.close()  
            # print("Connection to MySQL database closed")  
  
    def query(self, sql):  
        cursor = self.conn.cursor()  
        try:
            cursor.execute(sql)  
            result = cursor.fetchall()

            # Get column names from cursor.description
            column_names = [column[0].upper() for column in cursor.description] 

        except Exception as e:
            print(e)
            result = [(0,)]  
            column_names = ['RESULT']

        

        # Define a function to format numeric values
        def format_numeric(value):
            if isinstance(value, (int, float)):
                form_value = f'{value:,.2f}'
                form_value = form_value.replace('.', '|')
                form_value = form_value.replace(',', '.')
                form_value = form_value.replace('|', ',')
                return form_value
            return value

        # Format the float values in the result set
        formatted_result = [
            tuple(format_numeric(value) for value in row)
            for row in result
        ]

        print(formatted_result)

        cursor.close()  
        return formatted_result, column_names  
    

class MyLocalSQL:
    def __init__(self, db_name) -> None:
        self.db_name = db_name
        self.conn = None 

    def connect(self):
        try:
            # Connect to the SQLite database  
            self.conn = sqlite3.connect('my_local_database.db')

        except mysql.connector.Error as e:
            self.conn = None
            

    def close(self):
        if self.conn is not None:
            self.conn.close()
    
    def query(self, query):

        # Set the locale to Brazilian Portuguese
        # locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')

        # Create a cursor object to execute SQL queries  
        cursor = self.conn.cursor()

        # Execute the query and fetch the results  
        cursor.execute(query)  
        result = cursor.fetchall() 

        # Get column names from cursor.description
        column_names = [column[0] for column in cursor.description] 

        # Define a function to format numeric values
        def format_numeric(value):
            if isinstance(value, (int, float)):
                return "{:.2f}".format(value)
            return value

        # Format the float values in the result set
        formatted_result = [
            tuple(format_numeric(value) for value in row)
            for row in result
        ]
    
        # Close the cursor and connection  
        cursor.close()

        return formatted_result, column_names


        
