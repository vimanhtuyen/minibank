import re
import tkinter as tk
from tkinter import ttk

BIDV_DARK_BLUE = '#003b73'
BIDV_BLUE = '#005aa9'
BIDV_LIGHT_BLUE = '#eaf3fb'
BIDV_RED = '#da1f26'
BIDV_TEXT = '#16324f'
BIDV_MUTED = '#6e7f93'
BIDV_SURFACE = '#ffffff'
BIDV_BACKGROUND = '#f3f7fb'
BIDV_BORDER = '#d7e3f1'


def read_non_negative_integer(text: str) -> int:
    raw = str(text).strip()
    if raw == '' or not raw.isdigit():
        return -1
    return int(raw)


def read_positive_integer(text: str) -> int:
    value = read_non_negative_integer(text)
    if value <= 0:
        return -1
    return value


def is_pin_format_valid(pin_code: str) -> bool:
    raw = str(pin_code).strip()
    return raw.isdigit() and 4 <= len(raw) <= 6


def normalize_money_text(text: str) -> str:
    raw = str(text).strip()
    raw = re.sub(r'[\s\.,_]', '', raw)
    return raw


def read_money_amount(text: str) -> int:
    raw = normalize_money_text(text)
    if raw == '' or not raw.isdigit():
        return -1
    value = int(raw)
    if value < 0:
        return -1
    return value


def format_money_vnd(amount: int) -> str:
    try:
        value = int(amount)
    except Exception:
        value = 0
    return f'{value:,} VNĐ'.replace(',', '.')


def format_interest_rate(rate: float) -> str:
    try:
        value = float(rate)
    except Exception:
        value = 0.0
    return f'{value:.2f}%/năm'


def mask_pin(pin_code: str) -> str:
    raw = str(pin_code)
    return '' if raw == '' else '*' * len(raw)


def get_transaction_type_display(transaction_type: str) -> str:
    raw = str(transaction_type).strip().lower()
    mapping = {
        'deposit': 'Nạp tiền',
        'withdraw': 'Rút tiền',
        'transfer_out': 'Chuyển đi',
        'transfer_in': 'Nhận tiền',
        'transfer': 'Chuyển khoản',
        'savings_open': 'Gửi tiết kiệm',
        'savings_close': 'Tất toán tiết kiệm',
    }
    return mapping.get(raw, str(transaction_type))


def build_transaction_search_text(transaction) -> str:
    parts = [
        str(getattr(transaction, 'transaction_id', '')),
        str(getattr(transaction, 'time_text', '')),
        str(getattr(transaction, 'transaction_type', '')),
        str(getattr(transaction, 'amount', '')),
        str(getattr(transaction, 'note', '')),
        str(getattr(transaction, 'from_account_id', '')),
        str(getattr(transaction, 'to_account_id', '')),
    ]
    return ' '.join(parts).lower()


def short_account_text(account_id: str) -> str:
    raw = str(account_id).strip()
    if len(raw) <= 4:
        return raw
    return f'...{raw[-4:]}'


def clamp_window_size(widget, desired_width: int, desired_height: int, min_width: int = 640, min_height: int = 420, margin_x: int = 80, margin_y: int = 100):
    screen_width = max(int(widget.winfo_screenwidth()), min_width)
    screen_height = max(int(widget.winfo_screenheight()), min_height)
    width = max(min_width, min(int(desired_width), screen_width - margin_x))
    height = max(min_height, min(int(desired_height), screen_height - margin_y))
    return width, height


def center_window(window, parent=None, width=None, height=None) -> None:
    window.update_idletasks()
    if width is None:
        width = max(window.winfo_width(), 1)
    if height is None:
        height = max(window.winfo_height(), 1)

    if parent is not None and parent.winfo_exists():
        parent.update_idletasks()
        try:
            parent_x = parent.winfo_rootx()
            parent_y = parent.winfo_rooty()
            parent_width = parent.winfo_width()
            parent_height = parent.winfo_height()
            x = parent_x + max((parent_width - width) // 2, 0)
            y = parent_y + max((parent_height - height) // 2, 0)
        except Exception:
            x = max((window.winfo_screenwidth() - width) // 2, 0)
            y = max((window.winfo_screenheight() - height) // 2 - 20, 0)
    else:
        x = max((window.winfo_screenwidth() - width) // 2, 0)
        y = max((window.winfo_screenheight() - height) // 2 - 20, 0)
    window.geometry(f'{width}x{height}+{x}+{y}')


def apply_responsive_toplevel(window, parent=None, default_width: int = 900, default_height: int = 620, min_width: int = 680, min_height: int = 460) -> None:
    width, height = clamp_window_size(window, default_width, default_height, min_width=min_width, min_height=min_height)
    window.geometry(f'{width}x{height}')
    window.minsize(min_width, min_height)
    window.resizable(True, True)
    center_window(window, parent=parent, width=width, height=height)


class ScrollableContent(ttk.Frame):
    def __init__(self, parent, frame_style: str = 'App.TFrame', canvas_bg: str = BIDV_BACKGROUND):
        super().__init__(parent, style=frame_style)
        self.canvas = tk.Canvas(self, highlightthickness=0, borderwidth=0, background=canvas_bg)
        self.scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)

        self.body = ttk.Frame(self.canvas, style=frame_style)
        self.window_id = self.canvas.create_window((0, 0), window=self.body, anchor='nw')

        self.body.bind('<Configure>', self._on_body_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        self.canvas.bind('<Enter>', self._bind_mousewheel)
        self.canvas.bind('<Leave>', self._unbind_mousewheel)

    def _on_body_configure(self, event=None) -> None:
        bbox = self.canvas.bbox('all')
        if bbox is not None:
            self.canvas.configure(scrollregion=bbox)

    def _on_canvas_configure(self, event=None) -> None:
        if event is not None:
            self.canvas.itemconfigure(self.window_id, width=event.width)

    def _bind_mousewheel(self, event=None) -> None:
        self.canvas.bind_all('<MouseWheel>', self._on_mousewheel)
        self.canvas.bind_all('<Button-4>', self._on_mousewheel_linux)
        self.canvas.bind_all('<Button-5>', self._on_mousewheel_linux)

    def _unbind_mousewheel(self, event=None) -> None:
        self.canvas.unbind_all('<MouseWheel>')
        self.canvas.unbind_all('<Button-4>')
        self.canvas.unbind_all('<Button-5>')

    def _on_mousewheel(self, event) -> None:
        delta = 0
        if getattr(event, 'delta', 0) != 0:
            delta = -1 if event.delta > 0 else 1
        if delta != 0:
            self.canvas.yview_scroll(delta, 'units')

    def _on_mousewheel_linux(self, event) -> None:
        if getattr(event, 'num', None) == 4:
            self.canvas.yview_scroll(-1, 'units')
        elif getattr(event, 'num', None) == 5:
            self.canvas.yview_scroll(1, 'units')
