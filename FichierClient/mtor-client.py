#!/usr/bin/python3
# -*-coding:Utf-8 -*

import time
import os
import socket
import sys
from threading import Thread, Lock

import Utils

REFRESH_LOADING_RATE = 0.25
NB_BLOCK_TOTAL = 0
MAX_SIZE_PACKET = 32768

BlockList = []

#the list of tuple containing ("ip", port)
IPServers = []
#the transfert speed in bytes for each Thread [th1Speed, th2Speed, ...]
TransfertSpeed = []

#the list of tuple Thread
ThreadList = []
lock = Lock()

#distribute the block over 12 block minimum
#It will make more if each one is superior to 
#the maximum size
def distributeBlocks(sizeTotal):
    global NB_BLOCK_TOTAL
    sizeLeft = sizeTotal
    offset = 0
    blockSize = int(sizeTotal / 12)

    if blockSize > MAX_SIZE_PACKET:
        blockSize = MAX_SIZE_PACKET

    while blockSize > 0:
        BlockList.append((offset, blockSize))
        

        offset = offset + blockSize
        sizeLeft = sizeLeft - blockSize

        if sizeLeft < blockSize:
            blockSize = sizeLeft

    NB_BLOCK_TOTAL = len(BlockList)

#The loading screen UI launched from another thread
def loadingScreen(filename, IPServers, size):
    Finished = False
    Error = 0

    while not Finished:
        if len(ThreadList) == 0:
            Error = 1
            break

        if len(BlockList) == 0:
            Finished = True

        charCompleted = "="
        charHeadProgress = ">"
        charIncompleted = " "
        percentDone = float((NB_BLOCK_TOTAL - len(BlockList)) / NB_BLOCK_TOTAL * 100)
        

        interiorOfLoading = "[" 
        for i in range(0, 25):
            if i*4 < percentDone < (i+1)*4:
                interiorOfLoading = interiorOfLoading + charHeadProgress
            elif i*4 > percentDone:
                interiorOfLoading = interiorOfLoading + charIncompleted
            
            else:
                interiorOfLoading =interiorOfLoading + charCompleted
            
        interiorOfLoading = interiorOfLoading + "]"

        
        strFileDownload = "Downloading File with the name : {0}".format(filename)
        loadingMSG = "Downloading " + Utils.bytes2human(size) + "\t{0}\t{1}%".format(interiorOfLoading, round(percentDone,1))
        
        strIpServer = ""
        for ip in IPServers:
            print(ip)
            strIpServer = strIpServer + "Server state {0} : {1}\n".format(ip[0], "UP")
        strIpServer = strIpServer + "\n"

        os.system('cls' if os.name == 'nt' else 'clear')
        print(strFileDownload)
        print(strIpServer)
        print(loadingMSG)

        time.sleep(REFRESH_LOADING_RATE)

    #if no Error found the file is download
    if Error == 0:
        print("No error were found!")
        print("Download of {0} has succeed".format(filename))
        sys.exit(0)
    elif Error == 1:
        print("No servers up to download the file " + filename + "\nExiting ...")
        sys.exit(1)
    elif Error == 2:
        print("Connection Timed out with all servers\nExiting ...")
        sys.exit(1)


#function of the launching thread
def ThreadDownload(ip, filename, transfertID):
    global lock
    global TransfertSpeed

    try:
        sockClient = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockClient.connect(ip)
    except ConnectionError as e:
        return
    #Communicate file name
    
    sockClient.send(str.encode(filename))

    

    #recv the READY tag or the error
    mes = sockClient.recv(4096).decode()
    

    if mes == "READY":

        
        #ReceiveNWrite(sockClient, lock, fichier)
        lock.acquire()
        restant = len(BlockList)
        lock.release()

        while restant > 0:
            #Wait for the readiness of the server
            #It will send READY when it is
            #ready = sockClient.recv(MAX_SIZE_PACKET).decode()

            #remove the block to send
            lock.acquire()
            #(offset, size)
            offset, size = BlockList.pop(0)
            lock.release()
            
            #print(blockToSend)
            #print(sockClient)
            #SENDING
            
            sockClient.send(str.encode("{0};{1}".format(offset, size)))
            #RECEIVING
            data = sockClient.recv(MAX_SIZE_PACKET + 1)
            
            #verify wether server is still connected
            if data != b"":
                #reparse the file
                if len(data) < size:
                    newOffset = offset + len(data)
                    newSize = size - len(data)
                    BlockList.append((newOffset, newSize))

                lock.acquire()
                #Write data
                fichier = open(filename, "rb+")
                fichier.seek(offset)
                fichier.write(data)
                fichier.close()

                #set for the next loop
                restant = len(BlockList)
                #print(restant)
                lock.release()
                #loadingScreen(filename, ip)

            #if the data is empty, means that the connection is lost
                

        #finish the server
        #SENDING
        #loadingScreen(filename, ip)
        sockClient.send(str.encode("NO BLOCK"))

    else:
        print(mes)
        sockClient.close()


def main():
    if len(sys.argv) != 3:

        print ("Usage: mtor-client.py <file name> <Port>\nExiting ...")
        sys.exit(1)

    if  sys.argv[1].split(".")[1] != "mtr":
        print ("the file need to be a .mtr\nExiting ...")
        sys.exit(1)

    if not os.path.isfile(sys.argv[1]):
        print("The file {0} doesn't exist\nExiting ...".format(sys.argv[1]))
        sys.exit(1)
    fileName = ""
    taille = 0
    

    file = open(sys.argv[1])
    
    compt = 0    
    for line in file:
        compt = compt + 1
        if compt == 1:
            fileName = line[:-1]
        elif compt == 2:
            taille = int(line.rstrip())
            distributeBlocks(taille)
        else:
            IPServers.append((line.rstrip(), int(sys.argv[2])))
       

    newFic = open(fileName, "wb")
    newFic.seek(taille - 1)
    newFic.write(b'\0')
    newFic.close()
    
    nbThread = 0
    for ip in IPServers:
        # (Thread , ("ip", port))
        
        TransfertSpeed.append(0)
        ThreadList.append(Thread(target=ThreadDownload, args=(ip, fileName, nbThread), name=ip[0]))
        ThreadList[-1].start()
        
        nbThread = nbThread + 1
        
    
    #start the loading UI thread
    Thread(target=loadingScreen, args=(fileName, IPServers, taille), name="LoadingUI").start()
    

if __name__ == "__main__":
    main()
