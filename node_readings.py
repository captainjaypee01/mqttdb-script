# send node readings also to check if node is offline

# get current readings from sqlite

from datetime import datetime, timedelta
import sqlite3
import redis
import functools


# ==================== READING ENVIRONMENT ====================
__ENV_FILE_PATH = '/boot/wirepas/gateway.env'


@functools.lru_cache
def read_environment_file(file_path):
    config_data = {}
    with open(file_path, 'r') as config_file:
        for line in config_file:
            if line and line != "\n" and line[0] != '#':
                key, value = line.strip().split("=", 1)
                config_data[key] = value.strip('"')
    return config_data


def get_value(config_data, key, default):
    return config_data.get(key, default)


def get_int_value(config_data, key, default):
    value = get_value(config_data, key, str(default))
    try:
        return int(value)
    except ValueError:
        return int(default)


config_data = read_environment_file(__ENV_FILE_PATH)

__NETWORK_TYPE = get_value(config_data, 'WM_MQTT_NETWORK_TYPE', 'DEFAULT')
__SENDER_ID = get_value(config_data, 'WM_GATEWAY_SENDER_ID', None)
__NODE_OFFLINE_THRESHOLD = get_int_value(
    config_data, 'WM_GATEWAY_OFFLINE_STATUS_THRESHOLD', 900)
__SQL_PATH = get_value(config_data, 'WM_MQTT_DB_SQLITE_NAME_PATH',
                       '/home/smart/wirepas/database/mqttdb')
__DEBUGGER_ON = get_value(
    config_data, 'WM_GATEWAY_ENABLE_DATA_MESSAGES', 'False') == 'True'
__OFFSET_HOURS = get_int_value(
    config_data, 'WM_GATEWAY_OFFSET_HOURS', 8)
__VENDOR_NAME = get_value(config_data, 'WM_GATEWAY_VENDOR_NAME',
                          'LJDigital')

# ==================== READING ENVIRONMENT ====================


def getLocalTime():
    currentTimeStamp = datetime.utcnow().timestamp()

    currentTimeStamp = datetime.fromtimestamp(
        currentTimeStamp) + timedelta(hours=__OFFSET_HOURS)

    return currentTimeStamp.strftime(
        '%Y-%m-%d %H:%M:%S.%f')[:-3]


def processNodeReading(node):
    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
    channel = 'gw-data-pipeline/data/' + node[8] + '/readings'
    currentDateTime = getLocalTime()

    node_type = node[2]
    postal_code = str(node[4])
    level = node[5]
    sector_name = node[6]
    meter_value = node[7]

    message = '{{"SenderId":"{SenderId}","SensorId":"{SensorId}","Resourcepath":{ResourcePath},"EventId":"{EventId}","EventType":"{EventType}","Parameters": {{"SensorStatus": "{SensorStatus}","Time":"{Time}","Severity":{Severity},"WaterUsage":{Data}}}}}'.format(
        SenderId=__SENDER_ID,
        SensorId=processIds(
            [node_type, __VENDOR_NAME, postal_code, level, sector_name]),
        ResourcePath=postal_code,
        EventId=processIds(["EV", postal_code, str(node[1]), str(currentDateTime).replace(":", "").replace(
            " ", "").replace("-", "").replace(".", "")]),
        EventType="Water/sub-meter#reading",
        SensorStatus='online',
        Time=currentDateTime,
        Severity=6,
        Data=meter_value
    )

    redis_client.publish(channel, message)


def processIds(array):
    array = [x for x in array if x is not None]

    return "-".join(array)


def executeSql(sql_path, query):
    sqlite_connection = None

    try:
        sqlite_connection = sqlite3.connect(sql_path)
        sqlite_cursor = sqlite_connection.cursor()

        sqlite_cursor.execute(query)
        sqlite_connection.commit()
    except Exception as e:
        print(e)
    finally:
        if sqlite_connection != None:
            sqlite_connection.close()


def fetchRows(sql_path, query):
    sqlite_connection = None
    sql_data = None

    try:
        sqlite_connection = sqlite3.connect(sql_path)
        sqlite_cursor = sqlite_connection.cursor()

        sqlite_cursor.execute(query)
        sql_data = sqlite_cursor.fetchall()
    except Exception as e:
        print(e)
    finally:
        if sqlite_connection != None:
            sqlite_connection.close()

    return sql_data


def logger_info(message):
    if __DEBUGGER_ON:
        print("[" + datetime.now().strftime(
            '%Y-%m-%d %H:%M:%S.%f') + "]: " + message)


def main():
    datetime_to = datetime.now().strftime(
        '%Y-%m-%d %H:%M:%S')
    datetime_from = (datetime.now() - timedelta(seconds=__NODE_OFFLINE_THRESHOLD)).strftime(
        '%Y-%m-%d %H:%M:%S')

    __GET_WM_READING = 'SELECT nlr.updated_at, nd.ServiceID, nd.NodeType, nd.NodeName, nd.postal_code, nd.BuildingLevel, nd.SectorName, nlr.value, nd.NodeID FROM node_latest_readings as nlr inner join node_details as nd on nd.NodeID = nlr.NodeID WHERE nlr.updated_at BETWEEN "{SCHEDULE_DATE_FROM}" AND "{SCHEDULE_DATE_TO}";'.format(
        SCHEDULE_DATE_FROM=datetime_from,
        SCHEDULE_DATE_TO=datetime_to,
    )

    nodes = fetchRows(__SQL_PATH, __GET_WM_READING)

    for node in nodes:
        logger_info("sending data for: " + str(node[1]) + " " + str(node[3]))
        processNodeReading(node)


logger_info("=======process starting=======")
if __NETWORK_TYPE == "SMART_HUB":
    main()
logger_info("=======process completed=======")
