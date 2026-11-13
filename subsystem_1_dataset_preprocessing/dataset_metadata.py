"""DatasetMetadata - documents where the data comes from (PPT requirement:
"Document dataset source/license")."""

from __future__ import annotations


class DatasetMetadata:
    """Holds source, licence and version information of the dataset.

    OOP idea: ENCAPSULATION with both styles of accessors:
      * Pythonic ``@property`` (``meta.version``)
      * UML-style methods (``meta.getVersion()`` / ``meta.setVersion(...)``)
    The UML class diagram in the PPT uses get/set names, so both exist.
    """

    def __init__(self, source: str = "RealWaste (UCI) + TrashPanda custom images",
                 license: str = "See each source's page - confirm before publishing",
                 version: str = "1.0"):
        self._source = source
        self._license = license
        self._version = version

    # ---- properties -----------------------------------------------------
    @property
    def source(self) -> str:
        return self._source

    @source.setter
    def source(self, value: str) -> None:
        self._source = str(value)

    @property
    def license(self) -> str:
        return self._license

    @license.setter
    def license(self, value: str) -> None:
        self._license = str(value)

    @property
    def version(self) -> str:
        return self._version

    @version.setter
    def version(self, value: str) -> None:
        self._version = str(value)

    # ---- UML-style accessors (thin wrappers) -----------------------------
    def getSource(self) -> str: return self._source
    def setSource(self, value: str) -> None: self.source = value
    def getLicense(self) -> str: return self._license
    def setLicense(self, value: str) -> None: self.license = value
    def getVersion(self) -> str: return self._version
    def setVersion(self, value: str) -> None: self.version = value

    def to_dict(self) -> dict:
        """Metadata as a dict (written into the manifest header)."""
        return {"source": self._source, "license": self._license, "version": self._version}

    def __str__(self) -> str:
        return f"Dataset v{self._version} - {self._source} ({self._license})"
