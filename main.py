from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Payload:
    label: str; confidence: float; box: tuple[float,float,float,float]

class Processor(ABC):
    @abstractmethod
    def process(self, payload: Payload) -> Payload | None: ...
    def __or__(self, other): return Pipeline([self, other])

class ConfidenceProcessor(Processor):
    def __init__(self, threshold=.5): self.threshold=threshold
    def process(self, payload): return payload if payload.confidence >= self.threshold else None

class MaterialProcessor(Processor):
    def process(self, payload):
        aliases={"bottle":"plastic","can":"metal","newspaper":"paper"}
        return Payload(aliases.get(payload.label.lower(),payload.label.lower()),payload.confidence,payload.box)

class BoxNormalizer(Processor):
    def process(self, payload):
        x1,y1,x2,y2=payload.box
        return Payload(payload.label,payload.confidence,(round(x1/1000,3),round(y1/1000,3),round(x2/1000,3),round(y2/1000,3)))

class Pipeline(Processor):
    def __init__(self, processors): self.processors=processors
    def __or__(self, other): return Pipeline(self.processors+[other])
    def process(self,payload):
        for processor in self.processors:
            payload=processor.process(payload)
            if payload is None: return None
        return payload

def stream(payloads):
    for payload in payloads: yield payload

if __name__ == "__main__":
    pipeline=ConfidenceProcessor(.5)|MaterialProcessor()|BoxNormalizer()
    payloads=[Payload("bottle",.92,(10,20,300,500)),Payload("can",.2,(0,0,10,10))]
    print([pipeline.process(item) for item in stream(payloads)])
