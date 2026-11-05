class IntegrationController:
    def __init__(self,recognitionService,guidanceService,dashboardService,repository): self.__recognitionService,self.__guidanceService,self.__dashboardService,self.__repository=recognitionService,guidanceService,dashboardService,repository
    def initialize(self): self.__recognitionService.initialize(); self.__guidanceService.initialize(); return self.__dashboardService.initialize()
    def classifyWaste(self,image): return self.__recognitionService.recognizeImage(image)
    def requestGuidance(self,category): return self.__guidanceService.getDisposalGuidance(category)
    def handleResponse(self,image):
        prediction=self.classifyWaste(image); guidance=self.requestGuidance(prediction.getWasteCategory()); result={**prediction.getResultDetails(),**guidance.getResponse()}; self.__repository.saveResult(result); return result
    def getRecognitionService(self): return self.__recognitionService
    def setRecognitionService(self,v): self.__recognitionService=v
    def getGuidanceService(self): return self.__guidanceService
    def setGuidanceService(self,v): self.__guidanceService=v
