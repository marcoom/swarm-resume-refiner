"""Word Counter Tool for Resume Writer.

This tool counts words in text and checks if the count is within an acceptable
range of the target word count. The target is automatically read from the
TARGET_RESUME_WORDS environment variable.
"""

import os
from typing import Any, Dict, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ..constants import (
    DEFAULT_TARGET_WORDS,
    WORD_COUNT_TOLERANCE_MIN,
    WORD_COUNT_TOLERANCE_MAX,
)
from ..validation import validate_target_words


class WordCounterInput(BaseModel):
    """Input schema for WordCounterTool."""

    text: str = Field(
        ..., description="The text to count words in (e.g., markdown resume content)"
    )


class WordCounterOutput(BaseModel):
    """Output schema for WordCounterTool."""

    word_count: int = Field(
        ..., description="The actual number of words counted in the text"
    )
    target_word_count: int = Field(
        ..., description="The target word count that was provided"
    )
    is_within_target: bool = Field(
        ...,
        description=(
            f"True if the word count is within "
            f"{int(WORD_COUNT_TOLERANCE_MIN * 100)}%-"
            f"{int(WORD_COUNT_TOLERANCE_MAX * 100)}% of the target. "
            "False if adjustments are needed."
        ),
    )
    message: str = Field(..., description="Human-readable explanation of the result")


class WordCounterTool(BaseTool):
    """Tool for counting words and checking against target word count."""

    name: str = "Word Counter and Target Checker"
    description: str = (
        "Counts the number of words in text and checks if it's within the target range. "
        "The target word count is automatically read from the TARGET_RESUME_WORDS environment variable. "
        "Returns word_count, target_word_count, is_within_target flag, and a message. "
        f"When is_within_target is True, the word count is within "
        f"{int(WORD_COUNT_TOLERANCE_MIN * 100)}%-{int(WORD_COUNT_TOLERANCE_MAX * 100)}% range. "
        "Use this tool to check if your resume meets the word count target. "
        "IMPORTANT: Only pass the text parameter - the target is read automatically from configuration."
    )
    args_schema: Type[BaseModel] = WordCounterInput

    def _run(self, text: str) -> Dict[str, Any]:
        """Count words in text and check if within acceptable range of target.

        The target word count is automatically read from TARGET_RESUME_WORDS
        environment variable.

        Args:
            text: The text to count words in.

        Returns:
            Dictionary with word_count, target_word_count, is_within_target, and message.
        """
        target_words = int(os.getenv("TARGET_RESUME_WORDS", str(DEFAULT_TARGET_WORDS)))
        validate_target_words(target_words)

        word_count = len(text.split())

        min_acceptable = int(WORD_COUNT_TOLERANCE_MIN * target_words)
        max_acceptable = int(WORD_COUNT_TOLERANCE_MAX * target_words)

        is_within_target = min_acceptable <= word_count <= max_acceptable

        if is_within_target:
            percentage = (word_count / target_words) * 100
            message = (
                f"Word count is within target range! "
                f"Current: {word_count} words ({percentage:.1f}% of target). "
                f"Acceptable range: {min_acceptable}-{max_acceptable} words."
            )
        elif word_count < min_acceptable:
            words_needed = target_words - word_count
            message = (
                f"Word count is below target. "
                f"Current: {word_count} words. "
                f"Need about {words_needed} more words to reach target ({target_words}). "
                f"Consider expanding descriptions or adding less-critical but relevant items."
            )
        else:
            words_to_remove = word_count - target_words
            message = (
                f"Word count exceeds target. "
                f"Current: {word_count} words. "
                f"Need to remove about {words_to_remove} words to reach target ({target_words}). "
                f"Consider removing irrelevant sections or rephrasing more concisely."
            )

        return {
            "word_count": word_count,
            "target_word_count": target_words,
            "is_within_target": is_within_target,
            "message": message,
        }
