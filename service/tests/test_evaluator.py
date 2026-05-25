"""Tests for evaluator.py — threshold logic."""

from evaluator import evaluate_reading


def test_normal_reading_below_warning():
    """A reading well below warning threshold returns 'normal'."""
    result = evaluate_reading(current_level=5.0, warning=7.0, critical=7.3)
    assert result == "normal"


def test_warning_reading_at_warning_threshold():
    """A reading exactly at the warning threshold returns 'warning'."""
    result = evaluate_reading(current_level=7.0, warning=7.0, critical=7.3)
    assert result == "warning"


def test_warning_reading_between_thresholds():
    """A reading between warning and critical returns 'warning'."""
    result = evaluate_reading(current_level=7.1, warning=7.0, critical=7.3)
    assert result == "warning"


def test_critical_reading_at_critical_threshold():
    """A reading exactly at the critical threshold returns 'critical'."""
    result = evaluate_reading(current_level=7.3, warning=7.0, critical=7.3)
    assert result == "critical"


def test_critical_reading_above_critical_threshold():
    """A reading above critical returns 'critical'."""
    result = evaluate_reading(current_level=8.0, warning=7.0, critical=7.3)
    assert result == "critical"
