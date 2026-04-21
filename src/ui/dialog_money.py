import re
import tkinter as tk
from tkinter import ttk, messagebox

from src.ui.ui_helpers import apply_responsive_toplevel, center_window, format_money_vnd, read_positive_integer


class MoneyDialog(tk.Toplevel):
    def __init__(self, parent, title_text: str, current_balance: int, submit_callback):
        super().__init__(parent)
        self.title(title_text)
        apply_responsive_toplevel(self, parent=parent, default_width=640, default_height=460, min_width=560, min_height=430)
        self.transient(parent)
        self.grab_set()

        self.title_text = title_text
        self.current_balance = int(current_balance)
        self.submit_callback = submit_callback
        self.summary_var = tk.StringVar(value='Chưa có thông tin xem trước.')
        self.is_withdraw = 'Rút' in title_text

        main = ttk.Frame(self, style='Card.TFrame', padding=(20, 18))
        main.pack(fill='both', expand=True)

        ttk.Label(main, text=title_text, style='SectionTitle.TLabel').pack(anchor='w')
        ttk.Label(main, text=f'Số dư hiện tại: {format_money_vnd(self.current_balance)}', style='Surface.TLabel').pack(anchor='w', pady=(6, 14))

        form = ttk.LabelFrame(main, text='Thông tin giao dịch', style='Card.TLabelframe')
        form.pack(fill='x')
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text='Số tiền (VNĐ)', style='Surface.TLabel').grid(row=0, column=0, sticky='w', pady=8)
        self.amount_entry = ttk.Entry(form, width=30)
        self.amount_entry.grid(row=0, column=1, sticky='ew', pady=8)

        ttk.Label(form, text='Ghi chú', style='Surface.TLabel').grid(row=1, column=0, sticky='w', pady=8)
        self.note_entry = ttk.Entry(form, width=30)
        self.note_entry.grid(row=1, column=1, sticky='ew', pady=8)
        self.note_entry.insert(0, '')

        self.hint_label = ttk.Label(main, text='Gợi ý: nhập số nguyên dương, ví dụ 50.000.', style='Muted.TLabel')
        self.hint_label.pack(anchor='w', pady=(12, 8))

        quick_frame = ttk.LabelFrame(main, text='Chọn nhanh số tiền', style='Card.TLabelframe')
        quick_frame.pack(fill='x', pady=(0, 12))
        quick_amounts = [50000, 100000, 200000, 500000]
        for index, amount in enumerate(quick_amounts):
            ttk.Button(quick_frame, text=format_money_vnd(amount), command=lambda value=amount: self.set_quick_amount(value), style='Light.TButton').grid(row=0, column=index, padx=6, pady=8)
        if self.is_withdraw:
            ttk.Button(quick_frame, text='Rút toàn bộ số dư', command=lambda: self.set_quick_amount(self.current_balance), style='Secondary.TButton').grid(row=0, column=len(quick_amounts), padx=6, pady=8)

        preview_frame = ttk.LabelFrame(main, text='Xem trước', style='Card.TLabelframe')
        preview_frame.pack(fill='x', pady=(0, 14))
        ttk.Label(preview_frame, textvariable=self.summary_var, style='Surface.TLabel', justify='left').pack(anchor='w')

        button_frame = ttk.Frame(main, style='Card.TFrame')
        button_frame.pack(anchor='e')
        ttk.Button(button_frame, text='Xác nhận', command=self.on_submit, style='Primary.TButton').grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text='Làm trống', command=self.clear_form, style='Secondary.TButton').grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text='Đóng', command=self.destroy, style='Light.TButton').grid(row=0, column=2)

        self.amount_entry.bind('<KeyRelease>', self.on_amount_change)
        self.note_entry.bind('<KeyRelease>', self.on_note_change)
        self.amount_entry.bind('<Return>', lambda event: self.on_submit())
        self.amount_entry.bind('<KP_Enter>', lambda event: self.on_submit())
        self.note_entry.bind('<Return>', lambda event: self.on_submit())
        self.note_entry.bind('<KP_Enter>', lambda event: self.on_submit())
        self.amount_entry.bind('<FocusOut>', self.on_amount_focus_out)
        self.bind('<Escape>', lambda event: self.destroy())
        self.amount_entry.focus_set()

        center_window(self, parent=parent)
        self.update_preview()

    def _parse_amount_relaxed(self, text: str) -> int:
        raw = str(text).strip()
        if raw == '':
            return -1
        raw = re.sub(r'[\s\.,_]', '', raw)
        return read_positive_integer(raw)

    def clear_form(self) -> None:
        self.amount_entry.delete(0, tk.END)
        self.note_entry.delete(0, tk.END)
        self.amount_entry.focus_set()
        self.on_amount_change()
        self.on_note_change()

    def set_quick_amount(self, amount: int) -> None:
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, f'{int(amount):,}'.replace(',', '.'))
        self.on_amount_change()

    def on_amount_focus_out(self, event=None) -> None:
        amount = self._parse_amount_relaxed(self.amount_entry.get())
        if amount != -1:
            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(0, f'{amount:,}'.replace(',', '.'))
        self.update_preview()

    def on_amount_change(self, event=None) -> None:
        amount = self._parse_amount_relaxed(self.amount_entry.get())
        if amount == -1:
            self.hint_label.configure(text='Gợi ý: nhập số nguyên dương, ví dụ 50.000.', foreground='#6e7f93')
        elif self.is_withdraw and amount > self.current_balance:
            self.hint_label.configure(text='Cảnh báo: số tiền rút lớn hơn số dư hiện tại.', foreground='#da1f26')
        else:
            self.hint_label.configure(text=f'Bạn nhập: {format_money_vnd(amount)}', foreground='#12805c')
        self.update_preview()

    def on_note_change(self, event=None) -> None:
        self.update_preview()

    def update_preview(self) -> None:
        amount = self._parse_amount_relaxed(self.amount_entry.get())
        note_text = self.note_entry.get().strip() or '(không có ghi chú)'
        amount_text = '(chưa hợp lệ)' if amount == -1 else format_money_vnd(amount)
        if amount == -1:
            after_text = '(chưa tính)'
        elif self.is_withdraw:
            after_text = 'không đủ số dư' if amount > self.current_balance else format_money_vnd(self.current_balance - amount)
        else:
            after_text = format_money_vnd(self.current_balance + amount)
        self.summary_var.set(
            f'Loại giao dịch: {self.title_text}\n'
            f'Số tiền: {amount_text}\n'
            f'Ghi chú: {note_text}\n'
            f'Số dư sau giao dịch: {after_text}'
        )

    def on_submit(self) -> None:
        amount = self._parse_amount_relaxed(self.amount_entry.get())
        note = self.note_entry.get().strip()
        if amount == -1:
            messagebox.showwarning('Lỗi nhập liệu', 'Số tiền phải là số nguyên dương.', parent=self)
            return
        if self.is_withdraw and amount > self.current_balance:
            messagebox.showwarning('Không đủ số dư', 'Số tiền rút lớn hơn số dư hiện tại.', parent=self)
            return
        balance_after = self.current_balance - amount if self.is_withdraw else self.current_balance + amount
        note_display = note if note else '(không có)'
        confirm_text = (
            f'{self.title_text} {format_money_vnd(amount)}?\n\n'
            f'Ghi chú: {note_display}\n'
            f'Số dư sau giao dịch: {format_money_vnd(balance_after)}'
        )
        confirm = messagebox.askyesno('Xác nhận', confirm_text, parent=self)
        if not confirm:
            return
        ok, message = self.submit_callback(amount, note)
        if ok:
            messagebox.showinfo('Thành công', message, parent=self)
            self.destroy()
        else:
            messagebox.showwarning('Không thành công', message, parent=self)
