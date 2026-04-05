"""
Unit tests for diet_config.py

Test strategy: pure-function coverage with no external dependencies
(no database, no network). Each test is self-contained and deterministic.

Framework: pytest
Coverage: BMR/TDEE calculation, macro adherence scoring,
          allergen detection, portion feedback, macro gram conversion.
"""
import sys
import os
import pytest

# Ensure project root is on path so imports resolve without installing the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from diet_config import (
    calculate_bmr,
    calculate_tdee,
    calculate_macro_grams,
    compute_macro_adherence_10pt,
    detect_allergens_from_text,
    portion_feedback,
    score_meal_adherence,
    get_activity_multiplier,
)


# ---------------------------------------------------------------------------
# TC-01  calculate_bmr — male
# ---------------------------------------------------------------------------
class TestCalculateBmrMale:
    """
    Test case TC-01: BMR calculation for a male user.

    Input:  weight_kg=70, height_cm=175, age=25, biological_sex='male'
    Formula (Mifflin-St Jeor): (10×70) + (6.25×175) − (5×25) + 5 = 1673.75
    Oracle: returns 1673.75
    Success: assert result == 1673.75
    Failure: any other numeric value or exception
    """

    def test_bmr_male_known_values(self):
        result = calculate_bmr(
            weight_kg=70, height_cm=175, age=25, biological_sex="male"
        )
        assert result == pytest.approx(1673.75, rel=1e-4), (
            f"Expected 1673.75, got {result}"
        )

    def test_bmr_male_offset_is_positive_5(self):
        """Male formula adds +5; female subtracts -161. Difference should be 166."""
        male = calculate_bmr(70, 175, 25, "male")
        female = calculate_bmr(70, 175, 25, "female")
        assert pytest.approx(male - female, rel=1e-4) == 166


# ---------------------------------------------------------------------------
# TC-02  calculate_bmr — female
# ---------------------------------------------------------------------------
class TestCalculateBmrFemale:
    """
    Test case TC-02: BMR calculation for a female user.

    Input:  weight_kg=60, height_cm=165, age=30, biological_sex='female'
    Formula: (10×60) + (6.25×165) − (5×30) − 161 = 1320.25
    Oracle: returns 1320.25
    Success: assert result == 1320.25
    Failure: any other numeric value or exception
    """

    def test_bmr_female_known_values(self):
        result = calculate_bmr(
            weight_kg=60, height_cm=165, age=30, biological_sex="female"
        )
        assert result == pytest.approx(1320.25, rel=1e-4), (
            f"Expected 1320.25, got {result}"
        )

    def test_bmr_other_sex_uses_female_formula(self):
        """'other' should use the female branch (subtract 161)."""
        other = calculate_bmr(60, 165, 30, "other")
        female = calculate_bmr(60, 165, 30, "female")
        assert other == pytest.approx(female, rel=1e-4)

