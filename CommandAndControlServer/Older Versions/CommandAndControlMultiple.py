import sys
from PyQt4 import QtGui

import paramiko
import socket
import vlc
from subprocess import *
import time


connections = [] #remote ssh connections
raspberryPIs = ['rPI1', 'rPI2']#, 'rPI3']#, 'rPI4', 'rPI5','rPI6'] #Raspberry PIs
#list details of the connections

#hosts = ['10.42.0.88,pi,raspberry','10.42.0.72,pi,raspberry','10.42.0.89,pi,raspberry']
#hosts = ['10.42.0.75,pi,raspberry','10.42.0.14,pi,raspberry','10.42.0.12,pi,raspberry']
#hosts = ['10.42.0.77,pi,raspberry','10.42.0.99,pi,raspberry','10.42.0.64,pi,raspberry']
#hosts = ['10.42.0.36,pi,raspberry','10.42.0.76,pi,raspberry','10.42.0.52,pi,raspberry',
		#'10.42.0.75,pi,raspberry','10.42.0.14,pi,raspberry','10.42.0.12,pi,raspberry']
hosts = ['192.168.1.68,pi,raspberry', '192.168.1.229,pi,raspberry']

#close all the SSH connections, and processes



class connecthosts:
    def __init__(self,hostInfo,deviceName):
        """
		Args:
            hostInfo: IP username password
            deviceName: beaglebone/raspberryPi			
        return:
            none
        usage:
            builds up the connection with remote systems via ssh using paramiko module		
		"""
		#Paramiko would not work without log file
        paramiko.util.log_to_file("paramiko.log")
        items=hostInfo.split(',')
        print "Connecting to %s..." % deviceName
        try:
		
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(items[0],username=items[1],password=items[2])
            self.client = client
            connections.append(client)
        except paramiko.SSHException, e:
            print "Password is invalid:", e
        except paramiko.AuthenticationException:
            print "Authentication failed"
        except socket.error,e:
            print "Socket connection failed on %s" % deviceName
        #atexit.register(client.close)
    
    def __call__(self,command,isInfo,isPID):
        """
		    args: 
			    command: the command for the remote systems
				isInfo: whether no not to print the information from the remote system
				isPID: whether no not to get the pid of the process				
			return:
			    pid of the process is required
			usage:
    		    function to executes the command
		"""
        stdin, stdout, stderr = self.client.exec_command(command)
        if (isInfo):
            """print out the information shown in the remote system when required"""
            sshdata = stdout.readlines()
            for line in sshdata:
                print(line)
        if (isPID):
            """get the process pid when required"""
            try:
                pid = int(stdout.readline())
                return pid
            except:
                return 0


    
def stop():
	"""disconnect the ssh connections"""
        for conn in connections:
            print conn
            conn.close()
            connections[:]=[]
            print 'SSH connections are off.' 



def vlcView():
    """run the capture.c file in remote system with """
    #remoteRPI('cd ~/Documents/boneCV; ./streamVideoUDP_infinite',isInfo=False, isPID=False)
    p = vlc.MediaPlayer('udp://@:1234')
    p.play()
    #call(['cvlc', 'udp://@:1234', '--play-and-exit']) #this one blocks the interface


def stopRemotePro():
	"""stop the capture program in raspberry pi"""
	
	for x in range(0,len(raspberryPIs)):
	
	
           capturePID = raspberryPIs[x]('pidof capture',isInfo=False, isPID=True)
        if capturePID: #kill the remote process when the pid returned is not zero
		    killcommand = 'kill -9 {pid}'.format(pid=capturePID)
		    raspberryPIs[x](killcommand,isInfo=True, isPID=False)
		    
	#capturePID2 = remoteRPI2('pidof capture',isInfo=False, isPID=True)
     #   if capturePID2: #kill the remote process when the pid returned is not zero
		#    killcommand = 'kill -9 {pid}'.format(pid=capturePID2)
		 #   remoteRPI2(killcommand,isInfo=True, isPID=False)
		    
	#capturePID3 = remoteRPI3('pidof capture',isInfo=False, isPID=True)
     #   if capturePID3: #kill the remote process when the pid returned is not zero
		#    killcommand = 'kill -9 {pid}'.format(pid=capturePID3)
		 #   remoteRPI3(killcommand,isInfo=True, isPID=False)
		    

