import ch
import random
import sys
import re
import time

if sys.version_info[0] > 2:
    import urllib.request as urlreq
else:
    import urllib2 as urlreq

dictionary = dict() #volatile... of course...

dancemoves = [
    "(>^.^)>",
    "(v^.^)v",
    "v(^.^v)",
    "<(^.^<)"
]

class TestBot(ch.RoomManager):
    def onInit(self):
        self.setNameColor("F9F")
        self.setFontColor("F33")
        self.setFontFace("1")
        self.setFontSize(10)
        self.enableBg()
        self.enableRecording()
    
    def onConnect(self, room):
        print("Connected")
        print("You are level: " + str(room.getLevel(self.user)))
    
    def onReconnect(self, room):
        print("Reconnected")
    
    def onDisconnect(self, room):
        print("Disconnected")
    
    def onMessage(self, room, user, message):
        if room.getLevel(self.user) > 0:
            print(user.name, message.ip, message.body)
        else:
            print(formatMsg(message))
    
    def onFloodWarning(self, room):
        room.reconnect()
    
    def onJoin(self, room, user):
        print(str(user) + " joined")
    
    def onLeave(self, room, user):
        print(str(user) + " left")
    
    def onUserCountChange(self, room):
        print("users: " + str(room.usercount))
    
    def onMessageDelete(self, room, user, msg):
        print("Uh oh message deleted")
    
    def onPMMessage(self, pm, user, body):
        print("you got a message!")

def formatMsg(message):
    return "<" + time.ctime(message.time) + ">" + str(message.user.name) + ": " + str(message.body)

if __name__ == "__main__": TestBot.easy_start()
