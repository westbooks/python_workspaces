# -*- coding: utf-8 -*-
'''
Serial通讯类帮助类
'''

__author__ = 'shixiaofeng'
__version__ = 'V1.0'

import sys
import serial
import time
import logging
import threading
import binascii


class SerialHelper(object):
    def __init__(self, Port='COM5' , BandRate='9600', ByteSize='8', Parity='N', StopBits='1'):
        '''
        初始化参数
        '''
        self.l_serial = None
        self.alive = False
        self.port = Port
        self.bandRate = BandRate
        self.byteSize = ByteSize
        self.stopBits = StopBits
        self.parity = Parity
        self.thresholdValue = 64
        self.receive_data = ""

    def start(self):
        '''
        打开串口
        :return:
        '''
        self.l_serial = serial.Serial()
        self.l_serial.port = self.port
        self.l_serial.baudrate = self.bandRate
        self.l_serial.bytesize = int(self.byteSize)
        self.l_serial.stopbits = int(self.stopBits)
        self.l_serial.parity = self.parity
        self.l_serial.timeout = 2

        try:
            self.l_serial.open()
            if self.l_serial.is_open:
                self.alive = True
        except Exception as e:
            self.alive = False
            logging.error(e)


    def stop(self):
        '''
        结束，关闭串口
        :return:
        '''
        self.alive = False
        if self.l_serial.is_open:
            self.l_serial.close()

    def read(self):
        '''
        循环读取串口发送的数据信息
        :return:
        '''
        while self.alive:
            try:
                number = self.l_serial.inWaiting()
                if number:
                    self.receive_data += self.l_serial.read(number).replace(binascii.unhexlify("00"),"")
                    if self.thresholdValue < len(self.receive_data):
                        self.receive_data = ""
            except Exception as e:
                logging.error(e)

    def write(self, data, isHex=False):
        '''
        发送数据给串口设备
        :return:
        '''
        if self.alive:
            if self.l_serial.is_open():
                if isHex:
                    data = binascii.unhexlify(data)
                self.l_serial.write(data)


if __name__ == '__main__':
    import threading
    ser = SerialHelper()
    ser.start()

    ser.write("123", isHex= False)
    thread_read = threading.Thread(target=ser.read())
    thread_read.setDaemon(True)
    thread_read.start()
    import time
    time.sleep(25)
    ser.stop()