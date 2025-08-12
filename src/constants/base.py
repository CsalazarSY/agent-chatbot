"""
Base classes for constants package.

This module provides the foundational enum classes that all other
constants modules inherit from.
"""

from enum import Enum
from typing import List


class BaseEnum(str, Enum):
    """
    Base enum class for all constants.
    
    Inherits from both str and Enum to allow string comparison
    and provides utility methods for working with enum values.
    """
    
    @classmethod
    def get_all_values(cls) -> List[str]:
        """Get all enum values as a list of strings."""
        return [e.value for e in cls]
    
    @classmethod 
    def has_value(cls, value: str) -> bool:
        """Check if a value exists in the enum."""
        return value in cls.get_all_values()
    
    def __str__(self) -> str:
        """Return the string value of the enum."""
        return self.value
