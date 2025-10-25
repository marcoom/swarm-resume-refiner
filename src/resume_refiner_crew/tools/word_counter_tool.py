"""
Word Counter Tool for Resume Writer

This tool counts words in text and checks if the count is within an acceptable
range of the target word count. The target is automatically read from the
TARGET_RESUME_WORDS environment variable.
"""

import os
from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field


class WordCounterInput(BaseModel):
    """Input schema for WordCounterTool."""
    text: str = Field(..., description="The text to count words in (e.g., markdown resume content)")


class WordCounterOutput(BaseModel):
    """Output schema for WordCounterTool."""
    word_count: int = Field(..., description="The actual number of words counted in the text")
    target_word_count: int = Field(..., description="The target word count that was provided")
    is_within_target: bool = Field(
        ...,
        description="True if the word count is within 85%-115% of the target (approximately at target). "
                    "False if adjustments are needed."
    )
    message: str = Field(..., description="Human-readable explanation of the result")


class WordCounterTool(BaseTool):
    name: str = "Word Counter and Target Checker"
    description: str = (
        "Counts the number of words in text and checks if it's within the target range. "
        "The target word count is automatically read from the TARGET_RESUME_WORDS environment variable. "
        "Returns word_count, target_word_count, is_within_target flag, and a message. "
        "When is_within_target is True, the word count is approximately at the target "
        "(within 85%-115% range). Use this tool to check if your resume meets the word count target. "
        "IMPORTANT: Only pass the text parameter - the target is read automatically from configuration."
    )
    args_schema: Type[BaseModel] = WordCounterInput

    def _run(self, text: str) -> dict:
        """
        Count words in text and check if within acceptable range of target.
        The target word count is automatically read from TARGET_RESUME_WORDS environment variable.

        Args:
            text: The text to count words in

        Returns:
            Dictionary with word_count, target_word_count, is_within_target, and message
        """
        # Read target from environment variable
        target_words = int(os.getenv("TARGET_RESUME_WORDS", "500"))
        # Count words by splitting on whitespace
        # This handles markdown formatting naturally
        word_count = len(text.split())

        # Calculate acceptable range (85% to 115% of target)
        min_acceptable = int(0.85 * target_words)
        max_acceptable = int(1.15 * target_words)

        # Check if within target range
        is_within_target = min_acceptable <= word_count <= max_acceptable

        # Generate appropriate message
        if is_within_target:
            percentage = (word_count / target_words) * 100
            message = (
                f"✓ Word count is within target range! "
                f"Current: {word_count} words ({percentage:.1f}% of target). "
                f"Acceptable range: {min_acceptable}-{max_acceptable} words."
            )
        elif word_count < min_acceptable:
            words_needed = target_words - word_count
            message = (
                f"⚠ Word count is below target. "
                f"Current: {word_count} words. "
                f"Need about {words_needed} more words to reach target ({target_words}). "
                f"Consider expanding descriptions or adding less-critical but relevant items."
            )
        else:  # word_count > max_acceptable
            words_to_remove = word_count - target_words
            message = (
                f"⚠ Word count exceeds target. "
                f"Current: {word_count} words. "
                f"Need to remove about {words_to_remove} words to reach target ({target_words}). "
                f"Consider removing irrelevant sections or rephrasing more concisely."
            )

        return {
            "word_count": word_count,
            "target_word_count": target_words,
            "is_within_target": is_within_target,
            "message": message
        }
