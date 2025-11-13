"""
YAML Parser для DSL валидации презентаций
Парсит YAML файлы с правилами и создает ValidationEngine
"""

import yaml
from typing import List, Dict, Any, Union, Set
from app.services.kernel.validation_engine import ValidationEngine
from app.services.kernel.base_checks import PresentationCheck, SlideCheck
from app.services.kernel.checks.slides_count_check import SlidesCountCheck
from app.services.kernel.checks.font_count_check import FontCountPresentationCheck, FontCountSlideCheck
from app.services.kernel.checks.heading_presence_check import HeadingPresenceCheck


class DSLParseError(Exception):
    """Ошибка парсинга DSL"""
    pass


class CheckRegistry:
    """Реестр доступных проверок"""
    
    # Проверки уровня презентации
    PRESENTATION_CHECKS = {
        'slides_count': {
            'class': SlidesCountCheck,
            'available_levels': ['presentation'],
            'default_level': 'presentation'
        },
        'font_count': {
            'class': FontCountPresentationCheck,
            'available_levels': ['presentation', 'slide'],
            'default_level': None  # требуется явное указание
        }
    }
    
    # Проверки уровня слайда
    SLIDE_CHECKS = {
        'font_count': {
            'class': FontCountSlideCheck,
            'available_levels': ['presentation', 'slide'],
            'default_level': None  # требуется явное указание
        },
        'heading_presence': {
            'class': HeadingPresenceCheck,
            'available_levels': ['slide'],
            'default_level': 'slide'
        }
    }
    
    @classmethod
    def get_check_info(cls, check_type: str) -> Dict[str, Any]:
        """Получить информацию о проверке"""
        if check_type in cls.PRESENTATION_CHECKS:
            return cls.PRESENTATION_CHECKS[check_type]
        if check_type in cls.SLIDE_CHECKS:
            return cls.SLIDE_CHECKS[check_type]
        raise DSLParseError(f"Неизвестный тип проверки: {check_type}")


class ScopeParser:
    """Парсер области применения (scope) для slide-level проверок"""
    
    @staticmethod
    def parse(scope: Union[str, int, List]) -> Union[str, Set[int]]:
        """
        Парсит scope в формат, понятный SlideCheck
        
        Возможные форматы:
        - 'all' -> 'all'
        - 5 -> {5}
        - '3-5' -> {3, 4, 5}
        - [1, 4, 9] -> {1, 4, 9}
        - [1, '3-5', '9-10', 11] -> {1, 3, 4, 5, 9, 10, 11}
        """
        if scope == 'all':
            return 'all'
        
        if isinstance(scope, int):
            return {scope}
        
        if isinstance(scope, str):
            # Попытка распарсить диапазон '3-5'
            if '-' in scope:
                return ScopeParser._parse_range(scope)
            # Если просто число в виде строки
            try:
                return {int(scope)}
            except ValueError:
                raise DSLParseError(f"Некорректный формат scope: {scope}")
        
        if isinstance(scope, list):
            result = set()
            for item in scope:
                if isinstance(item, int):
                    result.add(item)
                elif isinstance(item, str):
                    if '-' in item:
                        result.update(ScopeParser._parse_range(item))
                    else:
                        try:
                            result.add(int(item))
                        except ValueError:
                            raise DSLParseError(f"Некорректный элемент scope: {item}")
                else:
                    raise DSLParseError(f"Некорректный тип элемента scope: {type(item)}")
            return result
        
        raise DSLParseError(f"Некорректный тип scope: {type(scope)}")
    
    @staticmethod
    def _parse_range(range_str: str) -> Set[int]:
        """Парсит диапазон '3-5' в {3, 4, 5}"""
        try:
            parts = range_str.split('-')
            if len(parts) != 2:
                raise DSLParseError(f"Некорректный формат диапазона: {range_str}")
            
            start = int(parts[0].strip())
            end = int(parts[1].strip())
            
            if start > end:
                raise DSLParseError(f"Начало диапазона больше конца: {range_str}")
            
            return set(range(start, end + 1))
        except ValueError:
            raise DSLParseError(f"Некорректный формат диапазона: {range_str}")


