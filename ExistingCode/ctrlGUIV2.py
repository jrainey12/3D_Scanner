__author__ = 'SGong'

"""
This file sets up a simple user interface to start/stop the remote programs, 
VLC viewing, records the video and grabs images from the video.
"""

import sys
from PyQt4 import QtGui

import paramiko
import socket
import vlc
from subprocess import *
import time

connections = [] #remote ssh connections


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
		
        items=hostInfo.split(',')
        print "Connecting to %s..." % deviceName
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(items[0],
                           username=items[1],
                           password=items[2])
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



#close all the SSH connections, and processes
def stop():
	"""disconnect the ssh connections"""
for conn in connections:
        print conn
        conn.close()
connections[:]=[]
print 'SSH connections are off.'


def vlcView():
    """run the capture.c file in remote system with """
    remoteBBB('cd /home/debian/boneCV; ./streamVideoUDP_infinite',isInfo=False, isPID=False)
    p = vlc.MediaPlayer('udp://@:1234')
    p.play()
    #call(['cvlc', 'udp://@:1234', '--play-and-exit']) #this one blocks the interface

def stopRemotePro():
	"""stop the capture program in beaglebone"""
        capturePID = remoteBBB('pidof capture',isInfo=False, isPID=True)
        if capturePID: #kill the remote proess when the pid returned is not zero
		killcommand = 'kill -9 {pid}'.format(pid=capturePID)
		remoteBBB(killcommand,isInfo=True, isPID=False)


class ctrlGUI(QtGui.QWidget):
	"""set up the interface"""
def __init__(self):
        super(ctrlGUI, self).__init__()
        self.initUI()

def initUI(self):
    """
	Four buttons:
	bt1: start, once hit, start the main function
	bt2: stop, disconnect the SSH connections
	bt3: VLC viewing, show the live stream in VLC
	bt4: stop the remote running capture.c file
	"""
	    
    btn3 = QtGui.QPushButton('VLC viewing', self)
    btn3.resize(btn3.sizeHint())
    btn3.move(50, 100)
    btn3.clicked.connect(vlcView)

    btn4 = QtGui.QPushButton('stop viewing', self)
    btn4.resize(btn4.sizeHint())
    btn4.move(200, 100)
    btn4.clicked.connect(stopRemotePro)


        #Button to send parameters to raspberryPi
    btn1 = QtGui.QPushButton('Start', self)
    btn1.resize(btn1.sizeHint())
    btn1.move(50, 200)
    btn1.clicked.connect(main)

        #caution /lambda:/ is needed here to avoid the typeError:
        #connect() slotargument should be a callable or a signal, not nonType.
        #when the function eg. test() has no input parameter, then it can be simply written btn.clicked.connect(test), otherwise should be btn.clicked.connect(lambda: test(x))

        #Button to close all the ssh
    btn2 = QtGui.QPushButton('Stop', self)
    btn2.resize(btn2.sizeHint())
    btn2.move(200, 200)
    btn2.clicked.connect(stop)


    self.setGeometry(300, 300, 500, 500)
    self.setWindowTitle('Control Interface')
    self.show()


'''******************Here starts the main program******************'''

"""the global variables"""
#list details of the connections
#hosts = ['192.168.0.13,root,root','192.168.0.102,pi,raspberry']
hosts = ['10.42.0.21,pi,raspberry','192.168.0.102,pi,raspberry']

#connection with beaglebone
remoteBBB = connecthosts(hosts[0], 'Beaglebone Black')
remoteBBB('uptime', isInfo=True, isPID=False)

#connection with raspberryPi
#remoteRPI = connecthosts(hosts[1], 'RaspberryPi')
#remoteRPI('uptime', isInfo=True, isPID=False)




def main():

    stopRemotePro() #make sure the infinite running video capture program has been killed

    loop = 2 #define how many times that the motor should turn
	
    for i in range(loop):

        """run the motor control program in raspberryPi, the parameters passed through are angle, power, turn times, sleep time"""
        remoteRPI('cd /home/pi/Desktop/BrickPi_Python/Sensor_Examples; python motorCtrl.py 180 90 1 0',isInfo=True, isPID=False)
        time.sleep(1)
        print 'Current time {} \n'.format(time.strftime("%H%M%S"))

        """start the StreamVideoUDP program in Beaglebone and record the live video to the 'collection' folder"""
        videoName = ''.join(['/home/threedscanner/SG_pros/ctrlGUIV2/collection/StreamVideo-',time.strftime("%y%m%d-%H%M%S")])
        remoteBBB('cd /home/debian/boneCV; ./streamVideoUDP',isInfo=False, isPID=False)
        cmd1 = "socat  -d -d -d -u -T 10 UDP4-RECV:1234,reuseaddr OPEN:" + videoName + ",creat,append"
        process1 = Popen(cmd1, shell=True)
        process1.wait()

        """grab five images from the freshly recorded video"""
        cmd2 = "/home/threedscanner/bin/ffmpeg -i " + videoName + " -r 0.3 -f image2 " + videoName + "_%d.jpg"
        process2 = Popen(cmd2, shell=True)
        process2.wait()


if __name__ == '__main__':

    """start the user interface"""
    app = QtGui.QApplication(sys.argv) #The basic GUI widgets are located in the QtGui module
    ex = ctrlGUI()
    sys.exit(app.exec_())
