from abc import ABC, abstractmethod
from pathlib import Path
from domain.entities import Presentation

class BaseParser(ABC):
    
    @abstractmethod
    def parse(self, file_path: Path) -> Presentation:
        pass
    
    def can_parse(self, file_path: Path) -> bool:
        return file_path.suffix.lower() == ".pdf"
