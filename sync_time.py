import serial
import time
import os


def send_command(command):
    try:
        ser = serial.Serial('/dev/ttyUSB2', baudrate=9600, timeout=1)
        ser.write(command.encode())
        time.sleep(1)
        response = ser.read_all().decode().strip()
        ser.close()

        return response
    except serial.SerialException as e:
        print("[SERIAL EXCEPTION]")
        print(e)
        print("[SERIAL EXCEPTION]")
    except Exception as e:
        print("[EXCEPTION]")
        print(e)
        print("[EXCEPTION]")
        return None


commandResponse = send_command('AT+QLTS=1\r')

if commandResponse is None or commandResponse == '':
    print("something wrong with the message...")
    exit()

commandResponse = commandResponse.split('\n')

if len(commandResponse) < 2:
    print("length not appropriate")
    exit()

start_index = commandResponse[1].find('"')
end_index = commandResponse[1].find('+', start_index + 1)
date_string = commandResponse[1][start_index + 1:end_index]
date_part = date_string.replace(',', ' ').replace('/', '-')

os.system("timedatectl set-time '" + date_part + "'")

print("Time is set to: " + date_part)
