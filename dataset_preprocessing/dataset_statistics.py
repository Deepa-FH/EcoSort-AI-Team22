from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DatasetStatistics:
    total_images: int
    extensions: dict[str, int]

    @classmethod
    def from_folder(cls, folder: Path) -> "DatasetStatistics":
        files = [p for p in folder.rglob("*") if p.is_file()]
        extensions: dict[str, int] = {}
        for file in files:
            suffix = file.suffix.lower() or "[none]"
            extensions[suffix] = extensions.get(suffix, 0) + 1
        return cls(len(files), extensions)
