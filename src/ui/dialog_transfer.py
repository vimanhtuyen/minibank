import re
import tkinter as tk
from tkinter import ttk, messagebox

from src.ui.ui_helpers import apply_responsive_toplevel, center_window, format_money_vnd, read_positive_integer


class TransferDialog(tk.Toplevel):
    def __init__(self, parent, bank_service, from_account_id: str, success_callback):
        super().__init__(parent)
        self.title('Chuyển khoản')
        apply_responsive_toplevel(self, parent=parent, default_width=760, default_height=600, min_width=680, min_height=540)
        self.transient(parent)
        self.grab_set()

        self.bank_service = bank_service
        self.from_account_id = str(from_account_id)
        self.success_callback = success_callback
        self.max_note_length = 80
        self.note_count_var = tk.StringVar(value=f'0/{self.max_note_length} ký tự')
        self.summary_var = tk.StringVar(value='Chưa có thông tin xem trước.')

        from_account = self.bank_service.get_account(self.from_account_id)
        self.from_balance = 0
        self.from_name = ''
        if from_account is not None:
            self.from_balance = int(from_account.balance)
            self.from_name = str(from_account.owner_name)

        main = ttk.Frame(self, style='Card.TFrame', padding=(20, 18))
        main.pack(fill='both', expand=True)

        ttk.Label(main, text='Chuyển khoản', style='SectionTitle.TLabel').pack(anchor='w')
        ttk.Label(main, text='Nhập tài khoản nhận, số tiền và ghi chú. Phần xem trước sẽ cập nhật tức thời.', style='Surface.TLabel', wraplength=620, justify='left').pack(anchor='w', pady=(6, 14))

        sender_frame = ttk.LabelFrame(main, text='Thông tin tài khoản gửi', style='Card.TLabelframe')
        sender_frame.pack(fill='x')
        sender_frame.columnconfigure(0, weight=1)
        sender_frame.columnconfigure(1, weight=1)
        ttk.Label(sender_frame, text=f'Số tài khoản: {self.from_account_id}', style='Strong.TLabel').grid(row=0, column=0, sticky='w', pady=(0, 6))
        ttk.Label(sender_frame, text=f'Số dư hiện tại: {format_money_vnd(self.from_balance)}', style='Strong.TLabel').grid(row=0, column=1, sticky='e', pady=(0, 6))
        sender_name = self.from_name if self.from_name else '(không rõ)'
        ttk.Label(sender_frame, text=f'Chủ tài khoản: {sender_name}', style='Surface.TLabel').grid(row=1, column=0, sticky='w')
        ttk.Label(sender_frame, text='Có thể chọn nhanh số tiền ở phía dưới.', style='Surface.TLabel').grid(row=1, column=1, sticky='e')

        form = ttk.LabelFrame(main, text='Thông tin chuyển khoản', style='Card.TLabelframe')
        form.pack(fill='x', pady=(12, 12))
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text='Số tài khoản nhận', style='Surface.TLabel').grid(row=0, column=0, sticky='w', pady=8)
        self.to_account_entry = ttk.Entry(form, width=34)
        self.to_account_entry.grid(row=0, column=1, sticky='ew', pady=8)
        self.to_name_label = ttk.Label(form, text='Tên người nhận: (chưa nhập)', style='Surface.TLabel')
        self.to_name_label.grid(row=1, column=1, sticky='w', pady=(0, 8))

        ttk.Label(form, text='Số tiền (VNĐ)', style='Surface.TLabel').grid(row=2, column=0, sticky='w', pady=8)
        self.amount_entry = ttk.Entry(form, width=34)
        self.amount_entry.grid(row=2, column=1, sticky='ew', pady=8)
        self.balance_after_label = ttk.Label(form, text='Số dư dự kiến sau chuyển: (chưa tính)', style='Surface.TLabel')
        self.balance_after_label.grid(row=3, column=1, sticky='w', pady=(0, 8))

        ttk.Label(form, text='Ghi chú', style='Surface.TLabel').grid(row=4, column=0, sticky='w', pady=8)
        self.note_entry = ttk.Entry(form, width=34)
        self.note_entry.grid(row=4, column=1, sticky='ew', pady=8)
        self.note_count_label = ttk.Label(form, textvariable=self.note_count_var, style='Muted.TLabel')
        self.note_count_label.grid(row=5, column=1, sticky='w')

        self.hint_label = ttk.Label(main, text='Gợi ý: nhập số nguyên dương, ví dụ 100.000.', style='Muted.TLabel')
        self.hint_label.pack(anchor='w', pady=(0, 8))

        quick_frame = ttk.LabelFrame(main, text='Chọn nhanh số tiền', style='Card.TLabelframe')
        quick_frame.pack(fill='x', pady=(0, 12))
        for index, amount in enumerate([50000, 100000, 200000, 500000]):
            ttk.Button(quick_frame, text=format_money_vnd(amount), command=lambda value=amount: self.set_quick_amount(value), style='Light.TButton').grid(row=0, column=index, padx=6, pady=8)
        ttk.Button(quick_frame, text='Toàn bộ số dư', command=self.set_full_balance_amount, style='Secondary.TButton').grid(row=0, column=4, padx=6, pady=8)

        preview_frame = ttk.LabelFrame(main, text='Xem trước giao dịch', style='Card.TLabelframe')
        preview_frame.pack(fill='x', pady=(0, 14))
        ttk.Label(preview_frame, textvariable=self.summary_var, style='Surface.TLabel', justify='left').pack(anchor='w')

        button_frame = ttk.Frame(main, style='Card.TFrame')
        button_frame.pack(anchor='e')
        ttk.Button(button_frame, text='Xác nhận chuyển', command=self.on_submit, style='Primary.TButton').grid(row=0, column=0, padx=(0, 10))
        ttk.Button(button_frame, text='Làm trống', command=self.clear_form, style='Secondary.TButton').grid(row=0, column=1, padx=(0, 10))
        ttk.Button(button_frame, text='Đóng', command=self.destroy, style='Light.TButton').grid(row=0, column=2)

        self.to_account_entry.bind('<KeyRelease>', self.on_to_account_change)
        self.amount_entry.bind('<KeyRelease>', self.on_amount_change)
        self.note_entry.bind('<KeyRelease>', self.on_note_change)
        self.to_account_entry.bind('<Return>', lambda event: self.on_submit())
        self.to_account_entry.bind('<KP_Enter>', lambda event: self.on_submit())
        self.amount_entry.bind('<Return>', lambda event: self.on_submit())
        self.amount_entry.bind('<KP_Enter>', lambda event: self.on_submit())
        self.note_entry.bind('<Return>', lambda event: self.on_submit())
        self.note_entry.bind('<KP_Enter>', lambda event: self.on_submit())
        self.amount_entry.bind('<FocusOut>', self.on_amount_focus_out)
        self.bind('<Escape>', lambda event: self.destroy())
        self.to_account_entry.focus_set()

        center_window(self, parent=parent)
        self.on_to_account_change()
        self.on_amount_change()
        self.on_note_change()

    def clear_form(self) -> None:
        self.to_account_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.note_entry.delete(0, tk.END)
        self.to_account_entry.focus_set()
        self.on_to_account_change()
        self.on_amount_change()
        self.on_note_change()

    def set_quick_amount(self, amount: int) -> None:
        self.amount_entry.delete(0, tk.END)
        self.amount_entry.insert(0, f'{int(amount):,}'.replace(',', '.'))
        self.on_amount_change()

    def set_full_balance_amount(self) -> None:
        self.set_quick_amount(self.from_balance)

    def _parse_amount_relaxed(self, text: str) -> int:
        raw = str(text).strip()
        if raw == '':
            return -1
        raw = re.sub(r'[\s\.,_]', '', raw)
        return read_positive_integer(raw)

    def on_amount_focus_out(self, event=None) -> None:
        amount = self._parse_amount_relaxed(self.amount_entry.get())
        if amount != -1:
            self.amount_entry.delete(0, tk.END)
            self.amount_entry.insert(0, f'{amount:,}'.replace(',', '.'))
        self.update_preview()

    def get_receiver_account(self):
        to_account_id = self.to_account_entry.get().strip()
        return None if to_account_id == '' else self.bank_service.get_account(to_account_id)

    def on_to_account_change(self, event=None) -> None:
        to_account_id = self.to_account_entry.get().strip()
        if to_account_id == '':
            self.to_name_label.configure(text='Tên người nhận: (chưa nhập)', foreground='#6e7f93')
            self.update_preview()
            return
        if str(to_account_id) == str(self.from_account_id):
            self.to_name_label.configure(text='Tên người nhận: không thể là chính bạn', foreground='#da1f26')
            self.update_preview()
            return
        to_account = self.bank_service.get_account(to_account_id)
        if to_account is None:
            self.to_name_label.configure(text='Tên người nhận: không tìm thấy tài khoản', foreground='#da1f26')
            self.update_preview()
            return
        self.to_name_label.configure(text=f'Tên người nhận: {to_account.owner_name}', foreground='#12805c')
        self.update_preview()

    def on_amount_change(self, event=None) -> None:
        amount = self._parse_amount_relaxed(self.amount_entry.get())
        if amount == -1:
            self.hint_label.configure(text='Gợi ý: nhập số nguyên dương, ví dụ 100.000.', foreground='#6e7f93')
            self.balance_after_label.configure(text='Số dư dự kiến sau chuyển: (chưa tính)', foreground='#6e7f93')
            self.update_preview()
            return
        if amount > self.from_balance:
            self.hint_label.configure(text='Cảnh báo: số tiền chuyển lớn hơn số dư.', foreground='#da1f26')
            self.balance_after_label.configure(text='Số dư dự kiến sau chuyển: không đủ số dư', foreground='#da1f26')
            self.update_preview()
            return
        remaining = self.from_balance - amount
        self.hint_label.configure(text=f'Bạn nhập: {format_money_vnd(amount)}', foreground='#12805c')
        self.balance_after_label.configure(text=f'Số dư dự kiến sau chuyển: {format_money_vnd(remaining)}', foreground='#12805c')
        self.update_preview()

    def on_note_change(self, event=None) -> None:
        note = self.note_entry.get()
        if len(note) > self.max_note_length:
            self.note_entry.delete(self.max_note_length, tk.END)
            note = self.note_entry.get()
        self.note_count_var.set(f'{len(note)}/{self.max_note_length} ký tự')
        self.update_preview()

    def update_preview(self) -> None:
        to_account_id = self.to_account_entry.get().strip()
        amount = self._parse_amount_relaxed(self.amount_entry.get())
        note_text = self.note_entry.get().strip() or '(không có ghi chú)'
        receiver = self.get_receiver_account()
        receiver_name = '(chưa xác định)' if receiver is None else str(receiver.owner_name)
        amount_text = '(chưa hợp lệ)' if amount == -1 else format_money_vnd(amount)
        sender_name = self.from_name if self.from_name else '(không rõ)'
        receiver_account_text = to_account_id if to_account_id else '(chưa nhập)'  # new

        lines = [
            f'Tài khoản gửi: {self.from_account_id} - {sender_name}',
            f'Tài khoản nhận: {receiver_account_text} - {receiver_name}',
            f'Số tiền: {amount_text}',
            f'Ghi chú: {note_text}',
        ]
        if amount != -1 and amount <= self.from_balance:
            lines.append(f'Số dư còn lại sau chuyển: {format_money_vnd(self.from_balance - amount)}')
        elif amount != -1:
            lines.append('Số dư còn lại sau chuyển: không đủ số dư')
        self.summary_var.set('\n'.join(lines))

    def validate_before_submit(self):
        to_account_id = self.to_account_entry.get().strip()
        amount = self._parse_amount_relaxed(self.amount_entry.get())
        note = self.note_entry.get().strip()
        if to_account_id == '':
            return False, 'Số tài khoản nhận không được để trống.', None, amount, note
        if str(to_account_id) == str(self.from_account_id):
            return False, 'Không thể chuyển khoản cho chính mình.', None, amount, note
        to_account = self.bank_service.get_account(to_account_id)
        if to_account is None:
            return False, 'Tài khoản nhận không tồn tại.', None, amount, note
        if amount == -1:
            return False, 'Số tiền phải là số nguyên dương.', to_account, amount, note
        if amount > self.from_balance:
            return False, 'Số tiền chuyển lớn hơn số dư hiện tại.', to_account, amount, note
        return True, '', to_account, amount, note

    def on_submit(self) -> None:
        is_valid, error_message, to_account, amount, note = self.validate_before_submit()
        if not is_valid:
            messagebox.showwarning('Lỗi nhập liệu', error_message, parent=self)
            return
        note_display = note if note else '(không có)'
        confirm_text = (
            'Xác nhận chuyển khoản?\n\n'
            f'Tài khoản gửi: {self.from_account_id}\n'
            f'Tài khoản nhận: {to_account.account_id} ({to_account.owner_name})\n'
            f'Số tiền: {format_money_vnd(amount)}\n'
            f'Ghi chú: {note_display}\n'
            f'Số dư còn lại: {format_money_vnd(self.from_balance - amount)}'
        )
        confirm = messagebox.askyesno('Xác nhận', confirm_text, parent=self)
        if not confirm:
            return
        ok, message = self.bank_service.transfer_money(self.from_account_id, str(to_account.account_id), amount, note)
        if ok:
            if self.success_callback is not None:
                self.success_callback()
            messagebox.showinfo('Thành công', message, parent=self)
            self.destroy()
        else:
            messagebox.showwarning('Không thành công', message, parent=self)
