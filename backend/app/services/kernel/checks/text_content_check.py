import re
from typing import List
from app.services.kernel.base_checks import  SlideCheck
from app.services.kernel.validation_result import ValidationResult, ValidationStatus, Severity
from app.domain.entities import Slide

class LongPhrasesCheck(SlideCheck):
    
    def validate(self, slide: Slide) -> ValidationResult:
        max_phrase_length = self.params.get('max_length', 80)
        long_phrases = []
        
        for block in slide.blocks:
            sentences = self._split_into_sentences(block.text)
            for sentence in sentences:
                phrases = self._split_into_phrases(sentence)
                for phrase in phrases:
                    clean_phrase = phrase.strip()
                    if len(clean_phrase) > max_phrase_length:
                        long_phrases.append(clean_phrase[:50] + "..." if len(clean_phrase) > 50 else clean_phrase)
        
        if long_phrases:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=(
                    f"Слайд {slide.page_number}: обнаружены длинные фразы "
                    f"(>{max_phrase_length} символов): {', '.join(long_phrases[:3])}"
                    f"{'...' if len(long_phrases) > 3 else ''}"
                )
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=f"Слайд {slide.page_number}: длинные фразы в норме"
        )
    
    def _split_into_sentences(self, text: str) -> List[str]:
        if not text:
            return []        
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _split_into_phrases(self, sentence: str) -> List[str]:
        if not sentence:
            return []
        
        phrases = re.split(r'[,;:]+', sentence)
        return [p.strip() for p in phrases if p.strip()]

class ParagraphLengthCheck(SlideCheck):
    
    def validate(self, slide: Slide) -> ValidationResult:
        max_paragraph_length = self.params.get('max_length', 300)  
        min_paragraph_length = self.params.get('min_length', 10)   
        long_paragraphs = []
        short_paragraphs = []
        
        for i, block in enumerate(slide.blocks, 1):
            text_length = len(block.text.strip())
            
            if text_length > max_paragraph_length:
                long_paragraphs.append((i, text_length))
            elif text_length < min_paragraph_length and text_length > 0:
                short_paragraphs.append((i, text_length))
        
        issues = []
        if long_paragraphs:
            long_desc = ", ".join([f"абзац {num}({length} симв.)" for num, length in long_paragraphs[:3]])
            issues.append(f"слишком длинные абзацы: {long_desc}")
        
        if short_paragraphs:
            short_desc = ", ".join([f"абзац {num}({length} симв.)" for num, length in short_paragraphs[:3]])
            issues.append(f"слишком короткие абзацы: {short_desc}")
        
        if issues:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: {'; '.join(issues)}"
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=f"Слайд {slide.page_number}: длина абзацев в норме"
        )

class SentenceCountCheck(SlideCheck):
    
    def validate(self, slide: Slide) -> ValidationResult:
        max_sentences = self.params.get('max_sentences', 5)
        min_sentences = self.params.get('min_sentences', 1)
        
        problematic_paragraphs = []
        
        for i, block in enumerate(slide.blocks, 1):
            sentences = self._count_sentences(block.text)
            
            if sentences > max_sentences:
                problematic_paragraphs.append((i, sentences, "много"))
            elif sentences < min_sentences and block.text.strip():
                problematic_paragraphs.append((i, sentences, "мало"))
        
        if problematic_paragraphs:
            issues = []
            for num, count, problem in problematic_paragraphs:
                issues.append(f"абзац {num}({count} предл.)")
            
            problem_desc = ", ".join(issues[:3])
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: {problem_desc}"
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=f"Слайд {slide.page_number}: количество предложений в абзацах в норме"
        )
    
    def _count_sentences(self, text: str) -> int:
        if not text.strip():
            return 0
        
        sentences = re.split(r'[.!?]+', text)
        return len([s for s in sentences if s.strip()])

class TextDensityCheck(SlideCheck):
    
    def validate(self, slide: Slide) -> ValidationResult:
        max_total_chars = self.params.get('max_total_chars', 1500)
        max_blocks = self.params.get('max_blocks', 10)
        
        total_chars = sum(len(block.text) for block in slide.blocks)
        blocks_count = len(slide.blocks)
        
        issues = []
        if total_chars > max_total_chars:
            issues.append(f"слишком много текста ({total_chars} символов)")
        
        if blocks_count > max_blocks:
            issues.append(f"слишком много блоков ({blocks_count})")
        
        if issues:
            return ValidationResult(
                status=ValidationStatus.FAILED,
                severity=Severity[self.severity.upper()],
                rule_name=self.rule_name,
                message=f"Слайд {slide.page_number}: {'; '.join(issues)}"
            )
        
        return ValidationResult(
            status=ValidationStatus.PASSED,
            severity=Severity[self.severity.upper()],
            rule_name=self.rule_name,
            message=f"Слайд {slide.page_number}: плотность текста в норме"
        )

class CapitalizationCheck(SlideCheck):
    
    def validate(self, slide: Slide) -> ValidationResult:
        check_titles = self.params.get('check_titles', True)
        check_sentences = self.params.get('check_sentences', True)
        
        issues = []
        
        for i, block in enumerate(slide.blocks, 1):
            text = block.text.strip()
            if not text:
                continue
            
            if check_titles and i == 1 and not text[0].isupper():
                issues.append(f"абзац {i}: заголовок должен начинаться с заглавной буквы")
            
            if check_sentences:
                sentence_issues = self._check_sentence_capitalization(text, i)
                issues.extend(sentence_issues)
        
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
            message=f"Слайд {slide.page_number}: капитализация в норме"
        )
    
    def _check_sentence_capitalization(self, text: str, paragraph_num: int) -> List[str]:
        issues = []
        sentences = re.split(r'[.!?]+', text)
        
        for j, sentence in enumerate(sentences):
            clean_sentence = sentence.strip()
            if not clean_sentence:
                continue
            
            if len(clean_sentence) < 5:
                continue
            
            if not clean_sentence[0].isupper():
                preview = clean_sentence[:20] + "..." if len(clean_sentence) > 20 else clean_sentence
                issues.append(f"абзац {paragraph_num}: предложение '{preview}' должно начинаться с заглавной буквы")
        
        return issues
