import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *


import paramiko
import socket
import vlc
from subprocess import *
import time
import threading


connections = [] #remote ssh connections
raspberryPIs = ['rPI1','rPI2','rPI3','rPI4','rPI5','rPI6','rPI7','rPI8','rPI9','rPI10','rPI11','rPI12'] #Raspberry PIs
#list details of the connections

#hosts = ['10.42.0.88,pi,raspberry','10.42.0.72,pi,raspberry','10.42.0.89,pi,raspberry']
#hosts = ['10.42.0.75,pi,raspberry,1234','10.42.0.14,pi,raspberry,1236','10.42.0.12,pi,raspberry,1238']
#hosts = ['10.42.0.77,pi,raspberry','10.42.0.99,pi,raspberry','10.42.0.64,pi,raspberry']
hosts = ['10.42.0.75,pi,raspberry,1234','10.42.0.14,pi,raspberry,1236','10.42.0.12,pi,raspberry,1238',
		'10.42.0.36,pi,raspberry,1240','10.42.0.76,pi,raspberry,1242','10.42.0.52,pi,raspberry,1244',
		'10.42.0.74,pi,raspberry,1246', '10.42.0.96,pi,raspberry,1248', '10.42.0.53,pi,raspberry,1250',
		'10.42.0.77,pi,raspberry,1252', '10.42.0.65,pi,raspberry,1254', '10.42.0.28,pi,raspberry,1256']
#hosts = ['192.168.1.68,pi,raspberry,1234', '192.168.1.229,pi,raspberry,1236']

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



def vlcView(text):
    """run the capture.c file in remote system with """
    #remoteRPI('cd ~/Documents/boneCV; ./streamVideoUDP_infinite',isInfo=False, isPID=False)
    
    items = text.split(',',2)
    port = items[2]
    position = int(items[0])
    raspberryPIs[position]('cd ~/threeDScanner; ./streamVideoUDP',isInfo=False, isPID=False)
    p = vlc.MediaPlayer('udp://@:'+ port)
    p.play()
    #call(['cvlc', 'udp://@:1234', '--play-and-exit']) #this one blocks the interface


def stopRemotePro():
	"""stop the capture program in raspberry pi"""
	
	for x in range(0,len(raspberryPIs)):
	
	
           capturePID = raspberryPIs[x]('pidof capture',isInfo=False, isPID=True)
        if capturePID: #kill the remote process when the pid returned is not zero
		    killcommand = 'kill -9 {pid}'.format(pid=capturePID)
		    raspberryPIs[x](killcommand,isInfo=True, isPID=False)
		    
			    

def captureImage():
	
	imgThreads = []
	
	for x in range(0,len(raspberryPIs)):
		items=hosts[x].split(',')		
		port = items[3]
		imageName = ''.join(['/home/james/Pictures/collection/Image' + str(x) + '-',time.strftime("%y%m%d-%H%M%S")])
		img = threading.Thread(target=startImageCapture(port,imageName,x))
		imgThreads.append(img)
		
		
	for t in imgThreads:
			t.start()
			
	for t in imgThreads:
		    t.join()
	
	print 'Images saved to Home/Pictures/collection'
	

#"""capture image"""
#	for x in range(0,len(raspberryPIs)):		      
 #           raspberryPIs[x]('cd ~/threeDScanner; ./captureImage',isInfo=False, isPID=False)
  #          ImageName = ''.join(['/home/james/Pictures/collection/Image-',time.strftime("%y%m%d-%H%M%S")])   
   #    
    #    
     #   cmd1 = "socat  -d -d -d -u -T 10 UDP4-RECV:1234,reuseaddr OPEN:" + ImageName + ",creat,append"    
      #  process2 = Popen(cmd1, shell=True)
       # process2.wait()   

def shutdownPIs():
	
	"""shutdown Raspberry Pis"""
        for x in range(0,len(raspberryPIs)):		      
            raspberryPIs[x]('sudo shutdown now',isInfo=False, isPID=False)
            
  
        
def startImageCapture(port,imageName,position):
	"""Start Image Capture"""
	raspberryPIs[position]('cd ~/threeDScanner; ./captureImage',isInfo=False, isPID=False)       
	cmd2 = "socat -u -T 10 UDP4-RECV:" + str(port) + ",reuseaddr OPEN:" + imageName + ",creat,append"    
	process2 = Popen(cmd2, shell=True)
 
    
def startStream(port,videoName,position):
	"""Start Video Capture"""
	raspberryPIs[position]('cd ~/threeDScanner; ./streamVideoUDP',isInfo=False, isPID=False)
	cmd = "socat -u -T 10 UDP4-RECV:" + str(port) + ",reuseaddr OPEN:" + videoName + ",creat,append"    
	process = Popen(cmd, shell=True)
	#process.wait()      

