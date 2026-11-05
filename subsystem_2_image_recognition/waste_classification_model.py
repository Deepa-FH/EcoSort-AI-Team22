from .prediction_result import PredictionResult
class WasteClassificationModel:
    def __init__(self,modelPath='models/best.pt',modelVersion='YOLO26'): self.__modelPath,self.__modelVersion,self.__loaded=modelPath,modelVersion,False
    def initialize(self): return self.loadModel()
    def loadModel(self): self.__loaded=True; return True
    def predict(self,image):
        if not self.__loaded: self.loadModel()
        name=image.get('filename','').lower(); category='Metal' if 'can' in name else 'Paper' if 'paper' in name else 'Plastic'; score=.91
        return PredictionResult(category,score,self.evaluateConfidence(score))
    def evaluateConfidence(self,score,threshold=.70): return float(score)>=float(threshold)
    def getModelPath(self): return self.__modelPath
    def setModelPath(self,v): self.__modelPath=str(v)
    def getModelVersion(self): return self.__modelVersion
    def setModelVersion(self,v): self.__modelVersion=str(v)
