class PredictionResult:
    def __init__(self,wasteCategory='Unknown',confidenceScore=0.0,isReliable=False): self.__wasteCategory,self.__confidenceScore,self.__isReliable=wasteCategory,float(confidenceScore),bool(isReliable)
    def initialize(self): return self.getResultDetails()
    def getResultDetails(self): return {'wasteCategory':self.__wasteCategory,'confidenceScore':self.__confidenceScore,'isReliable':self.__isReliable}
    def getWasteCategory(self): return self.__wasteCategory
    def setWasteCategory(self,v): self.__wasteCategory=str(v)
    def getConfidenceScore(self): return self.__confidenceScore
    def setConfidenceScore(self,v): self.__confidenceScore=float(v)
    def getIsReliable(self): return self.__isReliable
    def setIsReliable(self,v): self.__isReliable=bool(v)