class Window(QWidget):
    def __init__(self):
        
        QWidget.__init__(self)        
        layout = QGridLayout()
        layout.setHorizontalSpacing(10)
        layout.setVerticalSpacing(10)

        #Vlc stream label
        self.vlcLbl = QLabel('VLC Viewing')
        self.vlcLbl.setAlignment(Qt.AlignHCenter)        
        layout.addWidget(self.vlcLbl, 0,1,1,2) 
       
       #Camera Combo box label
        self.comboLbl = QLabel('Camera :')
        self.comboLbl.setAlignment(Qt.AlignHCenter)
        layout.addWidget(self.comboLbl,1,1)
        
        #combo box to select camera for vlc view
        self.cameraCombo = QComboBox()    
         
        for y in range(0,len(raspberryPIs)):
			items=hosts[y].split(',')		
			port =  str(y) + ',' + items[0] + ',' + items[3] 
			self.cameraCombo.addItem(port)	
			
        self.cameraCombo.setMaxVisibleItems(5)   		
        layout.addWidget(self.cameraCombo,1,2)
        
       # selectedText = str(self.cameraCombo.currentText())
       
         #Button to Start infinite UDP stream to VLC
        self.button1 = QPushButton('Start', self)
        self.button1.clicked.connect(lambda: vlcView(str(self.cameraCombo.currentText())))      
        self.button1.resize(125, 30)       
        layout.addWidget(self.button1,2,1)
        
       
        
        
        #Button to stop UDP stream
        self.button2 = QPushButton('Stop', self)
        self.button2.clicked.connect(stopRemotePro)
        self.button2.resize(125, 30)      
        layout.addWidget(self.button2, 2,2)
        
        layout.setRowMinimumHeight(3, 25)
        
        
        self.dividingLine1 = QFrame()
        self.dividingLine1.setFrameStyle(QFrame.HLine)
        #self.dividingLine1.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout.addWidget(self.dividingLine1,4,1,1,2)
        
       # layout.setRowMinimumHeight(5, 25)
        
        #record label
        self.recordLbl = QLabel('Recording')
        self.recordLbl.setAlignment(Qt.AlignHCenter)        
        layout.addWidget(self.recordLbl, 6,1,1,2)
        
        #Button to record video on raspberry pi
        self.button3 = QPushButton('Record Video', self)
        self.button3.clicked.connect(main)
        self.button3.resize(125,30)       
        layout.addWidget(self.button3, 7,1)
        
        #Button to capture image
        self.button5 = QPushButton('Capture Image', self)
        self.button5.clicked.connect(captureImage)
        self.button5.resize(125,30)        
        layout.addWidget(self.button5,7,2)
        
        layout.setRowMinimumHeight(8, 25)
        
        self.dividingLine2 = QFrame()
        self.dividingLine2.setFrameStyle(QFrame.HLine)
        layout.addWidget(self.dividingLine2,9,1,1,2)
        
        
           
        #record label
        self.recordLbl = QLabel('Raspberry Pi Management')
        self.recordLbl.setAlignment(Qt.AlignHCenter)        
        layout.addWidget(self.recordLbl, 11,1,1,2)
        
        #Button to close SSH connections to pi
        self.button4 = QPushButton('Disconnect', self)
        self.button4.clicked.connect(stop)
        self.button4.resize(125,30)        
        layout.addWidget(self.button4,12,1)
        
        #Button to shutdown raspberry PIs
        self.button6 = QPushButton('Shutdown PIs', self)
        self.button6.clicked.connect(shutdownPIs)
        self.button6.resize(125, 30)        
        layout.addWidget(self.button6,12,2)
        
        layout.setRowMinimumHeight(13, 10)
        
        self.setLayout(layout)
        
       
        
for x in range(0,len(raspberryPIs)):
	raspberryPIs[x] = connecthosts(hosts[x], 'Raspberry Pi' + str((x + 1))) 
	raspberryPIs[x]('uptime', isInfo=True, isPID=False)
	
	 

def main():

    stopRemotePro() #make sure the infinite running video capture program has been killed


    """start the StreamVideoUDP program in Raspberry Pi and record the live video to the 'collection' folder"""
    #for x in range(0,len(raspberryPIs)):
		#raspberryPIs[x]('cd ~/threeDScanner; ./streamVideoUDP',isInfo=False, isPID=False)		      
      
    threads = []
    
    for y in range(0,len(raspberryPIs)):
		items=hosts[y].split(',')		
		port = items[3]
		videoName = ''.join(['/home/james/Videos/collection/StreamVideo' + str(y) + '-',time.strftime("%y%m%d-%H%M%S")])
		t = threading.Thread(target=startStream(port,videoName,y))
		threads.append(t)
		
		
    for t in threads:
			t.start()
			
    for t in threads:
		    t.join()
		    
    print 'Recordings saved to Home/Videos/collection'
		
   
	  

    
if __name__ == '__main__':

    """Set up main window and start UI"""
    app = QApplication(sys.argv)
    window = Window()
    window.setFixedSize(400,400)
    window.setWindowTitle('Command And Control')
    window.show()
    sys.exit(app.exec_())
    
    
   



