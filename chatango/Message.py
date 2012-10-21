
################################################################
# Message class
################################################################
class Message(object):
    """Class that represents a message."""
    ####
    # Attach/detach
    ####
    def attach(self, room, msgid):
        """
        Attach the Message to a message id.
        
        @type msgid: str
        @param msgid: message id
        """
        if self._msgid == None:
            self._room = room
            self._msgid = msgid
            self._room._msgs[msgid] = self
    
    def detach(self):
        """Detach the Message."""
        if self._msgid != None and self._msgid in self._room._msgs:
            del self._room._msgs[self._msgid]
            self._msgid = None
    
    ####
    # Init
    ####
    def __init__(self, **kw):
        self._msgid = None
        self._time = None
        self._user = None
        self._body = None
        self._room = None
        self._raw = ""
        self._ip = None
        self._unid = ""
        self._nameColor = "000"
        self._fontSize = 12
        self._fontFace = "0"
        self._fontColor = "000"
        for attr, val in kw.items():
            if val == None: continue
            setattr(self, "_" + attr, val)
    
    ####
    # Properties
    ####
    def getId(self): return self._msgid
    def getTime(self): return self._time
    def getUser(self): return self._user
    def getBody(self): return self._body
    def getUid(self): return self._uid
    def getIP(self): return self._ip
    def getFontColor(self): return self._fontColor
    def getFontFace(self): return self._fontFace
    def getFontSize(self): return self._fontSize
    def getNameColor(self): return self._nameColor
    def getRoom(self): return self._room
    def getRaw(self): return self._raw
    def getUnid(self): return self._unid
    
    msgid = property(getId)
    time = property(getTime)
    user = property(getUser)
    body = property(getBody)
    uid = property(getUid)
    room = property(getRoom)
    ip = property(getIP)
    fontColor = property(getFontColor)
    fontFace = property(getFontFace)
    fontSize = property(getFontSize)
    raw = property(getRaw)
    nameColor = property(getNameColor)
    unid = property(getUnid)
