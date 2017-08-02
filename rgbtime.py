# set date and time for rgb mono display from system time
# for propriatary display http://www.rgb-technology.de/GX.html
# version: 0.1 alpha
# date: 26.07.2017

import datetime
import socket
import hexdump
import struct

port = 2101
host = "192.168.178.11"
buffersize = 4096


def hex_dump(data):
    return hexdump.dump(data)


class RBGpanelException(Exception):
    pass


class RGBpanel(object):
    def __init__(self, panel_host, panel_port):
        # create socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (panel_host, panel_port)
        self.sock.connect(server_address)

    def communicate(self, msg, expect):
        self.sock.sendall(msg)
        recv = self.sock.recv(buffersize)
        if recv != expect:
            raise RBGpanelException("communication error:\nsend:\n%s\nexpected:\n%s\nreceived:\n%s" % (
                hex_dump(msg),
                hex_dump(expect),
                hex_dump(recv)
            ))

    def update_time(self):
        self.setup()

        self.sock.sendall(b'Mn5G\xd0')

        now = datetime.datetime.now()
        # 1, 0 could be TZ?
        time_data = struct.pack("8B", now.hour, now.minute, now.second, now.year - 2000, now.month, now.day, 1, 0)
        self.communicate(time_data, b'\xaa\xaa')

    def setup(self):
        self.communicate(b'RGB?', b'Ok\x02')
        self.communicate(b'RGBi', b'Mn5G\x05\x03\x47\x49\x47\x43\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x5c')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.sock.close()


with RGBpanel(host, port) as panel:
    panel.update_time()
