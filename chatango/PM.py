import socket
from chatango import User

################################################################
# PM class
################################################################
class PM(object):
    """Manages a connection with Chatango PM."""
    ####
    # Init
    ####
    def __init__(self, mgr):
        self._connected = False
        self._mgr = mgr
        self._auid = None
        self._blocklist = set()
        self._contacts = set()
        self._wlock = False
        self._firstCommand = True
        self._wbuf = b""
        self._wlockbuf = b""
        self._rbuf = b""
        self._pingTask = None
        self._connect()
    
    ####
    # Connections
    ####
    def _connect(self):
        self._wbuf = b""
        self._sock = socket.socket()
        self._sock.connect((self._mgr._PMHost, self._mgr._PMPort))
        self._sock.setblocking(False)
        self._firstCommand = True
        if not self._auth(): return
        self._pingTask = self.mgr.setInterval(self._mgr._pingDelay, self.ping)
        self._connected = True
    
    def _auth(self):
        self._auid = _getAuth(self._mgr.name, self._mgr.password)
        if self._auid == None:
            self._sock.close()
            self._callEvent("onLoginFail")
            self._sock = None
            return False
        self._sendCommand("tlogin", self._auid, "2")
        self._setWriteLock(True)
        return True
    
    def disconnect(self):
        self._disconnect()
        self._callEvent("onPMDisconnect")
    
    def _disconnect(self):
        self._connected = False
        self._sock.close()
        self._sock = None
    
    ####
    # Feed
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
    # Properties
    ####
    def getManager(self): return self._mgr
    def getContacts(self): return self._contacts
    def getBlocklist(self): return self._blocklist
    
    mgr = property(getManager)
    contacts = property(getContacts)
    blocklist = property(getBlocklist)
    
    ####
    # Received Commands
    ####
    def rcmd_OK(self, args):
        self._setWriteLock(False)
        self._sendCommand("wl")
        self._sendCommand("getblock")
        self._callEvent("onPMConnect")
    
    def rcmd_wl(self, args):
        self._contacts = set()
        for i in range(len(args) // 4):
            name, last_on, is_on, idle = args[i * 4: i * 4 + 4]
            user = User(name)
            self._contacts.add(user)
        self._callEvent("onPMContactlistReceive")
    
    def rcmd_block_list(self, args):
        self._blocklist = set()
        for name in args:
            if name == "": continue
            self._blocklist.add(User(name))
    
    def rcmd_DENIED(self, args):
        self._disconnect()
        self._callEvent("onLoginFail")
    
    def rcmd_msg(self, args):
        user = User(args[0])
        body = strip_html(":".join(args[5:]))
        self._callEvent("onPMMessage", user, body)
    
    def rcmd_msgoff(self, args):
        user = User(args[0])
        body = strip_html(":".join(args[5:]))
        self._callEvent("onPMOfflineMessage", user, body)
    
    def rcmd_wlonline(self, args):
        self._callEvent("onPMContactOnline", User(args[0]))
    
    def rcmd_wloffline(self, args):
        self._callEvent("onPMContactOffline", User(args[0]))
    
    def rcmd_kickingoff(self, args):
        self.disconnect()
    
    ####
    # Commands
    ####
    def ping(self):
        self._sendCommand("")
        self._callEvent("onPMPing")
    
    def message(self, user, msg):
        self._sendCommand("msg", user.name, msg)
    
    def addContact(self, user):
        if user not in self._contacts:
            self._sendCommand("wladd", user.name)
            self._contacts.add(user)
            self._callEvent("onPMContactAdd", user)
    
    def removeContact(self, user):
        if user in self._contacts:
            self._sendCommand("wldelete", user.name)
            self._contacts.remove(user)
            self._callEvent("onPMContactRemove", user)
    
    def block(self, user):
        if user not in self._blocklist:
            self._sendCommand("block", user.name)
            self._block.remove(user)
            self._callEvent("onPMBlock", user)
    
    def unblock(self, user):
        if user in self._blocklist:
            self._sendCommand("unblock", user.name)
            self._block.remove(user)
            self._callEvent("onPMUnblock", user)
    
    ####
    # Util
    ####
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
        self._write(":".join(args).encode() + terminator)

