import re
import tkinter as tk
from tkinter import ttk, messagebox

from src.core.models import get_current_time_text
from src.ui.ui_helpers import center_window, format_interest_rate, format_money_vnd, read_positive_integer


class SavingDepositDialog(tk.Toplevel):
    def __init__(self, parent, bank_service, account_id: str, current_balance: int, success_callback):
        super().__init__(parent)
        self.bank_service = bank_service
        self.account_id = str(account_id)
        self.current_balance = int(current_balance)
        self.success_callback = success_callback

        self.title('Gửi tiết kiệm theo lãi suất')
        dialog_width = min(max(self.winfo_screenwidth() - 120, 720), 780)
        dialog_height = min(max(self.winfo_screenheight() - 140, 520), 640)
        self.geometry(f'{dialog_width}x{dialog_height}')
        self.minsize(720, 520)
        self.resizable(True, True)
        self.transient(parent)
        self.grab_set()

        self.summary_var = tk.StringVar(value='Chưa có thông tin xem trước.')
        self.term_var = tk.StringVar(value='6')

        outer = ttk.Frame(self, style='Card.TFrame')
        outer.pack(fill='both', expand=True)

        content_shell = ttk.Frame(outer, style='Card.TFrame')
        content_shell.pack(fill='both', expand=True)

        self.canvas = tk.Canvas(content_shell, highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(content_shell, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)

        self.scroll_frame = ttk.Frame(self.canvas, style='Card.TFrame')
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor='nw')
        self.scroll_frame.bind('<Configure>', self._on_scroll_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)

        main = ttk.Frame(self.scroll_frame, style='Card.TFrame', padding=(20, 18))
        main.pack(fill='both', expand=True)

        ttk.Label(main, text='Mở sổ tiết kiệm', style='SectionTitle.TLabel').pack(anchor='w')
        ttk.Label(
            main,
            text='Nhập số tiền gửi, lãi suất năm và kỳ hạn tháng. Hệ thống sẽ tự tính tiền lãi dự kiến và ngày đáo hạn.',
            style='Surface.TLabel',
            wraplength=700,
            justify='left',
        ).pack(anchor='w', pady=(6, 14))

        info_frame = ttk.LabelFrame(main, text='Thông tin tài khoản', style='Card.TLabelframe')
        info_frame.pack(fill='x')
        info_frame.columnconfigure(0, weight=1)
        info_frame.columnconfigure(1, weight=1)
        ttk.Label(info_frame, text=f'Số tài khoản: {self.account_id}', style='Strong.TLabel').grid(row=0, column=0, sticky='w', pady=(0, 6))
        ttk.Label(info_frame, text=f'Số dư khả dụng: {format_money_vnd(self.current_balance)}', style='Strong.TLabel').grid(row=0, column=1, sticky='e', pady=(0, 6))
        ttk.Label(info_frame, text='Gợi ý: chọn kỳ hạn 1, 3, 6, 12 hoặc 24 tháng.', style='Surface.TLabel').grid(row=1, column=0, sticky='w')
        ttk.Label(info_frame, text='Lãi được tính theo công thức đơn: gốc × lãi suất năm × số tháng / 12.', style='Surface.TLabel').grid(row=1, column=1, sticky='e')

        form = ttk.LabelFrame(main, text='Thiết lập sổ tiết kiệm', style='Card.TLabelframe')
        form.pack(fill='x', pady=(12, 12))
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text='Số tiền gửi (VNĐ)', style='Surface.TLabel').grid(row=0, column=0, sticky='w', pady=8)
        self.amount_entry = ttk.Entry(form, width=34)
        self.amount_entry.grid(row=0, column=1, sticky='ew', pady=8)

        ttk.Label(form, text='Lãi suất (%/năm)', style='Surface.TLabel').grid(row=1, column=0, sticky='w', pady=8)
        self.rate_entry = ttk.Entry(form, width=34)
        self.rate_entry.grid(row=1, column=1, sticky='ew', pady=8)
        self.rate_entry.insert(0, '6.5')

        ttk.Label(form, text='Kỳ hạn (tháng)', style='Surface.TLabel').grid(row=2, column=0, sticky='w', pady=8)
        self.term_combo = ttk.Combobox(form, textvariable=self.term_var, values=['1', '3', '6', '9', '12', '24', '36'], width=12, state='readonly')
        self.term_combo.grid(row=2, column=1, sticky='w', pady=8)

        ttk.Label(form, text='Ghi chú', style='Surface.TLabel').grid(row=3, column=0, sticky='w', pady=8)
        self.note_entry = ttk.Entry(form, width=34)
        self.note_entry.grid(row=3, column=1, sticky='ew', pady=8)

        self.hint_label = ttk.Label(main, text='Gợi ý: nhập số tiền bằng số nguyên dương, ví dụ 5.000.000.', style='Muted.TLabel')
        self.hint_label.pack(anchor='w', pady=(0, 8))

        quick_frame = ttk.LabelFrame(main, text='Chọn nhanh số tiền', style='Card.TLabelframe')
        quick_frame.pack(fill='x', pady=(0, 12))
        for index, amount in enumerate([500000, 1000000, 2000000, 5000000, 10000000]):
            ttk.Button(quick_frame, text=format_money_vnd(amount), command=lambda value=amount: self.set_quick_amount(value), style='Light.TButton').grid(row=0, column=index, padx=6, pady=8)

        preview_frame = ttk.LabelFrame(main, text='Xem trước sổ tiết kiệm', style='Card.TLabelframe')
        preview_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(preview_frame, textvariable=self.summary_var, style='Surface.TLabel', justify='left').pack(anchor='w')

        footer = ttk.Frame(outer, style='Card.TFrame', padding=(20, 8, 20, 16))
        footer.pack(fill='x', side='bottom')
        ttk.Label(footer, text='Mẹo: nhấn Enter để mở sổ.', style='Muted.TLabel').pack(side='left')

        button_frame = ttk.Frame(footer, style='Card.TFrame')
        button_frame.pack(side='right')
        self.submit_button = ttk.Button(button_frame, text='Mở sổ', command=self.on_submit, style='Primary.TButton')
        self.submit_button.grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text='Làm trống', command=self.clear_form, style='Secondary.TButton').grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text='Đóng', command=self.destroy, style='Light.TButton').grid(row=0, column=2)

        self.amount_entry.bind('<KeyRelease>', self.on_input_change)
        self.rate_entry.bind('<KeyRelease>', self.on_input_change)
        self.note_entry.bind('<KeyRelease>', self.on_input_change)
        self.term_combo.bind('<<ComboboxSelected>>', self.on_input_change)
        self.amount_entry.bind('<FocusOut>', self.on_amount_focus_out)
        self.bind('<Escape>', lambda event: self.destroy())
        self._bind_submit_shortcuts(self)
        self._bind_submit_shortcuts(self.amount_entry)
        self._bind_submit_shortcuts(self.rate_entry)
        self._bind_submit_shortcuts(self.note_entry)
        self._bind_submit_shortcuts(self.term_combo)
        self.amount_entry.focus_set()

        center_window(self, parent=parent)
        self.lift()
        self.focus_force()
        self.on_input_change()

    def _bind_submit_shortcuts(self, widget) -> None:
        widget.bind('<Return>', self._submit_from_event, add='+')
        widget.bind('<KP_Enter>', self._submit_from_event, add='+')

    def _submit_from_event(self, event=None):
        self.on_submit()
        return 'break'

    def _on_scroll_frame_configure(self, event=None) -> None:
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def _on_canvas_configure(self, event) -> None:
        self.canvas.itemconfigure(self.canvas_window, width=event.width)

    def _parse_amount_relaxed(self, text: str) -> int:
        raw = str(text).strip()
        if raw == '':
            return -1
        raw = re.sub(r'[\s\.,_]', '', raw)
        return read_positive_integer(raw)

    def _parse_rate_relaxed(self, text: str) -> float:
        raw = str(text).strip().replace(',', '.').replace('%', '').strip()
        if raw == '':
            return -1.0
        try:
            value = float(raw)
        except Exception:
            return -1.0
        if value <= 0:
            return -1.0
        return value

    def _parse_term(self) -> int:
        raw = str(self.term_var.get()).strip()
        return read_positive_integer(raw)

    def set_quick_amount(self, amount: int) -> None:
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, f'{int(amount):,}'.replace(',', '.'))
        self.on_input_change()

    def clear_form(self) -> None:
        self.amount_entry.delete(0, tk.END)
        self.rate_entry.delete(0, tk.END)
        self.rate_entry.insert(0, '6.5')
        self.term_var.set('6')
        self.note_entry.delete(0, tk.END)
        self.amount_entry.focus_set()
        self.on_input_change()

    def on_amount_focus_out(self, event=None) -> None:
        amount = self._parse_amount_relaxed(self.amount_entry.get())
        if amount != -1:
            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(0, f'{amount:,}'.replace(',', '.'))
        self.update_preview()

    def on_input_change(self, event=None) -> None:
        amount = self._parse_amount_relaxed(self.amount_entry.get())
        rate = self._parse_rate_relaxed(self.rate_entry.get())
        term_months = self._parse_term()

        if amount == -1:
            self.hint_label.configure(text='Gợi ý: nhập số tiền gửi hợp lệ.', foreground='#6e7f93')
        elif amount > self.current_balance:
            self.hint_label.configure(text='Cảnh báo: số tiền gửi lớn hơn số dư hiện có.', foreground='#da1f26')
        elif rate == -1.0:
            self.hint_label.configure(text='Gợi ý: nhập lãi suất hợp lệ, ví dụ 6.5 hoặc 6.5%.', foreground='#d07b00')
        elif term_months == -1:
            self.hint_label.configure(text='Gợi ý: chọn kỳ hạn hợp lệ theo tháng.', foreground='#d07b00')
        else:
            self.hint_label.configure(text='Thông tin hợp lệ, bạn có thể mở sổ.', foreground='#12805c')

        self.update_preview()

    def update_preview(self) -> None:
        amount = self._parse_amount_relaxed(self.amount_entry.get())
        rate = self._parse_rate_relaxed(self.rate_entry.get())
        term_months = self._parse_term()
        note_text = self.note_entry.get().strip() or '(không có ghi chú)'

        if amount == -1 or rate == -1.0 or term_months == -1:
            self.summary_var.set(
                'Số tiền gửi: (chưa hợp lệ)\n'
                'Lãi suất: (chưa hợp lệ)\n'
                'Kỳ hạn: (chưa hợp lệ)\n'
                'Tiền lãi dự kiến: (chưa tính)\n'
                'Ngày đáo hạn: (chưa tính)\n'
                f'Ghi chú: {note_text}'
            )
            return

        interest = self.bank_service.calculate_saving_interest(amount, rate, term_months)
        maturity_date = self.bank_service.add_months(get_current_time_text(), term_months)
        balance_after = self.current_balance - amount
        self.summary_var.set(
            f'Số tiền gửi: {format_money_vnd(amount)}\n'
            f'Lãi suất: {format_interest_rate(rate)}\n'
            f'Kỳ hạn: {term_months} tháng\n'
            f'Tiền lãi dự kiến: {format_money_vnd(interest)}\n'
            f'Tổng nhận khi đáo hạn: {format_money_vnd(amount + interest)}\n'
            f'Ngày đáo hạn dự kiến: {maturity_date}\n'
            f'Số dư còn lại sau khi mở sổ: {format_money_vnd(balance_after)}\n'
            f'Ghi chú: {note_text}'
        )

    def on_submit(self) -> None:
        amount = self._parse_amount_relaxed(self.amount_entry.get())
        rate = self._parse_rate_relaxed(self.rate_entry.get())
        term_months = self._parse_term()
        note = self.note_entry.get().strip()

        if amount == -1:
            messagebox.showwarning('Lỗi nhập liệu', 'Số tiền gửi phải là số nguyên dương.', parent=self)
            return
        if amount > self.current_balance:
            messagebox.showwarning('Không đủ số dư', 'Số tiền gửi lớn hơn số dư hiện tại.', parent=self)
            return
        if rate == -1.0:
            messagebox.showwarning('Lỗi nhập liệu', 'Lãi suất phải là số dương, ví dụ 6.5 hoặc 6.5%.', parent=self)
            return
        if term_months == -1:
            messagebox.showwarning('Lỗi nhập liệu', 'Kỳ hạn phải là số nguyên dương.', parent=self)
            return

        interest = self.bank_service.calculate_saving_interest(amount, rate, term_months)
        maturity_date = self.bank_service.add_months(get_current_time_text(), term_months)
        confirm_text = (
            f'Mở sổ tiết kiệm {format_money_vnd(amount)}?\n\n'
            f'Lãi suất: {format_interest_rate(rate)}\n'
            f'Kỳ hạn: {term_months} tháng\n'
            f'Lãi dự kiến: {format_money_vnd(interest)}\n'
            f'Đáo hạn dự kiến: {maturity_date}\n'
            f'Ghi chú: {note if note else "(không có)"}'
        )
        confirm = messagebox.askyesno('Xác nhận mở sổ', confirm_text, parent=self)
        if not confirm:
            return

        ok, message = self.success_callback(amount, rate, term_months, note)
        if ok:
            messagebox.showinfo('Thành công', message, parent=self)
            self.destroy()
        else:
            messagebox.showwarning('Không thành công', message, parent=self)
