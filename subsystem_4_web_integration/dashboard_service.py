class DashboardService:
    def __init__(self,repository=None): self.__repository=repository
    def initialize(self): return self.__repository is not None
    def getStatistics(self):
        rows=self.__repository.fetchHistory(); counts={}
        for row in rows: counts[row['wasteCategory']]=counts.get(row['wasteCategory'],0)+1
        return {'totalScans':len(rows),'categoryCounts':counts}
    def getRecentResults(self,limit=5): return self.__repository.fetchHistory()[-limit:]
    def getRepository(self): return self.__repository
    def setRepository(self,v): self.__repository=v
