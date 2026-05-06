"""
Evaluates a water level reading against a station's thresholds.
"""

from typing import Literal

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
    # Тести залишаються такими ж крутими, як і були
    test_cases = [
        (7.5, 7.0, 7.3, "critical"),
        (7.1, 7.0, 7.3, "warning"),
        (6.5, 7.0, 7.3, "normal"),
        (7.3, 7.0, 7.3, "critical"),
        (7.0, 7.0, 7.3, "warning"),
    ]

    print("Running evaluator tests...")
    for current, warning, critical, expected in test_cases:
        result = evaluate_reading(current, warning, critical)
        mark = "✅" if result == expected else "❌"
        print(f"{mark} Level: {current} (W: {warning}, C: {critical}) -> {result}")
