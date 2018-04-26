# -*- coding: utf-8 -*-

__author__ = 'shixiaofeng'
__version__ = 'v1.0'

import time
import datetime
import threading
import binascii
import logging
import platform


from UI import SerialTool
from COM import SerialHelper


if platform.system() == 'Windows':
    from serial.tools import list_ports
elif platform.system() == 'Linux':
    import glob, os, re


import tkinter as tk
from tkinter import ttk


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s % (filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S')


class MainSerialToolUI(SerialTool.SerialToolUI):
    def __init__(self, master=None):
        super(MainSerialToolUI, self).__init__()
        self.ser = None
        self.receive_count = 0
        self.receive_data = ''
        self.list_box_serial = list()
        self.find_all_serial()

    def __del__(self):
        if platform.system() == 'Linux':
            try:
                self.ser.SetStopEvent()
            except:
                pass

    def find_all_serial(self):
        '''
        获取到串口列表
        :return:
        '''
        if platform.system() == 'Windows':
            try:
                self.temp_serial = list()
                for com in list_ports.comports():
                    strCom = com[0] + ": " + com[1][:-7].encode('utf-8').decode('utf-8')
                    self.temp_serial.append(strCom)
                for item in self.temp_serial:
                    if item not in self.list_box_serial:
                        self.frm_left_listbox.insert('end', item)
                for item in self.list_box_serial:
                    if item not in self.temp_serial:
                        index = list(self.frm_left_listbox.get(0, self.frm_left_listbox.size())).index(item)
                        self.frm_left_listbox.delete(index)

                self.list_box_serial = self.temp_serial

                self.thread_findserial = threading.Timer(1, self.find_all_serial)
                self.thread_findserial.setDaemon(True)
                self.thread_findserial.start()

            except Exception as e:
                logging.error(e)
        elif platform.system() == 'Linux':
            try:
                self.temp_serial =list()
                self.temp_serial = self.find_usb_tty()
                for item in self.temp_serial:
                    if item not in self.list_box_serial:
                        self.frm_left_listbox.insert("end", item)

                for item in self.list_box_serial:
                    if item not in self.temp_serial:
                        index = list(self.frm_left_listbox.get(0, self.frm_left_listbox.size())).index(item)
                        self.frm_left_listbox.delete(index)

                self.list_box_serial = self.temp_serial

                self.thread_findserial = threading.Timer(1, self.find_all_serial)
                self.thread_findserial.setDaemon(True)
                self.thread_findserial.start()
            except Exception as e:
                logging.error(e)

    def Toggle(self):
        '''
        打开和关闭串口
        :return:
        '''
        if self.frm_left_btn['text'] == "Open":
            try:
                self.currentStrCom = self.frm_left_listbox.get(self.frm_left_listbox.curselection())
                if platform.system() == 'Windows':
                    self.port = self.currentStrCom.split(":")[0]
                elif platform.system() == 'Linux':
                    self.port = self.currentStrCom

                self.baudrate = self.frm_left_combobox_baudrate.get()
                self.parity = self.frm_left_combobox_parity.get()
                self.databit = self.frm_left_combobox_databit.get()
                self.stopbit = self.frm_left_combobox_stopbit.get()
                self.ser = SerialHelper.SerialHelper(Port=self.port, BandRate=self.baudrate, ByteSize=self.databit, Parity=self.parity, StopBits=self.stopbit)
                self.ser.start()

                if self.ser.alive:
                    self.frm_status_label['text'] = "Open [{0}] Successful!".format(self.currentStrCom)
                    self.frm_status_label['fg'] = "#66CD00"
                    self.frm_left_btn['text'] = "Close"
                    self.frm_left_btn['bg'] = "#F08080"

                    self.thread_read = threading.Thread(target=self.SerialRead)
                    self.thread_read.setDaemon(True)
                    self.thread_read.start()

            except Exception as e:
                logging.error(e)
                try:
                    self.frm_status_label['text'] = "Open [{0}] Failed!".format(self.currentStrCom)
                    self.frm_status_label["fg"] = "#DC143C"
                except Exception as ex:
                    logging.error(ex)

        elif self.frm_left_btn['text'] == 'Close':
            try:
                self.ser.stop()
                self.receive_count = 0
            except Exception as e:
                logging.error(e)
            self.frm_left_btn["text"] = "Open"
            self.frm_left_btn["bg"] = "#008B8B"
            self.frm_status_label["text"] = "Close Serial Successful!"
            self.frm_status_label["fg"] = "#8DEEEE"

    def Open(self, event):
        '''
        双击列表打开/关闭串口
        :param event:
        :return:
        '''

        self.Toggle()

    def Clear(self):
        '''
        清除
        :return:
        '''
        self.frm_right_receive.delete("0.0", "end")
        self.receive_count = 0

    def Send(self):
        '''
        发送信息
        如果为Hex发送，示例："31 32 33" [即为字符串 "123"]
        :return:
        '''
        if self.ser:
            try:
                # 发送新行
                if self.new_line_cbtn_var.get() == 0:
                    send_data = str(self.frm_right_send.get('0.0','end').encode('gbk')).strip()
                else:
                    send_data = str(self.frm_right_send.get("0.0", "end")).strip() + "\r\n"

                # 是否十六进制发送
                if self.send_hex_cbtn_var.get() == 1:
                    self.ser.write(send_data, isHex=True)
                else:
                    self.ser.write(send_data)
            except Exception as e:
                logging.error(e)

    def SerialRead(self):
        '''
        线程读取串口发送来的信息
        :return:
        '''
        while self.ser.alive:
            try:
                n = self.ser.l_serial.inWaiting()
                if n:
                    self.receive_data += self.ser.l_serial.read(n).replace(binascii.unhexlify("00"), "")
                    if self.thresholdValue <= len(self.receive_data):
                        self.receive_count += 1

                        # 接收显示是否为Hex
                        if self.receive_hex_cbtn_var.get() == 1:
                            self.receive_data = self.space_b2a_hex(self.receive_data)
                        self.frm_right_receive.insert("end", "[" + str(datetime.datetime.now()) + " - "
                                                      + str(self.receive_count) + "]:\n", "green")
                        self.frm_right_receive.insert("end", self.receive_data + "\n")
                        self.frm_right_receive.see("end")
                        self.receive_data = ""
            except Exception as e:
                logging.error(e)
                self.receive_data = ""
                self.ser.stop()
                self.ser = None

    def find_usb_tty(self, vendor_id=None, product_id=None):
        '''
        发现串口设备 linux
        '''
        tty_devs = list()
        for dn in glob.glob('/sys/bus/usb/devices/*'):
            try:
                vid = int(open(os.path.join(dn, "idVendor")).read().strip(), 16)
                pid = int(open(os.path.join(dn, "idProduct")).read().strip(), 16)
                if ((vendor_id is None) or (vid == vendor_id)) and ((product_id is None) or (pid == product_id)):
                    dns = glob.glob(os.path.join(dn, os.path.basename(dn) + "*"))
                    for sdn in dns:
                        for fn in glob.glob(os.path.join(sdn, "*")):
                            if re.search(r"\/ttyUSB[0-9]+$", fn):
                                tty_devs.append(os.path.join("/dev", os.path.basename(fn)))
            except Exception as ex:
                pass
        return tty_devs

    def space_b2a_hex(self, data):
        '''
        格式化接收到的数据字符串
        示例：123 --> 31 32 33
        '''
        new_data_list = list()
        new_data = ""

        hex_data = binascii.b2a_hex(data)
        temp_data = ""
        for index, value in enumerate(hex_data):
            temp_data += value
            if len(temp_data) == 2:
                new_data_list.append(temp_data)
                temp_data = ""
        for index, value in enumerate(new_data_list):
            if index % 25 == 0 and index != 0:
                new_data += "\n"
            new_data += value
            new_data += " "

        return new_data

if __name__ == '__main__':
    '''
    main loop
    '''
    root = tk.Tk()
    root.title("窗口调试助手")
    if SerialTool.g_default_theme == 'dark':
        root.configure(bg="#292929")
        combostyle = ttk.Style()
        combostyle.theme_use('alt')
        combostyle.configure("TCombobox", selectbackground="#292929", fieldbackground="#292929",
                             background="#292929", foreground="#FFFFFF")
    MainSerialToolUI(master=root)
    root.resizable(False, False)
    root.mainloop()







