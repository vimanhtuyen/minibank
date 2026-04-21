import re

def format_money_vnd(amount: int) -> str:
    try:
        value = int(amount)
    except Exception:
        value = 0
    return f"{value:,} VNĐ".replace(',', '.')


def format_interest_rate(rate: float) -> str:
    try:
        value = float(rate)
    except Exception:
        value = 0.0
    return f"{value:.2f}%/năm"


def normalize_money_text(text: str) -> str:
    return re.sub(r'[\s\.,_]', '', str(text).strip())


def parse_money_amount(text: str) -> int:
    raw = normalize_money_text(text)
    if raw == '' or not raw.isdigit():
        return -1
    value = int(raw)
    if value <= 0:
        return -1
    return value


def is_pin_format_valid(pin_code: str) -> bool:
    raw = str(pin_code).strip()
    return raw.isdigit() and 4 <= len(raw) <= 6


def transaction_type_display(transaction_type: str) -> str:
    mapping = {
        'deposit': 'Nạp tiền',
        'withdraw': 'Rút tiền',
        'transfer_out': 'Chuyển đi',
        'transfer_in': 'Nhận tiền',
        'transfer': 'Chuyển khoản',
        'savings_open': 'Gửi tiết kiệm',
        'savings_close': 'Tất toán tiết kiệm',
    }
    return mapping.get(str(transaction_type).strip().lower(), str(transaction_type))
