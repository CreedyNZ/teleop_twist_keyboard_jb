#!/usr/bin/env python
import roslib; roslib.load_manifest('teleop_twist_keyboard')
import rospy

from geometry_msgs.msg import Twist, Transform
from ros_arduino_msgs.msg import PhoenixState
import sys, select, termios, tty

msg = """
Reading from the keyboard  and Publishing to Twist!
---------------------0------
Moving around:
   u    i    o
   j    k    l
   m    ,    .

v : rotate left
b ; rotate right

q/z : increase/decrease max speeds by 10%
w/x : increase/decrease only linear speed by 10%
e/c : increase/decrease only angular speed by 10%
anything else : stop

CTRL-C to quit
"""

moveBindings = {
        'i':(1,0),
        'o':(1,-1),
        'j':(0,1),
        'l':(0,-1),
        'u':(1,1),
        ',':(-1,0),
        '.':(-1,1),
        'm':(-1,-1),
           }

translateBindings = {
        'I':(1,0,0),
        'O':(1,-1,0),
        'J':(0,1,0),
        'L':(0,-1,0),
        'U':(1,1,0),
        '"':(-1,0,0),
        '>':(-1,1,0),
        '>':(-1,-1,0),
	'(':(0,0,-1),
        ')':(0,0,1),
           }


rotateBindings = {
        '[':(1),
        ']':(-1),
           }

speedBindings={
        'q':(1.1,1.1),
        'z':(.9,.9),
        'w':(1.1,1),
        'x':(.9,1),
        'e':(1,1.1),
        'c':(1,.9),
          }

gaitBindings = {
        '1':(1),
        '2':(2),
        '3':(3),
        '4':(4),
        '5':(5),
        '6':(6),
           }

stateBindings = {
        'b':(1),
        'n':(0),
        'd':(2),
        '9':(3),
	'0':(4),
           }

def getKey():
    tty.setraw(sys.stdin.fileno())
    select.select([sys.stdin], [], [], 0)
    key = sys.stdin.read(1)
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

speed = .5
turn = 1

def vels(speed,turn):
    return "currently:\tspeed %s\tturn %s " % (speed,turn)

if __name__=="__main__":
    settings = termios.tcgetattr(sys.stdin)

    pub = rospy.Publisher('cmd_vel', Twist)
    pubtranslate = rospy.Publisher('cmd_trans', Transform)
    pubstate = rospy.Publisher('cmd_phstate', PhoenixState)
    rospy.init_node('teleop_twist_keyboard')

    x = 0
    y =0
    th = 0
    tx = 0
    ty =0
    tz = 0
    rx = 0
    ry =0
    rz = 0
    rw = 0
    state = [0,0,0]
    status = 0
   
    gaitkey = 1

    
    try:
        print msg
        print vels(speed,turn)
        while(1):
            key = getKey()
            if key in moveBindings.keys():
                x = moveBindings[key][0]
                y = moveBindings[key][1]
	    elif key in translateBindings.keys():
                tx = translateBindings[key][0]
                ty = translateBindings[key][1]
		tz = translateBindings[key][2]
            elif key in rotateBindings.keys():
                th = rotateBindings[key]
	    elif key in gaitBindings.keys():
                gaitkey = gaitBindings[key]
            elif key in stateBindings.keys():
                if stateBindings[key] == 0:
		   state = [0,0,1]
		elif stateBindings[key] == 1:
		   state[0] = 1
		elif stateBindings[key] == 2:
		   state[1] = 1
		elif stateBindings[key] == 3:
		   state[2] = 0
		elif stateBindings[key] == 4:
		   state[2] = 1
            elif key in speedBindings.keys():
                speed = speed * speedBindings[key][0]
                turn = turn * speedBindings[key][1]

                print vels(speed,turn)
                if (status == 14):
                    print msg
                status = (status + 1) % 15
            else:
                x = 0
                y = 0
                th = 0
                if (key == '\x03'):
                    break

            twist = Twist()
            twist.linear.x = x*speed; twist.linear.y = y*speed; twist.linear.z = 0
            twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = th*turn
            pub.publish(twist)
 	    transform = Transform()
            transform.translation.x = tx*speed; transform.translation.y = ty*speed; transform.translation.z = tz*speed
            transform.rotation.x = rx*speed; transform.rotation.y = ry*speed; transform.rotation.z = rz*speed; transform.rotation.w = rw*speed
            pubtranslate.publish(transform)
	    phstate = PhoenixState()
	    phstate.gait = gaitkey
	    phstate.balance = state[0]
	    phstate.doubleT = state[1]
	    phstate.stand = state[2]
	    pubstate.publish(phstate)
																					

    except:
        print "Keyboard Error"
	e = sys.exc_info()[0]
	f = sys.exc_info()[1]
   	print  e 
	print f

    finally:
        twist = Twist()
        twist.linear.x = 0; twist.linear.y = 0; twist.linear.z = 0
        twist.angular.x = 0; twist.angular.y = 0; twist.angular.z = 0
        pub.publish(twist)
	phstate = PhoenixState()
	phstate.gait = gaitkey
	phstate.balance = state[0]
	phstate.doubleT = state[1]
	phstate.stand = state[2]
	pubstate.publish(phstate)
        
	termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)


