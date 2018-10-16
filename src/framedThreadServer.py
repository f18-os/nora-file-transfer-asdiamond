#! /usr/bin/env python3
import os
import socket
import sys
from threading import Thread, Lock

# from framedSock import FramedStreamSock
from lib import framedSock as fsock
from lib import params

switchesVarDefaults = (
    (('-l', '--listenPort'), 'listenPort', 50001),
    (('-d', '--debug'), "debug", False),  # boolean (set if present)
    (('-?', '--usage'), "usage", False),  # boolean (set if present)
)

put_mutex = Lock()

# serverthread extends thread
class ServerThread(Thread):
    requestCount = 0  # one instance / class

    def __init__(self, sock, debug, path):
        Thread.__init__(self, daemon=True)
        self.fsock, self.debug = fsock.FramedStreamSock(sock, debug), debug
        self.path = path

    def run(self):
        """
        Always write files that have been sent with 'put' into self.path
        Retrieves files when it encounters a get from self.path

        :return:
        """
        while True:
            filename = self.fsock.receivemsg().decode('utf-8')
            print(f'filename: {filename}')

            action = self.fsock.receivemsg().decode('utf-8')
            print(f"action: {action}")

            if action == 'put':
                # only allow one person to put at a time
                put_mutex.acquire()
                if os.access(self.path + filename, os.R_OK | os.W_OK):
                    print('File already exists')
                    sys.exit(1)
                writer = open(self.path + filename, 'w')
                file = self.fsock.receivemsg().decode('utf-8')  # receive file contents
                if len(file) < 1:
                    print('file must not be empty')
                writer.write(file)

                put_mutex.release()
                return  # everything was ok
            elif action == 'get':
                if not os.access(self.path + filename, os.W_OK | os.R_OK):
                    self.fsock.sendmsg(b"404 FILE NOT FOUND")
                    return
                file = open(self.path + filename).read()
                self.fsock.sendmsg(file.encode('utf-8'))
                return


def main():
    progname = "echoserver"
    paramMap = params.parseParams(switchesVarDefaults)
    debug, listenPort = paramMap['debug'], paramMap['listenPort']
    if paramMap['usage']:
        params.usage()
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # listener socket
    bindAddr = ("127.0.0.1", listenPort)
    lsock.bind(bindAddr)
    lsock.listen(5)
    print("listening on:", bindAddr)
    while True:
        sock, addr = lsock.accept()
        ServerThread(sock, debug=False, path='../server-files/').start()


if __name__ == '__main__':
    main()
