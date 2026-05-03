"""
Formats Telegram alert messages for breach events.
Replaces the message-formatting logic in your n8n Telegram nodes.
"""
from datetime import datetime


def format_alert(
    station_name: str,
    river: str,
    current_level: float,
    threshold: float,
    status: str,
    reading_time: str,
) -> str:
    """Build a human-readable Telegram message for a breach."""
    
    icon = "🚨" if status == "critical" else "⚠️"
    label = "CRITICAL" if status == "critical" else "WARNING"
    
    over_by = current_level - threshold
    over_pct = (over_by / threshold) * 100
    
    return (
        f"{icon} {label}: {station_name} ({river})\n"
        f"Level: {current_level:.2f}m (threshold {threshold:.2f}m)\n"
        f"Exceeded by {over_by:.2f}m ({over_pct:.1f}%)\n"
        f"Reading time: {reading_time}\n"
        f"Generated: {datetime.utcnow().isoformat()}Z"
    )


if __name__ == "__main__":
    msg = format_alert(
        station_name="Kingston",
        river="Thames",
        current_level=4.35,
        threshold=4.2,
        status="critical",
        reading_time="2026-05-01T14:30:00Z",
    )
    print(msg)