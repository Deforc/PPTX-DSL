from app.services.kernel.checks.slides_count_check import SlidesCountCheck
from app.services.kernel.checks.font_count_check import (
    FontCountPresentationCheck,
    FontCountSlideCheck
)
from app.services.kernel.checks.heading_presence_check import HeadingPresenceCheck
from app.services.kernel.checks.font_sizes_count_check import (
    FontSizesCountPresentationCheck,
    FontSizesCountSlideCheck
)
from app.services.kernel.checks.sentence_length_check import SentenceLengthCheck
from app.services.kernel.checks.list_nesting_check import ListNestingCheck
from app.services.kernel.checks.list_consistency_check import (
    ListConsistencyPresentationCheck,
    ListConsistencySlideCheck
)
from app.services.kernel.checks.font_min_size_check import (
    FontMinSizePresentationCheck,
    FontMinSizeSlideCheck
)
from app.services.kernel.checks.uppercase_percent_check import (
    UppercasePercentPresentationCheck,
    UppercasePercentSlideCheck
)
from app.services.kernel.checks.elements_count_check import ElementsCountCheck
from app.services.kernel.checks.spelling_check import SpellingCheck

__all__ = [
    'SlidesCountCheck',
    'FontCountPresentationCheck',
    'FontSizesCountPresentationCheck',
    'ListConsistencyPresentationCheck',
    'FontMinSizePresentationCheck',
    'UppercasePercentPresentationCheck',
    
    'FontCountSlideCheck',
    'HeadingPresenceCheck',
    'FontSizesCountSlideCheck',
    'SentenceLengthCheck',
    'ListNestingCheck',
    'ListConsistencySlideCheck',
    'FontMinSizeSlideCheck',
    'UppercasePercentSlideCheck',
    'ElementsCountCheck',
    'SpellingCheck',
]
