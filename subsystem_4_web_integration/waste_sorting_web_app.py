class WasteSortingWebApp:
    def __init__(self,controller,userInput='',uploadedImage=None): self.__controller,self.__userInput,self.__uploadedImage=controller,userInput,uploadedImage
    def initialize(self): return self.__controller.initialize()
    def uploadImage(self,image): self.setUploadedImage(image); return self.__controller.handleResponse(image)
    def submitQuestion(self,question): self.setUserInput(question); return self.__controller.requestGuidance(question)
    def displayResults(self,result): return '\n'.join([f'{key}: {value}' for key,value in result.items()])
    def getUserInput(self): return self.__userInput
    def setUserInput(self,v): self.__userInput=str(v)
    def getUploadedImage(self): return self.__uploadedImage
    def setUploadedImage(self,v): self.__uploadedImage=v
