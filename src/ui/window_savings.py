import tkinter as tk
from tkinter import ttk, messagebox

from src.ui.dialog_savings import SavingDepositDialog
from src.ui.ui_helpers import apply_responsive_toplevel, center_window, format_interest_rate, format_money_vnd


class SavingsWindow(tk.Toplevel):
    def __init__(self, parent, bank_service, account_id: str, save_callback, refresh_callback=None):
        super().__init__(parent)
        self.bank_service = bank_service
        self.account_id = str(account_id)
        self.save_callback = save_callback
        self.refresh_callback = refresh_callback

        self.title(f'Sổ tiết kiệm - {self.account_id}')
        apply_responsive_toplevel(self, parent=parent, default_width=1240, default_height=720, min_width=980, min_height=600)
        self.transient(parent)
        self.grab_set()

        self.summary_var = tk.StringVar(value='')
        self.balance_var = tk.StringVar(value='')
        self.deposits = []

        main = ttk.Frame(self, style='Card.TFrame', padding=(20, 18))
        main.pack(fill='both', expand=True)

        ttk.Label(main, text=f'Quản lý sổ tiết kiệm của tài khoản {self.account_id}', style='SectionTitle.TLabel').pack(anchor='w')
        ttk.Label(main, text='Bạn có thể mở sổ mới, theo dõi lãi dự kiến và tất toán khi cần.', style='Surface.TLabel', wraplength=980, justify='left').pack(anchor='w', pady=(6, 14))

        top_actions = ttk.Frame(main, style='Card.TFrame')
        top_actions.pack(fill='x')
        ttk.Label(top_actions, textvariable=self.balance_var, style='Strong.TLabel').pack(side='left')
        ttk.Button(top_actions, text='Mở sổ mới', command=self.open_new_deposit_dialog, style='Primary.TButton').pack(side='right', padx=(10, 0))
        ttk.Button(top_actions, text='Tất toán sổ đã chọn', command=self.settle_selected_deposit, style='Secondary.TButton').pack(side='right', padx=(10, 0))
        ttk.Button(top_actions, text='Xem chi tiết', command=self.show_selected_detail, style='Light.TButton').pack(side='right', padx=(10, 0))
        ttk.Button(top_actions, text='Làm mới', command=self.refresh_data, style='Light.TButton').pack(side='right')

        table_card = ttk.Frame(main, style='Card.TFrame', padding=(0, 16, 0, 0))
        table_card.pack(fill='both', expand=True)

        columns = ('deposit_id', 'principal', 'rate', 'term', 'opened_at', 'maturity_at', 'status', 'payout')
        self.tree = ttk.Treeview(table_card, columns=columns, show='headings', height=16)
        self.tree.heading('deposit_id', text='Mã sổ')
        self.tree.heading('principal', text='Tiền gốc')
        self.tree.heading('rate', text='Lãi suất')
        self.tree.heading('term', text='Kỳ hạn')
        self.tree.heading('opened_at', text='Ngày mở')
        self.tree.heading('maturity_at', text='Ngày đáo hạn')
        self.tree.heading('status', text='Trạng thái')
        self.tree.heading('payout', text='Nhận khi tất toán')
        self.tree.column('deposit_id', width=110, anchor='center')
        self.tree.column('principal', width=135, anchor='e')
        self.tree.column('rate', width=100, anchor='center')
        self.tree.column('term', width=90, anchor='center')
        self.tree.column('opened_at', width=160, anchor='center')
        self.tree.column('maturity_at', width=160, anchor='center')
        self.tree.column('status', width=135, anchor='center')
        self.tree.column('payout', width=150, anchor='e')
        self.tree.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(table_card, orient='vertical', command=self.tree.yview)
        scrollbar.pack(side='right', fill='y', padx=(10, 0))
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.bind('<Double-1>', self.show_selected_detail)

        bottom_frame = ttk.Frame(main, style='Card.TFrame')
        bottom_frame.pack(fill='x', pady=(14, 0))
        ttk.Label(bottom_frame, textvariable=self.summary_var, style='Strong.TLabel').pack(side='left')
        action_frame = ttk.Frame(bottom_frame, style='Card.TFrame')
        action_frame.pack(side='right')
        ttk.Button(action_frame, text='Copy mã sổ', command=self.copy_selected_deposit_id, style='Light.TButton').grid(row=0, column=0, padx=(0, 10))
        ttk.Button(action_frame, text='Đóng', command=self.destroy, style='Light.TButton').grid(row=0, column=1)

        self.refresh_data()
        center_window(self, parent=parent)
        self.lift()
        self.focus_force()

    def get_account_balance(self) -> int:
        account = self.bank_service.get_account(self.account_id)
        return 0 if account is None else int(account.balance)

    def refresh_data(self) -> None:
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)

        self.deposits = self.bank_service.get_saving_deposits(self.account_id)
        self.balance_var.set(f'Số dư khả dụng hiện tại: {format_money_vnd(self.get_account_balance())}')

        if len(self.deposits) == 0:
            self.tree.insert('', 'end', values=('-', '-', '-', '-', '-', '-', '-', 'Chưa có sổ tiết kiệm'))
            self.summary_var.set('Số sổ: 0 | Đang hoạt động: 0 | Tổng gốc đang gửi: 0 VNĐ')
            return

        for deposit in self.deposits:
            preview = self.bank_service.get_saving_settlement_preview(deposit)
            if str(deposit.status).upper() == 'ACTIVE':
                status_text = 'Đang hiệu lực' if preview['is_matured'] else 'Đang khóa vốn'
            else:
                status_text = 'Đã tất toán'
            self.tree.insert(
                '',
                'end',
                values=(
                    deposit.deposit_id,
                    format_money_vnd(deposit.principal_amount),
                    format_interest_rate(deposit.annual_interest_rate),
                    f'{deposit.term_months} tháng',
                    deposit.opened_at,
                    deposit.maturity_at,
                    status_text,
                    format_money_vnd(preview['payout_amount'] if str(deposit.status).upper() == 'ACTIVE' else deposit.maturity_amount),
                ),
            )

        summary = self.bank_service.get_savings_summary(self.account_id)
        self.summary_var.set(
            f'Số sổ: {len(self.deposits)} | '
            f'Đang hoạt động: {summary["active_count"]} | '
            f'Tổng gốc đang gửi: {format_money_vnd(summary["total_principal"])} | '
            f'Lãi dự kiến: {format_money_vnd(summary["total_interest"])}'
        )

    def open_new_deposit_dialog(self) -> None:
        current_balance = self.get_account_balance()

        def submit(amount: int, rate: float, term_months: int, note: str):
            ok, message, _deposit_id = self.bank_service.create_saving_deposit(self.account_id, amount, rate, term_months, note)
            if ok:
                self.save_callback()
                self.refresh_data()
                if callable(self.refresh_callback):
                    self.refresh_callback()
            return ok, message

        SavingDepositDialog(self, self.bank_service, self.account_id, current_balance, submit)

    def get_selected_deposit_id(self):
        selected_items = self.tree.selection()
        if len(selected_items) == 0:
            return None
        values = self.tree.item(selected_items[0], 'values')
        if not values or values[0] == '-':
            return None
        return str(values[0])

    def copy_selected_deposit_id(self) -> None:
        deposit_id = self.get_selected_deposit_id()
        if deposit_id is None:
            messagebox.showinfo('Thông báo', 'Hãy chọn một sổ tiết kiệm để copy mã sổ.', parent=self)
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(deposit_id)
            messagebox.showinfo('Copy', 'Đã copy mã sổ tiết kiệm.', parent=self)
        except Exception:
            messagebox.showwarning('Lỗi', 'Không thể copy vào clipboard.', parent=self)

    def settle_selected_deposit(self) -> None:
        deposit_id = self.get_selected_deposit_id()
        if deposit_id is None:
            messagebox.showinfo('Thông báo', 'Hãy chọn một sổ tiết kiệm để tất toán.', parent=self)
            return

        saving_deposit = self.bank_service.get_saving_deposit(self.account_id, deposit_id)
        if saving_deposit is None:
            messagebox.showwarning('Lỗi', 'Không tìm thấy sổ tiết kiệm đã chọn.', parent=self)
            return
        if str(saving_deposit.status).upper() != 'ACTIVE':
            messagebox.showinfo('Thông báo', 'Sổ này đã tất toán trước đó.', parent=self)
            return

        preview = self.bank_service.get_saving_settlement_preview(saving_deposit)
        confirm_text = (
            f'Tất toán sổ {saving_deposit.deposit_id}?\n\n'
            f'Tiền gốc: {format_money_vnd(saving_deposit.principal_amount)}\n'
            f'Trạng thái: {preview["message"]}\n'
            f'Số tiền nhận khi tất toán: {format_money_vnd(preview["payout_amount"])}'
        )
        if preview['is_matured']:
            confirm_text += f'\nTiền lãi nhận được: {format_money_vnd(preview["interest_earned"])}'
        confirm = messagebox.askyesno('Xác nhận tất toán', confirm_text, parent=self)
        if not confirm:
            return

        ok, message = self.bank_service.settle_saving_deposit(self.account_id, deposit_id)
        if ok:
            self.save_callback()
            self.refresh_data()
            if callable(self.refresh_callback):
                self.refresh_callback()
            messagebox.showinfo('Thành công', message, parent=self)
        else:
            messagebox.showwarning('Không thành công', message, parent=self)

    def show_selected_detail(self, event=None) -> None:
        deposit_id = self.get_selected_deposit_id()
        if deposit_id is None:
            if event is None:
                messagebox.showinfo('Thông báo', 'Hãy chọn một sổ tiết kiệm để xem chi tiết.', parent=self)
            return
        saving_deposit = self.bank_service.get_saving_deposit(self.account_id, deposit_id)
        if saving_deposit is None:
            return
        preview = self.bank_service.get_saving_settlement_preview(saving_deposit)
        status_text = 'Đã tất toán' if str(saving_deposit.status).upper() != 'ACTIVE' else ('Đã đến hạn' if preview['is_matured'] else 'Chưa đến hạn')
        messagebox.showinfo(
            'Chi tiết sổ tiết kiệm',
            f'Mã sổ: {saving_deposit.deposit_id}\n'
            f'Tiền gốc: {format_money_vnd(saving_deposit.principal_amount)}\n'
            f'Lãi suất: {format_interest_rate(saving_deposit.annual_interest_rate)}\n'
            f'Kỳ hạn: {saving_deposit.term_months} tháng\n'
            f'Ngày mở: {saving_deposit.opened_at}\n'
            f'Ngày đáo hạn: {saving_deposit.maturity_at}\n'
            f'Trạng thái: {status_text}\n'
            f'Tiền lãi dự kiến/đã nhận: {format_money_vnd(saving_deposit.interest_earned)}\n'
            f'Số tiền tất toán hiện tại: {format_money_vnd(preview["payout_amount"] if str(saving_deposit.status).upper() == "ACTIVE" else saving_deposit.maturity_amount)}\n'
            f'Ghi chú: {saving_deposit.note if saving_deposit.note else "-"}\n'
            f'Tất toán lúc: {saving_deposit.settled_at if saving_deposit.settled_at else "Chưa tất toán"}',
            parent=self,
        )
