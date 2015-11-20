__author__ = 'SG'

import sys
import time

from BrickPi import *

#PORT = 8080

def motorRotateDegree2(power,deg,port,sampling_time=.1,delay_when_stopping=.05):
    """Rotate the selected motors by specified degre

    Args:
      power    : an array of the power values at which to rotate the motors (0-255)
      deg    : an array of the angle's (in degrees) by which to rotate each of the motor
      port    : an array of the port's on which the motor is connected
      sampling_time  : (optional) the rate(in seconds) at which to read the data in the encoders
	  delay_when_stopping:	(optional) the delay (in seconds) for which the motors are run in the opposite direction before stopping

    Returns:
      0 on success

    Usage:
      Pass the arguments in a list. if a single motor has to be controlled then the arguments should be
      passed like elements of an array,e.g, motorRotateDegree([255],[360],[PORT_A]) or
      motorRotateDegree([255,255],[360,360],[PORT_A,PORT_B])
    """

    num_motor=len(power)    #Number of motors being used, len(power) gets the size of power array
    init_val=[0]*num_motor
    final_val=[0]*num_motor
    BrickPiUpdateValues()
    for i in range(num_motor):
        BrickPi.MotorEnable[port[i]] = 1        #Enable the Motors
        power[i]=abs(power[i])
        #For running clockwise and anticlockwise
        if deg[i]>0:
			BrickPi.MotorSpeed[port[i]] = power[i]
        elif deg[i]<0:
			BrickPi.MotorSpeed[port[i]] = -power[i]
        else:
            BrickPi.MotorSpeed[port[i]] = 0
        init_val[i]=BrickPi.Encoder[port[i]]        #Initial reading of the encoder
        final_val[i]=(init_val[i]+deg[i]*2)        #Final value when the motor has to be stopped;One encoder value counts for 0.5 degrees
    run_stat=[0]*num_motor
    while True:
        result = BrickPiUpdateValues()          #Ask BrickPi to update values for sensors/motors
        if not result :
            print ( BrickPi.Encoder[port[i]] %720 ) /2   # print the encoder degrees
            for i in range(num_motor):        #Do for each of the motors
                if run_stat[i]==1:
                    continue
                # Check if final value reached for each of the motors
                if(deg[i]>0 and final_val[i]>init_val[i]) or (deg[i]<0 and final_val[i]<init_val[i]) :
                    # Read the encoder degrees, and update the init_val
                    init_val[i]=BrickPi.Encoder[port[i]]
                else:
                    run_stat[i]=1
                    if deg[i]>0:
                        BrickPi.MotorSpeed[port[i]] = -power[i]
                    elif deg[i]<0:
			BrickPi.MotorSpeed[port[i]] = power[i]
                    else:
			BrickPi.MotorSpeed[port[i]] = 0
                    BrickPiUpdateValues()
                    time.sleep(delay_when_stopping)
                    BrickPi.MotorEnable[port[i]] = 0
                    BrickPiUpdateValues()
        time.sleep(sampling_time)          #sleep for the sampling time given (default:100 ms)
        if(all(e==1 for e in run_stat)):        #If all the motors have already completed their rotation, then stop
          break
    return 0

BrickPiSetup()  # setup the serial port for sudo su communication
BrickPiSetupSensors()       #Send the properties of sensors to BrickPi
BrickPiUpdateValues()



class Motor():
    """get the parameters from the system args"""
    angle = int(sys.argv[1])
    power = [int(sys.argv[2])]
    loop = int(sys.argv[3])
    sleeptime = int(sys.argv[4])

    time.sleep(0.1)

    print "Motor will turn with these parameters:\n"
    print "angle = %d \t" % angle
    print "power = %d \t" % power[0]
    print "loop = %d \t" % loop
    print "sleeptime = %d \t\n" % sleeptime

    deg=[angle]
    port=[PORT_A]

	"""send parameters to and run the motorRotateDegree2 function"""
    for i in range(loop):
        motorRotateDegree2(power,deg,port,0)
        print "Motor turned% d times" % (i+1)
        time.sleep(sleeptime)  #sleeptime, unit s

    print "Operation finished."


if __name__ == '__main__':
    motor = Motor
 
