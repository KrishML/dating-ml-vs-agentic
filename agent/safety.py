"""
Safety and ethical constraints for the dating agent.

These are FIRST-CLASS and must override all other decisions.
They are not buried in prompts—they are explicit Python code.
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class SafetyViolation:
    """Represents a safety constraint violation."""
    constraint_id: str
    description: str
    severity: str  # "HARD" (blocks decision) or "SOFT" (informs decision)


class EthicalConstraints:
    """
    Explicit safety and ethical boundaries for the agent.
    
    These must be checked BEFORE any decision is made.
    """
    
    HARD_CONSTRAINTS = {
        "age_minimum": {
            "description": "Must be 18 years old minimum",
            "check": lambda profile: profile.age >= 18,
        },
        "no_catfish": {
            "description": "Profile must show consistent, authentic identity across photos",
            "check": lambda profile: True,  # Requires vision model in production
        },
        "no_harm_intent": {
            "description": "No indicators of intent to harm or abuse",
            "check": lambda profile: not any(
                kw in profile.bio.lower() for kw in ["kill", "hurt", "abuse", "harm"]
            ),
        },
    }
    
    SOFT_CONSTRAINTS = {
        "age_gap_concerns": {
            "description": "Significant age gaps may indicate power imbalance",
            "check": lambda profile: True,  # Inform but don't block
        },
        "red_flag_language": {
            "description": "Language patterns suggesting emotional unavailability",
            "check": lambda profile: not any(
                kw in profile.bio.lower() for kw in ["toxic", "drama", "control", "angry"]
            ),
        },
    }
    
    @staticmethod
    def check_hard_constraints(profile) -> list[SafetyViolation]:
        """
        Check hard constraints. Any violation blocks a RIGHT decision.
        
        Returns: List of violations (empty if all pass)
        """
        violations = []
        for constraint_id, constraint in EthicalConstraints.HARD_CONSTRAINTS.items():
            if not constraint["check"](profile):
                violations.append(
                    SafetyViolation(
                        constraint_id=constraint_id,
                        description=constraint["description"],
                        severity="HARD",
                    )
                )
        return violations
    
    @staticmethod
    def check_soft_constraints(profile) -> list[SafetyViolation]:
        """
        Check soft constraints. Violations inform decision but don't block.
        
        Returns: List of violations (empty if all pass)
        """
        violations = []
        for constraint_id, constraint in EthicalConstraints.SOFT_CONSTRAINTS.items():
            if not constraint["check"](profile):
                violations.append(
                    SafetyViolation(
                        constraint_id=constraint_id,
                        description=constraint["description"],
                        severity="SOFT",
                    )
                )
        return violations
    
    @staticmethod
    def check_all(profile) -> tuple[list[SafetyViolation], list[SafetyViolation]]:
        """
        Check both hard and soft constraints.
        
        Returns: (hard_violations, soft_violations)
        """
        hard = EthicalConstraints.check_hard_constraints(profile)
        soft = EthicalConstraints.check_soft_constraints(profile)
        return hard, soft


class BiasDetector:
    """
    Detect and mitigate agent bias in decision-making.
    
    Common biases to watch:
    - Attractiveness bias (over-weighting photo quality)
    - Racial/ethnic bias (if visible in photos)
    - Age bias (systematic penalization of certain ages)
    - Location bias (systematic rejection of certain areas)
    """
    
    @staticmethod
    def flag_potential_biases(decision_log: dict) -> list[str]:
        """
        Analyze a series of decisions for systematic bias.
        
        In production, this would run after multiple decisions
        to detect patterns like "rejecting all profiles from X location".
        """
        # Placeholder for production bias detection
        # Would need statistical analysis of decision history
        return []
