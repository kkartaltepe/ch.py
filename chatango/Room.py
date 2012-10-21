
################################################################
# Room class
################################################################
class Room(object):
    """Manages a connection with a Chatango room."""
    ####
    # Init
    ####
    def __init__(self, room, uid = None, server = None, port = None, mgr = None):
        # Basic stuff
        self._name = room
        self._server = server or getServer(room)
        self._port = port or 443
        self._mgr = mgr
        
        # Under the hood
        self._connected = False
        self._reconnecting = False
        self._uid = uid or genUid()
        self._rbuf = b""
        self._wbuf = b""
        self._wlockbuf = b""
        self._owner = None
        self._mods = set()
        self._mqueue = dict()
        self._history = list()
        self._userlist = list()
        self._firstCommand = True
        self._connectAmmount = 0
        self._premium = False
        self._userCount = 0
        self._pingTask = None
        self._users = dict()
        self._msgs = dict()
        self._wlock = False
        self._silent = False
        self._banlist = list()
        
        # Inited vars
        if self._mgr: self._connect()
    
    ####
    # User and Message management
    ####
    def getMessage(self, mid):
        return self._msgs.get(mid)
    
    def createMessage(self, msgid, **kw):
        if msgid not in self._msgs:
            msg = Message(msgid = msgid, **kw)
            self._msgs[msgid] = msg
        else:
            msg = self._msgs[msgid]
        return msg
    
    ####
    # Connect/disconnect
    ####
    def _connect(self):
        """Connect to the server."""
        self._sock = socket.socket()
        self._sock.connect((self._server, self._port))
        self._sock.setblocking(False)
        self._firstCommand = True
        self._wbuf = b""
        self._auth()
        self._pingTask = self.mgr.setInterval(self.mgr._pingDelay, self.ping)
        if not self._reconnecting: self.connected = True
    
    def reconnect(self):
        """Reconnect."""
        self._reconnect()
    
    def _reconnect(self):
        """Reconnect."""
        self._reconnecting = True
        if self.connected:
            self._disconnect()
        self._uid = genUid()
        self._connect()
        self._reconnecting = False
    
    def disconnect(self):
        """Disconnect."""
        self._disconnect()
        self._callEvent("onDisconnect")
    
    def _disconnect(self):
        """Disconnect from the server."""
        if not self._reconnecting: self.connected = False
        for user in self._userlist:
            user.clearSessionIds(self)
        self._userlist = list()
        self._pingTask.cancel()
        self._sock.close()
        if not self._reconnecting: del self.mgr._rooms[self.name]
    
    def _auth(self):
        """Authenticate."""
        self._sendCommand("bauth", self.name, self._uid, self.mgr.name, self.mgr.password)
        self._setWriteLock(True)
    
    ####
    # Properties
    ####
    def getName(self): return self._name
    def getManager(self): return self._mgr
    def getUserlist(self, mode = None, unique = None, memory = None):
        ul = None
        if mode == None: mode = self.mgr._userlistMode
        if unique == None: unique = self.mgr._userlistUnique
        if memory == None: memory = self.mgr._userlistMemory
        if mode == Userlist_Recent:
            ul = map(lambda x: x.user, self._history[-memory:])
        elif mode == Userlist_All:
            ul = self._userlist
        if unique:
            return list(set(ul))
        else:
            return ul
    def getUserNames(self):
        ul = self.userlist
        return list(map(lambda x: x.name, ul))
    def getUser(self): return self.mgr.user
    def getOwner(self): return self._owner
    def getOwnerName(self): return self._owner.name
    def getMods(self):
        newset = set()
        for mod in self._mods:
            newset.add(mod)
        return newset
    def getModNames(self):
        mods = self.getMods()
        return [x.name for x in mods]
    def getUserCount(self): return self._userCount
    def getSilent(self): return self._silent
    def setSilent(self, val): self._silent = val
    def getBanlist(self): return [record[2] for record in self._banlist]
        
    name = property(getName)
    mgr = property(getManager)
    userlist = property(getUserlist)
    usernames = property(getUserNames)
    user = property(getUser)
    owner = property(getOwner)
    ownername = property(getOwnerName)
    mods = property(getMods)
    modnames = property(getModNames)
    usercount = property(getUserCount)
    silent = property(getSilent, setSilent)
    banlist = property(getBanlist)
    
    ####
    # Feed/process
    ####
    def _feed(self, data):
        """
        Feed data to the connection.
        
        @type data: bytes
        @param data: data to be fed
        """
        self._rbuf += data
        while self._rbuf.find(b"\x00") != -1:
            data = self._rbuf.split(b"\x00")
            for food in data[:-1]:
                self._process(food.decode().rstrip("\r\n")) #numnumz ;3
            self._rbuf = data[-1]
    
    def _process(self, data):
        """
        Process a command string.
        
        @type data: str
        @param data: the command string
        """
        self._callEvent("onRaw", data)
        data = data.split(":")
        cmd, args = data[0], data[1:]
        func = "rcmd_" + cmd
        if hasattr(self, func):
            getattr(self, func)(args)
    
    ####
    # Received Commands
    ####
    def rcmd_ok(self, args):
        if args[2] != "M": #unsuccesful login
            self._callEvent("onLoginFail")
            self.disconnect()
        self._owner = User(args[0])
        self._uid = args[1]
        self._aid = args[1][4:8]
        self._mods = set(map(lambda x: User(x), args[6].split(";")))
        self._i_log = list()
    
    def rcmd_denied(self, args):
        self._disconnect()
        self._callEvent("onConnectFail")
    
    def rcmd_inited(self, args):
        self._sendCommand("g_participants", "start")
        self._sendCommand("getpremium", "1")
        self.requestBanlist()
        if self._connectAmmount == 0:
            self._callEvent("onConnect")
            for msg in reversed(self._i_log):
                user = msg.user
                self._callEvent("onHistoryMessage", user, msg)
                self._addHistory(msg)
            del self._i_log
        else:
            self._callEvent("onReconnect")
        self._connectAmmount += 1
        self._setWriteLock(False)
    
    def rcmd_premium(self, args):
        if float(args[1]) > time.time():
            self._premium = True
            if self.user._mbg: self.setBgMode(1)
            if self.user._mrec: self.setRecordingMode(1)
        else:
            self._premium = False
    
    def rcmd_mods(self, args):
        modnames = args
        mods = set(map(lambda x: User(x), modnames))
        premods = self._mods
        for user in mods - premods: #modded
            self._mods.add(user)
            self._callEvent("onModAdd", user)
        for user in premods - mods: #demodded
            self._mods.remove(user)
            self._callEvent("onModRemove", user)
        self._callEvent("onModChange")
    
    def rcmd_b(self, args):
        mtime = float(args[0])
        puid = args[3]
        ip = args[6]
        name = args[1]
        rawmsg = ":".join(args[8:])
        msg, n, f = clean_message(rawmsg)
        if name == "":
            nameColor = None
            name = "#" + args[2]
            if name == "#":
                name = "!anon" + getAnonId(n, puid)
        else:
            if n: nameColor = parseNameColor(n)
            else: nameColor = None
        i = args[5]
        unid = args[4]
        #Create an anonymous message and queue it because msgid is unknown.
        if f: fontColor, fontFace, fontSize = parseFont(f)
        else: fontColor, fontFace, fontSize = None, None, None      
        msg = Message(
            time = mtime,
            user = User(name),
            body = msg,
            raw = rawmsg,
            uid = puid,
            ip = ip,
            nameColor = nameColor,
            fontColor = fontColor,
            fontFace = fontFace,
            fontSize = fontSize,
            unid = unid,
            room = self
        )
        self._mqueue[i] = msg
    
    def rcmd_u(self, args):
        msg = self._mqueue[args[0]]
        if msg.user != self.user:
            msg.user._fontColor = msg.fontColor
            msg.user._fontFace = msg.fontFace
            msg.user._fontSize = msg.fontSize
            msg.user._nameColor = msg.nameColor
        del self._mqueue[args[0]]
        msg.attach(self, args[1])
        self._addHistory(msg)
        self._callEvent("onMessage", msg.user, msg)
    
    def rcmd_i(self, args):
        mtime = float(args[0])
        puid = args[3]
        ip = args[6]
        if ip == "": ip = None
        name = args[1]
        rawmsg = ":".join(args[8:])
        msg, n, f = clean_message(rawmsg)
        msgid = args[5]
        if name == "":
            nameColor = None
            name = "#" + args[2]
            if name == "#":
                name = "!anon" + getAnonId(n, puid)
        else:
            if n: nameColor = parseNameColor(n)
            else: nameColor = None
        if f: fontColor, fontFace, fontSize = parseFont(f)
        else: fontColor, fontFace, fontSize = None, None, None
        msg = self.createMessage(
            msgid = msgid,
            time = mtime,
            user = User(name),
            body = msg,
            raw = rawmsg,
            ip = args[6],
            unid = args[4],
            nameColor = nameColor,
            fontColor = fontColor,
            fontFace = fontFace,
            fontSize = fontSize,
            room = self
        )
        if msg.user != self.user:
            msg.user._fontColor = msg.fontColor
            msg.user._fontFace = msg.fontFace
            msg.user._fontSize = msg.fontSize
            msg.user._nameColor = msg.nameColor
        self._i_log.append(msg)
    
    def rcmd_g_participants(self, args):
        args = ":".join(args)
        args = args.split(";")
        for data in args:
            data = data.split(":")
            name = data[3].lower()
            if name == "none": continue
            user = User(
                name = name,
                room = self
            )
            user.addSessionId(self, data[0])
            self._userlist.append(user)
    
    def rcmd_participant(self, args):
        if args[0] == "0": #leave
            name = args[3].lower()
            if name == "none": return
            user = User(name)
            user.removeSessionId(self, args[1])
            self._userlist.remove(user)
            if user not in self._userlist or not self.mgr._userlistEventUnique:
                self._callEvent("onLeave", user)
        else: #join
            name = args[3].lower()
            if name == "none": return
            user = User(
                name = name,
                room = self
            )
            user.addSessionId(self, args[1])
            if user not in self._userlist: doEvent = True
            else: doEvent = False
            self._userlist.append(user)
            if doEvent or not self.mgr._userlistEventUnique:
                self._callEvent("onJoin", user)
    
    def rcmd_show_fw(self, args):
        self._callEvent("onFloodWarning")
    
    def rcmd_show_tb(self, args):
        self._callEvent("onFloodBan")
    
    def rcmd_tb(self, args):
        self._callEvent("onFloodBanRepeat")
    
    def rcmd_delete(self, args):
        msg = self.getMessage(args[0])
        if msg:
            if msg in self._history:
                self._history.remove(msg)
                self._callEvent("onMessageDelete", msg.user, msg)
                msg.detach()
    
    def rcmd_deleteall(self, args):
        for msgid in args:
            self.rcmd_delete([msgid])
    
    def rcmd_n(self, args):
        self._userCount = int(args[0], 16)
        self._callEvent("onUserCountChange")
    
    def rcmd_blocklist(self, args):
        self._banlist = list()
        sections = ":".join(args).split(";")
        for section in sections:
            params = section.split(":")
            if len(params) != 5: continue
            if params[2] == "": continue
            self._banlist.append((
                params[0], #unid
                params[1], #ip
                User(params[2]), #target
                float(params[3]), #time
                User(params[4]) #src
            ))
        self._callEvent("onBanlistUpdate")
    
    def rcmd_blocked(self, args):
        if args[2] == "": return
        target = User(args[2])
        user = User(args[3])
        self._banlist.append((args[0], args[1], target, float(args[4]), user))
        self._callEvent("onBan", user, target)
        self.requestBanlist()
    
    def rcmd_unblocked(self, args):
        if args[2] == "": return
        target = User(args[2])
        user = User(args[3])
        self._callEvent("onUnban", user, target)
        self.requestBanlist()
    
    ####
    # Commands
    ####
    def ping(self):
        """Send a ping."""
        self._sendCommand("")
        self._callEvent("onPing")
    
    def rawMessage(self, msg):
        """
        Send a message without n and f tags.
        
        @type msg: str
        @param msg: message
        """
        if not self._silent:
            self._sendCommand("bmsg", msg)
    
    def message(self, msg, html = False):
        """
        Send a message.
        
        @type msg: str
        @param msg: message
        """
        if not html:
            msg = msg.replace("<", "&lt;").replace(">", "&gt;")
        if len(msg) > self.mgr._maxLength:
            if self.mgr._tooBigMessage == BigMessage_Cut:
                self.message(msg[:self.mgr._maxLength], html = html)
            elif self.mgr._tooBigMessage == BigMessage_Multiple:
                while len(msg) > 0:
                    sect = msg[:self.mgr._maxLength]
                    msg = msg[self.mgr._maxLength:]
                    self.message(sect, html = html)
            return
        msg = "<n" + self.user.nameColor + "/>" + msg
        msg = "<f x%0.2i%s=\"%s\">" %(self.user.fontSize, self.user.fontColor, self.user.fontFace) + msg
        msg = "pi11:" + msg #we gotta figure out what this is but for now this works
        self.rawMessage(msg)
    
    def setBgMode(self, mode):
        self._sendCommand("msgbg", str(mode))
    
    def setRecordingMode(self, mode):
        self._sendCommand("msgmedia", str(mode))

    def addMod(self, user):
        """
        Add a moderator.
        
        @type user: User
        @param user: User to mod.
        """
        if self.getLevel(self.user) == 2:
            self._sendCommand("addmod", user.name)
        
    def removeMod(self, user):
        """
        Remove a moderator.
        
        @type user: User
        @param user: User to demod.
        """
        if self.getLevel(self.user) == 2:
            self._sendCommand("removemod", user.name)
    
    def flag(self, message):
        """
        Flag a message.
        
        @type message: Message
        @param message: message to flag
        """
        self._sendCommand("g_flag", message.msgid)
    
    def flagUser(self, user):
        """
        Flag a user.
        
        @type user: User
        @param user: user to flag
        
        @rtype: bool
        @return: whether a message to flag was found
        """
        msg = self.getLastMessage(user)
        if msg:
            self.flag(msg)
            return True
        return False
    
    def delete(self, message):
        """
        Delete a message. (Moderator only)
        
        @type message: Message
        @param message: message to delete
        """
        if self.getLevel(self.user) > 0:
            self._sendCommand("delmsg", message.msgid)
    
    def rawClearUser(self, unid):
        self._sendCommand("delallmsg", unid)
    
    def clearUser(self, user):
        """
        Clear all of a user's messages. (Moderator only)
        
        @type user: User
        @param user: user to delete messages of
        
        @rtype: bool
        @return: whether a message to delete was found
        """
        if self.getLevel(self.user) > 0:
            msg = self.getLastMessage(user)
            if msg:
                self.rawClearUser(msg.unid)
            return True
        return False
    
    def clearall(self):
        """Clear all messages. (Owner only)"""
        if self.getLevel(self.user) == 2:
            self._sendCommand("clearall")
    
    def rawBan(self, name, ip, unid):
        """
        Execute the block command using specified arguments.
        (For advanced usage)
        
        @type name: str
        @param name: name
        @type ip: str
        @param ip: ip address
        @type unid: str
        @param unid: unid
        """
        self._sendCommand("block", unid, ip, name)
    
    def ban(self, msg):
        """
        Ban a message's sender. (Moderator only)
        
        @type message: Message
        @param message: message to ban sender of
        """
        if self.getLevel(self.user) > 0:
            self.rawBan(msg.user.name, msg.ip, msg.unid)
    
    def banUser(self, user):
        """
        Ban a user. (Moderator only)
        
        @type user: User
        @param user: user to ban
        
        @rtype: bool
        @return: whether a message to ban the user was found
        """
        msg = self.getLastMessage(user)
        if msg:
            self.ban(msg)
            return True
        return False
    
    def requestBanlist(self):
        """Request an updated banlist."""
        self._sendCommand("blocklist", "block", "", "next", "500")
    
    def rawUnban(self, name, ip, unid):
        """
        Execute the unblock command using specified arguments.
        (For advanced usage)
        
        @type name: str
        @param name: name
        @type ip: str
        @param ip: ip address
        @type unid: str
        @param unid: unid
        """
        self._sendCommand("removeblock", unid, ip, name)
    
    def unban(self, user):
        """
        Unban a user. (Moderator only)
        
        @type user: User
        @param user: user to unban
        
        @rtype: bool
        @return: whether it succeeded
        """
        rec = self._getBanRecord(user)
        if rec:
            self.rawUnban(rec[2].name, rec[1], rec[0])
            return True
        else:
            return False
    
    ####
    # Util
    ####
    def _getBanRecord(self, user):
        for record in self._banlist:
            if record[2] == user:
                return record
        return None
    
    def _callEvent(self, evt, *args, **kw):
        getattr(self.mgr, evt)(self, *args, **kw)
        self.mgr.onEventCalled(self, evt, *args, **kw)
    
    def _write(self, data):
        if self._wlock:
            self._wlockbuf += data
        else:
            self.mgr._write(self, data)
    
    def _setWriteLock(self, lock):
        self._wlock = lock
        if self._wlock == False:
            self._write(self._wlockbuf)
            self._wlockbuf = b""
    
    def _sendCommand(self, *args):
        """
        Send a command.
        
        @type args: [str, str, ...]
        @param args: command and list of arguments
        """
        if self._firstCommand:
            terminator = b"\x00"
            self._firstCommand = False
        else:
            terminator = b"\r\n\x00"
        print(":".join(args).encode())
        self._write(":".join(args).encode() + terminator)
    
    def getLevel(self, user):
        if user == self._owner: return 2
        if user in self._mods: return 1
        return 0
    
    def getLastMessage(self, user = None):
        if user:
            try:
                i = 1
                while True:
                    msg = self._history[-i]
                    if msg.user == user:
                        return msg
                    i += 1
            except IndexError:
                return None
        else:
            try:
                return self._history[-1]
            except IndexError:
                return None
        return None
    
    def findUser(self, name):
        name = name.lower()
        ul = self.getUserlist()
        udi = dict(zip([u.name for u in ul], ul))
        cname = None
        for n in udi.keys():
            if n.find(name) != -1:
                if cname: return None #ambigious!!
                cname = n
        if cname: return udi[cname]
        else: return None
    
    ####
    # History
    ####
    def _addHistory(self, msg):
        """
        Add a message to history.
        
        @type msg: Message
        @param msg: message
        """
        self._history.append(msg)
        if len(self._history) > self.mgr._maxHistoryLength:
            rest, self._history = self._history[:-self.mgr._maxHistoryLength], self._history[-self.mgr._maxHistoryLength:]
            for msg in rest: msg.detach()