def captureImage():
	
	"""capture image"""
	for x in range(0,len(raspberryPIs)):		      
            raspberryPIs[x]('cd ~/threeDScanner; ./captureImage',isInfo=False, isPID=False)
            ImageName = ''.join(['/home/james/Pictures/collection/Image-',time.strftime("%y%m%d-%H%M%S")])   
        #remoteRPI1('cd ~/threeDScanner; ./captureImage',isInfo=False, isPID=False)
        #remoteRPI2('cd ~/threeDScanner; ./captureImage',isInfo=False, isPID=False)
        #remoteRPI3('cd ~/threeDScanner; ./captureImage',isInfo=False, isPID=False)
        
        cmd1 = "socat  -d -d -d -u -T 10 UDP4-RECV:1234,reuseaddr OPEN:" + ImageName + ",creat,append"    
        process2 = Popen(cmd1, shell=True)
        process2.wait()   

def shutdownPIs():
	
	"""shutdown Raspberry Pis"""
        for x in range(0,len(raspberryPIs)):		      
            raspberryPIs[x]('sudo shutdown now',isInfo=False, isPID=False)
#        remoteRPI1('sudo shutdown now',isInfo=False, isPID=False)
#        remoteRPI2('sudo shutdown now',isInfo=False, isPID=False)
#        remoteRPI3('sudo shutdown now',isInfo=False, isPID=False)
        
       
    
       

class Window(QtGui.QWidget):
    def __init__(self):
        
        QtGui.QWidget.__init__(self)        
        layout = QtGui.QVBoxLayout(self)
        
        #Button to Start infinite UDP stream to VLC
        self.button1 = QtGui.QPushButton('VLC Viewing', self)
        self.button1.clicked.connect(vlcView)       
        self.button1.resize(125, 30)       
        self.button1.move(50, 100)
        #layout.addWidget(self.button1)
        
        #Button to stop UDP stream
        self.button2 = QtGui.QPushButton('Stop VLC Stream', self)
        self.button2.clicked.connect(stopRemotePro)
        self.button2.resize(125, 30)      
        self.button2.move(225, 100)
        #layout.addWidget(self.button2)
        
        #Button to record video on raspberry pi
        self.button3 = QtGui.QPushButton('Record Video', self)
        self.button3.clicked.connect(main)
        self.button3.resize(125,30)       
        self.button3.move(50, 200)
       # layout.addWidget(self.button3)
        
        #Button to capture image
        self.button5 = QtGui.QPushButton('Capture Image', self)
        self.button5.clicked.connect(captureImage)
        self.button5.resize(125,30)        
        self.button5.move(225, 200)
        #layout.addWidget(self.button5)
        
        #Button to close SSH connections to pi
        self.button4 = QtGui.QPushButton('Disconnect', self)
        self.button4.clicked.connect(stop)
        self.button4.resize(125,30)        
        self.button4.move(50, 300)
       # layout.addWidget(self.button4)
        
        #Button to shutdown raspberry PIs
        self.button6 = QtGui.QPushButton('Shutdown PIs', self)
        self.button6.clicked.connect(shutdownPIs)
        self.button6.resize(125, 30)        
        self.button6.move(225, 300)
        #layout.addWidget(self.button6)
        
       
        
for x in range(0,len(raspberryPIs)):
	raspberryPIs[x] = connecthosts(hosts[x], 'Raspberry Pi' + str((x + 1))) 
	raspberryPIs[x]('uptime', isInfo=True, isPID=False)
	
	 
#connection with raspberry pis
#remoteRPI1 = connecthosts(hosts[0], 'Raspberry Pi 1')
#remoteRPI1('uptime', isInfo=True, isPID=False)

#remoteRPI2 = connecthosts(hosts[1], 'Raspberry Pi 2')
#remoteRPI2('uptime', isInfo=True, isPID=False)

#remoteRPI3 = connecthosts(hosts[2], 'Raspberry Pi 3')
#remoteRPI3('uptime', isInfo=True, isPID=False)




def main():

    stopRemotePro() #make sure the infinite running video capture program has been killed


    """start the StreamVideoUDP program in Raspberry Pi and record the live video to the 'collection' folder"""
    for x in range(0,len(raspberryPIs)):		      
        raspberryPIs[x]('cd ~/threeDScanner; ./streamVideoUDP',isInfo=False, isPID=False)
        videoName = ''.join(['/home/james/Videos/collection/StreamVideo-',time.strftime("%y%m%d-%H%M%S")])
    
    cmd1 = "socat  -d -d -d -u -T 10 UDP4-RECV:1234,reuseaddr OPEN:" + videoName + ",creat,append"    
    process1 = Popen(cmd1, shell=True)
    #process1.wait()
    #remoteRPI2('cd ~/threeDScanner; ./streamVideoUDP',isInfo=False, isPID=False)
    #remoteRPI3('cd ~/threeDScanner; ./streamVideoUDP',isInfo=False, isPID=False)
    

    
if __name__ == '__main__':

    """Set up main window and start UI"""
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.setGeometry(300, 300, 400, 400)
    window.setWindowTitle('Command And Control')
    window.show()
    sys.exit(app.exec_())
    
    
   



