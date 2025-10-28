"""Validation utilities and custom exceptions for Resume Refiner Crew."""

from functools import wraps
from typing import Any, Callable, Dict, TypeVar

from .constants import (
    MAX_TARGET_WORDS_LIMIT,
    MIN_API_KEY_LENGTH,
    MIN_TARGET_WORDS,
)


class ValidationError(Exception):
    """Base exception for validation errors."""

    pass


class InvalidInputError(ValidationError):
    """Raised when input parameters are invalid."""

    pass


class InvalidFileError(ValidationError):
    """Raised when a file is invalid or corrupted."""

    pass


class ConfigurationError(ValidationError):
    """Raised when configuration is missing or invalid."""

    pass


F = TypeVar('F', bound=Callable[..., Any])


def validate_required_fields(*fields: str) -> Callable[[F], F]:
    """Decorator to validate required fields in a dictionary parameter.

    Args:
        *fields: Field names that must be present in the data.

    Returns:
        Decorator function.

    Examples:
        >>> @validate_required_fields('name', 'email')
        ... def process_user(data: Dict[str, Any]) -> None:
        ...     pass
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if args and isinstance(args[0], dict):
                data = args[0]
                missing = [field for field in fields if field not in data]
                if missing:
                    raise InvalidInputError(
                        f"Missing required fields: {', '.join(missing)}"
                    )
            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


def validate_target_words(target_words: int) -> None:
    """Validate target word count parameter.

    Args:
        target_words: The target word count to validate.

    Raises:
        InvalidInputError: If target_words is outside valid range.
    """
    if not isinstance(target_words, int):
        raise InvalidInputError(
            f"Target words must be an integer, got {type(target_words).__name__}"
        )

    if target_words < MIN_TARGET_WORDS:
        raise InvalidInputError(
            f"Target words must be at least {MIN_TARGET_WORDS}, got {target_words}"
        )

    if target_words > MAX_TARGET_WORDS_LIMIT:
        raise InvalidInputError(
            f"Target words must be at most {MAX_TARGET_WORDS_LIMIT}, got {target_words}"
        )


def validate_api_key(api_key: str) -> None:
    """Validate OpenAI API key.

    Args:
        api_key: The API key to validate.

    Raises:
        InvalidInputError: If API key is invalid.
    """
    if not api_key or not api_key.strip():
        raise InvalidInputError("API key cannot be empty")

    if len(api_key) < MIN_API_KEY_LENGTH:
        raise InvalidInputError(
            f"API key appears to be invalid (too short: {len(api_key)} characters)"
        )


def validate_non_empty_string(value: str, field_name: str = "value") -> None:
    """Validate that a string is not empty.

    Args:
        value: The string value to validate.
        field_name: Name of the field for error messages.

    Raises:
        InvalidInputError: If string is empty or whitespace-only.
    """
    if not isinstance(value, str):
        raise InvalidInputError(
            f"{field_name} must be a string, got {type(value).__name__}"
        )

    if not value.strip():
        raise InvalidInputError(f"{field_name} cannot be empty")


def validate_model_name(model: str) -> None:
    """Validate OpenAI model name.

    Args:
        model: The model name to validate.

    Raises:
        InvalidInputError: If model name is invalid.
    """
    validate_non_empty_string(model, "Model name")

    valid_prefixes = ("gpt-", "o1-", "o3-")
    if not any(model.startswith(prefix) for prefix in valid_prefixes):
        raise InvalidInputError(
            f"Model name '{model}' does not appear to be a valid OpenAI model"
        )


def validate_resume_bytes(resume_bytes: bytes) -> None:
    """Validate resume PDF bytes.

    Args:
        resume_bytes: The resume PDF bytes to validate.

    Raises:
        InvalidInputError: If resume bytes are invalid.
    """
    if not resume_bytes:
        raise InvalidInputError("Resume PDF bytes cannot be empty")

    if len(resume_bytes) < 100:
        raise InvalidInputError(
            f"Resume PDF appears to be invalid (too small: {len(resume_bytes)} bytes)"
        )

    if not resume_bytes.startswith(b'%PDF'):
        raise InvalidInputError("Resume file does not appear to be a valid PDF")
