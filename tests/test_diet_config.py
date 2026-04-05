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


# ---------------------------------------------------------------------------
# TC-03  calculate_tdee — activity multipliers
# ---------------------------------------------------------------------------
class TestCalculateTdee:
    """
    Test case TC-03: TDEE = BMR × activity multiplier.

    Inputs:  bmr=2000, various activity levels
    Expected multipliers: sedentary=1.2, moderately_active=1.55,
    very_active=1.725, unknown→defaults to 1.2
    Oracle: TDEE equals bmr × expected_multiplier
    Success: all assertions pass
    Failure: wrong multiplier applied or exception raised
    """

    BMR = 2000.0

    def test_sedentary(self):
        assert calculate_tdee(self.BMR, "sedentary") == pytest.approx(2400.0, rel=1e-4)

    def test_lightly_active(self):
        assert calculate_tdee(self.BMR, "lightly_active") == pytest.approx(2750.0, rel=1e-4)

    def test_moderately_active(self):
        assert calculate_tdee(self.BMR, "moderately_active") == pytest.approx(3100.0, rel=1e-4)

    def test_very_active(self):
        assert calculate_tdee(self.BMR, "very_active") == pytest.approx(3450.0, rel=1e-4)

    def test_extremely_active(self):
        assert calculate_tdee(self.BMR, "extremely_active") == pytest.approx(3800.0, rel=1e-4)

    def test_unknown_activity_defaults_to_sedentary(self):
        """An unrecognised level must fall back to the sedentary multiplier (1.2)."""
        assert calculate_tdee(self.BMR, "couch_surfing") == pytest.approx(2400.0, rel=1e-4)

    def test_none_activity_defaults_to_sedentary(self):
        assert calculate_tdee(self.BMR, None) == pytest.approx(2400.0, rel=1e-4)


# ---------------------------------------------------------------------------
# TC-04  compute_macro_adherence_10pt — edge cases and scoring
# ---------------------------------------------------------------------------
class TestComputeMacroAdherence:
    """
    Test case TC-04: 10-point macro adherence scoring.

    Scoring rules:
      - Returns score=None when calories <= 0 or macros are missing.
      - Perfect match to diet targets → score == 10.0.
      - Each macro that deviates > 5% from target costs points; score is
        clamped to [1.0, 10.0].

    Oracle for perfect standard_american (50% carbs / 20% protein / 30% fat):
      2000 kcal → carbs=250g, protein=100g, fat=66.67g → score 10.0

    Oracle for deliberately wrong keto (5/25/70):
      2000 kcal with 250g carbs (= 50% vs 5% target) → heavy penalty → score 1.0
    """

    def test_zero_calories_returns_none_score(self):
        result = compute_macro_adherence_10pt(0, 50, 30, 20, "standard_american")
        assert result["score"] is None

    def test_negative_calories_returns_none_score(self):
        result = compute_macro_adherence_10pt(-100, 50, 30, 20, "standard_american")
        assert result["score"] is None

    def test_none_macro_returns_none_score(self):
        """Missing a macro value should surface a None score with explanation."""
        result = compute_macro_adherence_10pt(2000, None, 100, 66.7, "standard_american")
        assert result["score"] is None
        assert "missing" in result["explanation"].lower() or "Missing" in result["explanation"]

    def test_perfect_standard_american_scores_10(self):
        """
        standard_american: carbs=50%, protein=20%, fat=30%
        2000 kcal → carbs=250g, protein=100g, fat=66.67g → all within ±5% → 10.0
        """
        result = compute_macro_adherence_10pt(2000, 250, 100, 66.67, "standard_american")
        assert result["score"] == pytest.approx(10.0, abs=0.1)

    def test_severely_wrong_macros_score_clamps_to_1(self):
        """
        Keto target: carbs=5%, protein=25%, fat=70%
        Actual: carbs=250g(50%), protein=100g(20%), fat=66.7g(30%)
        carbs diff = 45% → penalty (0.45-0.05)*20 = 8
        fat   diff = 40% → penalty (0.40-0.05)*20 = 7
        total penalty = 15 → score = max(1, 10-15) = 1.0
        """
        result = compute_macro_adherence_10pt(2000, 250, 100, 66.7, "ketogenic")
        assert result["score"] == pytest.approx(1.0, abs=0.1)

    def test_score_is_between_1_and_10(self):
        """Score must always be within [1.0, 10.0] regardless of inputs."""
        result = compute_macro_adherence_10pt(500, 200, 5, 2, "ketogenic")
        assert 1.0 <= result["score"] <= 10.0

    def test_explanation_present_for_valid_score(self):
        result = compute_macro_adherence_10pt(2000, 250, 100, 66.67, "standard_american")
        assert "explanation" in result
        assert isinstance(result["explanation"], str)


