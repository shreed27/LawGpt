"""Language detection for Hinglish vs English."""
import re
from typing import Literal

# Hinglish indicators - common Hindi words in English script
HINGLISH_WORDS = {
    "aap", "tum", "aapka", "tumhara", "aapki", "tumhari", "aapne", "tumne",
    "hai", "hain", "ho", "hoga", "hogi", "honge", "hote", "hoti",
    "kya", "kyun", "kaise", "kab", "kahan", "kisne", "kisko", "kiski",
    "mein", "se", "ko", "ka", "ki", "ke", "par", "aur", "ya", "bhi",
    "nahi", "nahin", "na", "toh", "phir", "ab", "tab", "jab", "agar",
    "to", "lekin", "magar", "kyunki", "karke", "kar", "kara", "kare",
    "hota", "hoti", "hote", "hona", "hone", "honi", "hone", "huye",
    "gaya", "gayi", "gaye", "ja", "jaye", "jaye", "jata", "jati", "jate"
}

# Hinglish patterns
HINGLISH_PATTERNS = [
    r'\b(aap|tum|aapka|tumhara)\b',
    r'\b(kya|kyun|kaise|kab|kahan)\b',
    r'\b(hai|hain|ho|hoga|hogi)\b',
    r'\b(mein|se|ko|ka|ki|ke|par|aur)\b',
    r'\b(nahi|nahin|na|toh|phir)\b',
]


def detect_hinglish_preference(query: str) -> Literal["hinglish", "english"]:
    """
    Detect if user prefers Hinglish or English response.
    
    Args:
        query: User query text
        
    Returns:
        "hinglish" or "english" based on detected preference
    """
    query_lower = query.lower()
    
    # Count Hinglish words
    hinglish_count = sum(1 for word in HINGLISH_WORDS if word in query_lower)
    
    # Check for Hinglish patterns
    pattern_matches = sum(
        1 for pattern in HINGLISH_PATTERNS 
        if re.search(pattern, query_lower)
    )
    
    # If significant Hinglish indicators, return hinglish
    if hinglish_count >= 2 or pattern_matches >= 2:
        return "hinglish"
    
    # Check for mixed language (Hindi words in English context)
    hindi_word_ratio = hinglish_count / max(len(query_lower.split()), 1)
    if hindi_word_ratio > 0.1:  # More than 10% Hindi words
        return "hinglish"
    
    return "english"

