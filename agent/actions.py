"""
Investigative actions: the mechanisms that reduce uncertainty.

Each action gathers data about a specific aspect of the profile.
"""

from typing import Optional


class BioAnalyzer:
    """Analyze profile bio for values, interests, and red flags."""
    
    # Semantic keywords mapped to values
    VALUES_KEYWORDS = {
        "honest": ["honest", "authentic", "genuine", "real", "sincere"],
        "ambitious": ["goal", "career", "passion", "startup", "achievement", "driven"],
        "adventurous": ["travel", "hike", "adventure", "explore", "backpack"],
        "family_oriented": ["family", "kids", "home", "tradition", "roots"],
        "intellectual": ["book", "read", "think", "philosophy", "science", "learn"],
        "creative": ["art", "music", "write", "design", "create"],
        "outdoorsy": ["nature", "trail", "bike", "climb", "ski"],
        "social": ["friend", "party", "community", "people", "connect"],
    }
    
    RED_FLAG_KEYWORDS = [
        "toxic",
        "drama",
        "control",
        "angry",
        "hate",
        "never again",
        "broken",
        "single parent (depending on context)",
        "ex",
    ]
    
    @staticmethod
    def analyze(bio: str) -> dict:
        """
        Extract values and red flags from bio text.
        
        Returns:
            {
                "values": ["honest", "ambitious", ...],
                "red_flags": ["drama", ...],
                "length": int,
                "word_count": int,
            }
        """
        bio_lower = bio.lower()
        
        # Extract values
        detected_values = []
        for value, keywords in BioAnalyzer.VALUES_KEYWORDS.items():
            if any(kw in bio_lower for kw in keywords):
                detected_values.append(value)
        
        # Extract red flags
        detected_flags = [kw for kw in BioAnalyzer.RED_FLAG_KEYWORDS if kw in bio_lower]
        
        return {
            "values": detected_values,
            "red_flags": detected_flags,
            "length": len(bio),
            "word_count": len(bio.split()),
        }


class PhotoAnalyzer:
    """Analyze photos for authenticity, quality, and consistency."""
    
    @staticmethod
    def analyze(photos: list[str]) -> dict:
        """
        Analyze photos for authenticity and quality.
        
        In production, this would call a vision model.
        For demo, we use simple heuristics.
        
        Args:
            photos: List of photo URLs or descriptions
        
        Returns:
            {
                "authenticity": "high" | "medium" | "low",
                "quality": "good" | "fair" | "poor",
                "diversity": "varied" | "limited",
                "count": int,
            }
        """
        if not photos:
            return {
                "authenticity": "low",
                "quality": "poor",
                "diversity": "none",
                "count": 0,
            }
        
        count = len(photos)
        
        # Heuristic: more photos = higher authenticity (simple proxy)
        if count >= 4:
            authenticity = "high"
        elif count >= 2:
            authenticity = "medium"
        else:
            authenticity = "low"
        
        # Quality: assume good if more than 1 photo
        quality = "good" if count > 1 else "fair"
        
        # Diversity: variety in photos
        diversity = "varied" if count >= 3 else "limited"
        
        return {
            "authenticity": authenticity,
            "quality": quality,
            "diversity": diversity,
            "count": count,
        }


class RedFlagDetector:
    """Detect behavioral red flags beyond safety constraints."""
    
    RED_FLAGS = {
        "age_gap": {
            "description": "Significant age difference (>10 years)",
            "check": lambda profile, user_age=30: abs(profile.age - user_age) > 10,
        },
        "vague_bio": {
            "description": "Bio is too vague (less than 50 chars)",
            "check": lambda profile: len(profile.bio) < 50,
        },
        "no_photos": {
            "description": "No photos provided",
            "check": lambda profile: len(profile.photos) == 0,
        },
        "single_photo": {
            "description": "Only one photo (higher catfish risk)",
            "check": lambda profile: len(profile.photos) == 1,
        },
    }
    
    @staticmethod
    def check(profile) -> list[str]:
        """
        Check for behavioral red flags.
        
        Returns: List of detected red flag names
        """
        flags = []
        for flag_name, flag_def in RedFlagDetector.RED_FLAGS.items():
            try:
                if flag_def["check"](profile):
                    flags.append(flag_name)
            except Exception:
                # Gracefully skip if check fails
                pass
        return flags
