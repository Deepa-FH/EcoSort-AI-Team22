class AskAIService:
    def __init__(self,question=''): self.__question=question
    def initialize(self): return True
    def askQuestion(self,question): self.setQuestion(question); return self.generateAnswer()
    def generateAnswer(self): return 'Sortly AI explanation: '+self.__question if self.__question else 'Please provide a recycling question.'
    def getQuestion(self): return self.__question
    def setQuestion(self,v): self.__question=str(v)
