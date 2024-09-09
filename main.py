import queue
import struct
import sys
import time

import socket
import timeit

from PyQt5.QtCore import QThread, QCoreApplication, Qt, pyqtSignal, QRegExp, QStringListModel
from PyQt5.QtWidgets import QApplication, QMainWindow
from Modbus2FDX_ui import Ui_MainWindow
from pymodbus.client import ModbusSerialClient

read_params = [
    {'com': 3,'slave': 1, 'count': 9},
    # {'com': 3,'slave': 2, 'count': 9},
    # {'com': 3,'slave': 3, 'count': 9},
    # {'com': 3,'slave': 4, 'count': 9},
    # {'com': 3,'slave': 5, 'count': 9},
    # {'com': 3,'slave': 6, 'count': 9},
    # {'com': 3,'slave': 7, 'count': 9},
    # {'com': 3,'slave': 8, 'count': 9},
    # {'com': 3,'slave': 9, 'count': 9},
    # {'com': 3,'slave': 10, 'count': 9},
    # {'com': 3,'slave': 11, 'count': 9},
    # {'com': 3,'slave': 12, 'count': 9},
    # {'com': 3,'slave': 13, 'count': 9},
    # {'com': 3,'slave': 14, 'count': 9},
    # {'com': 3,'slave': 15, 'count': 9},
    # {'com': 3,'slave': 16, 'count': 9},
    # {'com': 3,'slave': 17, 'count': 9},
    # {'com': 3,'slave': 18, 'count': 9},
    # {'com': 3,'slave': 19, 'count': 9},
    # {'com': 3,'slave': 20, 'count': 9}
]


class FDX_send_Thread(QThread):
    def __init__(self, FDX_send_socket, FDX_send_queue, remote_ip_port):
        super().__init__()
        self.daemon = True  # 设置为守护进程
        self.FDX_send_queue = FDX_send_queue
        self.FDX_send_socket = FDX_send_socket
        self.isRun = True
        self.remote_ip_port = remote_ip_port

    def stop(self):
        self.isRun = False

    def run(self):
        count = 0

        while self.isRun:
            send_data = bytearray([0x43, 0x41, 0x4E, 0x6F, 0x65, 0x46, 0x44, 0x58,
                                   0x02, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00,
                                   0x00, 0x16, 0x00, 0x05, 0x00, 0xfe, 0x00, 0x0e])
            count = count + 1
            if count == 0xffff:
                count = 0
            try:
                # 使用阻塞式的 get() 方法，如果没有数据，线程会阻塞在这里
                # 直到有数据可用或超时
                data = self.FDX_send_queue.get(block=True, timeout=1)  # 设置超时时间，例如 1 秒
                # print(data)
                send_data.extend(data['data'])

                # dataBytes
                send_data[16] = ((data['len'] + 8) >> 8) & 0xFF
                send_data[17] = (data['len'] + 8) & 0xFF

                # dataBytes
                send_data[22] = (data['len'] >> 8) & 0xFF
                send_data[23] = data['len'] & 0xFF

                # id
                send_data[20] = (data['slave'] >> 8) & 0xFF
                send_data[21] = data['slave'] & 0xFF
                # count
                send_data[12] = (count >> 8) & 0xFF
                send_data[13] = count & 0xFF

                self.FDX_send_socket.sendto(send_data, self.remote_ip_port)
            except queue.Empty:
                # 处理队列为空的情况，例如打印日志或进行其他操作
                pass
                # print("队列为空，等待数据...")


class add_modbus_read_Thread(QThread):
    def __init__(self, modbus_send_queue):
        super().__init__()
        self.daemon = True  # 设置为守护进程
        self.modbus_send_queue = modbus_send_queue
        self.isRun = True

    def stop(self):
        self.isRun = False

    def run(self):
        commands = []
        while self.isRun:
            commands=read_params*3
            self.modbus_send_queue.put(commands)
            time.sleep(0.01)
        # data = {'com': 3, 'count': 7, 'slave': 100}
        # print(data)
        # self.modbus_send_queue.put(data * 3)
        # while self.isRun:
        #     data={'com':3,'count':7,'slave':100}
        #     self.modbus_send_queue.put(data)



class FDX_recive_Thread(QThread):
    def __init__(self, FDX_recive_socket, modbus_send_queue):
        super().__init__()
        self.daemon = True  # 设置为守护进程
        self.modbus_send_queue = modbus_send_queue
        self.FDX_recive_socket = FDX_recive_socket
        self.isRun = True

    def stop(self):
        self.isRun = False


