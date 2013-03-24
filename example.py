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

def login(room, args):
    if args and len(args) > 1:
        room.login(args[0], args[1])
    elif args:
        room.login(args[0], None)

def logout(room, args):
    room.logout(args)

dictionary = dict() #volatile... of course...
wordCount = dict()
adminList = ["botsmcgee"]
commandList = {"topword": getTopWord,
               "top4lword": getTop4LWord,
               "login": login,
               "logout": logout}
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
        self.polling = dict()
        self.voters = dict()
        self.votes = dict()
        commandList["startPoll"] = self.startPoll
        commandList["endPoll"] = self.endPoll
        commandList["lastPoll"] = self.lastPoll
    
    def onConnect(self, room):
        print("Connected")
        self.polling[room.name] = False
    
    def onReconnect(self, room):
        print("Reconnected")
    
    def onDisconnect(self, room):
        print("Disconnected")
    
    def onMessage(self, room, user, message):
        if room.getLevel(room.getUser) > 0:
            print(user.name, message.ip, message.body)
        else:
            print(formatMsg(message))
        self.handlePolling(room, message)
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
        if(user.name in adminList and
           body[0]==TRIGGER_CHAR):
            handleCommand(pm, message)
        print("you got a message!")
    
    def onLoginFail(self, room):
        print("Login failed in " + room.name)
    
    def onLoginSuccess(self, room, loginType):
        print("Login succeeded in room " + room.name)
    
    def onPMConnect(self, pm):
        print("Connected to PM")
    
    def onPMLoginFail(self, PM):
        print("Login to PM system failed")
    
    def startPoll(self, room, args):
        self.voters[room.name] = list()
        self.votes[room.name] = dict()
        self.polling[room.name] = True
        room.message("Polling has begun please vote a number 0-9 (only your" +
                     "first number will be counted. You only get one vote)")
    
    def endPoll(self, room, args):
        if not self.polling[room.name]:
            return
        self.polling[room.name] = False
        topChoice, numVotes = getPollResults(self.votes[room.name])
        room.message("The winner is: " + topChoice[0] + " (" +
                     str(topChoice[1]) + "/" + str(numVotes) + ")")
    
    def lastPoll(self, room, args):
        topChoice, numVotes = getPollResults(self.votes[room.name])
        room.message("The last poll's winner was: " + topChoice[0] + " (" +
                     str(topChoice[1]) + "/" + str(numVotes) + ")")
    
    def handlePolling(self, room, message):
        if not self.polling[room.name]:
            return
        match = re.match("(?!Polling).*([\d])", message.body)
        if match and not message.user.name in self.voters[room.name]:
            match = match.group(1)
            self.voters[room.name].append(message.user.name)
            self.votes[room.name][match] = self.votes[room.name].get(match, 0) + 1
    

def formatMsg(message):
    return u"<" + time.ctime(message.time) + u">" + message.user.name + u": " + message.body

def analyzeMsg(message):
    global topWord, top4LWord
    body = message.body
    normBody = re.sub("[^\w\s]","", body).lower()
    normBody = normBody.split(" ")
    for word in normBody:
        wordCount[word] = wordCount.get(word, 0) + 1
        if wordCount[word] > topWord[1]:
            topWord = (word, wordCount[word])
        if wordCount[word] > top4LWord[1] and len(word) > 3:
            top4LWord = (word, wordCount[word])

def handleCommand(room, message):
    commandAndArg = message.body[1:].split(" ", 1)
    command = commandAndArg[0]
    args = None if len(commandAndArg)<2 else commandAndArg[1].split(" ")
    commandList.get(command, lambda room, args: None)(room, args)

def getPollResults(votes):
    numVotes = 0
    topChoice = "Nothing", 0
    for choice in votes.keys():
        numVotes += votes[choice]
        if votes[choice] > topChoice[1]:
            topChoice = choice, votes[choice]
    return topChoice, numVotes

if __name__ == "__main__": TestBot.easy_start()
