"""
Formats Telegram alert messages for breach events.
"""
from datetime import datetime, timezone
# Імпортуємо моделі для кращої типізації
from models import EvaluationResult

def format_alert(result: EvaluationResult) -> str:
    """
    Build a human-readable Telegram message from an EvaluationResult object.
    """
    icon = "🚨" if result.status == "critical" else "⚠️"
    label = "CRITICAL" if result.status == "critical" else "WARNING"
    
    # Визначаємо поріг для розрахунку (це логіка, яку ми передали в повідомлення)
    # Примітка: у самій моделі EvaluationResult ми не зберігаємо поріг, 
    # тому в ідеалі його краще передати або додати в модель. 
    # Але для простоти використаємо поточні дані.
    
    # Форматуємо час для Telegram (наприклад: 14:30 01.05.2026)
    time_str = result.reading_time.strftime("%H:%M %d.%m.%Y") if result.reading_time else "N/A"
    
    msg_lines = [
        f"{icon} {label}: {result.station_name}",
        f"Level: {result.current_level:.2f}m",
        f"Time: {time_str}",
        f"Status: {result.message if result.message else 'Threshold breached'}",
        f"\nGenerated: {datetime.now(timezone.utc).strftime('%H:%M:%S')} UTC"
    ]
    
    return "\n".join(msg_lines)

# Залишаємо стару версію для сумісності, якщо ти ще не готова міняти виклик у main.py
def format_alert_raw(
    station_name: str,
    river: str,
    current_level: float,
    threshold: float,
    status: str,
    reading_time: datetime, # Тепер це datetime!
) -> str:
    icon = "🚨" if status == "critical" else "⚠️"
    over_by = current_level - threshold
    
    return (
        f"{icon} {status.upper()}: {station_name} ({river})\n"
        f"Level: {current_level:.2f}m (threshold {threshold:.2f}m)\n"
        f"Over by: {over_by:.2f}m\n"
        f"Time: {reading_time.strftime('%Y-%m-%d %H:%M')}"
    )

if __name__ == "__main__":
    # Тест нової логіки
    test_result = EvaluationResult(
        station_id="123",
        station_name="Kingston",
        current_level=4.35,
        reading_time=datetime.now(),
        status="critical",
        message="Water level is dangerously high!"
    )
    print(format_alert(test_result))