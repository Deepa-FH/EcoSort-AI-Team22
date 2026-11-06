class PreprocessingPipeline:
    def __init__(self, imageSize=640, normalizationMethod='0-1 scaling'):
        self.__imageSize,self.__normalizationMethod=int(imageSize),normalizationMethod
    def initialize(self):
        if self.__imageSize <= 0: raise ValueError('imageSize must be positive')
        return True
    def resizeImages(self,images): return [{**x,'imageSize':self.__imageSize} for x in images]
    def normalizeImages(self,images): return [{**x,'normalization':self.__normalizationMethod} for x in images]
    def preprocessImages(self,images): return self.normalizeImages(self.resizeImages(images))
    def getImageSize(self): return self.__imageSize
    def setImageSize(self,v): self.__imageSize=int(v)
    def getNormalizationMethod(self): return self.__normalizationMethod
    def setNormalizationMethod(self,v): self.__normalizationMethod=str(v)
