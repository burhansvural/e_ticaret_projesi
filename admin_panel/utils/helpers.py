"""
Helper utility functions
"""
import re
from datetime import datetime


def format_currency(amount: float) -> str:
    """Format amount as Turkish Lira currency"""
    if amount is None:
        return "₺0.00"
    return f"₺{amount:,.2f}".replace(",", ".")


def format_date(date_str: str) -> str:
    """Format ISO date string to readable format"""
    if not date_str:
        return ""
    
    try:
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime("%d.%m.%Y %H:%M")
    except:
        return date_str


def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate Turkish phone number format"""
    if not phone:
        return True  # Phone is optional
    
    # Remove spaces and common separators
    phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # Check if it's a valid Turkish phone number
    pattern = r'^(\+90|0)?[0-9]{10}$'
    return re.match(pattern, phone) is not None


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to max length with ellipsis"""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."


def get_status_color(status: str) -> str:
    """Get color for order status"""
    status_colors = {
        "pending": "#FFA726",      # Orange
        "processing": "#42A5F5",   # Blue
        "shipped": "#66BB6A",      # Green
        "delivered": "#26A69A",    # Teal
        "cancelled": "#EF5350",    # Red
        "returned": "#AB47BC"      # Purple
    }
    return status_colors.get(status.lower(), "#757575")


def get_status_text(status: str) -> str:
    """Get Turkish text for order status"""
    status_texts = {
        "pending": "Beklemede",
        "processing": "İşleniyor",
        "shipped": "Kargoda",
        "delivered": "Teslim Edildi",
        "cancelled": "İptal Edildi",
        "returned": "İade Edildi"
    }
    return status_texts.get(status.lower(), status)