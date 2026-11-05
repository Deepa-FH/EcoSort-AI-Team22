# How the OOP requirements are met

`Processor` is an ABC with `process` as an abstract method. `ConfidenceProcessor`, `MaterialProcessor`, and `BoxNormalizer` inherit from it and are interchangeable. `Processor.__or__` composes processors into a `Pipeline`. `stream` is a generator and `Pipeline` processes a stream one item at a time. The confidence processor filters unreliable predictions, then the other processors normalize the box and transform visual labels into material categories.
