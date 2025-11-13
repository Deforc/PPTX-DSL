from typing import List, Dict, Any, Tuple
from app.services.kernel.base_checks import SlideCheck
from app.services.kernel.validation_result import ValidationResult, ValidationStatus, Severity
from app.domain.entities import Slide, Paragraph, ListType

class ListItemsCountCheck(SlideCheck):
    """Проверка количества пунктов в маркированных и нумерованных списках"""
    
    def validate(self, slide: Slide) -> ValidationResult:
        """Проверяет что списки содержат разумное количество пунктов"""
        min_items = self.params.get('min_items', 1)      
        max_items = self.params.get('max_items', 8)      
        check_bullet = self.params.get('check_bullet', True)
        check_numbered = self.params.get('check_numbered', True)
        check_nested = self.params.get('check_nested', False)   
        
        lists_info = self._find_lists_on_slide(slide, check_bullet, check_numbered, check_nested)
        
        if not lists_info:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: списки не обнаружены"
            )
        
        issues = []
        
        for list_type, items_count, list_position in lists_info:
            if items_count < min_items:
                issues.append(
                    f"{list_type} список (позиция {list_position}): "
                    f"всего {items_count} пунктов, минимум {min_items}"
                )
            
            if items_count > max_items:
                issues.append(
                    f"{list_type} список (позиция {list_position}): "
                    f"всего {items_count} пунктов, максимум {max_items}"
                )
        
        if issues:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: {'; '.join(issues[:3])}"
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=f"Слайд {slide.page_number}: количество пунктов в списках в норме"
        )
    
    def _find_lists_on_slide(self, slide: Slide, check_bullet: bool, check_numbered: bool, check_nested: bool) -> List[Tuple[str, int, int]]:
        """Находит все списки на слайде и возвращает информацию о них"""
        lists_info = []
        current_list = None
        list_start_position = 0
        list_items_count = 0
        list_type = None
        
        for i, block in enumerate(slide.blocks, 1):
            if block.list_type == ListType.NONE:
                if current_list is not None:
                    lists_info.append((list_type, list_items_count, list_start_position))
                    current_list = None
                    list_items_count = 0
                continue
            
            block_list_type = self._get_list_type_name(block.list_type)
            
            if (block.list_type == ListType.BULLET and not check_bullet) or \
               (block.list_type in [ListType.NUMBERED, ListType.ALPHA, ListType.ROMAN] and not check_numbered):
                continue
            
            if not check_nested and block.level > 0:
                continue
            
            if current_list is None or \
               block.list_type != current_list or \
               block.level != current_list_level:
                
                if current_list is not None:
                    lists_info.append((list_type, list_items_count, list_start_position))
                
                current_list = block.list_type
                current_list_level = block.level
                list_type = block_list_type
                list_start_position = i
                list_items_count = 1
            else:
                list_items_count += 1
        
        if current_list is not None:
            lists_info.append((list_type, list_items_count, list_start_position))
        
        return lists_info
    
    def _get_list_type_name(self, list_type: ListType) -> str:
        """Возвращает читаемое название типа списка"""
        type_names = {
            ListType.BULLET: "маркированный",
            ListType.NUMBERED: "нумерованный",
            ListType.ALPHA: "буквенный",
            ListType.ROMAN: "римский"
        }
        return type_names.get(list_type, "неизвестный")


class NestedListsDepthCheck(SlideCheck):
    """Проверка глубины вложенности списков"""
    
    def validate(self, slide: Slide) -> ValidationResult:
        """        Проверяет максимальную глубину вложенности списков"""
        max_depth = self.params.get('max_depth', 2)  
        check_bullet = self.params.get('check_bullet', True)
        check_numbered = self.params.get('check_numbered', True)
        
        max_found_depth = 0
        deep_lists = []
        
        for i, block in enumerate(slide.blocks, 1):
            if block.list_type == ListType.NONE:
                continue
            
            if (block.list_type == ListType.BULLET and not check_bullet) or \
               (block.list_type in [ListType.NUMBERED, ListType.ALPHA, ListType.ROMAN] and not check_numbered):
                continue
            
            if block.level > max_found_depth:
                max_found_depth = block.level
            
            if block.level > max_depth:
                list_type_name = self._get_list_type_name(block.list_type)
                deep_lists.append(f"{list_type_name} список (позиция {i}, уровень {block.level})")
        
        if deep_lists:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=(
                    f"Слайд {slide.page_number}: превышена глубина вложенности "
                    f"(макс. {max_depth}): {', '.join(deep_lists[:2])}"
                )
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=f"Слайд {slide.page_number}: глубина вложенности списков в норме (макс. {max_found_depth})"
        )
    
    def _get_list_type_name(self, list_type: ListType) -> str:
        """Возвращает читаемое название типа списка"""
        type_names = {
            ListType.BULLET: "маркированный",
            ListType.NUMBERED: "нумерованный",
            ListType.ALPHA: "буквенный",
            ListType.ROMAN: "римский"
        }
        return type_names.get(list_type, "неизвестный")


class MixedListsCheck(SlideCheck):
    """Проверка смешанных типов списков на одном слайде"""
    
    def validate(self, slide: Slide) -> ValidationResult:
        """
        Проверяет что на слайде не смешаны разные типы списков
        """
        allow_mixed = self.params.get('allow_mixed', False)
        
        if allow_mixed:
            return ValidationResult(
                status=ValidationStatus.PASSED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: смешанные списки разрешены"
            )
        
        found_list_types = set()
        
        for block in slide.blocks:
            if block.list_type != ListType.NONE:
                found_list_types.add(block.list_type)
        
        if len(found_list_types) > 1:
            type_names = [self._get_list_type_name(t) for t in found_list_types]
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=(
                    f"Слайд {slide.page_number}: смешаны разные типы списков: "
                    f"{', '.join(type_names)}"
                )
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=f"Слайд {slide.page_number}: типы списков согласованы"
        )
    
    def _get_list_type_name(self, list_type: ListType) -> str:
        """Возвращает читаемое название типа списка"""
        type_names = {
            ListType.BULLET: "маркированный",
            ListType.NUMBERED: "нумерованный",
            ListType.ALPHA: "буквенный",
            ListType.ROMAN: "римский"
        }
        return type_names.get(list_type, "неизвестный")