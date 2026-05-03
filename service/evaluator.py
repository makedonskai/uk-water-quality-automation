"""
Evaluates a water level reading against a station's thresholds.
Replaces the 'Switch' node logic from n8n.
"""

def evaluate_reading(current_level: float, warning: float, critical: float) -> str:
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
    # Quick sanity check — same data we'd test in pytest later
    test_cases = [
        (7.5, 7.0, 7.3, "critical"),
        (7.1, 7.0, 7.3, "warning"),
        (6.5, 7.0, 7.3, "normal"),
        (7.3, 7.0, 7.3, "critical"),  # boundary: exactly at critical
        (7.0, 7.0, 7.3, "warning"),   # boundary: exactly at warning
    ]
    
    for current, warning, critical, expected in test_cases:
        result = evaluate_reading(current, warning, critical)
        status = "✓" if result == expected else "✗"
        print(f"{status} level={current} w={warning} c={critical} → {result} (expected {expected})")