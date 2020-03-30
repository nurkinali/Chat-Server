#!/usr/bin/env python

import sys
import time
import Queue
import socket
import threading
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class ReadThread (threading.Thread):
    def __init__(self, name, cSocket, writeQueue, screenQueue):
        threading.Thread.__init__(self)
        self.screenQueue = screenQueue
        self.writeQueue = writeQueue
        self.cSocket = cSocket
        self.nickname = ""
        self.name = name

    def incoming_parser(self, data):
        data = data.strip()

        if len(data) == 0:
            return

        if len(data) > 2 and not data[2] == " ":
            response = "ER"
            self.writeQueue.put(response)
            self.screenQueue.put("Local: Bad command")
            return
        rest = data[3:]

        if data[0:2] == "RO":
            nickname = data.strip().split(" ")[1]
            response = "Server: Registered as " + nickname
            self.writeQueue.put(response)
            self.screenQueue.put(response)
        if data[0:2] == "RN":
            nickname = data.strip().split(" ")[1]
            response = "Server: User registration denied: " + nickname
            self.writeQueue.put(response)
            self.screenQueue.put(response)
        if data[0:2] == "UO":
            nickname = data.strip().split(" ")[1]
            response = "Server: " + nickname + " logged in."
            self.writeQueue.put(response)
            self.screenQueue.put(response)
        if data[0:2] == "UN":
            nickname = data.strip().split(" ")[1]
            response = "Server: " + nickname + " refused connection -wrong password-."
            self.writeQueue.put(response)
            self.screenQueue.put(response)
        if data[0:2] == "UR":
            nickname = data.strip().split(" ")[1]
            response = "Server: " + nickname + " refused connection -not registered-."
            self.writeQueue.put(response)
            self.screenQueue.put(response)
        if data[0:2] == "KI":
            data = data.replace("KI", "").strip() # Sistem mesajlarini iki sekilde yapabilirdik, biri client digeri ise server uzerinden. Burada her ikisinin de mumkun oldugunu gostermek icin ilk kismi client uzerinden, diger kismi ise server uzerinden yaptim.
        if data[0:2] == "BY":
            data = data.replace("BY", "").strip()
        if data[0:2] == "LA":
            data = data.replace("LA", "").strip()
        if data[0:2] == "GO":
            nickname = data.strip().split(" ")[1]
            message = data.replace("GO", "").strip().replace(nickname, "").strip()
            response = nickname + " " + message
            self.writeQueue.put(response)
            self.screenQueue.put(response)
        if data[0:2] == "TO":
            data = data.replace("TO", "").strip()
        if data[0:2] == "CO":
            data = data.replace("CO", "").strip()
        if data[0:2] == "CN":
            data = data.replace("CN", "").strip()
        if data[0:2] == "PO":
            nickname = data.strip().split(" ")[1]
            message = data.replace("PO", "").strip().replace(nickname, "").strip()
            response = nickname + " " + message
            self.writeQueue.put(response)
            self.screenQueue.put(response)
        if data[0:2] == "PN":
            data = data.replace("PN", "").strip()
        if data[0:2] == "SM":
            response = data.strip().replace("SM", "").strip()
            self.writeQueue.put("Server: " + response)
            self.screenQueue.put("Server: " + response)

    def run(self):
        while True:
            data = self.cSocket.recv(1024)
            self.incoming_parser(data)

class WriteThread (threading.Thread):
    def __init__(self, name, cSocket, writeQueue):
        threading.Thread.__init__(self)
        self.writeQueue = writeQueue
        self.cSocket = cSocket
        self.name = name

    def run(self):
        while True:
            data = self.writeQueue.get()
            self.cSocket.send(data)

class ClientDialog (QDialog):
    def __init__(self, writeQueue, screenQueue):
        self.screenQueue = screenQueue
        self.writeQueue = writeQueue

        self.qt_app = QApplication(sys.argv)

        QDialog.__init__(self, None)

        self.setWindowTitle('IRC Client')
        self.setMinimumSize(500, 200)

        self.vbox = QVBoxLayout()

        self.sender = QLineEdit("", self)

        self.channel = QTextBrowser()

        self.send_button = QPushButton("Send")

        self.send_button.clicked.connect(self.outgoing_parser)

        self.vbox.addWidget(self.channel)
        self.vbox.addWidget(self.sender)
        self.vbox.addWidget(self.send_button)

        self.vbox.addStretch(100)

        self.setLayout(self.vbox)

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateText)

        self.timer.start(10)

    def updateText(self):
        if not self.screenQueue.empty():
            data = self.screenQueue.get()
            t = time.localtime()
            pt = "%02d:%02d" % (t.tm_hour, t.tm_min)

            self.channel.append(pt + " " + data)
        else:
            return

    def outgoing_parser(self):
        data = self.sender.text()
        self.screenQueue.put(data)
        if len(data) == 0:
            return
        if data[0] == "/":
            command = data.strip().split(" ")[0].strip("/")
            if command == "list": # /list
                self.writeQueue.put("LQ")
            elif command == "register": # /register nickname password
                nickname = data.strip().split(" ")[1].strip("/")
                password = data.strip().split(" ")[2].strip("/")
                self.writeQueue.put("RG " + nickname + ":" + password)
            elif command == "quit": # /quit
                self.writeQueue.put("QU")
                self.close()
            elif command == "change": # /change oldpass newpass
                oldPassword = data.strip().split(" ")[1].strip("/")
                newPassword = data.strip().split(" ")[2].strip("/")
                self.writeQueue.put("CP " + oldPassword + ":" + newPassword)
            elif command == "nick": # /nick nickname password
                nickname = data.strip().split(" ")[1].strip("/")
                password = data.strip().split(" ")[2].strip("/")
                self.writeQueue.put("US " + nickname + ":" + password)
            elif command == "msg": # /msg nickname message
                nickname = data.strip().split(" ")[1].strip("/")
                message = data.replace("/msg " + nickname, "").strip()
                self.writeQueue.put("PM " + nickname + ":" + message)
            elif command == "control": # /control
                self.writeQueue.put("TI")
            else:
                self.screenQueue.put("Local: Command error")
        else:
            self.writeQueue.put("GM " + data)

        self.sender.clear()

    def run(self):
        self.show()
        self.qt_app.exec_()

s = socket.socket()
host = "127.0.0.1"
port = 2596

s.connect((host, port))

while True:
    screenQueue = Queue.Queue(500)
    writeQueue = Queue.Queue(500)

    app = ClientDialog(screenQueue, writeQueue)

    rt = ReadThread("ReadThread", s, writeQueue, screenQueue)
    rt.start()

    wt = WriteThread("WriteThread", s, screenQueue)
    wt.start()

    app.run()

    rt.join()
    wt.join()
    s.close()
