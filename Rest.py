# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 11:45:13 2019

@author: dnathani
"""

import json
import logging
import os

import pandas as pd
from flask import Flask
from flask import Response
from flask import request
from flask_cors import CORS

import NLP_deploy_0
from ConnectBlob import downloadFile
from ConnectToDB import get_db_connection

###############################################################################
# Flask Configuration
###############################################################################

app = Flask(__name__, static_url_path="", static_folder="static")
CORS(app)
app.secret_key = os.urandom(24)

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.DEBUG)


#######################################################################
# TAKING INPUT FOR PROCESSING FROM DB
#######################################################################
def readInputData(cursor):
    try:

        query = "SELECT * FROM PredictedClasses"
        cursor.execute(query)
        row = cursor.fetchall()
        combined_corpus_binary_test, vesselName, vesselID, equipName, equipID, IDs = [
                                                                                         'Maintenance Details. Additional Maintenance Details'], [
                                                                                         'Vessel Name'], [
                                                                                         'Vessel ID'], [
                                                                                         'Equipment Name'], [
                                                                                         'Equipment ID'], []
        for data in row:
            combined_corpus_binary_test.append(data[0])
            vesselName.append(data[6])
            vesselID.append(data[7])
            equipName.append(data[8])
            equipID.append(data[9])
            IDs.append(data[11])
        return combined_corpus_binary_test, vesselName, vesselID, equipName, equipID, IDs
    except:
        raise Exception("There was error while processing your data, Please reupload your file.")


def storeJSONResults(cursor, results, ActivityId):
    try:
        jsonData = []
        for data in results:
            temp = []
            for content in data:
                temp.append(str(content))
            temp.append(ActivityId)
            jsonData.append({
                "data": {"MaintenanceDetails": temp[0],
                         "Algorithm1": temp[1],
                         "Algorithm1Probability": temp[2],
                         "Algorithm2": temp[3],
                         "Algorithm2Probability": temp[4],
                         "FinalClassLabel": temp[5],
                         "VesselName": temp[6],
                         "VesselID": temp[7],
                         "EquipmentName": temp[8],
                         "EquipmentID": temp[9],
                         "ActivityId": temp[10]}})

        jsonData = json.dumps(jsonData)
        query = '''
    INSERT INTO [dbo].[NLP_PredictedClasses]  ([MaintenanceDetails],[Algorithm1],[Algorithm1Probability],[Algorithm2],[Algorithm2Probability],[FinalClassLabel],[VesselName],[VesselID],[EquipmentName],[EquipmentID],[ActivityId])
    SELECT *  
    FROM OPENJSON ({})    
    	WITH (  
                  MaintenanceDetails    varchar(max) N'$.data.MaintenanceDetails',   
                  Algorithm1  varchar(max) N'$.data.Algorithm1',
                  Algorithm1Probability    varchar(max) N'$.data.Algorithm1Probability',   
                  Algorithm2  varchar(max) N'$.data.Algorithm2',
                  Algorithm2Probability    varchar(max) N'$.data.Algorithm2Probability',   
                  FinalClassLabel  varchar(max) N'$.data.FinalClassLabel',
                  VesselName    varchar(max) N'$.data.VesselName',   
                  VesselID    varchar(max) N'$.data.VesselID',   
                  EquipmentName  varchar(max) N'$.data.EquipmentName',
                  EquipmentID    varchar(max) N'$.data.EquipmentID', 
                  ActivityId  int N'$.data.ActivityId'
               )  
      AS SalesOrderJsonData;
    '''.format('''N'{}'
                '''.format(jsonData))
        # print(query)
        cursor.execute(query)
        cursor.commit()
    except:
        raise Exception("There was error while processing your data, Please reupload your file.")


#######################################################################
# STORING PROCESSED DATA
#######################################################################      

def storeResults(cursor, results, ActivityId):
    try:
        counter = 0
        finalRes = []
        for data in results:
            temp = []
            for content in data:
                temp.append(str(content))
            temp.append(ActivityId)
            finalRes.append(tuple(temp))
            # query="UPDATE [dbo].[PredictedClasses] SET Algorithm1='"+temp[1]+"', Algorithm1Probability='"+temp[2]+"',Algorithm2='"+temp[3]+"', Algorithm2Probability='"+temp[4]+"',FinalClassLabel='"+temp[5]+"' WHERE IncidenceID= "+str(IDs[counter])+";"
            # query="INSERT INTO PredictedClasses ([MaintenanceDetails],[Algorithm1],[Algorithm1Probability],[Algorithm2],[Algorithm2Probability],[FinalClassLabel],[VesselName],[VesselID],[EquipmentName],[EquipmentID],[ActivityId]) values ('"+temp[0]+"','"+temp[1]+"','"+temp[2]+"','"+temp[3]+"','"+temp[4]+"','"+temp[5]+"','"+temp[6]+"','"+temp[7]+"','"+temp[8]+"','"+temp[9]+"',"+str(ActivityId)+")"
            # query=

            cursor.executemany(
                'INSERT INTO [NLP_PredictedClasses] ([MaintenanceDetails],[Algorithm1],[Algorithm1Probability],[Algorithm2],[Algorithm2Probability],[FinalClassLabel],[VesselName],[VesselID],[EquipmentName],[EquipmentID],[ActivityId]) VALUES (?, ?, ?,?, ?, ?,?, ?, ?,?, ?)',
                finalRes)
            cursor.commit()
            counter += 1
    except:
        raise Exception("There was error while processing your data, Please reupload your file.")


def updateActivity(cursor, ActivityId, FailureProb, NonFailureProb):
    try:
        query = "UPDATE [dbo].[NLP_Activity] SET Status='Completed', FailureProb=" + str(
            FailureProb) + ", NonFailureProb=" + str(NonFailureProb) + "WHERE ActivityId= '" + str(ActivityId) + "';"
        cursor.execute(query)
        cursor.commit()
    except:
        raise Exception("There was error while processing your data, Please reupload your file.")


def getActivityId(cursor, fileName):
    try:
        query = "SELECT ActivityId From [dbo].[NLP_Activity] WHERE InternalFileName='" + fileName + "';"
        cursor.execute(query)
        return cursor.fetchall()[0][0]
    except:
        raise Exception("There was error while processing your data, Please reupload your file.")


#######################################################################
# RUNNING NLP ALGORITHM
#######################################################################
def runNlp(filePath):
    try:
        NLP_deploy_0.runAll(filePath)
    except Exception as e:
        logging.error(e)
        raise Exception("Please upload a valid csv file.")


def getResults():
    try:
        df = pd.read_csv('PredictedClasses.csv')
        resultClass = df['Final Class Label'].tolist()
        FailureProb = int((resultClass.count('Failures') / len(resultClass)) * 100)
        NonFailureProb = 100 - FailureProb
        results = df.values.tolist()
        return results, FailureProb, NonFailureProb
    except:
        raise Exception("There was error while processing your data, Please reupload your file.")


def generate_json(results):
    """
    returns json dictionary
    """
    try:
        return json.dumps(
            [{"Classification": result[5],
              "MaintenanceDetails": result[0],
              "Vessel": result[6],
              "EquipmentId": result[9],
              "Equipment": result[8],
              "Probability": result[2]} for result in results])
    except:
        raise Exception("There was error while processing your data, Please reupload your file.")


def get_details(cursor, guid):
    try:
        query = f"SELECT ActivityId, InternalFileName From [dbo].[NLP_Activity] WHERE guid='{str(guid)}'"
        cursor.execute(query)
        record_set = cursor.fetchall()
        if not record_set:
            logging.error(f"No Activity found for GUID '{str(guid)}'")
            raise ValueError('Invalid Identifier')
        return record_set[0][0], record_set[0][1]
    except:
        raise Exception("There was error while processing your data, Please reupload your file.")


###############################################################################
# Rest API's
###############################################################################

@app.route('/runnlp')
def controller_ExecuteNLP():
    """
        controller for NLP
    """
    try:
        cursor = get_db_connection().cursor()
        file_id = request.args.get('id')
        activity_id, blob_file_name = get_details(cursor, file_id)
        logging.info('Downloading Blob')
        path = downloadFile(blob_file_name)
        logging.info('Starting NLP Run')
        runNlp(path)
        logging.info('Storing Results')
        results, FailureProb, NonFailureProb = getResults()
        storeJSONResults(cursor, results, activity_id)
        logging.info('Done Storing Results')
        updateActivity(cursor, activity_id, FailureProb, NonFailureProb)
        cursor.close()
        response = json.dumps({
            'status': 'success',
            'activity_id': activity_id
        })
        return Response(response, status=200, mimetype='application/json')
    except Exception as err:
        msg = str(err)
        print(msg)
        return Response(msg, status=500, mimetype='text/plain')


#
# if __name__ == '__main__':
#     Strating Server
#     app.run('0.0.0.0', 1307)
