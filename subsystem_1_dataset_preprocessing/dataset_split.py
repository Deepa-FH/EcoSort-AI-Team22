class DatasetSplit:
    def __init__(self, trainSet=None, validationSet=None, testSet=None):
        self.__trainSet,self.__validationSet,self.__testSet=list(trainSet or []),list(validationSet or []),list(testSet or [])
    def initialize(self): return self.getSplitInfo()
    def splitData(self, images, trainRatio=.7, validationRatio=.2):
        images=list(images); a=int(len(images)*trainRatio); b=a+int(len(images)*validationRatio)
        self.__trainSet,self.__validationSet,self.__testSet=images[:a],images[a:b],images[b:]
        return self.getSplitInfo()
    def getSplitInfo(self): return {'train':len(self.__trainSet),'validation':len(self.__validationSet),'test':len(self.__testSet)}
    def getTrainSet(self): return list(self.__trainSet)
    def setTrainSet(self,v): self.__trainSet=list(v)
    def getValidationSet(self): return list(self.__validationSet)
    def setValidationSet(self,v): self.__validationSet=list(v)
    def getTestSet(self): return list(self.__testSet)
    def setTestSet(self,v): self.__testSet=list(v)