def list_to_bytes(lst):
    # 将每个整数转换为2字节的格式（大端模式：高字节为0）
    byte_array = b''.join(struct.pack('>H', x) for x in lst)
    return byte_array


class modbus_sendThread(QThread):

    def __init__(self, modbus_client, modbus_send_queue, FDX_send_queue):
        super().__init__()
        self.daemon = True  # 设置为守护进程
        self.client = modbus_client
        self.modbus_send_queue = modbus_send_queue
        self.FDX_send_queue = FDX_send_queue
        self.isRun = True


    def test(self):
        try:
            # 使用阻塞式的 get() 方法，如果没有数据，线程会阻塞在这里
            # 直到有数据可用或超时
            commands = self.modbus_send_queue.get(block=True, timeout=1)  # 设置超时时间，例如 1 秒
            print(commands)
            for command in commands:
                if command['com'] == 3:
                    # 读取寄存器，例如读取保持寄存器地址为100的寄存器
                    result = self.client.read_holding_registers(slave=command['slave'], count=command['count'],
                                                                address=0)
                    if not result.isError():
                        data_rec = {"slave": command['slave'], "len": command['count'] * 2,
                                    "data": list_to_bytes(result.registers)}
                        # print(f"寄存器值: {data}")
                        self.FDX_send_queue.put(data_rec)
                        # print(data_rec)
                    else:
                        print("读取失败")
        except queue.Empty:
            # 处理队列为空的情况，例如打印日志或进行其他操作
            pass
            # print("队列为空，等待数据...")
    def run(self):
        # execution_time = timeit.timeit(self.test, number=10)
        # print(f"函数平均运行时间: {execution_time } 豪秒")
        while self.isRun:
            try:
                # 使用阻塞式的 get() 方法，如果没有数据，线程会阻塞在这里
                # 直到有数据可用或超时
                commands = self.modbus_send_queue.get(block=True, timeout=1)  # 设置超时时间，例如 1 秒

                for command in commands:
                    if command['com'] == 3:
                        # 读取寄存器，例如读取保持寄存器地址为100的寄存器
                        start_time = time.time()
                        result = self.client.read_holding_registers(slave=command['slave'], count=command['count'],
                                                                    address=0)
                        if not result.isError():
                            data_rec = {"slave": command['slave'], "len": command['count'] * 2,
                                        "data": list_to_bytes(result.registers)}
                            # print(f"寄存器值: {data}")
                            self.FDX_send_queue.put(data_rec)
                            # print(data_rec)
                        else:
                            print("读取失败")
                        end_time = time.time()
                        execution_time = end_time - start_time

                        print(f"程序运行时间: {execution_time} 秒")

            except queue.Empty:
                # 处理队列为空的情况，例如打印日志或进行其他操作
                pass
                print("队列为空，等待数据...")
        self.client.close()

    def stop(self):
        self.isRun = False


class MainWindows(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init()

    def init(self):
        self.modbus_send_queue = queue.Queue()

        self.FDX_send_queue = queue.Queue()
        self.pushButton_start.clicked.connect(self.run)

    def run(self):
        self.creat_modbus_connect()
        self.creat_FDX_tx_connect()
        self.modbus_read()

    def creat_modbus_connect(self):
        # 创建Modbus串口客户端
        self.client = ModbusSerialClient(framer='rtu', port='COM1', baudrate=115200, timeout=1, parity='N', stopbits=1,
                                         bytesize=8)
        # 连接到Modbus设备
        self.client.connect()
        self.modbus_send_Thread = modbus_sendThread(self.client, self.modbus_send_queue, self.FDX_send_queue)

        self.modbus_send_Thread.start()

    def creat_FDX_tx_connect(self):
        try:
            # 创建UDP套接字
            self.local_socket = socket.socket(socket.AF_INET,
                                              socket.SOCK_DGRAM)  # udp协议
            # self.local_socket.bind(('127.0.0.1', 2809))
            self.remote_ip_port = ('127.0.0.1', 2809)

            self.fdx_send_Thread = FDX_send_Thread(self.local_socket, self.FDX_send_queue, self.remote_ip_port)
            self.fdx_send_Thread.start()

        except Exception as e:
            print(f"Error in UDP server: {e}")

    def modbus_read(self):
        self.add_read_request_Thread = add_modbus_read_Thread(self.modbus_send_queue)
        self.add_read_request_Thread.start()

    def close_modbus_connect(self):
        self.modbus_send_Thread.stop()


if __name__ == "__main__":
    # 高dpi
    # QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    app.setStyle("WindowsVista")
    w = MainWindows()
    w.show()
    sys.exit(app.exec_())
