# import mysql.connector
import sqlite3
import datetime
import requests
import json 

now = datetime.datetime.utcnow()
utctime = (now.strftime("%Y-%m-%d %H:%M:%S"))

DROP_TABLE_NODEDETAILS_IF_EXIST_QUERY = "DROP TABLE IF EXISTS node_details"
DROP_TABLE_NODECONFIG_IF_EXIST_QUERY = "DROP TABLE IF EXISTS node_config"
CREATE_NODEDETAILS_TABLE_QUERY = """CREATE TABLE node_details (
    NetworkID TEXT,
    NodeID TEXT,
    ServiceID  TEXT,
    SystemID TEXT, 
    AreaID TEXT,
    NodeType TEXT,
    Status TEXT,
    NodeName TEXT,
    postal_code TEXT,
    BuildingName TEXT,
    BuildingLevel TEXT,
    SectorName TEXT,
    ApplicationCode TEXT,
    ApplicationName TEXT
)"""
CREATE_NODECONFIG_TABLE_QUERY = """CREATE TABLE node_config (
    AreaID TEXT,
    NodeType TEXT,
    Config  TEXT,
    ConfigName TEXT, 
    Measurement TEXT,
    UnitOfMeasurement TEXT
)"""
INSERT_DATA_NODEDETAILS_TABLE_QUERY = """
    INSERT INTO node_details(NetworkID,NodeID,ServiceID,SystemID,AreaID,NodeType,Status,NodeName,postal_code,BuildingName,BuildingLevel,SectorName,ApplicationCode,ApplicationName)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
"""
INSERT_DATA_NODECONFIG_TABLE_QUERY = """
    INSERT INTO node_config(AreaID,NodeType,Config,ConfigName,Measurement,UnitOfMeasurement)
    VALUES (?,?,?,?,?,?)
"""

def executeSqliteQueryByTable(sqlite_cursor, DROPQUERY, CREATETABLEQUERY, INSERTQUERY, DATALIST):
    
    sqlite_cursor.execute(DROPQUERY)
    sqlite_cursor.execute(CREATETABLEQUERY)
    sqlite_cursor.executemany(INSERTQUERY, DATALIST)
    
    recordString = '{utctime} | Success query'.format(
                                    utctime=utctime
                                )
    print(recordString) 

def printTotalRowsByTable(table, rowcount):
    
    recordString = '{utctime} | Total number of rows in table {table}: ", {rowcount}'.format(
                                    utctime=utctime,
                                    rowcount=rowcount,
                                    table=table
                                )
    print(recordString)

try:
    fileArray = []
    with open('/home/smart/wirepas/network') as file:
        for line in file:
            fileArray.append(line.strip('\n'))

    networkid = fileArray[0]
    res = requests.get('https://mapi-ljdigitalsmart.com/api/get-gateway-data/' + networkid)
    jsonData = res.json()
    nodeList = jsonData['nodeList']
    configList = jsonData['configList']
    configListValues = []
    nodeListValues = []
    for key in configList:
        configListValues.append(list(key.values()))

    for key in nodeList:
        nodeListValues.append(list(key.values()))

    printTotalRowsByTable('node details', len(jsonData['nodeList']))
    printTotalRowsByTable('node config', len(jsonData['configList']))
    DB_NAME = "/home/smart/wirepas/mqttdb"
    sqlite_connection = sqlite3.connect(DB_NAME)
    sqlite_cursor = sqlite_connection.cursor()
    # print(nodeList)
    executeSqliteQueryByTable(sqlite_cursor, DROP_TABLE_NODEDETAILS_IF_EXIST_QUERY, CREATE_NODEDETAILS_TABLE_QUERY, INSERT_DATA_NODEDETAILS_TABLE_QUERY, nodeListValues)
    executeSqliteQueryByTable(sqlite_cursor, DROP_TABLE_NODECONFIG_IF_EXIST_QUERY, CREATE_NODECONFIG_TABLE_QUERY, INSERT_DATA_NODECONFIG_TABLE_QUERY, configListValues)


except sqlite3.Error as e:
    print(utctime, "Error reading data from SQLite3 table", e)
finally:
    sqlite_connection.close()
    recordString = '{utctime} | SQLite3 connection is closed'.format( utctime=utctime  )
    print(recordString)
    print("==============================================")
# print(response)