class RuleParser:
    """Парсер отдельного правила"""
    
    def __init__(self, rule_data: Dict[str, Any]):
        self.rule_data = rule_data
        self._validate_rule_structure()
    
    def _validate_rule_structure(self):
        """Валидация базовой структуры правила"""
        required_fields = ['name', 'check', 'params', 'severity']
        for field in required_fields:
            if field not in self.rule_data:
                raise DSLParseError(f"Отсутствует обязательное поле: {field}")
        
        severity = self.rule_data['severity']
        if severity not in ['error', 'warning', 'info']:
            raise DSLParseError(f"Некорректный уровень severity: {severity}")
    
    def parse(self) -> Union[PresentationCheck, SlideCheck]:
        """Парсит правило и создает экземпляр проверки"""
        check_type = self.rule_data['check']
        check_info = CheckRegistry.get_check_info(check_type)
        
        # Определяем уровень проверки
        level = self._determine_level(check_info)
        
        # Создаем проверку нужного уровня
        if level == 'presentation':
            return self._create_presentation_check(check_type, check_info)
        elif level == 'slide':
            return self._create_slide_check(check_type, check_info)
        else:
            raise DSLParseError(f"Некорректный level: {level}")
    
    def _determine_level(self, check_info: Dict[str, Any]) -> str:
        """Определяет уровень проверки"""
        available_levels = check_info['available_levels']
        default_level = check_info['default_level']
        specified_level = self.rule_data.get('level')
        
        # Если level указан явно
        if specified_level:
            if specified_level not in available_levels:
                raise DSLParseError(
                    f"Проверка {self.rule_data['check']} не поддерживает level: {specified_level}. "
                    f"Доступные уровни: {available_levels}"
                )
            return specified_level
        
        # Если level не указан, используем default
        if default_level:
            return default_level
        
        # Если default нет, требуется явное указание
        raise DSLParseError(
            f"Для проверки {self.rule_data['check']} необходимо указать level. "
            f"Доступные уровни: {available_levels}"
        )
    
    def _create_presentation_check(self, check_type: str, check_info: Dict[str, Any]) -> PresentationCheck:
        """Создает проверку уровня презентации"""
        check_class = CheckRegistry.PRESENTATION_CHECKS[check_type]['class']
        
        return check_class(
            rule_name=self.rule_data['name'],
            params=self.rule_data['params'],
            severity=self.rule_data['severity']
        )
    
    def _create_slide_check(self, check_type: str, check_info: Dict[str, Any]) -> SlideCheck:
        """Создает проверку уровня слайда"""
        check_class = CheckRegistry.SLIDE_CHECKS[check_type]['class']
        
        # Парсим scope (по умолчанию 'all')
        scope_raw = self.rule_data.get('scope', 'all')
        scope = ScopeParser.parse(scope_raw)
        
        return check_class(
            rule_name=self.rule_data['name'],
            params=self.rule_data['params'],
            severity=self.rule_data['severity'],
            scope=scope
        )


class DSLParser:
    """Основной парсер DSL для валидации презентаций"""
    
    @staticmethod
    def parse_yaml_file(file_path: str) -> ValidationEngine:
        """
        Парсит YAML файл с правилами и создает ValidationEngine
        
        Args:
            file_path: путь к YAML файлу с правилами
            
        Returns:
            ValidationEngine с настроенными проверками
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except FileNotFoundError:
            raise DSLParseError(f"Файл не найден: {file_path}")
        except yaml.YAMLError as e:
            raise DSLParseError(f"Ошибка парсинга YAML: {e}")
        
        return DSLParser.parse_yaml_data(data)
    
    @staticmethod
    def parse_yaml_string(yaml_string: str) -> ValidationEngine:
        """
        Парсит YAML строку с правилами и создает ValidationEngine
        
        Args:
            yaml_string: YAML строка с правилами
            
        Returns:
            ValidationEngine с настроенными проверками
        """
        try:
            data = yaml.safe_load(yaml_string)
        except yaml.YAMLError as e:
            raise DSLParseError(f"Ошибка парсинга YAML: {e}")
        
        return DSLParser.parse_yaml_data(data)
    
    @staticmethod
    def parse_yaml_data(data: Any) -> ValidationEngine:
        """
        Парсит данные из YAML и создает ValidationEngine
        
        Args:
            data: распарсенные данные из YAML
            
        Returns:
            ValidationEngine с настроенными проверками
        """
        if not isinstance(data, dict) or 'rules' not in data:
            raise DSLParseError("YAML файл должен содержать ключ 'rules' со списком правил")
        
        rules = data['rules']
        if not isinstance(rules, list):
            raise DSLParseError("'rules' должен быть списком")
        
        presentation_checks = []
        slide_checks = []
        
        for i, rule_data in enumerate(rules):
            if not isinstance(rule_data, dict) or 'rule' not in rule_data:
                raise DSLParseError(f"Правило #{i+1}: должно содержать ключ 'rule'")
            
            try:
                rule_parser = RuleParser(rule_data['rule'])
                check = rule_parser.parse()
                
                if isinstance(check, PresentationCheck):
                    presentation_checks.append(check)
                elif isinstance(check, SlideCheck):
                    slide_checks.append(check)
            except DSLParseError as e:
                raise DSLParseError(f"Ошибка в правиле '{rule_data.get('rule', {}).get('name', f'#{i+1}')}': {e}")
        
        return ValidationEngine(
            presentation_checks=presentation_checks,
            slide_checks=slide_checks
        )


# Удобные функции для использования
def load_validation_engine(file_path: str) -> ValidationEngine:
    """
    Загружает ValidationEngine из YAML файла
    
    Args:
        file_path: путь к YAML файлу
        
    Returns:
        ValidationEngine
    """
    return DSLParser.parse_yaml_file(file_path)


def load_validation_engine_from_string(yaml_string: str) -> ValidationEngine:
    """
    Загружает ValidationEngine из YAML строки
    
    Args:
        yaml_string: YAML строка
        
    Returns:
        ValidationEngine
    """
    return DSLParser.parse_yaml_string(yaml_string)

