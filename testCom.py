#-*- coding: utf-8 -*
import serial
import serial.tools.list_ports

plist = list(serial.tools.list_ports.comports())

if len(plist) <= 0:
    print("The Serial port can't find!")
else:
    print(len(plist))
    plist_0 = list(plist[0])
    serialName = plist_0[0]
    serialFd = serial.Serial(serialName, 9600, timeout=60)
    print("check which port was really used >", serialFd.name)

ser = serial.Serial("COM5", 9600, timeout=0.5)
for i in range(0, 100-1):
    ser.write('hello\r\n'.encode())
print(ser.readline())
ser.close()