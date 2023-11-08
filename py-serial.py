import serial
import serial.tools.list_ports
import serial.serialutil

def is_hexadecimal(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False
    
def is_valid_hex_string(hex_string):
    try:
        # Convert the hex string to bytes
        bytes_data = bytes.fromhex(hex_string)
        return True
    except ValueError:
        # An error occurred during conversion (invalid hex string)
        return False
    
def send_data(serial_port):
    while True:
        data_to_send = input("Enter data to send (or 'exit' to quit): ")

        if(is_valid_hex_string(data_to_send) == False):
            print("Invalid Hex String")
            continue

        dataBytes = bytes.fromhex(data_to_send)
        if data_to_send.lower() == 'exit':
            break
        serial_port.write(dataBytes.hex())

def receive_data(serial_port):
    try:
        while True:
            data_bytes = serial_port.readline()
            data = data_bytes.hex()
            if data:
                print(f"Received data: {data}")
    except KeyboardInterrupt:
        print("Stopped Receiving.")

if __name__ == "__main__":
    # Replace '/dev/ttyS0' with the actual path of your serial port
    # On Raspberry Pi 3 and 4, the default serial port is '/dev/ttyS0'
    # On older Raspberry Pi models, the default serial port is '/dev/ttyAMA0'
    # serial_port = serial.Serial('/dev/ttyS0', baudrate=9600, timeout=1)
    
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(port.device)

    port = "/dev/ttyAMA0"
    baudrate = 115200
    parity = serial.PARITY_NONE
    stopbits = serial.STOPBITS_ONE
    databits = serial.EIGHTBITS
    # try:
    serial_port = serial.Serial(port, baudrate, bytesize=databits, parity=parity, stopbits=stopbits, timeout=1)
    # serial_port.is_open()
    try:
        print("Serial Debug Assistant - Python Version")
        print("Type 'exit' to quit.")

        while True:
            action = input("Choose an action (send, receive, exit): ").lower()

            if action == 'send':
                send_data(serial_port)
            elif action == 'receive':
                receive_data(serial_port)
            elif action == 'exit':
                break
            else:
                print("Invalid action. Please choose 'send', 'receive', or 'exit'.")
                
    except KeyboardInterrupt:
        print("\nSerial communication stopped.")
    finally:
        serial_port.close()

    print("Serial Debug Assistant - Python Version closed.")
    # except Exception:
    #     print("serial port not available", port)