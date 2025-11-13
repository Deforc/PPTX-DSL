"""
Тесты для YAML парсера DSL
"""

import pytest

from app.services.dsl.yaml_parser import (
    ScopeParser,
    DSLParseError,
    load_validation_engine_from_string
)
from app.services.kernel.validation_engine import ValidationEngine


class TestScopeParser:
    """Тесты парсера scope"""
    
    def test_parse_all(self):
        result = ScopeParser.parse('all')
        assert result == 'all'
    
    def test_parse_single_int(self):
        result = ScopeParser.parse(5)
        assert result == {5}
    
    def test_parse_single_string(self):
        result = ScopeParser.parse('5')
        assert result == {5}
    
    def test_parse_range(self):
        result = ScopeParser.parse('3-5')
        assert result == {3, 4, 5}
    
    def test_parse_list_of_ints(self):
        result = ScopeParser.parse([1, 4, 9])
        assert result == {1, 4, 9}
    
    def test_parse_list_with_ranges(self):
        result = ScopeParser.parse([1, '3-5', 9])
        assert result == {1, 3, 4, 5, 9}
    
    def test_parse_complex_list(self):
        result = ScopeParser.parse([1, '3-5', '9-10', 15])
        assert result == {1, 3, 4, 5, 9, 10, 15}
    
    def test_parse_invalid_range(self):
        with pytest.raises(DSLParseError):
            ScopeParser.parse('10-5')
    
    def test_parse_invalid_format(self):
        with pytest.raises(DSLParseError):
            ScopeParser.parse('abc')


class TestDSLParser:
    """Тесты основного парсера"""
    
    def test_parse_slides_count_check(self):
        yaml_string = """
rules:
  - rule:
      name: "Количество слайдов"
      check: slides_count
      params:
        min: 5
        max: 30
      severity: error
"""
        engine = load_validation_engine_from_string(yaml_string)
        
        assert isinstance(engine, ValidationEngine)
        assert len(engine.presentation_checks) == 1
        assert len(engine.slide_checks) == 0
        
        check = engine.presentation_checks[0]
        assert check.rule_name == "Количество слайдов"
        assert check.params == {'min': 5, 'max': 30}
        assert check.severity == 'error'
    
    def test_parse_font_count_presentation(self):
        yaml_string = """
rules:
  - rule:
      name: "Максимум 3 шрифта"
      level: presentation
      check: font_count
      params:
        max: 3
      severity: error
"""
        engine = load_validation_engine_from_string(yaml_string)
        
        assert len(engine.presentation_checks) == 1
        check = engine.presentation_checks[0]
        assert check.rule_name == "Максимум 3 шрифта"
        assert check.params == {'max': 3}
    
    def test_parse_font_count_slide(self):
        yaml_string = """
rules:
  - rule:
      name: "Максимум 2 шрифта на слайде"
      level: slide
      scope: all
      check: font_count
      params:
        max: 2
      severity: warning
"""
        engine = load_validation_engine_from_string(yaml_string)
        
        assert len(engine.slide_checks) == 1
        check = engine.slide_checks[0]
        assert check.rule_name == "Максимум 2 шрифта на слайде"
        assert check.scope == 'all'
    
    def test_parse_heading_presence_with_scope(self):
        yaml_string = """
rules:
  - rule:
      name: "Заголовки на слайдах 2-10"
      level: slide
      scope: 2-10
      check: heading_presence
      params:
        required: true
      severity: error
"""
        engine = load_validation_engine_from_string(yaml_string)
        
        assert len(engine.slide_checks) == 1
        check = engine.slide_checks[0]
        assert check.scope == {2, 3, 4, 5, 6, 7, 8, 9, 10}
    
    def test_parse_multiple_rules(self):
        yaml_string = """
rules:
  - rule:
      name: "Количество слайдов"
      check: slides_count
      params:
        min: 5
        max: 30
      severity: error
  
  - rule:
      name: "Шрифты в презентации"
      level: presentation
      check: font_count
      params:
        max: 3
      severity: error
  
  - rule:
      name: "Заголовки на всех слайдах"
      scope: all
      check: heading_presence
      params:
        required: true
      severity: warning
"""
        engine = load_validation_engine_from_string(yaml_string)
        
        assert len(engine.presentation_checks) == 2
        assert len(engine.slide_checks) == 1
    
    def test_parse_default_level_for_heading(self):
        """Тест автоматического определения level для heading_presence"""
        yaml_string = """
rules:
  - rule:
      name: "Заголовки"
      check: heading_presence
      params:
        required: true
      severity: warning
"""
        engine = load_validation_engine_from_string(yaml_string)
        
        # heading_presence имеет только level: slide, должен использоваться автоматически
        assert len(engine.slide_checks) == 1
        assert len(engine.presentation_checks) == 0
    
    def test_parse_default_scope_for_slide_check(self):
        """Тест автоматического scope: all для slide проверок"""
        yaml_string = """
rules:
  - rule:
      name: "Заголовки"
      level: slide
      check: heading_presence
      params:
        required: true
      severity: warning
"""
        engine = load_validation_engine_from_string(yaml_string)
        
        check = engine.slide_checks[0]
        assert check.scope == 'all'
    
    def test_missing_level_for_ambiguous_check(self):
        """Тест ошибки при отсутствии level для font_count"""
        yaml_string = """
rules:
  - rule:
      name: "Шрифты"
      check: font_count
      params:
        max: 3
      severity: error
"""
        with pytest.raises(DSLParseError, match="необходимо указать level"):
            load_validation_engine_from_string(yaml_string)
    
    def test_invalid_severity(self):
        """Тест ошибки при некорректном severity"""
        yaml_string = """
rules:
  - rule:
      name: "Слайды"
      check: slides_count
      params:
        min: 5
      severity: critical
"""
        with pytest.raises(DSLParseError, match="Некорректный уровень severity"):
            load_validation_engine_from_string(yaml_string)
    
    def test_missing_required_field(self):
        """Тест ошибки при отсутствии обязательного поля"""
        yaml_string = """
rules:
  - rule:
      name: "Слайды"
      check: slides_count
      severity: error
"""
        with pytest.raises(DSLParseError, match="Отсутствует обязательное поле: params"):
            load_validation_engine_from_string(yaml_string)
    
    def test_unknown_check_type(self):
        """Тест ошибки при неизвестном типе проверки"""
        yaml_string = """
rules:
  - rule:
      name: "Неизвестная проверка"
      check: unknown_check
      params:
        value: 123
      severity: error
"""
        with pytest.raises(DSLParseError, match="Неизвестный тип проверки"):
            load_validation_engine_from_string(yaml_string)
    
    def test_invalid_level_for_check(self):
        """Тест ошибки при недоступном level для проверки"""
        yaml_string = """
rules:
  - rule:
      name: "Слайды на slide уровне"
      level: slide
      check: slides_count
      params:
        min: 5
      severity: error
"""
        with pytest.raises(DSLParseError, match="не поддерживает level"):
            load_validation_engine_from_string(yaml_string)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

