import hashlib
import re
from typing import Dict


def calculate_sha256(text: str) -> str:
    """
    Calculate the SHA-256 hash of a string.
    
    Args:
        text: The input string to hash
        
    Returns:
        The hexadecimal SHA-256 hash string
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def is_palindrome(text: str) -> bool:
    """
    Check if a string is a palindrome.
    Case-insensitive comparison, ignores spaces and non-alphanumeric characters.
    
    Args:
        text: The input string to check
        
    Returns:
        True if the string is a palindrome, False otherwise
    """
    # Remove non-alphanumeric characters and convert to lowercase
    cleaned = re.sub(r'[^a-zA-Z0-9]', '', text).lower()
    return cleaned == cleaned[::-1]


def count_unique_characters(text: str) -> int:
    """
    Count the number of distinct characters in a string.
    
    Args:
        text: The input string to analyze
        
    Returns:
        The count of unique characters
    """
    return len(set(text))


def get_word_count(text: str) -> int:
    """
    Count the number of words in a string.
    Words are separated by whitespace.
    
    Args:
        text: The input string to analyze
        
    Returns:
        The number of words in the string
    """
    # Split by whitespace and filter out empty strings
    words = text.split()
    return len(words)


def get_character_frequency(text: str) -> Dict[str, int]:
    """
    Calculate the frequency of each character in a string.
    
    Args:
        text: The input string to analyze
        
    Returns:
        A dictionary mapping each character to its frequency count
    """
    frequency_map = {}
    for char in text:
        frequency_map[char] = frequency_map.get(char, 0) + 1
    return frequency_map
