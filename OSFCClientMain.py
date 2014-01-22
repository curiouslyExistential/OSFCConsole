'''
Author:     Dorion Beaudin

About:      This python script serves as a client towards OSFC until such a time as the official OSFC client is released.
            It is intended for personal use only, and will likely never see a public release.

Copyright:  Copyright 2014, Dorion Beaudin

License:    GNU GENERAL PUBLIC LICENSE Version 2

Version:    0.0.2

Email:      dorionbeaudin@live.ca
'''
import socket   #for sockets
import json #for JSON decode
import sys  #for exit
import time #for waiting
from threading import Thread #for multi-threading
from Queue import Queue


def sendData(data, q):
    try :
        #Set the whole string
        print "\n<= \n" + data
        s.sendall(data)
    except socket.error:
        #Send failed
        print 'Network error: Send failed. Exiting.'
        s.close()
        q.put(None)

def consoleThread(threadname, q):
    user = raw_input("Handle: ") #Initialize handle and establish handle with server using the "register" command.
    sendData('{"cmd": "register", "handle": "' + user + '"}\x00', q)
    while True:
        localloop = 1
        q.put(localloop)
        '''
        Best described as a converter. It takes in commands and a syntax that is
        easy for the user to understand and type and then converts the results into
        something the server can understand.
        '''
        time.sleep(2.5)
        userInput = raw_input("Enter command: ")
        if userInput == "exit":
            s.close()
            q.put(None)
            return
        elif userInput == "help":
            print 'Valid commands are: help, exit, msg, who, friend, join, part, raw'
        elif userInput == "msg":
            sendTo = raw_input("Send message to who?: ")
            msg = raw_input("What is the message?: ")
            sendData('{"cmd": "msg", "handle": "' + sendTo + '", "msg": "' + msg + '"}\x00', q)
        elif userInput == "who":
            sendData('{"cmd": "who"}\x00', q)
        elif userInput == "friend":
            friend = raw_input("Who to friend?(Only one at a time): ")
            sendData('{"cmd": "friend", "handles": ["' + friend + '"]}\x00', q)
        elif userInput == "join":
            channel = raw_input("Join what channel?(Ex. #Testing): ")
            reqPassword = raw_input("Does the channel require a password?(Y/N): ")
            if reqPassword == "Y":
                password = raw_input("Channel password?: ")
                sendData('{"cmd": "join", "channel": "' + channel + '", "password": "' + password + '"}\x00', q)
            elif reqPassword == "N":
                sendData('{"cmd": "join", "channel": "' + channel + '"}\x00', q)
            else:
                print "You did not enter Y/N"
        elif userInput == "part":
            channel = raw_input("Part what channel?(Ex. #Testing): ")
            sendData('{"cmd": "part", "channel": "' + channel + '"}\x00', q)
        elif userInput == "raw":
            rawsend = raw_input("Type JSON-formatted command: ")
            sendData(rawsend, q)
        else:
            print "Invalid command. Valid commands are: help, exit, msg, who, friend, join, part, raw"

def recieveDataThread(threadname, q):
    s.settimeout(3)
    while True:
        localloop = q.get()
        if localloop is None:
            s.close()
            return
        try:
            serverreply = s.recv(4096) #Wait for a response repeatedly.
            replied = 1
        except:
            replied = 0
        if replied == 1:
            print "\n=> \n" + json.dumps(serverreply, sort_keys=True, indent=4, separators=(',', ': '))
            '''
            A bit of formatting of the response, to make the whole thing a bit easier to read.
            I don't know how to properly parse JSON yet, but that's not this client's intention.
            I only need what I'm sending to be formatted and easy to send. I can look at the
            response myself and understand it's meaning just fine.
            '''

try:
    #create an AF_INET, STREAM socket (TCP)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error, msg:
    print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
    sys.exit();

print '\nSocket Created\n'

primaryhost = 'irc1.mindfang.org' #The server(s)
backuphost = 'irc2.mindfang.org'
port = 1420

'''
This checks if the server address can be resolved to an IP. If not,
it falls back to the backup. If THAT fails as well, the script quits.
'''
try:
    remote_ip = socket.gethostbyname( primaryhost )
    usedhost = primaryhost
except socket.gaierror:
    #could not resolve
    print 'Hostname could not be resolved. Trying backup server: ' + backuphost + '\n'
    try:
        remote_ip = socket.gethostbyname( backuphost )
        usedhost = backuphost
    except socket.gaierror:
        #could not resolve
        print 'Hostname could not be resolved. Exiting.\n'
        sys.exit()

print 'Ip address of ' + usedhost + ' is ' + remote_ip + '\n'

'''
This attempts a connection to the primary server. If it fails, it
attempts to resolve the backup server and connect to it instead.
Failing that, it will quit.
'''
try:
    print 'Connecting...'
    s.connect((remote_ip , port))
except:
    print 'Connection failed to establish. Trying backup server: ' + backuphost + '\n'
    try:
        remote_ip = socket.gethostbyname( backuphost )
        print 'Ip address of ' + backuphost + ' is ' + remote_ip + '\n'
    except socket.gaierror:
        #could not resolve
        print 'Hostname could not be resolved. Exiting.\n'
        sys.exit()
    try:
        print 'Connecting...'
        s.connect((remote_ip , port))
        usedhost = backuphost
    except:
        print 'Connection failed to establish. Exiting.'
        sys.exit()
print 'Socket Connected to ' + usedhost + ' on ip ' + remote_ip + '\n'

queue = Queue()
localloop = 1
queue.put(localloop)
Client = Thread( target=consoleThread, args=("Client",queue)) #Start threads. Let the fun begin.
Server = Thread( target=recieveDataThread, args=("Server",queue))
Client.start()
time.sleep(1)
Server.start()
Client.join()
Server.join()
print 'Done.\n'
sys.exit()