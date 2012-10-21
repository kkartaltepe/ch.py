
################################################################
# RoomManager class
################################################################
class RoomManager(object):
    """Class that manages multiple connections."""
    ####
    # Config
    ####
    _Room = Room
    _PM = PM
    _PMHost = "c1.chatango.com"
    _PMPort = 5222
    _TimerResolution = 0.2 #at least x times per second
    _pingDelay = 20
    _userlistMode = Userlist_Recent
    _userlistUnique = True
    _userlistMemory = 50
    _userlistEventUnique = False
    _tooBigMessage = BigMessage_Multiple
    _maxLength = 1800
    _maxHistoryLength = 150
    
    ####
    # Init
    ####
    def __init__(self, name = None, password = None, pm = True):
        self._name = name
        self._password = password
        self._running = False
        self._tasks = set()
        self._rooms = dict()
        if pm:
            self._pm = self._PM(mgr = self)
        else:
            self._pm = None
    
    ####
    # Join/leave
    ####
    def joinRoom(self, room):
        """
        Join a room or return None if already joined.
        
        @type room: str
        @param room: room to join
        
        @rtype: Room or None
        @return: the room or nothing
        """
        room = room.lower()
        if room not in self._rooms:
            con = self._Room(room, mgr = self)
            self._rooms[room] = con
            return con
        else:
            return None
    
    def leaveRoom(self, room):
        """
        Leave a room.
        
        @type room: str
        @param room: room to leave
        """
        room = room.lower()
        if room in self._rooms:
            con = self._rooms[room]
            con.disconnect()
    
    def getRoom(self, room):
        """
        Get room with a name, or None if not connected to this room.
        
        @type room: str
        @param room: room
        
        @rtype: Room
        @return: the room
        """
        room = room.lower()
        if room in self._rooms:
            return self._rooms[room]
        else:
            return None
    
    ####
    # Properties
    ####
    def getUser(self): return User(self._name)
    def getName(self): return self._name
    def getPassword(self): return self._password
    def getRooms(self): return set(self._rooms.values())
    def getRoomNames(self): return set(self._rooms.keys())
    def getPM(self): return self._pm
    
    user = property(getUser)
    name = property(getName)
    password = property(getPassword)
    rooms = property(getRooms)
    roomnames = property(getRoomNames)
    pm = property(getPM)
    
    ####
    # Virtual methods
    ####
    def onInit(self):
        """Called on init."""
        pass
    
    def onConnect(self, room):
        """
        Called when connected to the room.
        
        @type room: Room
        @param room: room where the event occured
        """
        pass
    
    def onReconnect(self, room):
        """
        Called when reconnected to the room.
        
        @type room: Room
        @param room: room where the event occured
        """
        pass
    
    def onConnectFail(self, room):
        """
        Called when the connection failed.
        
        @type room: Room
        @param room: room where the event occured
        """
        pass
    
    def onDisconnect(self, room):
        """
        Called when the client gets disconnected.
        
        @type room: Room
        @param room: room where the event occured
        """
        pass
    
    def onLoginFail(self, room):
        """
        Called on login failure, disconnects after.
        
        @type room: Room
        @param room: room where the event occured
        """
        pass
    
    def onFloodBan(self, room):
        """
        Called when either flood banned or flagged.
        
        @type room: Room
        @param room: room where the event occured
        """
        pass
    
    def onFloodBanRepeat(self, room):
        """
        Called when trying to send something when floodbanned.
        
        @type room: Room
        @param room: room where the event occured
        """
        pass
    
    def onFloodWarning(self, room):
        """
        Called when an overflow warning gets received.
        
        @type room: Room
        @param room: room where the event occured
        """
        pass
    
    def onMessageDelete(self, room, user, message):
        """
        Called when a message gets deleted.
        
        @type room: Room
        @param room: room where the event occured
        @type user: User
        @param user: owner of deleted message
        @type message: Message
        @param message: message that got deleted
        """
        pass
    
    def onModChange(self, room):
        """
        Called when the moderator list changes.
        
        @type room: Room
        @param room: room where the event occured
        """
        pass
    
    def onModAdd(self, room, user):
        """
        Called when a moderator gets added.
        
        @type room: Room
        @param room: room where the event occured
        """
        pass
    
    def onModRemove(self, room, user):
        """
        Called when a moderator gets removed.
        
        @type room: Room
        @param room: room where the event occured
        """
        pass
    
    def onMessage(self, room, user, message):
        """
        Called when a message gets received.
        
        @type room: Room
        @param room: room where the event occured
        @type user: User
        @param user: owner of message
        @type message: Message
        @param message: received message
        """
        pass
    
    def onHistoryMessage(self, room, user, message):
        """
        Called when a message gets received from history.
        
        @type room: Room
        @param room: room where the event occured
        @type user: User
        @param user: owner of message
        @type message: Message
        @param message: the message that got added
        """
        pass
    
    def onJoin(self, room, user):
        """
        Called when a user joins. Anonymous users get ignored here.
        
        @type room: Room
        @param room: room where the event occured
        @type user: User
        @param user: the user that has joined
        """
        pass
    
    def onLeave(self, room, user):
        """
        Called when a user leaves. Anonymous users get ignored here.
        
        @type room: Room
        @param room: room where the event occured
        @type user: User
        @param user: the user that has left
        """
        pass
    
    def onRaw(self, room, raw):
        """
        Called before any command parsing occurs.
        
        @type room: Room
        @param room: room where the event occured
        @type raw: str
        @param raw: raw command data
        """
        pass
    
    def onPing(self, room):
        """
        Called when a ping gets sent.
        
        @type room: Room
        @param room: room where the event occured
        """
        pass
    
    def onUserCountChange(self, room):
        """
        Called when the user count changes.
        
        @type room: Room
        @param room: room where the event occured
        """
        pass
    
    def onBan(self, room, user, target):
        """
        Called when a user gets banned.
        
        @type room: Room
        @param room: room where the event occured
        @type user: User
        @param user: user that banned someone
        @type target: User
        @param target: user that got banned
        """
        pass
    
    def onUnban(self, room, user, target):
        """
        Called when a user gets unbanned.
        
        @type room: Room
        @param room: room where the event occured
        @type user: User
        @param user: user that unbanned someone
        @type target: User
        @param target: user that got unbanned
        """
        pass
    
    def onBanlistUpdate(self, room):
        """
        Called when a banlist gets updated.
        
        @type room: Room
        @param room: room where the event occured
        """
        pass
    
    def onPMConnect(self, pm):
        pass
    
    def onPMDisconnect(self, pm):
        pass
    
    def onPMPing(self, pm):
        pass
    
    def onPMMessage(self, pm, user, body):
        pass
    
    def onPMOfflineMessage(self, pm, user, body):
        pass
    
    def onPMContactlistReceive(self, pm):
        pass
    
    def onPMBlocklistReceive(self, pm):
        pass
    
    def onPMContactAdd(self, pm, user):
        pass
    
    def onPMContactRemove(self, pm, user):
        pass
    
    def onPMBlock(self, pm, user):
        pass
    
    def onPMUnblock(self, pm, user):
        pass
    
    def onPMContactOnline(self, pm, user):
        pass
    
    def onPMContactOffline(self, pm, user):
        pass
    
    def onEventCalled(self, room, evt, *args, **kw):
        """
        Called on every room-based event.
        
        @type room: Room
        @param room: room where the event occured
        @type evt: str
        @param evt: the event
        """
        pass
    
    ####
    # Deferring
    ####
    def deferToThread(self, callback, func, *args, **kw):
        """
        Defer a function to a thread and callback the return value.
        
        @type callback: function
        @param callback: function to call on completion
        @type cbargs: tuple or list
        @param cbargs: arguments to get supplied to the callback
        @type func: function
        @param func: function to call
        """
        def f(func, callback, *args, **kw):
            ret = func(*args, **kw)
            self.setTimeout(0, callback, ret)
        threading._start_new_thread(f, (func, callback) + args, kw)
    
    ####
    # Scheduling
    ####
    class _Task(object):
        def cancel(self):
            """Sugar for removeTask."""
            self.mgr.removeTask(self)
    
    def _tick(self):
        now = time.time()
        for task in set(self._tasks):
            if task.target <= now:
                task.func(*task.args, **task.kw)
                if task.isInterval:
                    task.target = now + task.timeout
                else:
                    self._tasks.remove(task)
    
    def setTimeout(self, timeout, func, *args, **kw):
        """
        Call a function after at least timeout seconds with specified arguments.
        
        @type timeout: int
        @param timeout: timeout
        @type func: function
        @param func: function to call
        
        @rtype: _Task
        @return: object representing the task
        """
        task = self._Task()
        task.mgr = self
        task.target = time.time() + timeout
        task.timeout = timeout
        task.func = func
        task.isInterval = False
        task.args = args
        task.kw = kw
        self._tasks.add(task)
        return task
    
    def setInterval(self, timeout, func, *args, **kw):
        """
        Call a function at least every timeout seconds with specified arguments.
        
        @type timeout: int
        @param timeout: timeout
        @type func: function
        @param func: function to call
        
        @rtype: _Task
        @return: object representing the task
        """
        task = self._Task()
        task.mgr = self
        task.target = time.time() + timeout
        task.timeout = timeout
        task.func = func
        task.isInterval = True
        task.args = args
        task.kw = kw
        self._tasks.add(task)
        return task
    
    def removeTask(self, task):
        """
        Cancel a task.
        
        @type task: _Task
        @param task: task to cancel
        """
        self._tasks.remove(task)
    
    ####
    # Util
    ####
    def _write(self, room, data):
        room._wbuf += data
    
    def getConnections(self):
        li = list(self._rooms.values())
        if self._pm:
            li.append(self._pm)
        return [c for c in li if c._sock != None]
    
    ####
    # Main
    ####
    def main(self):
        self.onInit()
        self._running = True
        while self._running:
            conns = self.getConnections()
            socks = [x._sock for x in conns]
            wsocks = [x._sock for x in conns if x._wbuf != b""]
            rd, wr, sp = select.select(socks, wsocks, [], self._TimerResolution)
            for sock in rd:
                con = [c for c in conns if c._sock == sock][0]
                try:
                    data = sock.recv(1024)
                    if(len(data) > 0):
                        con._feed(data)
                    else:
                        con.disconnect()
                except socket.error:
                    pass
            for sock in wr:
                con = [c for c in conns if c._sock == sock][0]
                try:
                    size = sock.send(con._wbuf)
                    con._wbuf = con._wbuf[size:]
                except socket.error:
                    pass
            self._tick()
    
    @classmethod
    def easy_start(cl, rooms = None, name = None, password = None, pm = True):
        """
        Prompts the user for missing info, then starts.
        
        @type rooms: list
        @param room: rooms to join
        @type name: str
        @param name: name to join as ("" = None, None = unspecified)
        @type password: str
        @param password: password to join with ("" = None, None = unspecified)
        """
        if not rooms: rooms = str(input("Room names separated by semicolons: ")).split(";")
        if len(rooms) == 1 and rooms[0] == "": rooms = []
        if not name: name = str(input("User name: "))
        if name == "": name = None
        if not password: password = str(input("User password: "))
        if password == "": password = None
        self = cl(name, password, pm = pm)
        for room in rooms:
            self.joinRoom(room)
        self.main()
    
    def stop(self):
        for conn in list(self._rooms.values()):
            conn.disconnect()
        self._running = False
    
    ####
    # Commands
    ####
    def enableBg(self):
        """Enable background if available."""
        self.user._mbg = True
        for room in self.rooms:
            room.setBgMode(1)
    
    def disableBg(self):
        """Disable background."""
        self.user._mbg = False
        for room in self.rooms:
            room.setBgMode(0)
    
    def enableRecording(self):
        """Enable recording if available."""
        self.user._mrec = True
        for room in self.rooms:
            room.setRecordingMode(1)
    
    def disableRecording(self):
        """Disable recording."""
        self.user._mrec = False
        for room in self.rooms:
            room.setRecordingMode(0)
    
    def setNameColor(self, color3x):
        """
        Set name color.
        
        @type color3x: str
        @param color3x: a 3-char RGB hex code for the color
        """
        self.user._nameColor = color3x
    
    def setFontColor(self, color3x):
        """
        Set font color.
        
        @type color3x: str
        @param color3x: a 3-char RGB hex code for the color
        """
        self.user._fontColor = color3x
    
    def setFontFace(self, face):
        """
        Set font face/family.
        
        @type face: str
        @param face: the font face
        """
        self.user._fontFace = face
    
    def setFontSize(self, size):
        """
        Set font size.
        
        @type size: int
        @param size: the font size (limited: 9 to 22)
        """
        if size < 9: size = 9
        if size > 22: size = 22
        self.user._fontSize = size

