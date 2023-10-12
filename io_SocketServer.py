# -*- coding: utf8 -*-
#
#  pyServer  2023.Oct.12
#  _____________________
#  io_SocketServer.py 
#  
#  Python web server for connecting sockets locally 
#   with browsers  as well as a generic TCP server.
#

import sys
import socket
import time
import select
import threading
import hashlib
import base64
import struct
import traceback
import linecache
import inspect

class socketIO():
    
    def __init__(self, port, uid, ioHandler):
        self.port = port
        self.con = None
        self.isHandleShake = False
        self.uid = uid
        self.io = ioHandler
        self.signKey = "ADS#@!D"        
        #self.lock = threading.Lock()
        self.thread_2 = threading.Thread(name='ioThread', target=self.run, daemon=False)
        self.stop_thread = False
        if uid == 0:
            self.isHandleShake = True
        
    def start(self):
        self.socketThreadRunning = True 
        self.thread_2.start()
    
    def Disconnect(self):
        self.socketThreadRunning = False
        self.con.close()

    def Connect(self):
        time.sleep(2)
        print("\r\n(-) Connecting . . .")
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', self.port))
        sock.listen(1)
        time.sleep(1)
        try:
            (self.con,address) = sock.accept()
            print("(+) Connected.\r\n")
            time.sleep(1)
            
        except socket.error as e:
            print("(-) Not Connected. ")
            print(" Socket Error: " + str(e))
            
        return self.con

    def stopThread(self):
        print("> Stopping Server ")
        self.socketThreadRunning = False
        return

    def run(self):
        self.socketThreadRunning = True
        time.sleep(0)
        while self.socketThreadRunning == True:
            time.sleep(0) #Used for threading, to step into server code at intervals.

            if not self.isHandleShake: 
                try:
                    self.con.setblocking(0)
                    ready = select.select([self.con], [], [], 1)
                    if ready[0]:
                        if "closed" in str(self.con):
                            return
                        try:
                            clientData  = self.con.recv(1024).decode()
                        except:
                            return
                        if clientData == '':
                            return
                        dataList = clientData.split("\r\n")
                        header = {}
                        
                        for data in dataList:
                            if ": " in data:
                                unit = data.split(": ")
                                header[unit[0]] = unit[1]
                        secKey = header['Sec-WebSocket-Key']
                        resKey = base64.encodebytes(hashlib.new("sha1",(secKey+"258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode('utf-8')).digest())
                        resKey = resKey.decode().replace("\n","")
                        response = '''HTTP/1.1 101 Switching Protocols\r\n'''
                        response += '''Upgrade: websocket\r\n'''
                        response += '''Connection: Upgrade\r\n'''
                        response += '''Sec-WebSocket-Accept: %s\r\n\r\n'''%(resKey,)
                        try:
                            self.con.send(bytes(response,'latin-1'))
                            self.isHandleShake = True
                            self.sendData("SETUID")
                            self.io.onConnect(self.io, self.uid)
                            time.sleep(1) # Wait a second after connecting. 
                        except Exception as e:
                            print(" io_SocketServer.py : " + str(e))

                            return
                        continue

                except Exception as e:
                    self.socketThreadRunning = False
                    exc_type, ex, tb = sys.exc_info()
                    imported_tb_info = traceback.extract_tb(tb)[-1]
                    line_number = imported_tb_info[1]
                    print_format = '{}: Exception in line: {}, message: {}'
                    print(print_format.format(exc_type.__name__, line_number, ex))
                    print(traceback.format_exc())
                    continue

            else:
                try:
                    self.con.setblocking(0)
                    if "closed" in str(self.con):
                            return
                    ready = select.select([self.con], [], [], 1)

                    if ready[0]:
                        if "closed" in str(self.con):
                            return
                        data_head = self.con.recv(1).decode('latin-1')

                        if repr(data_head) == '':
                            self.onClose("1")
                            return

                        if "closed" in str(self.con):
                            return

                        try:
                            header = struct.unpack("B",bytes(data_head,'latin-1'))[0]
                        except:
                            return
                        
                        opcode = header & 0b00001111

                        if opcode == 8:
                            print("* Closing Connection.")
                            self.socketThreadRunning = False
                            self.onClose("2")
                            continue

                        if "closed" in str(self.con):
                            return
                            
                        data_length = self.con.recv(1).decode('latin-1')
                        data_lengths= struct.unpack("B",bytes(data_length,'latin-1'))
                        data_length = data_lengths[0] & 0b01111111
                        masking = data_lengths[0] >> 7
                        
                        if data_length<=125:
                            payloadLength = data_length
                        elif data_length==126:
                            payloadLength = struct.unpack("H",bytes(self.con.recv(2).decode('latin-1'),'latin-1'))[0]
                        elif data_length==127:
                            payloadLength = struct.unpack("Q",bytes(self.con.recv(8).decode('latin-1'),'latin-1'))[0]
                        
                        if masking==1:
                            if "closed" in str(self.con):
                                return
                            maskingKey = self.con.recv(4).decode('latin-1')
                            self.maskingKey = maskingKey
                        data = self.con.recv(payloadLength).decode('latin-1')
                        
                        if masking==1:
                            i = 0
                            true_data = ''
                            for d in data:
                                true_data += chr(ord(d) ^ ord(maskingKey[i%4]))
                                i += 1
                            self.onData(true_data)
                        else:
                            self.onData(data)

                except socket.error as e:
                    print(traceback.format_exc())
                    print("Socket Error: " + str(e.errno))

                    if e.errno == 9 or e.errno == 10053 or e.errno == 10054 or e.errno == 10038:
                        self.socketThreadRunning = False
                    if e.errno == 10035:
                        continue

                    self.socketThreadRunning = False
                    self.onClose("io_SocketServer.py : Handshake Failure")
                    return
            
    def status(self):
        return self.socketThreadRunning
    def onData(self,text):
        
        try:
            uid,sign,value = text.split("<split>")
            print("Client(Browser) >>> " + str(value))
            if "Disconnect" in value:
                self.stopThread()
                self.onClose("*** Software Disconnect")
            uid = int(uid)
            #self.uid = uid
        except:
            self.con.close()
        hashStr = hashlib.new("md5",(str(uid)+self.signKey).encode('utf-8')).hexdigest()
        if hashStr!=sign:
            print(" io_SocketServer.py - onData() [ Browser Hash Invalid ]")
            self.con.close()
            return
        return self.io.onData(uid,value)

    def onClose(self, location):
        print("* Closing from location: " + str(location))
        self.socketThreadRunning = False
        try:        
            threading._after_fork()
        except:
            pass
        time.sleep(1)
        if "closed" not in str(self.con):
            self.con.close()
            self.io.onClose("io_SocketServer.py Closing()")
            
    def packData(self,text):
        sign = hashlib.new("md5",(str(self.uid)+self.signKey).encode('utf-8')).hexdigest()
        data = '%s<split>%s<split>%s'%(self.uid,sign,text)
        return data
       
            
    def sendData(self, text):
        print("Server(Python) >>> " + str(text))

        if self.uid == 0:
            try:
                text += "\r\n"
                text = bytes(text, 'utf-8')
                self.con.send(text)
            except Exception as e:
                self.socketThreadRunning = False
                self.onClose("WebSocket sendData()")  # Indicates to the function, the location socket was closed from.
                print("> Send Data Failure. Closing Socket. ")

        else: 
            try:
                
                text = self.packData(text)
                if "closed" in str(self.con):
                    self.socketThreadRunning = False
                    return
                self.con.send(struct.pack("!B",0x81))
                length = len(text)

                if length<=125:
                    self.con.send(struct.pack("!B",length))

                elif length<=65536:
                    self.con.send(struct.pack("!B",126))
                    self.con.send(struct.pack("!H",length))
                else:
                    self.con.send(struct.pack("!B",127))
                    self.con.send(struct.pack("!Q",length))

                value = struct.pack("!%ds" % (length,), bytes(text, 'utf-8'))
                self.con.send(value)

            except Exception as e:
                if e.errno == 10038:
                    self.socketThreadRunning = False
                    return

                exc_type, ex, tb = sys.exc_info()
                imported_tb_info = traceback.extract_tb(tb)[-1]
                line_number = imported_tb_info[1]
                print_format = '{}: Exception in line: {}, message: {}'
                print("io_SocketServer.py " + print_format.format(exc_type.__name__, line_number, ex))
                print(traceback.format_exc())

                return
