import yaml
from typing import List, Dict, Any, Union, Set
from app.services.kernel.validation_engine import ValidationEngine
from app.services.kernel.base_checks import PresentationCheck, SlideCheck
from app.services.kernel.checks.slides_count_check import SlidesCountCheck
from app.services.kernel.checks.font_count_check import FontCountPresentationCheck, FontCountSlideCheck
from app.services.kernel.checks.heading_presence_check import HeadingPresenceCheck
from app.services.kernel.checks.font_sizes_count_check import FontSizesCountPresentationCheck, FontSizesCountSlideCheck
from app.services.kernel.checks.sentence_length_check import SentenceLengthCheck
from app.services.kernel.checks.list_nesting_check import ListNestingCheck
from app.services.kernel.checks.list_consistency_check import ListConsistencyPresentationCheck, ListConsistencySlideCheck
from app.services.kernel.checks.font_min_size_check import FontMinSizePresentationCheck, FontMinSizeSlideCheck
from app.services.kernel.checks.uppercase_percent_check import UppercasePercentPresentationCheck, UppercasePercentSlideCheck
from app.services.kernel.checks.elements_count_check import ElementsCountCheck
from app.services.kernel.checks.spelling_check import SpellingCheck
from app.services.kernel.checks.bullet_content_check import BulletConsistencyCheck
from app.services.kernel.checks.list_count_check import ListItemsCountCheck, NestedListsDepthCheck, MixedListsCheck
from app.services.kernel.checks.numbers_check import SlideNumbersPresentationCheck, SlideNumbersSlideCheck
from app.services.kernel.checks.text_content_check import (
    LongPhrasesCheck, ParagraphLengthCheck, SentenceCountCheck, 
    TextDensityCheck, CapitalizationCheck
)

class DSLParseError(Exception):
    pass

class CheckRegistry:
    
    PRESENTATION_CHECKS = {
        'slides_count': {
            'class': SlidesCountCheck,
            'available_levels': ['presentation'],
            'default_level': 'presentation'
        },
        'font_count': {
            'class': FontCountPresentationCheck,
            'available_levels': ['presentation', 'slide'],
            'default_level': None
        },
        'font_sizes_count': {
            'class': FontSizesCountPresentationCheck,
            'available_levels': ['presentation', 'slide'],
            'default_level': None
        },
        'list_consistency': {
            'class': ListConsistencyPresentationCheck,
            'available_levels': ['presentation', 'slide'],
            'default_level': None
        },
        'font_min_size': {
            'class': FontMinSizePresentationCheck,
            'available_levels': ['presentation', 'slide'],
            'default_level': None
        },
        'uppercase_percent': {
            'class': UppercasePercentPresentationCheck,
            'available_levels': ['presentation', 'slide'],
            'default_level': None
        },
        'slide_numbers': {
            'class': SlideNumbersPresentationCheck,
            'available_levels': ['presentation', 'slide'],
            'default_level': None
        }
    }
    
    SLIDE_CHECKS = {
        'font_count': {
            'class': FontCountSlideCheck,
            'available_levels': ['presentation', 'slide'],
            'default_level': None
        },
        'heading_presence': {
            'class': HeadingPresenceCheck,
            'available_levels': ['slide'],
            'default_level': 'slide'
        },
        'font_sizes_count': {
            'class': FontSizesCountSlideCheck,
            'available_levels': ['presentation', 'slide'],
            'default_level': None
        },
        'sentence_length': {
            'class': SentenceLengthCheck,
            'available_levels': ['slide'],
            'default_level': 'slide'
        },
        'list_nesting': {
            'class': ListNestingCheck,
            'available_levels': ['slide'],
            'default_level': 'slide'
        },
        'list_consistency': {
            'class': ListConsistencySlideCheck,
            'available_levels': ['presentation', 'slide'],
            'default_level': None
        },
        'font_min_size': {
            'class': FontMinSizeSlideCheck,
            'available_levels': ['presentation', 'slide'],
            'default_level': None
        },
        'uppercase_percent': {
            'class': UppercasePercentSlideCheck,
            'available_levels': ['presentation', 'slide'],
            'default_level': None
        },
        'elements_count': {
            'class': ElementsCountCheck,
            'available_levels': ['slide'],
            'default_level': 'slide'
        },
        'spelling': {
            'class': SpellingCheck,
            'available_levels': ['slide'],
            'default_level': 'slide'
        },
        'bullet_consistency': {
            'class': BulletConsistencyCheck,
            'available_levels': ['slide'],
            'default_level': 'slide'
        },
        'list_items_count': {
            'class': ListItemsCountCheck,
            'available_levels': ['slide'],
            'default_level': 'slide'
        },
        'nested_lists_depth': {
            'class': NestedListsDepthCheck,
            'available_levels': ['slide'],
            'default_level': 'slide'
        },
        'mixed_lists': {
            'class': MixedListsCheck,
            'available_levels': ['slide'],
            'default_level': 'slide'
        },
        'slide_numbers': {
            'class': SlideNumbersSlideCheck,
            'available_levels': ['presentation', 'slide'],
            'default_level': None
        },
        'long_phrases': {
            'class': LongPhrasesCheck,
            'available_levels': ['slide'],
            'default_level': 'slide'
        },
        'paragraph_length': {
            'class': ParagraphLengthCheck,
            'available_levels': ['slide'],
            'default_level': 'slide'
        },
        'sentence_count': {
            'class': SentenceCountCheck,
            'available_levels': ['slide'],
            'default_level': 'slide'
        },
        'text_density': {
            'class': TextDensityCheck,
            'available_levels': ['slide'],
            'default_level': 'slide'
        },
        'capitalization': {
            'class': CapitalizationCheck,
            'available_levels': ['slide'],
            'default_level': 'slide'
        }
    }
    
    @classmethod
    def get_check_info(cls, check_type: str) -> Dict[str, Any]:
        if check_type in cls.PRESENTATION_CHECKS:
            return cls.PRESENTATION_CHECKS[check_type]
        if check_type in cls.SLIDE_CHECKS:
            return cls.SLIDE_CHECKS[check_type]
        raise DSLParseError(f"Неизвестный тип проверки: {check_type}")

