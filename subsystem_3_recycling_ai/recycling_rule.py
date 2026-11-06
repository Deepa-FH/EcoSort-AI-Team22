class RecyclingRule:
    def __init__(self,category,binType,region='Germany',instructions=''): self.__category,self.__binType,self.__region,self.__instructions=category,binType,region,instructions
    def initialize(self): return self.validateRule()
    def getRuleDetails(self): return {'category':self.__category,'binType':self.__binType,'region':self.__region,'instructions':self.__instructions}
    def validateRule(self): return bool(self.__category and self.__binType and self.__region)
    def getCategory(self): return self.__category
    def setCategory(self,v): self.__category=str(v)
    def getBinType(self): return self.__binType
    def setBinType(self,v): self.__binType=str(v)
    def getRegion(self): return self.__region
    def setRegion(self,v): self.__region=str(v)
    def getInstructions(self): return self.__instructions
    def setInstructions(self,v): self.__instructions=str(v)
