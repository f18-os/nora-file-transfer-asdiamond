#! /usr/bin/env python3

# Echo client program
import socket, sys, re
import os
import random
from lib import params
# from framedSock import FramedStreamSock
from lib import framedSock as fsock
from threading import Thread
import time

switchesVarDefaults = (
    (('-s', '--server'), 'server', "localhost:50001"),
    (('-d', '--debug'), "debug", False),  # boolean (set if present)
    (('-?', '--usage'), "usage", False),  # boolean (set if present)
)


class ClientThread(Thread):
    def __init__(self, serverHost, serverPort, debug, filename, path, operation):
        Thread.__init__(self, daemon=False)
        self.serverHost, self.serverPort, self.debug = serverHost, serverPort, debug
        self.filename, self.path, self.operation = filename, path, operation

    def safe_connect(self):
        s = None
        for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
            af, socktype, proto, canonname, sa = res
            try:
                print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
                s = socket.socket(af, socktype, proto)
            except socket.error as msg:
                print(" error: %s" % msg)
                s = None
                continue
            try:
                print(" attempting to connect to %s" % repr(sa))
                s.connect(sa)
            except socket.error as msg:
                print(" error: %s" % msg)
                s.close()
                s = None
                continue
            break
        if s is None:
            print('could not open socket')
            sys.exit(1)
        return s

    def run(self):
        """
        Sends self.filename out from self.path, into the framedSocket
        Always writes files it 'gets' to client-files/
        :return:
        """
        s = self.safe_connect()
        fs = fsock.FramedStreamSock(s, debug=debug)

        # send filename
        fs.sendmsg(self.filename.encode('utf-8'))
        print(f"sent filename: {self.filename}")

        fs.sendmsg(self.operation.encode('utf-8'))
        print(f"sent operation: {self.operation}")

        if self.operation == 'put':
            # send file
            print('reading file')
            try:
                file = open(self.path + self.filename, 'r').read()
            except:
                print('problem opening file, exiting')
                sys.exit(1)
            print('sending file')
            fs.sendmsg(file.encode('utf-8'))
        elif self.operation == 'get':
            print('getting file')
            file = fs.receivemsg().decode('utf-8')
            print('writting file')
            open('client-files/' + self.filename, 'w').write(file)


def main():
    global debug, serverHost, serverPort
    progname = "framedClient"
    paramMap = params.parseParams(switchesVarDefaults)
    server, usage, debug = paramMap["server"], paramMap["usage"], paramMap["debug"]
    if usage:
        params.usage()
    try:
        serverHost, serverPort = re.split(":", server)
        serverPort = int(serverPort)
    except:
        print("Can't parse server:port from '%s'" % server)
        sys.exit(1)

    # for i in range(100):
    #     ClientThread(serverHost, serverPort, debug)
    actions = ['put', 'get']
    files = os.listdir('../piracy/')  # we will grab our rando files from this dir

    for i in range(100):
        client = ClientThread(serverHost, serverPort, debug, random.choice(files), '../piracy/', 'put')
        client.start()

    # choose random file from piracy dir, and randomly 'put' or 'get'
    # ClientThread(serverHost, serverPort, debug, random.choice(files), random.choice(actions))
    # ClientThread(serverHost, serverPort, debug, 'apply.txt', '../piracy/', 'put').start()
    # ClientThread(serverHost, serverPort, debug, 'apply.txt', '../piracy/', 'put').start()
    # print(os.listdir('../src/descs'))

if __name__ == '__main__':
    main()
