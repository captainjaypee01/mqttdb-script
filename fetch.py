# import mysql.connector
import sqlite3
import datetime
import requests
import json 
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

def read_aes_key_from_file(file_path):
    with open(file_path, 'r') as file:
        aes_key_hex = file.read().strip()
    aes_key_bytes = bytes.fromhex(aes_key_hex)
    return aes_key_bytes

def decrypt_file(input_file, key):
    cipher = AES.new(key, AES.MODE_ECB)
    with open(input_file, 'rb') as file:
        encoded_ciphertext = file.read()

    ciphertext = base64.b64decode(encoded_ciphertext)
    decrypted_data = cipher.decrypt(ciphertext)
    plaintext = unpad(decrypted_data, AES.block_size)
    plaintext_lines = plaintext.decode().splitlines()

    if len(plaintext_lines) == 2:
        networkid = plaintext_lines[0]
        sinkid = plaintext_lines[1]
        return networkid, sinkid
    else:
        raise ValueError("Invalid number of lines in the decrypted file.")

CURRENT_ENV = 'LOCAL'
API_ENV = 'POC'
now = datetime.datetime.utcnow()
utctime = (now.strftime("%Y-%m-%d %H:%M:%S"))

DROP_TABLE_NODEDETAILS_IF_EXIST_QUERY = "DROP TABLE IF EXISTS node_details"
DROP_TABLE_NODECONFIG_IF_EXIST_QUERY = "DROP TABLE IF EXISTS node_config"
DROP_TABLE_GATEWAYS_IF_EXIST_QUERY = "DROP TABLE IF EXISTS gateways"
CREATE_NODEDETAILS_TABLE_QUERY = """CREATE TABLE node_details (
    NetworkID TEXT,
    NodeID TEXT,
    ServiceID  TEXT,
    SystemID TEXT, 
    AreaID TEXT,
    Config TEXT,
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
CREATE_GATEWAY_TABLE_QUERY = """CREATE TABLE gateways (
    NetworkID TEXT,
    SinkID TEXT,
    gateway_name TEXT,
    location TEXT
)"""
INSERT_DATA_NODEDETAILS_TABLE_QUERY = """
    INSERT INTO node_details(NetworkID,NodeID,ServiceID,SystemID,AreaID,Config,NodeType,Status,NodeName,postal_code,BuildingName,BuildingLevel,SectorName,ApplicationCode,ApplicationName)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
"""
INSERT_DATA_NODECONFIG_TABLE_QUERY = """
    INSERT INTO node_config(AreaID,NodeType,Config,ConfigName,Measurement,UnitOfMeasurement)
    VALUES (?,?,?,?,?,?)
"""
INSERT_DATA_GATEWAYS_TABLE_QUERY = """
    INSERT INTO gateways(NetworkID,SinkID,gateway_name,location)
    VALUES (?,?,?,?)
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


API_URL = {
    'POC': 'https://mapi-ljdigitalsmart.com/api/get-gateway-data/',
    'AZURE': 'https://ljd-az-api01.southeastasia.cloudapp.azure.com/api/get-gateway-data/',
}

env_api_url = {
    'PROD': API_URL[API_ENV],
    'UAT': 'https://192.168.3.154/api/get-gateway-data/',
    'LOCAL': 'http://localhost:9091/api/get-gateway-data/' 
}
env_apikey_url = {
    'PROD': '/boot/wirepas/api_key',
    'UAT': '/boot/wirepas/api_key',
    'LOCAL': 'api_key' 
}
env_db_name = {
    'PROD': "/home/smart/wirepas/database/mqttdb",
    'UAT': "/home/smart/wirepas/database/mqttdb",
    'LOCAL': 'mqttdb'
}
env_aes_file = {
    "LOCAL": "aes-key",
    "UAT": '/boot/wirepas/aes-key',
    "PROD": '/boot/wirepas/aes-key',
}
env_network_file = {
    "LOCAL": "network.bin",
    "UAT": '/home/smart/wirepas/network.bin',
    "PROD": '/home/smart/wirepas/network.bin'
}

