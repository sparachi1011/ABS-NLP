# -*- coding: utf-8 -*-
"""
Created on Thu Feb 21 11:52:47 2019

@author: dnathani
"""

from azure.storage.blob import BlockBlobService
from config import *
import datetime

def downloadFile(fileName):
    try:
        #today = str(datetime.date.today()).split("-")
        #fileName='NLP_'+today[1]+str(int(today[2])-1)+today[0]+'.csv'
        block_blob_service = BlockBlobService(account_name=account_name, account_key=account_key)
        full_path_to_file2 = './DownloadFile/'+fileName
        block_blob_service.get_blob_to_path('nlp-landing', fileName, full_path_to_file2)
        return full_path_to_file2
    except Exception as e:
        return "File Not Found: "+str(e)

def uploadFile(fileName):
        block_blob_service = BlockBlobService(account_name=account_name, account_key=account_key)
        full_path_to_file2 = './'+fileName
        block_blob_service.get_blob_to_path('nlp-landing', fileName, full_path_to_file2)
        block_blob_service.create_blob_from_path('nlp-landing', fileName, full_path_to_file2)
        print("Uploaded Successfully")