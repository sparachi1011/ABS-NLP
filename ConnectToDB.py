# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 15:15:19 2019

@author: dnathani
"""
import pyodbc

from config import DRIVER, SERVER_NAME, DATABASE, USERNAME, PASSWORD


def get_db_connection():
    try:
        db_connection = pyodbc.connect('DRIVER='+DRIVER+';SERVER='+SERVER_NAME+';PORT=1433;DATABASE='+DATABASE+';UID='+USERNAME+';PWD='+ PASSWORD)
        return db_connection
    except Exception as e:
        print("Error in connecting to DB.")
        return "There is some error"

import contextlib

def bulk_insert(table_name='[dbo].[NLP_PredictedClasses]', file_path=r'D:\Users\dnathani\Desktop\Runtime\ABS\NLP\NLP_Rev1\PredictedClasses.csv'):
    pyodbc.connect('DRIVER='+DRIVER+';SERVER='+SERVER_NAME+';PORT=1433;DATABASE='+DATABASE+';UID='+USERNAME+';PWD='+ PASSWORD)
    string = "BULK INSERT {} FROM '{}' (WITH FORMAT = 'CSV');"
    with contextlib.closing(pyodbc.connect("MYCONN")) as conn:
        with contextlib.closing(conn.cursor()) as cursor:
            cursor.execute(string.format(table_name, file_path))
        conn.commit()
        conn.close()
