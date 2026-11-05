class ImagePreprocessor:
    def __init__(self,targetImageSize=640,colorMode='RGB'): self.__targetImageSize,self.__colorMode=int(targetImageSize),colorMode
    def initialize(self): return self.__targetImageSize>0
    def validateImage(self,image):
        if not image or not image.get('content'): raise ValueError('Image content is required')
        return True
    def prepareImage(self,image): self.validateImage(image); return {**image,'targetImageSize':self.__targetImageSize,'colorMode':self.__colorMode}
    def getTargetImageSize(self): return self.__targetImageSize
    def setTargetImageSize(self,v): self.__targetImageSize=int(v)
    def getColorMode(self): return self.__colorMode
    def setColorMode(self,v): self.__colorMode=str(v)
