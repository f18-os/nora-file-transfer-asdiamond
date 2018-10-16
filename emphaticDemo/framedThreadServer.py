#! /usr/bin/env python3
import sys, os, socket, time
from lib import params
from threading import Thread
# from framedSock import FramedStreamSock
from lib import framedSock as fsock

switchesVarDefaults = (
    (('-l', '--listenPort'), 'listenPort', 50001),
    (('-d', '--debug'), "debug", False),  # boolean (set if present)
    (('-?', '--usage'), "usage", False),  # boolean (set if present)
)

# serverthread extends thread
class ServerThread(Thread):
    requestCount = 0  # one instance / class

    def __init__(self, sock, debug):
        Thread.__init__(self, daemon=True)
        self.fsock, self.debug = fsock.FramedStreamSock(sock, debug), debug
        self.start()

    def run(self):
        while True:
            msg = self.fsock.receivemsg()
            if not msg:
                if self.debug: print(self.fsock, "server thread done")
                return
            requestNum = ServerThread.requestCount
            # intentionally creating race condition?
            time.sleep(0.001)
            ServerThread.requestCount = requestNum + 1
            msg = ("%s! (%d)" % (msg, requestNum)).encode()
            self.fsock.sendmsg(msg)


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
        ServerThread(sock, debug)


if __name__ == '__main__':
    main()

