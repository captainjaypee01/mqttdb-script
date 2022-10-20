import mysql.connector
import sqlite3
import datetime
now = datetime.datetime.utcnow()
utctime = (now.strftime("%Y-%m-%d %H:%M:%S"))

nodeTypeList = ['EmerLight', 'ExitLight', 'Relay','FireExtinguisher', 'IndicatorPanel']
nodeTypeTuple = tuple(nodeTypeList)
GET_ALL_NODE_DETAILS_ACTIVE_LIST_QUERY = """select NetworkID, NodeID, ServiceID, SystemID, AreaID, NodeType, Status, NodeName, postal_code, BuildingName, BuildingLevel, SectorName, ApplicationCode, ApplicationName 
                                    from node_details 
                                    where status='Active'
                                    AND NodeType in {nodeTypes}
                        """.format(nodeTypes=nodeTypeTuple)
DROP_TABLE_IF_EXIST_QUERY = "DROP TABLE IF EXISTS node_details"
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
INSERT_DATA_NODEDETAILS_TABLE_QUERY = """
    INSERT INTO node_details(NetworkID,NodeID,ServiceID,SystemID,AreaID,NodeType,Status,NodeName,postal_code,BuildingName,BuildingLevel,SectorName,ApplicationCode,ApplicationName)
    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
"""
try:
    mysql_connection = mysql.connector.connect(host='10.104.0.101',
                                         database='smartnew',
                                         user='smart',
                                         password='Sm@r+M0n1t0r1n6')

    sqlite_connection = sqlite3.connect("/home/pi/wirepas/mqttdb")
    sqlite_cursor = sqlite_connection.cursor()
    sqlite_cursor.execute(DROP_TABLE_IF_EXIST_QUERY)
    sqlite_cursor.execute(CREATE_NODEDETAILS_TABLE_QUERY)

    cursor = mysql_connection.cursor()
    cursor.execute(GET_ALL_NODE_DETAILS_ACTIVE_LIST_QUERY)
    # get all records
    records = cursor.fetchall()
    recordString = '{utctime} | Total number of rows in table: ", {rowcount}'.format(
                                    utctime=utctime,
                                    rowcount=cursor.rowcount
                                )
    print(recordString)
    sqlite_cursor.executemany(INSERT_DATA_NODEDETAILS_TABLE_QUERY, records)
    sqlite_cursor.execute(GET_ALL_NODE_DETAILS_ACTIVE_LIST_QUERY)
    sqlite_connection.commit()

    recordString = '{utctime} | Success query'.format(
                                    utctime=utctime
                                )
    print(recordString) 
    

except mysql.connector.Error as e:
    print(utctime, "Error reading data from MySQL table", e)
finally:
    if mysql_connection.is_connected():
        mysql_connection.close()
        cursor.close()
        
        recordString = '{utctime} | MySQL connection is closed'.format( utctime=utctime  )
        print(recordString)
        print("==============================================")