from .image_preprocessor import ImagePreprocessor
from .waste_classification_model import WasteClassificationModel
class ImageRecognitionService:
    def __init__(self,modelVersion='YOLO26',confidenceThreshold=.70):
        self.__modelVersion,self.__confidenceThreshold=modelVersion,float(confidenceThreshold); self.preprocessor=ImagePreprocessor(); self.model=WasteClassificationModel(modelVersion=modelVersion); self.__lastResult=None
    def initialize(self): return self.model.initialize()
    def recognizeImage(self,image):
        self.__lastResult=self.predictCategory(self.preprocessor.prepareImage(image)); self.__lastResult.setIsReliable(self.model.evaluateConfidence(self.__lastResult.getConfidenceScore(),self.__confidenceThreshold)); return self.__lastResult
    def predictCategory(self,image): return self.model.predict(image)
    def getPredictionResult(self): return self.__lastResult
    def getModelVersion(self): return self.__modelVersion
    def setModelVersion(self,v): self.__modelVersion=str(v)
    def getConfidenceThreshold(self): return self.__confidenceThreshold
    def setConfidenceThreshold(self,v): self.__confidenceThreshold=float(v)
