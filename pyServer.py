# -*- coding: utf8 -*-
#
#  pyServer  2023.Oct.12
#  _____________________
#  pyServer.py 
#  
#  Rewrite of pywebsocketserver.py
#  Written  by suxianbaozi
#  Modified by Warren
#
#  Python web server for connecting sockets locally 
#   with browsers  as well as a generic TCP server.
#

import time,sys,os,threading
import io_SocketServer

class ioHandler():
    def __init__(self):
        self.server = None
        pass
    
    def setIO(self, setIO):
        self.server = setIO

    def onData(self, uid, text):
        ioCommand = text.split(":::")
        if str(ioCommand[0]) == "pyServer":
            if str(ioCommand[1]) == "PRINTDATA":
                self.server.sendData("pyServer:::SENDDATA:::Received:::" + str(ioCommand[2]))
            if ioCommand[1] == "Disconnect":
                print("*** Software Requests Disconnect")
                self.onClose("Soft Disconnect")

        return

    def onConnect(self, server, uid):
        self.server.sendData("pyServer:::Connected")
        return

    def onClose(self, location):
        print("*** Attempting shutdown")
        try:        
            threading._after_fork()
        except:
            pass
        return


port = 54123
while 1:                                                   # Loop. To reconnect on failure.
    io = ioHandler()                                       # Get instance to io handler.
    server_object = io_SocketServer.socketIO(port, 1, io)  #Init socketIO
    io.setIO(server_object)
    time.sleep(.1)
    connect_Status = server_object.Connect()               # Listen for connection.
    server_object.start()                                  # Start thread.
    time.sleep(1)

    print(">>> Running websocket server. \r\n\r\n")
    
    while server_object.status():
        time.sleep(0.1)  # Releases (Main) thread, to run other threads in background.
        continue
    
