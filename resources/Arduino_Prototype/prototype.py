from time import sleep
import serial

serial_connection = serial.Serial(
    port='COM4',
    baudrate=9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=2,
    bytesize=serial.EIGHTBITS
)

finished = False
try:
    print("waiting")
    while serial_connection.in_waiting:
        answer = (serial_connection.read()).decode('ascii')
        print(data)
    while not finished :
        data = input('Eingabe: ')
        print(data)
        dataEncoded = data.encode()
        print(dataEncoded)
        serial_connection.write(dataEncoded)
except Exception as e:
    print(e)
finally:
    serial_connection.close()