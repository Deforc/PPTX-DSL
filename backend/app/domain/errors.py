class ExtractionError(Exception):
    """Ошибка извлечения данных из PDF"""
    pass

class NormalizationError(Exception):
    """Ошибка нормализации текста"""
    pass

class LayoutAnalysisError(Exception):
    """Ошибка анализа layout"""
    pass