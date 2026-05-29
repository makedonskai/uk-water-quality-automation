"""
Evaluates a water level reading against a station's thresholds.
"""

import logging
from typing import Literal

from config import settings
from logging_config import setup_logging

logger = logging.getLogger(__name__)

# Визначаємо тип для статусів, щоб уникнути оддруковок
StatusType = Literal["normal", "warning", "critical", "error"]


def evaluate_reading(current_level: float, warning: float, critical: float) -> StatusType:
    """
    Return the breach status for a reading.

    Status values:
        "critical" — at or above critical threshold
        "warning"  — at or above warning threshold but below critical
        "normal"   — below warning threshold
    """
    if current_level >= critical:
        return "critical"
    if current_level >= warning:
        return "warning"
    return "normal"


if __name__ == "__main__":
    setup_logging(settings.log_level)
    # Тести залишаються такими ж крутими, як і були
    test_cases = [
        (7.5, 7.0, 7.3, "critical"),
        (7.1, 7.0, 7.3, "warning"),
        (6.5, 7.0, 7.3, "normal"),
        (7.3, 7.0, 7.3, "critical"),
        (7.0, 7.0, 7.3, "warning"),
    ]

    logger.info("Running evaluator tests")
    for current, warning, critical, expected in test_cases:
        result = evaluate_reading(current, warning, critical)
        passed = result == expected
        logger.info(
            "test case",
            extra={
                "level": current,
                "warning_threshold": warning,
                "critical_threshold": critical,
                "result": result,
                "expected": expected,
                "passed": passed,
            },
        )
