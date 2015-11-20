"""
Description: 
1.Recive the start command, set capture mode: video/photos;
2.excute the C program, run the generated file;
3.send the video back to PC.             
"""

import subprocess
import signal
import os
import sys
from os import getpid
import psutil

import time
#from datetime import datetime as dt

import SimpleHTTPServer
import SocketServer
from urlparse import parse_qs, urlparse

PORT = 8090


class MyHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def __init__(self,req,client_addr,server):
        SimpleHTTPServer.SimpleHTTPRequestHandler.__init__(self,req,client_addr,server)

    def do_GET(self):

        #*****************gong*******************
        #***********get the parameters***********
        parameters = parse_qs(urlparse(self.path).query, keep_blank_values=True)      
        start = ''.join(parameters['start'])
        #print start
        #*****************gong*******************

        time.sleep(1)

        #*****************gong*******************
        #********get the start/stop command******
        if start == '1':
            subprocess.check_call('./streamVideoUDP')
        else:
            #print sys.argv[0]             
            process_name = sys.argv[0] #get process name
            mypid = getpid()
            #for process in psutil.process_iter():
            os.kill(mypid,signal.SIGTERM)
                     
            #print process_name
            #log_file_name = sys.argv[2] 
            #kill process
            #proc = subprocess.Popen(["pgrep",process_name],stdout=subprocess.PIPE)
            #print subprocess.PIPE
            #for pid in proc.stdout:
            #    print pid                
            #    os.kill(int(pid),signal.SIGTERM)
                #check if the process we killed is alive
                #try:
                #    os.kill(int(pid),0)
                #    raise Exception("""unable to kill the process
                #                      HINT: use signal.SIGKILL or signal.SIGABOR""")
                #except OSError as ex:
                #    continue
        #*****************gong*******************

        
        self.send_response(200)
        self.send_header("Content-type","text/html")
        self.send_header("Content-length",len("Hello World"))
        self.end_headers()
        self.wfile.write("Hello World")

Handler = MyHandler

httpd = SocketServer.TCPServer(("", PORT), Handler)

print "serving at port", PORT
httpd.serve_forever()

