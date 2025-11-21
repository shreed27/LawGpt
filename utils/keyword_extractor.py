"""Keyword extraction with legal stopwords filtering."""
from typing import List
import re
from collections import Counter

# Legal stopwords to filter out
LEGAL_STOPWORDS = {
    "shall", "thereof", "hereby", "whereas", "herein", "therein",
    "thereto", "hereto", "thereunder", "hereunder", "thereafter",
    "hereafter", "thereby", "hereby", "whereby", "wherein", "therein",
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "should", "could", "may", "might", "must", "can", "this",
    "that", "these", "those", "it", "its", "which", "who", "whom",
    "what", "when", "where", "why", "how", "all", "each", "every",
    "some", "any", "no", "not", "only", "just", "also", "too", "very",
    "more", "most", "less", "least", "much", "many", "few", "little"
}


def extract_keywords(text: str, top_n: int = 5) -> List[str]:
    """
    Extract top N relevant keywords from text.
    Filters out legal stopwords and common words.
    
    Args:
        text: Input text to extract keywords from
        top_n: Number of top keywords to return (default: 5)
        
    Returns:
        List of top N keywords
    """
    # Convert to lowercase and split into words
    words = re.findall(r'\b\w+\b', text.lower())
    
    # Filter out stopwords and short words (less than 3 characters)
    keywords = [
        word for word in words 
        if word not in LEGAL_STOPWORDS 
        and len(word) > 3
    ]
    
    # Count frequency
    word_freq = Counter(keywords)
    
    # Return top N keywords
    return [word for word, _ in word_freq.most_common(top_n)]

