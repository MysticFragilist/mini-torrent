#!/usr/bin/python3
# -*-coding:Utf-8 -*

import os
import sys
import socket
from threading import Thread, Lock

clientThreadList = []
lock = Lock()

class server():

    def __init__(self, port):
        
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = ""  # socket.gethostname()
        self.socket.bind((self.host, int(self.port)))
    
    
    def listenForClients(self):
        self.socket.listen(30)
        print("The server has started")
        while True:
            print("Waiting for a connection...")
            clientSock, clientAddr = self.socket.accept()
            print("Connection address: " + str(clientAddr))
            clientThreadList.append(Thread(target=self.listenForFirstCommunication, args=(clientSock, clientAddr)))
            clientThreadList[-1].start()
    
    #send data
    def listenForFirstCommunication(self, clientSock, clientAddr):
        readSize = 8192
        #try:
            #read file name
        self.fileName = clientSock.recv(readSize).decode()
        
        print("File name : {0}".format(self.fileName))
        if self.fileName == "":
            raise Exception('Client disconnected')
        
        
        #print(os.path.isfile("{0}/{1}".format(sys.argv[1], self.fileName)))
        if os.path.isfile("{0}/{1}".format(sys.argv[1], self.fileName)):
            #send READY
            clientSock.send(str.encode("READY"))
            #self.BlockSend()
            anotherBlock = True
            while anotherBlock:

                print("Waiting for next block")
                #RECEIVING
                mes = clientSock.recv(4096).decode()
                print(mes)
                print("New Block arrived, started transferring...")
                anotherBlock = not mes == "NO BLOCK"
                print(anotherBlock, end="\n")
                
                if anotherBlock:
                    print(mes)
                    offset, size = mes.split(';')

                    fic = open("{0}/{1}".format(sys.argv[1], self.fileName), "rb")
                    fic.seek(int(offset))
                    toSend = fic.read(int(size))
                    fic.close()


                    print("Sending data block : ({0}, {1})".format(offset, size))
                    #SENDING
                    clientSock.send(toSend)
                    print("Finished Transmission of block")

        else:
            #SENDING
            clientSock.send(str.encode("Error : No such file"))
            raise Exception('Bad fileName')

        #except Exception as e:
        #    print(e)
            
        #    clientSock.close()
        #    return False    
    
    def BlockSend(self):
        anotherBlock = True
        while anotherBlock:
            #reading of the block
            mes = self.socket.recv(4096).decode()
            anotherBlock = not mes == "NO BLOCK"

            if anotherBlock:
                offset, size = mes.split(';')

                lock.acquire()
                fic = open(self.fileName, "rb")
                fic.seek(offset)
                toSend = fic.read(size)
                fic.close()
                lock.release()
                
                self.socket.send(toSend)
	
def main():
    if not len(sys.argv) == 3:
        print("Usage: mtor-serveur.py <folder name> <port>")
    else:
        server(sys.argv[2]).listenForClients()


if __name__ == "__main__":
    main()