class ScopeParser:
    
    @staticmethod
    def parse(scope: Union[str, int, List]) -> Union[str, Set[int]]:
        if scope == 'all':
            return 'all'
        
        if isinstance(scope, int):
            return {scope}
        
        if isinstance(scope, str):
            if '-' in scope:
                return ScopeParser._parse_range(scope)
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
    
    def __init__(self, rule_data: Dict[str, Any]):
        self.rule_data = rule_data
        self._validate_rule_structure()
    
    def _validate_rule_structure(self):
        required_fields = ['name', 'check', 'params', 'severity']
        for field in required_fields:
            if field not in self.rule_data:
                raise DSLParseError(f"Отсутствует обязательное поле: {field}")
        
        severity = self.rule_data['severity']
        if severity not in ['error', 'warning', 'info']:
            raise DSLParseError(f"Некорректный уровень severity: {severity}")
    
    def parse(self) -> Union[PresentationCheck, SlideCheck]:
        check_type = self.rule_data['check']
        check_info = CheckRegistry.get_check_info(check_type)
        
        level = self._determine_level(check_info)
        
        if level == 'presentation':
            return self._create_presentation_check(check_type, check_info)
        elif level == 'slide':
            return self._create_slide_check(check_type, check_info)
        else:
            raise DSLParseError(f"Некорректный level: {level}")
    
    def _determine_level(self, check_info: Dict[str, Any]) -> str:
        available_levels = check_info['available_levels']
        default_level = check_info['default_level']
        specified_level = self.rule_data.get('level')
        
        if specified_level:
            if specified_level not in available_levels:
                raise DSLParseError(
                    f"Проверка {self.rule_data['check']} не поддерживает level: {specified_level}. "
                    f"Доступные уровни: {available_levels}"
                )
            return specified_level
        
        if default_level:
            return default_level
        
        raise DSLParseError(
            f"Для проверки {self.rule_data['check']} необходимо указать level. "
            f"Доступные уровни: {available_levels}"
        )
    
    def _create_presentation_check(self, check_type: str, check_info: Dict[str, Any]) -> PresentationCheck:
        check_class = CheckRegistry.PRESENTATION_CHECKS[check_type]['class']
        
        return check_class(
            rule_name=self.rule_data['name'],
            params=self.rule_data['params'],
            severity=self.rule_data['severity']
        )
    
    def _create_slide_check(self, check_type: str, check_info: Dict[str, Any]) -> SlideCheck:
        check_class = CheckRegistry.SLIDE_CHECKS[check_type]['class']
        
        scope_raw = self.rule_data.get('scope', 'all')
        scope = ScopeParser.parse(scope_raw)
        
        return check_class(
            rule_name=self.rule_data['name'],
            params=self.rule_data['params'],
            severity=self.rule_data['severity'],
            scope=scope
        )

class DSLParser:
    
    @staticmethod
    def parse_yaml_file(file_path: str) -> ValidationEngine:
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
        try:
            data = yaml.safe_load(yaml_string)
        except yaml.YAMLError as e:
            raise DSLParseError(f"Ошибка парсинга YAML: {e}")
        
        return DSLParser.parse_yaml_data(data)
    
    @staticmethod
    def parse_yaml_data(data: Any) -> ValidationEngine:
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

def load_validation_engine(file_path: str) -> ValidationEngine:
    return DSLParser.parse_yaml_file(file_path)

def load_validation_engine_from_string(yaml_string: str) -> ValidationEngine:
    return DSLParser.parse_yaml_string(yaml_string)
