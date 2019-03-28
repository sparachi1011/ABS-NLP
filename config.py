# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 15:14:46 2019

@author: dnathani
"""
###############################################
# DB Details
###############################################

DRIVER = '{ODBC Driver 17 for SQL Server}'#'{ODBC Driver 13 for SQL Server}'
PORT=1433

SERVER_NAME = 'abs-asql.database.windows.net'
DATABASE = 'abs-sqldb-offshore_Copy'
USERNAME = 'absadmin@abs-asql'
PASSWORD = 'P@ssword1234'
SCHEMA =   'dbo'

###############################################
# Blob Details
###############################################

account_name='devabsstorage'
account_key='mh2TfKV6KzLHxHE3FfRcFb+UO/L7/E7c7M6LoQrfF8AcRkwk2QSwEz0AS6zq1YKm9mSDKLdnkWmqtW/NGCGpMQ=='
container_name='nlp-landing'