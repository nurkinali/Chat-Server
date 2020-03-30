#!/usr/bin/env python

import threading
import datetime
import socket
import Queue

onlineUsers = []
fihrist = {}

host = "0.0.0.0"
port = 2596

def currentTime():
    date = datetime.datetime.now().strftime("%I:%M:%p on %B %d, %Y")
    return date

def main():
    s = socket.socket()

    loggerQueue = Queue.Queue(500)

    s.bind((host, port))
    s.listen(5)

    counter = 0

    while True:
        c, addr = s.accept()

        threadQueue = Queue.Queue(50)

        writerThread = WriteThread(counter, "Thread-%s" %{counter}, c, addr, threadQueue, loggerQueue)
        readerThread = ReadThread(counter, "Thread-%s" %{counter}, c, addr, threadQueue, loggerQueue, onlineUsers, fihrist)
        loggerThread = LogThread(loggerQueue)

        writerThread.start()
        readerThread.start()
        loggerThread.start()

        counter+=1

    #loggerQueue.put(currentTime() + ": Got connection from ('" + str(host) + "', " + str(port) + ")" + "\n")

class ReadThread(threading.Thread):
    def __init__(self, threadID, name, cSocket, cAddress, threadQueue, loggerQueue, onlineUsers, fihrist):
        threading.Thread.__init__(self)
        self.name = name
        self.cSocket = cSocket
        self.fihrist = fihrist
        self.threadID = threadID
        self.cAddress = cAddress
        self.threadQueue = threadQueue
        self.loggerQueue = loggerQueue
        self.onlineUsers = onlineUsers

    def parser(self, data):
        data = data.strip()

        if data[0:2] == "RG":
            name = data.replace("RG", "").strip().split(":")[0]
            password = data.replace("RG", "").strip().split(":")[1]
            if name in self.fihrist:
                self.threadQueue.put("RN " + name + "\n")
            else:
                self.fihrist[name] = {}
                self.fihrist[name]["password"] = password
                self.fihrist[name]["threadQueue"] = self.threadQueue
                self.threadQueue.put("RO " + name + "\n")

        elif data[0:2] == "US":
            name = data.replace("US", "").strip().split(":")[0]
            if name in self.fihrist and name in self.onlineUsers:
                self.threadQueue.put("KI SM Already logged in from another tab")
               # self.cSocket.close()
            elif name in self.fihrist:
                name = data.replace("US", "").strip().split(":")[0]
                password = data.replace("US", "").strip().split(":")[1]
                if self.fihrist[name]["password"] == password:
                    if name not in onlineUsers:
                        self.name = name
                        for names in fihrist.keys():
                            self.fihrist[names]["threadQueue"].put("UO " + self.name + "\n")
                       # self.threadQueue.put("UO " + self.name + "\n")
                        self.fihrist[self.name]["cSocket"] = self.cSocket
                        self.fihrist[self.name]["threadQueue"] = self.threadQueue
                        self.onlineUsers.append(self.name)
                        self.loggerQueue.put(currentTime() + ": " + self.name + " has joined." + "\n")
                else:
                    for names in fihrist.keys():
                        self.fihrist[names]["threadQueue"].put("UN " + name + "\n")
                        #self.threadQueue.put("UR " + name + "\n")
            else:
                for names in fihrist.keys():
                            self.fihrist[names]["threadQueue"].put("UR " + name + "\n")
                 #   self.threadQueue.put("UN " + name + "\n")

        elif data[0:2] == "QU"  and self.name in self.onlineUsers:
            for names in fihrist.keys():
                self.fihrist[names]["threadQueue"].put("BY SM " + self.name + " logged out. \n")

            self.threadQueue.put("BY " + self.name + "\n")
            self.onlineUsers.remove(self.name)


            self.loggerQueue.put(currentTime() + ": Closing socket ('" + str(host) + "', " + str(port) + ")" + "\n")
            self.loggerQueue.put(currentTime() + ": Exiting WriteThread-" + str((self.threadID)+1) + "\n")
            self.loggerQueue.put(currentTime() + ": Exiting ReadThread-" + str((self.threadID)+1) + "\n")

            self.cSocket.close()

        elif data[0:2] == "TI" and self.name in self.onlineUsers:
            self.threadQueue.put("TI SM No connection problem found.")

        elif data[0:2] == "LQ" and self.name in self.onlineUsers:
            list = ""
            for x in self.onlineUsers:
                list = list + x + ":"

            self.threadQueue.put("LA SM Users connected: " + list + "\n")

        elif data[0:2] == "CP" and self.name in self.onlineUsers:
            oldPassword = data.replace("CP", "").strip().split(":")[0]
            newPassword = data.strip().split(":")[1]

            if self.fihrist[self.name]["password"] != oldPassword:
                self.threadQueue.put("CN SM Invalid password.")
            else:
                self.fihrist[self.name]["password"] = newPassword
                self.threadQueue.put("CO SM Password has been changed.")

        elif data[0:2] == "GM" and self.name in self.onlineUsers:
            message = data.replace("GM","").strip()
            #self.threadQueue.put("GO " + self.name + message)
            for users in self.onlineUsers:
                if self.name != users:
                    self.fihrist[users]["threadQueue"].put("GO " + self.name + ": " + message)

        elif data[0:2] == "PM" and self.name in self.onlineUsers:
            toSend = data.replace("PM","").strip().split(":")[0]
            message = data.replace("PM","").strip().split(":")[1]
            if toSend in self.fihrist:
                self.fihrist[toSend]["threadQueue"].put("PO " + self.name + ": " + message)
                #self.threadQueue.put("PO \n")
            else:
                self.threadQueue.put("PN SM A problem encountered when sending your message.")
                #self.threadQueue.put("PN ")

        elif self.name not in self.onlineUsers:
            self.threadQueue.put("EL \n")

        else:
            self.threadQueue.put("ER \n")

    def run(self):
        self.loggerQueue.put(currentTime() + ": Starting ReadThread-" + str(self.threadID) + "\n")
        while True:
            data = self.cSocket.recv(1024)
            data = unicode(data, errors = 'ignore')
            self.parser(data)

class WriteThread (threading.Thread):
    def __init__(self, counter, threadID, cSocket, cAddr, threadQueue, loggerQueue):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.counter = counter
        self.cSocket = cSocket
        self.cAddr = cAddr
        self.loggerQueue = loggerQueue
        self.threadQueue = threadQueue
    def run(self):
        self.loggerQueue.put(currentTime() + ": Starting WriteThread-" + str(self.counter) + "\n")
        while True:
            get_message = self.threadQueue.get()
            self.cSocket.send(get_message)

class LogThread (threading.Thread):
    def __init__(self, loggerQueue):
        threading.Thread.__init__(self)
        self.loggerQueue = loggerQueue
    def run(self):
        with open('log.log', 'w') as f:
            data = self.loggerQueue.get()
            while True:
                f.write(data)
                f.flush()
            l = logThread(loggerQueue)
            l.start()

if __name__ == "__main__":
    main()
