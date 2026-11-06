class WasteRepository:
    def __init__(self): self.__history=[]
    def initialize(self): return True
    def saveResult(self,result): self.__history.append(dict(result)); return len(self.__history)
    def fetchHistory(self): return list(self.__history)
    def getHistory(self): return list(self.__history)
    def setHistory(self,v): self.__history=list(v)
