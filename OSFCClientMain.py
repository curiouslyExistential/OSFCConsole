'''
Author:     Dorion Beaudin

About:      This python script serves as a client towards OSFC
            until such a time as the official OSFC client is
            released.
            It was intended for personal use only.

Copyright:  Copyright 2014, Dorion Beaudin

License:    GNU GENERAL PUBLIC LICENSE Version 2

Version:    0.0.1

Email:      dorionbeaudin@live.ca
'''
import socket   #for sockets
import json #for JSON decode
import sys  #for exit
import threading #for multi-threading

global loop #Used to tell threads that it's time to pack up and quit.

class consoleThread(threading.Thread):
    def __init__(self,userInput,msg,sendTo,friend,channel,reqPassword,password,rawData):
        threading.Thread.__init__(self)
        self.userInput = 0
        self.msg = 0
        self.sendTo = 0
        self.friend = 0
        self.channel = 0
        self.reqPassword = 0
        self.password = 0
        self.data = 0
        self.rawsend = 0

    def sendData(self,data):
        try :
            #Set the whole string
            print "<= " + data
            s.sendall(data)
        except socket.error:
            #Send failed
            print 'Network error: Send failed. Exiting.'
            s.close()
            loop = 0
            sys.exit()

    def run(self):
        loop = 1
        self.user = raw_input("Handle: ") #Initialize handle and establish handle with server using the "register" command.
        self.sendData('{"cmd": "register", "handle": "' + self.user + '"}\x00')
        while loop == 1:
            '''
            Best described as a converter. It takes in commands and a syntax that is
            easy for the user to understand and type and then converts the results into
            something the server can understand.
            '''
            self.userInput = raw_input("<= ")
            if self.userInput == "exit":
                s.close()
                loop = 0
                sys.exit()
            elif self.userInput == "help":
                print 'Valid commands are: help, exit, msg, who, friend, join, part, raw'
            elif self.userInput == "msg":
                self.sendTo = raw_input("Send message to who?: ")
                self.msg = raw_input("What is the message?: ")
                self.sendData('{"cmd": "msg", "handle": "' + self.sendTo + '", "msg": "' + self.msg + '"}\x00')
            elif self.userInput == "who":
                self.sendData('{"cmd": "who"}\x00')
            elif self.userInput == "friend":
                self.friend = raw_input("Who to friend?(Only one at a time): ")
                self.sendData('{"cmd": "friend", "handles": ["' + self.friend + '"]}\x00')
            elif self.userInput == "join":
                self.channel = raw_input("Join what channel?(Ex. #Testing): ")
                self.reqPassword = raw_input("Does the channel require a password?(Y/N): ")
                if self.reqPassword == "Y":
                    self.password = raw_input("Channel password?: ")
                    self.sendData('{"cmd": "join", "channel": "' + self.channel + '", "password": "' + self.password + '"}\x00')
                elif self.reqPassword == "N":
                    self.sendData('{"cmd": "join", "channel": "' + self.channel + '"}\x00')
                else:
                    print "You did not enter Y/N"
            elif self.userInput == "part":
                self.channel = raw_input("Part what channel?(Ex. #Testing): ")
                self.sendData('{"cmd": "part", "channel": "' + self.channel + '"}\x00')
            elif self.userInput == "raw":
                self.rawsend = raw_input("Type JSON-formatted command: ")
                self.sendData(self.rawsend)
            else:
                print "Invalid command. Valid commands are: help, exit, msg, who, friend, join, part, raw"

class recieveDataThread(threading.Thread):
    def __init__(self,serverreply,replied):
        threading.Thread.__init__(self)
        self.replied = 0
    def run(self):
        loop = 1
        while loop == 1:
            try:
                self.serverreply = s.recv(4096) #Wait for a response repeatedly.
                self.replied = 1
            except:
                self.replied = 0
            if self.replied == 1:
                print "=> \n" + json.dumps(self.serverreply, sort_keys=True, indent=4, separators=(',', ': '))
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


Thread1 = consoleThread(0,0,0,0,0,0,0,0) #Start threads. Let the fun begin.
Thread2 = recieveDataThread(0,0)
Thread1.start()
Thread2.start()
Thread1.join()
Thread2.join()
print 'Done.\n'