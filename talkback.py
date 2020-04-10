#!/usr/bin/env python

"""
    talkbot.py 
    
    Use the sound_play client to answer what is heard by the pocketsphinx recognizer.
    
"""

import rospy, os, sys
from std_msgs.msg import String
from sound_play.libsoundplay import SoundClient
from opencv_apps.msg import FaceArrayStamped
from opencv_apps.msg import RotatedRectStamped
from opencv_apps.msg import Face
from opencv_apps.msg import Rect
from opencv_apps.msg import RotatedRect
from opencv_apps.msg import Point2D


class TalkBack:
     def __init__(self, script_path):
         rospy.init_node('talkback')

         rospy.on_shutdown(self.cleanup)

         # Create the sound client object
         #self.soundhandle = SoundClient()
         self.soundhandle = SoundClient(blocking=True)

         # Wait a moment to let the client connect to the sound_play server
         rospy.sleep(1)

         # Make sure any lingering sound_play processes are stopped.
         self.soundhandle.stopAll()

         
         #Announce that we are ready
         self.soundhandle.say('Hello, it is nice to see you again. What can I do for you?',volume=0.1)
         rospy.sleep(3)

         rospy.loginfo("Say one of the navigation commands...")

         # Subscribe to the recognizer output and set the callback function
         rospy.Subscriber('/lm_data', String, self.talkback)

         #the position of face detected
         self.face_x=0
         self.face_y=0
         # Subscribe to the face_detection output
         rospy.Subscriber('/face_detection/faces', FaceArrayStamped, self.face_back)

         #Publish to the take_photo topic to use take_photo node
         self.take_photo = rospy.Publisher("/take_photo", String, queue_size=10)

     def face_back(self,face_data):
         pos = face_data.faces
         if pos:
             self.face_x=pos[0].face.x
             self.face_y=pos[0].face.y

     def talkback(self, msg):
         #Print the recognized words on the screen
         rospy.loginfo(msg.data)

         
         if msg.data.find('TAKE-A-PHOTO')>-1:
             rospy.loginfo("Amanda: OK, please look at the camera and smile.")
             self.soundhandle.say("OK, please look at the camera and smile.", volume=0.1)
             #rospy.sleep(1)
             while(True):
                 if self.face_x<240 and self.face_x>0:
                     if self.face_y<160 and self.face_y>0:
                         rospy.loginfo("Amanda: Please be lower to make you in the center of photo and move a little to your left.")
                         self.soundhandle.say("Please be lower to make you in the center of photo and move a little to your left.", volume=0.1)
                     elif self.face_y>300:
                         rospy.loginfo("Amanda: Please be higher to make you in the center of photo and move a little to your left.")
                         self.soundhandle.say("Please be higher to make you in the center of photo and move a little to your left.", volume=0.1)
                     else:
                         rospy.loginfo("Amanda: Please move a little to your left.")
                         self.soundhandle.say("Please move a little to your left.", volume=0.1)
                     self.face_x=0 
                     self.face_y=0
                     rospy.sleep(1)
                 elif self.face_x>420:
                     if self.face_y<160 and self.face_y>0:
                         rospy.loginfo("Amanda: Please be lower to make you in the center of photo and move a little to your right.")
                         self.soundhandle.say("Please be lower to make you in the center of photo and move a little to your right.", volume=0.1)
                     elif self.face_y>300:
                         rospy.loginfo("Amanda: Please be higher to make you in the center of photo and move a little to your right.")
                         self.soundhandle.say("Please be higher to make you in the center of photo and move a little to your right.", volume=0.1)
                     else:
                         rospy.loginfo("Amanda: Please move a little to your right.")
                         self.soundhandle.say("Please move a little to your right.", volume=0.1)
                     self.face_x=0
                     self.face_y=0
                     rospy.sleep(1)
                 elif self.face_x>=240 and self.face_x<=420:
                     if self.face_y<160 and self.face_y>0:
                         rospy.loginfo("Amanda: Please lower your head.")
                         self.soundhandle.say("Please lower your head.", volume=0.1)
                         self.face_x=0
                         self.face_y=0
                         rospy.sleep(1)
                     elif self.face_y>300:
                         rospy.loginfo("Amanda: Please be higher.")
                         self.soundhandle.say("Please be higher.", volume=0.1)
                         self.face_x=0
                         self.face_y=0
                         rospy.sleep(1)
                     else:
                         rospy.loginfo("Amanda: OK, keep the position. Smile and I will take photo.")
                         self.soundhandle.say("OK, keep the position. Smile and I will take photo.", volume=0.1)
                         break
                 elif self.face_x==0 or self.face_y==0:
                     rospy.loginfo("Amanda: Sorry, I can't see your face in the photo. Please be higher.")
                     self.soundhandle.say("Sorry, I can't see your face in the photo. Please be higher.", volume=0.1)
             rospy.loginfo("Amanda: 3! 2! 1!")
             self.soundhandle.say("3! 2! 1!", volume=0.1)
             self.take_photo.publish('take photo')
             rospy.loginfo("Amanda: Now you can see the photo.")
             self.soundhandle.say("Now you can see the photo.", volume=0.1)
             #rospy.sleep(1)
         elif msg.data=='':
             rospy.sleep(1)
             #rospy.sleep(2)

     def cleanup(self):
         self.soundhandle.stopAll()
         rospy.loginfo("Shutting down talkbot node...")

if __name__=="__main__":
    try:
        TalkBack(sys.path[0])
        rospy.spin()
    except rospy.ROSInterruptException:
        rospy.loginfo("talkback node terminated.")