DB_NAME = env_db_name[CURRENT_ENV]
sqlite_connection = sqlite3.connect(DB_NAME)
try:
            
    apiFile = []
    with open(env_apikey_url[CURRENT_ENV]) as file:
        for line in file:
            apiFile.append(line.strip('\n'))

    aes_file = env_aes_file[CURRENT_ENV]
    input_file = env_network_file[CURRENT_ENV]
    key = read_aes_key_from_file(aes_file)
    networkid, sinkid = decrypt_file(input_file, key)
    app_key = apiFile[0]
    data = {'app_key': app_key, 'access_name': 'smart_gateway_' + networkid, 'sink': sinkid}
    
    api_url = env_api_url[CURRENT_ENV] + networkid
    
    res = requests.get(api_url, params = data)
    
    print(res.status_code)
    if(res.status_code == 401):
        print(utctime + " | Unauthorized | " + api_url)
        exit()
    if(res.status_code == 403):
        print(utctime + " | Forbidden | " + api_url)
        exit()
        
    if(res.status_code == 500):
        print(utctime + " | Server Error | " + api_url)
        exit()

    if(res.status_code == 404):
        print(utctime + " | Not Found | " + api_url)
        exit()

    jsonData = res.json()
    nodeList = jsonData['nodeList']
    configList = jsonData['configList']
    gatewayList = jsonData.get('gatewayList', [])
    configListValues = []
    nodeListValues = []
    gatewayListValues = []
    for key in configList:
        configListValues.append(list(key.values()))

    for key in nodeList:
        nodeListValues.append(list(key.values()))

    for key in gatewayList:
        gatewayListValues.append(list(key.values()))

    printTotalRowsByTable('node details', len(jsonData['nodeList']))
    printTotalRowsByTable('node config', len(jsonData['configList']))
    printTotalRowsByTable('gateways', len(gatewayList))

    sqlite_cursor = sqlite_connection.cursor()
    
    executeSqliteQueryByTable(sqlite_cursor, DROP_TABLE_NODEDETAILS_IF_EXIST_QUERY, CREATE_NODEDETAILS_TABLE_QUERY, INSERT_DATA_NODEDETAILS_TABLE_QUERY, nodeListValues)
    executeSqliteQueryByTable(sqlite_cursor, DROP_TABLE_NODECONFIG_IF_EXIST_QUERY, CREATE_NODECONFIG_TABLE_QUERY, INSERT_DATA_NODECONFIG_TABLE_QUERY, configListValues)
    executeSqliteQueryByTable(sqlite_cursor, DROP_TABLE_GATEWAYS_IF_EXIST_QUERY, CREATE_GATEWAY_TABLE_QUERY, INSERT_DATA_GATEWAYS_TABLE_QUERY, gatewayListValues)

    network_address=networkid
    status='Active'
    # GET_NODELIST_QUERY = 'SELECT * FROM node_details'
    GET_INDICATOR_NODEID_BY_ID_QUERY = 'SELECT NodeID FROM node_details where Status="{status}" AND NetworkID = "{network}" AND NodeType="IndicatorPanel"'.format(
                            network=network_address,
                            status=status
                        )
                        
    sqlite_cursor.execute(GET_INDICATOR_NODEID_BY_ID_QUERY)
    indicatorNodes = sqlite_cursor.fetchall()
    # print(indicatorNodes)
    
    if indicatorNodes != None and len(indicatorNodes) != 0:
        for indicatorNode in indicatorNodes:
            print(indicatorNode, "exist")
    else:
        print("No indicator found")

    sqlite_connection.commit()

except sqlite3.Error as e:
    print(utctime, "Error reading data from SQLite3 table", e)
except FileNotFoundError as e:
    print(utctime, e)
finally:
    sqlite_connection.close()
    recordString = '{utctime} | SQLite3 connection is closed'.format( utctime=utctime  )
    print(recordString)
    print("==============================================")
# print(response)
