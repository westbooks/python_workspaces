# -*- coding: utf-8 -*-
import serial
from time import sleep


def recv(serial):
    while True:
        data = serial.read_all()
        if data == '':
            continue
        else:
            break
        sleep(0.02)
    return data


if __name__ == '__main__':

    serial = serial.Serial('COM4', 115200, timeout=0.5)
    if serial.isOpen():
        print("open success")
    else:
        print("open failed")

    while True:
        data = recv(serial)
        if data != b'':
            print("receive : ", data)
            serial.write(data) # 数据写回