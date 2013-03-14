import ch
import random
import sys
import re
import time

if sys.version_info[0] > 2:
    import urllib.request as urlreq
else:
    import urllib2 as urlreq

def getTopWord(room, args):
    room.message("The top word so far is: " + topWord[0]
                 + "(" + str(topWord[1]) + ")")

def getTop4LWord(room, args):
    room.message("The top 4+ letter word so far is: " + top4LWord[0]
                 + "(" + str(top4LWord[1]) + ")")

dictionary = dict() #volatile... of course...
wordCount = dict()
adminList = ["botsmcgee"]
commandList = {"topword": getTopWord,
               "top4lword": getTop4LWord}
TRIGGER_CHAR = '!'
topWord = "", 0
top4LWord = "", 0

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
    
    def onReconnect(self, room):
        print("Reconnected")
    
    def onDisconnect(self, room):
        uniqueWords = 0
        print("Most used word is \"" + topWord[0] + "\"(" + str(topWord[1]) + ")")
        print("Most used 4+ letter word is \"" + top4LWord[0] + "\"(" + str(top4LWord[1]) + ")")
        print("There were " + str(uniqueWords) + " different words captured")
        print("Disconnected")
    
    def onMessage(self, room, user, message):
        if room.getLevel(self.user) > 0:
            print(user.name, message.ip, message.body)
        else:
            print(formatMsg(message))
        if(message.user.name in adminList and
           message.body[0]==TRIGGER_CHAR):
            handleCommand(room, message)
        analyzeMsg(message)
    
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
        if(message.user.name in adminList and
           message.body[0]==TRIGGER_CHAR):
            handleCommand(pm, message)
        print("you got a message!")
    
    def onLoginFail(self, room):
        print("Login failed in " + room.name + ", continuing as anon")
    
    def onPMLoginFail(self, PM):
        print("Login to PM system failed")


def formatMsg(message):
    return u"<" + time.ctime(message.time) + u">" + message.user.name + u": " + message.body

def analyzeMsg(message):
    global topWord, top4LWord
    body = message.body
    normBody = re.sub("[^\w\s]","", body).lower()
    normBody = normBody.split(" ")
    for word in normBody:
        wordCount[word] = wordCount.get(word, 0)+1
        if wordCount[word] > topWord[1]:
            topWord = (word, wordCount[word])
        if wordCount[word] > top4LWord[1] and len(word) > 3:
            top4LWord = (word, wordCount[word])

def handleCommand(room, message):
    commandAndArg = message.body[1:].split(" ", 1)
    command = commandAndArg[0]
    args = None if len(commandAndArg)<2 else commandAndArg[1]
    commandList.get(command, lambda room, args: None)(room, args)


if __name__ == "__main__": TestBot.easy_start()
