class GuidanceResponse:
    def __init__(self,answer='',binRecommendation='',sourceReference='Local rules'): self.__answer,self.__binRecommendation,self.__sourceReference=answer,binRecommendation,sourceReference
    def initialize(self): return self.getResponse()
    def getResponse(self): return {'answer':self.__answer,'binRecommendation':self.__binRecommendation,'sourceReference':self.__sourceReference}
    def getAnswer(self): return self.__answer
    def setAnswer(self,v): self.__answer=str(v)
    def getBinRecommendation(self): return self.__binRecommendation
    def setBinRecommendation(self,v): self.__binRecommendation=str(v)
    def getSourceReference(self): return self.__sourceReference
    def setSourceReference(self,v): self.__sourceReference=str(v)
