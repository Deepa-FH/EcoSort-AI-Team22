from .ask_ai_service import AskAIService
from .guidance_response import GuidanceResponse
from .recycling_rule import RecyclingRule
class RecyclingGuidanceService:
    def __init__(self,region='Germany'):
        self.__region=region; self.askAIService=AskAIService(); self.__rules=[RecyclingRule('Plastic','Yellow bin',region,'Empty packaging before disposal.'),RecyclingRule('Metal','Yellow bin',region,'Place clean cans in packaging recycling.'),RecyclingRule('Paper','Blue bin',region,'Keep paper clean and dry.')]
    def initialize(self): return all(x.initialize() for x in self.__rules)
    def findApplicableRule(self,category): return next((x for x in self.__rules if x.getCategory().lower()==category.lower()),None)
    def explainWasteCategory(self,category): return self.askAIService.askQuestion('How should '+category+' be recycled?')
    def getDisposalGuidance(self,category):
        rule=self.findApplicableRule(category)
        return GuidanceResponse(rule.getInstructions(),rule.getBinType(),'Regional recycling rule') if rule else GuidanceResponse(self.explainWasteCategory(category),'Check local guidance','Sortly AI')
    def getRegion(self): return self.__region
    def setRegion(self,v): self.__region=str(v)
