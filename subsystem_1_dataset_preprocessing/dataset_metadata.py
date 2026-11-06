class DatasetMetadata:
    def __init__(self, sourceURL='local://demo', license='Educational use', version='1.0'):
        self.__sourceURL, self.__license, self.__version = sourceURL, license, version
    def initialize(self): return self.getMetadata()
    def getMetadata(self): return {'sourceURL':self.__sourceURL,'license':self.__license,'version':self.__version}
    def updateMetadata(self, sourceURL=None, license=None, version=None):
        if sourceURL is not None: self.setSourceURL(sourceURL)
        if license is not None: self.setLicense(license)
        if version is not None: self.setVersion(version)
        return self.getMetadata()
    def getSourceURL(self): return self.__sourceURL
    def setSourceURL(self,v): self.__sourceURL=str(v)
    def getLicense(self): return self.__license
    def setLicense(self,v): self.__license=str(v)
    def getVersion(self): return self.__version
    def setVersion(self,v): self.__version=str(v)
