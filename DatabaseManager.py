import urllib.parse
import pyodbc
from sqlalchemy import create_engine
import pandas as pd
import os


class DatabaseManager:
    def __init__(self):
        self.driver = self.find_sql_server_driver()
        self.server = os.environ.get('DATABASE_SERVER')
        self.database = os.environ.get('DATABASE_NAME')
        self.username = os.environ.get('DATABASE_USERNAME')
        self.password = os.environ.get('DATABASE_PASSWORD')
        self.connection_string = f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password}'
        self.sqlalchemy_connection_string = f"mssql+pyodbc://{self.username}:{self.password}@{self.server}/{self.database}?driver={urllib.parse.quote(self.driver)}"
        self.connection = None
        
    def reset(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            
    def create_connection(self):
        self.connection = pyodbc.connect(self.connection_string)
        
    def find_sql_server_driver(self):
        for driver in pyodbc.drivers():
            if driver.__contains__('ODBC'):
                return driver
            else:
                driver = 'ODBC Driver 17 for SQL Server'

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
    
    def create_db_engine(self):
        return create_engine(self.sqlalchemy_connection_string)
    
    def destroy_db_engine(self, db_engine):
        db_engine.dispose()

    def execute_query(self, query, *args):
        self.create_connection()
        cursor = self.connection.cursor()
        cursor.execute(query, *args)
        results = cursor.fetchall()
        cursor.close()
        return results

    def execute_non_query(self, query, *args):
        self.create_connection()
        cursor = self.connection.cursor()
        cursor.execute(query, *args)
        self.connection.commit()
        cursor.close()

    def execute_query_single_val(self, query, *args):
        self.create_connection()
        cursor = self.connection.cursor()
        cursor.execute(query, *args)
        results = cursor.fetchval()
        cursor.close()
        return results
    
    def insert_podcast(self, podcast, title, url, transcript):
        self.create_connection()
        cursor = self.connection.cursor()
        cursor.execute('INSERT INTO dbo.Podcasts (Podcast, Title, URL, Transcript) VALUES (?, ?, ?, ?)', podcast, title, url, transcript)
        self.connection.commit()
        cursor.close()