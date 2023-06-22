

def formatRequestPayload(packet, sensor, data, command, sub, area, nodename, timestamp, nodeid):
    
    nodeNameHex = nodename.encode('utf-8').hex()
    # print(nodeNameHex)
    # nodeNameHex = nodeNameHex[:(20*2)] #get 20 bytes
    print(nodeNameHex)
    timestampHex = hex(int(timestamp/1000)).replace("0x", "")
    if len(area) == 6:
        area = area + "06"

    nodeid = nodeid.zfill(8)
    print("Node ID", nodeid)

    nodeNameLen = int(len(nodeNameHex) / 2)
    nodeNameLenHex = hex(int(nodeNameLen)).replace("0x", "")
    print('nodename length', nodeNameLen)

    tempSubData = command + sub + area + nodeid + timestampHex + nodeNameLenHex + data
    totalLengthToSubtractNodeName = computeTotalLengthToSubtract(nodeNameHex, tempSubData)

    if totalLengthToSubtractNodeName > 0:
        nodename = nodename[:-totalLengthToSubtractNodeName]

    print('new node name', nodename)
    nodeNameHex = nodename.encode('utf-8').hex()
    nodeNameLen = (len(nodeNameHex) / 2)
    nodeNameLenHex = hex(int(nodeNameLen)).replace("0x", "").zfill(2)
    print('new node name hex', nodeNameHex)
    print('new node name len hex', nodeNameLenHex)
    
    # subPayloadData = command + sub + area + nodeid + timestampHex + nodeNameLenHex + nodeNameHex + data
    payloadData = command + sub + area + nodeid + timestampHex + nodeNameLenHex + nodeNameHex + data
    print("PAYLOAD DATA: ", payloadData)
    payloadDataLen = (len(payloadData) / 2)
    print("PAYLOAD DATA LEN: ", payloadDataLen)
    payloadDataLenHex = hex(int(payloadDataLen)).replace("0x", "").zfill(2)
    print("PAYLOAD DATA LEN HEX: ", payloadDataLenHex)
    payload = packet + sensor + payloadDataLenHex + payloadData
    # print(payload)
    return payload

def computeTotalLengthToSubtract(nodeNameHex, tempSubData):
    totalPayload = 80
    nodeNameLen = int(len(nodeNameHex) / 2)
    print('nodename length', nodeNameLen)

    tempSubDataLen = int(len(tempSubData) / 2)
    print('tempSubData length', tempSubDataLen)

    totalLen = tempSubDataLen + nodeNameLen
    diffNodeNameLen = 0 if(totalLen) <= totalPayload else totalLen - totalPayload
    print('total length', totalLen)
    print('diffNodeNameLen', diffNodeNameLen)

    return diffNodeNameLen


packet="01c5"
data = "e7000407ffff0004021400"
sensorNumber = "01"
command = "01"
subCommand = "00"
areaID = "80000006"
timestamp = 1681465231698
nodename = "FE-B43-LB1-11"
nodeid = 'aabbcc'

testPayload = formatRequestPayload(packet, sensorNumber, data, command, subCommand, areaID, nodename, timestamp, nodeid)

print(testPayload)
