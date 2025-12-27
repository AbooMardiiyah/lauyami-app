"""Caching layer for legal analysis results."""

import hashlib
import json
from datetime import datetime, timedelta
from typing import Any

from src.utils.logger_util import setup_logging

logger = setup_logging()

_analysis_cache: dict[str, dict[str, Any]] = {}
CACHE_TTL = timedelta(hours=24) 


def _generate_cache_key(agreement_text: str, language: str) -> str:
    """Generate a unique cache key from agreement text and language.
    
    Args:
        agreement_text: The agreement text
        language: Language code
        
    Returns:
        str: MD5 hash of the content
    """
    content = f"{agreement_text}:{language}"
    return hashlib.md5(content.encode()).hexdigest()


def get_cached_analysis(agreement_text: str, language: str = "en") -> str | None:
    """Get cached analysis if available and not expired.
    
    Args:
        agreement_text: The agreement text
        language: Language code
        
    Returns:
        str | None: Cached analysis text or None if not found/expired
    """
    cache_key = _generate_cache_key(agreement_text, language)
    
    if cache_key in _analysis_cache:
        cached = _analysis_cache[cache_key]
        cached_time = cached.get("timestamp")
        
        if cached_time and datetime.now() - cached_time < CACHE_TTL:
            logger.info(f"Cache HIT for key {cache_key[:8]}... (age: {datetime.now() - cached_time})")
            return cached.get("analysis")
        else:
            logger.info(f"Cache EXPIRED for key {cache_key[:8]}...")
            del _analysis_cache[cache_key]
    
    logger.info(f"Cache MISS for key {cache_key[:8]}...")
    return None


def set_cached_analysis(agreement_text: str, analysis: str, language: str = "en") -> None:
    """Cache analysis results.
    
    Args:
        agreement_text: The agreement text
        analysis: The analysis result
        language: Language code
    """
    cache_key = _generate_cache_key(agreement_text, language)
    
    _analysis_cache[cache_key] = {
        "analysis": analysis,
        "timestamp": datetime.now(),
        "language": language,
    }
    
    logger.info(f"Cached analysis for key {cache_key[:8]}... (total cached: {len(_analysis_cache)})")
    
    if len(_analysis_cache) > 1000:
        _cleanup_expired_cache()


def _cleanup_expired_cache() -> None:
    """Remove expired entries from cache."""
    now = datetime.now()
    expired_keys = [
        key for key, value in _analysis_cache.items()
        if now - value.get("timestamp", now) >= CACHE_TTL
    ]
    
    for key in expired_keys:
        del _analysis_cache[key]
    
    logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")


def clear_cache() -> None:
    """Clear all cached analyses."""
    _analysis_cache.clear()
    logger.info("Cache cleared")


def get_cache_stats() -> dict[str, Any]:
    """Get cache statistics.
    
    Returns:
        dict: Cache statistics
    """
    now = datetime.now()
    valid_entries = sum(
        1 for value in _analysis_cache.values()
        if now - value.get("timestamp", now) < CACHE_TTL
    )
    
    return {
        "total_entries": len(_analysis_cache),
        "valid_entries": valid_entries,
        "expired_entries": len(_analysis_cache) - valid_entries,
        "cache_ttl_hours": CACHE_TTL.total_seconds() / 3600,
    }

