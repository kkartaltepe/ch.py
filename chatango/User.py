
class _User(object):
    """Class that represents a user."""
    ####
    # Init
    ####
    def __init__(self, name, **kw):
        self._name = name.lower()
        self._sids = dict()
        self._msgs = list()
        self._nameColor = "000"
        self._fontSize = 12
        self._fontFace = "0"
        self._fontColor = "000"
        self._mbg = False
        self._mrec = False
        for attr, val in kw.items():
            if val == None: continue
            setattr(self, "_" + attr, val)
    
    ####
    # Properties
    ####
    def getName(self): return self._name
    def getSessionIds(self, room = None):
        if room:
            return self._sids.get(room, set())
        else:
            return set.union(*self._sids.values())
    def getRooms(self): return self._sids.keys()
    def getRoomNames(self): return [room.name for room in self.getRooms()]
    def getFontColor(self): return self._fontColor
    def getFontFace(self): return self._fontFace
    def getFontSize(self): return self._fontSize
    def getNameColor(self): return self._nameColor
    
    name = property(getName)
    sessionids = property(getSessionIds)
    rooms = property(getRooms)
    roomnames = property(getRoomNames)
    fontColor = property(getFontColor)
    fontFace = property(getFontFace)
    fontSize = property(getFontSize)
    nameColor = property(getNameColor)
    
    ####
    # Util
    ####
    def addSessionId(self, room, sid):
        if room not in self._sids:
            self._sids[room] = set()
        self._sids[room].add(sid)
    
    def removeSessionId(self, room, sid):
        try:
            self._sids[room].remove(sid)
            if len(self._sids[room]) == 0:
                del self._sids[room]
        except KeyError:
            pass
    
    def clearSessionIds(self, room):
        try:
            del self._sids[room]
        except KeyError:
            pass
    
    def hasSessionId(self, room, sid):
        try:
            if sid in self._sids[room]:
                return True
            else:
                return False
        except KeyError:
            return False
    
    ####
    # Repr
    ####
    def __repr__(self):
        return "<User: %s>" %(self.name)

