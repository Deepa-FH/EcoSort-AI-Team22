from pathlib import Path
from .dataset_metadata import DatasetMetadata
from .dataset_split import DatasetSplit
from .preprocessing_pipeline import PreprocessingPipeline

class DatasetManager:
    def __init__(self,datasetPath='demo_dataset',datasetSource='Sortly AI demo',license='Educational use'):
        self.__datasetPath,self.__datasetSource,self.__license=str(datasetPath),datasetSource,license
        self.__images=[]; self.metadata=DatasetMetadata(datasetSource,license); self.pipeline=PreprocessingPipeline(); self.datasetSplit=DatasetSplit()
    def initialize(self): self.pipeline.initialize(); return self.metadata.initialize()
    def loadDataset(self,images=None):
        self.__images=list(images or [{'filename':'bottle.jpg','content':b'demo','label':'Plastic'},{'filename':'can.jpg','content':b'demo','label':'Metal'},{'filename':'paper.jpg','content':b'demo','label':'Paper'}]); return list(self.__images)
    def validateDataset(self):
        if not self.__images: raise ValueError('Dataset is empty; call loadDataset first')
        return all(Path(x['filename']).suffix.lower() in {'.jpg','.jpeg','.png'} and x.get('content') for x in self.__images)
    def getDatasetInfo(self): return {'path':self.__datasetPath,'source':self.__datasetSource,'license':self.__license,'images':len(self.__images)}
    def getDatasetPath(self): return self.__datasetPath
    def setDatasetPath(self,v): self.__datasetPath=str(v)
    def getDatasetSource(self): return self.__datasetSource
    def setDatasetSource(self,v): self.__datasetSource=str(v)
    def getLicense(self): return self.__license
    def setLicense(self,v): self.__license=str(v)