# ---------------------------------------------------------------------------
# TC-05  detect_allergens_from_text
# ---------------------------------------------------------------------------
class TestDetectAllergens:
    """
    Test case TC-05: Keyword-based allergen detection.

    Rules:
      - Empty text or empty allergy list → returns [].
      - Returns at most one match dict per allergen (breaks after first keyword hit).
      - Each match has keys: allergen, keyword, confidence='medium'.
      - Unknown allergen slugs (not in the keywords map) → no match produced.

    Oracle:
      detect_allergens_from_text("contains milk", ["dairy"])
        → [{"allergen": "dairy", "keyword": "milk", "confidence": "medium"}]
    """

    def test_empty_text_returns_empty_list(self):
        assert detect_allergens_from_text("", ["dairy", "nuts"]) == []

    def test_none_text_returns_empty_list(self):
        assert detect_allergens_from_text(None, ["dairy"]) == []

    def test_empty_allergy_list_returns_empty_list(self):
        assert detect_allergens_from_text("contains milk and eggs", []) == []

    def test_no_matching_keywords_returns_empty_list(self):
        assert detect_allergens_from_text("grilled chicken with rice", ["dairy"]) == []

    def test_single_allergen_match(self):
        results = detect_allergens_from_text("a glass of milk", ["dairy"])
        assert len(results) == 1
        assert results[0]["allergen"] == "dairy"
        assert results[0]["keyword"] == "milk"
        assert results[0]["confidence"] == "medium"

    def test_multiple_allergens_detected(self):
        text = "pasta with cheese and egg"
        results = detect_allergens_from_text(text, ["dairy", "eggs", "gluten"])
        allergens_found = {r["allergen"] for r in results}
        assert "dairy" in allergens_found   # cheese → dairy
        assert "eggs" in allergens_found    # egg → eggs
        assert "gluten" in allergens_found  # pasta → gluten (via 'pasta' keyword)

    def test_only_one_match_per_allergen(self):
        """Text with multiple dairy keywords should only produce one dairy entry."""
        text = "butter, cheese, and milk in this dish"
        results = detect_allergens_from_text(text, ["dairy"])
        dairy_matches = [r for r in results if r["allergen"] == "dairy"]
        assert len(dairy_matches) == 1

    def test_case_insensitive_matching(self):
        """Detection should work regardless of letter case in the text."""
        results = detect_allergens_from_text("Contains MILK", ["dairy"])
        assert len(results) == 1

    def test_unknown_allergen_produces_no_match(self):
        """An allergen slug not in the keywords map should be silently skipped."""
        results = detect_allergens_from_text("contains something", ["unknown_allergen"])
        assert results == []


# ---------------------------------------------------------------------------
# TC-06  portion_feedback
# ---------------------------------------------------------------------------
class TestPortionFeedback:
    """
    Test case TC-06: Human-readable portion feedback string.

    Threshold table:
      < 20%  → 'Light meal'
      20-40% → 'Balanced portion'
      40-60% → 'Hearty meal'
      > 60%  → 'Very heavy'

    Returns '' when either calories or daily_target is falsy / zero.

    Oracle:
      portion_feedback(300, 2000, 'breakfast') → starts with 'Light meal'
      portion_feedback(0,   2000, 'lunch')     → ''
    """

    DAILY_TARGET = 2000.0

    def test_zero_calories_returns_empty_string(self):
        assert portion_feedback(0, self.DAILY_TARGET, "lunch") == ""

    def test_zero_daily_target_returns_empty_string(self):
        assert portion_feedback(400, 0, "lunch") == ""

    def test_none_daily_target_returns_empty_string(self):
        assert portion_feedback(400, None, "lunch") == ""

    def test_light_meal_below_20_percent(self):
        # 300 / 2000 = 15% → Light
        feedback = portion_feedback(300, self.DAILY_TARGET, "breakfast")
        assert feedback.startswith("Light meal")

    def test_balanced_portion_at_30_percent(self):
        # 600 / 2000 = 30% → Balanced
        feedback = portion_feedback(600, self.DAILY_TARGET, "lunch")
        assert feedback.startswith("Balanced portion")

    def test_hearty_meal_at_45_percent(self):
        # 900 / 2000 = 45% → Hearty
        feedback = portion_feedback(900, self.DAILY_TARGET, "dinner")
        assert feedback.startswith("Hearty meal")

    def test_very_heavy_above_60_percent(self):
        # 1400 / 2000 = 70% → Very heavy
        feedback = portion_feedback(1400, self.DAILY_TARGET, "dinner")
        assert feedback.startswith("Very heavy")

    def test_workout_context_note_appended(self):
        """pre_workout and post_workout contexts add ' for your workout' to feedback."""
        feedback = portion_feedback(300, self.DAILY_TARGET, "pre_workout")
        assert "workout" in feedback

    def test_non_workout_context_no_extra_note(self):
        feedback = portion_feedback(300, self.DAILY_TARGET, "lunch")
        assert "workout" not in feedback