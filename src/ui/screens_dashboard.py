from tkinter import ttk, messagebox

from src.ui.dialog_money import MoneyDialog
from src.ui.dialog_transfer import TransferDialog
from src.ui.ui_helpers import ScrollableContent, format_money_vnd, get_transaction_type_display
from src.ui.window_history import HistoryWindow
from src.ui.window_savings import SavingsWindow


class DashboardFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style='App.TFrame')
        self.app = app
        self.scrollable = ScrollableContent(self, frame_style='App.TFrame')
        self.scrollable.pack(fill='both', expand=True)
        self.page = self.scrollable.body

        self.header = ttk.Frame(self.page, style='Hero.TFrame', padding=(26, 22))
        self.header.pack(fill='x', pady=(0, 18))
        self.welcome_label = ttk.Label(self.header, text='Xin chào!', style='HeroTitle.TLabel')
        self.welcome_label.pack(anchor='w')
        self.info_line_label = ttk.Label(self.header, text='Đang tải thông tin tài khoản...', style='HeroText.TLabel', wraplength=1000, justify='left')
        self.info_line_label.pack(anchor='w', pady=(8, 0))

        self.metrics_wrap = ttk.Frame(self.page, style='App.TFrame')
        self.metrics_wrap.pack(fill='x', pady=(0, 16))
        self.metric_cards = []
        self.account_card, self.account_id_value = self._create_metric_card('Số tài khoản')
        self.balance_card, self.balance_value = self._create_metric_card('Số dư hiện tại')
        self.transaction_card, self.transaction_count_value = self._create_metric_card('Tổng giao dịch')
        self.savings_card, self.savings_count_value = self._create_metric_card('Sổ tiết kiệm đang mở')
        self.metric_cards.extend([self.account_card, self.balance_card, self.transaction_card, self.savings_card])

        self.action_wrap = ttk.Frame(self.page, style='App.TFrame')
        self.action_wrap.pack(fill='x', pady=(0, 16))

        self.left_actions = ttk.Frame(self.action_wrap, style='Card.TFrame', padding=(22, 18))
        self.left_actions_title = ttk.Label(self.left_actions, text='Giao dịch nhanh', style='SectionTitle.TLabel')
        self.left_actions_title.pack(anchor='w')
        self.actions_grid = ttk.Frame(self.left_actions, style='Card.TFrame')
        self.actions_grid.pack(fill='x', pady=(14, 0))

        action_specs = [
            ('Nạp tiền', self.open_deposit, 'Primary.TButton'),
            ('Rút tiền', self.open_withdraw, 'Secondary.TButton'),
            ('Chuyển khoản', self.open_transfer, 'Light.TButton'),
            ('Sổ tiết kiệm', self.open_savings, 'Light.TButton'),
            ('Lịch sử giao dịch', self.open_history, 'Secondary.TButton'),
            ('Copy số tài khoản', self.copy_account_id, 'Light.TButton'),
            ('Làm mới', self.refresh_information, 'Light.TButton'),
            ('Mở tài khoản mới', self.open_register_from_dashboard, 'Light.TButton'),
        ]
        self.action_buttons = []
        for text, command, style in action_specs:
            button = ttk.Button(self.actions_grid, text=text, command=command, style=style)
            self.action_buttons.append(button)

        self.right_actions = ttk.Frame(self.action_wrap, style='Card.TFrame', padding=(22, 18))
        ttk.Label(self.right_actions, text='Phiên làm việc', style='SectionTitle.TLabel').pack(anchor='w')
        self.session_label = ttk.Label(
            self.right_actions,
            text='Nhấn F5 để tải lại dữ liệu đang hiển thị. Chức năng sổ tiết kiệm cho phép khóa vốn và tính lãi theo kỳ hạn.',
            style='Surface.TLabel',
            wraplength=260,
            justify='left',
        )
        self.session_label.pack(anchor='w', pady=(8, 14))
        ttk.Button(self.right_actions, text='Đăng xuất', command=self.logout, style='Danger.TButton').pack(anchor='w')

        self.history_card = ttk.Frame(self.page, style='Card.TFrame', padding=(22, 18))
        self.history_card.pack(fill='both', expand=True)
        top_bar = ttk.Frame(self.history_card, style='Card.TFrame')
        top_bar.pack(fill='x')
        ttk.Label(top_bar, text='5 giao dịch gần nhất', style='SectionTitle.TLabel').pack(side='left')
        ttk.Label(top_bar, text='Nhấn đúp vào bảng để mở lịch sử đầy đủ', style='Muted.TLabel').pack(side='right')

        columns = ('time', 'type', 'amount', 'note')
        self.transaction_tree = ttk.Treeview(self.history_card, columns=columns, show='headings', height=11)
        self.transaction_tree.heading('time', text='Thời gian')
        self.transaction_tree.heading('type', text='Loại')
        self.transaction_tree.heading('amount', text='Số tiền')
        self.transaction_tree.heading('note', text='Ghi chú')
        self.transaction_tree.column('time', width=170, anchor='center')
        self.transaction_tree.column('type', width=150, anchor='center')
        self.transaction_tree.column('amount', width=150, anchor='e')
        self.transaction_tree.column('note', width=500, anchor='w')
        self.transaction_tree.pack(side='left', fill='both', expand=True, pady=(14, 0))

        scrollbar = ttk.Scrollbar(self.history_card, orient='vertical', command=self.transaction_tree.yview)
        scrollbar.pack(side='right', fill='y', pady=(14, 0), padx=(10, 0))
        self.transaction_tree.configure(yscrollcommand=scrollbar.set)
        self.transaction_tree.bind('<Double-1>', lambda event: self.open_history())

        self.page.bind('<Configure>', self.on_resize)
        self.on_resize()

    def _create_metric_card(self, title: str):
        card = ttk.Frame(self.metrics_wrap, style='Card.TFrame', padding=(18, 16))
        ttk.Label(card, text=title, style='CardTitle.TLabel').pack(anchor='w')
        value_label = ttk.Label(card, text='--', style='MetricValue.TLabel')
        value_label.pack(anchor='w', pady=(12, 2))
        ttk.Label(card, text='Dữ liệu hiện tại', style='MetricCaption.TLabel').pack(anchor='w')
        return card, value_label

    def on_resize(self, event=None) -> None:
        width = self.page.winfo_width() or self.winfo_width() or 1200
        self.info_line_label.configure(wraplength=max(420, width - 120))
        self.session_label.configure(wraplength=max(260, min(360, width - 160)))

        metric_cols = 2 if width < 1080 else 4
        for index, card in enumerate(self.metric_cards):
            card.grid_forget()
            row = index // metric_cols
            col = index % metric_cols
            pad_right = 10 if col < metric_cols - 1 else 0
            pad_bottom = 10 if row == 0 and len(self.metric_cards) > metric_cols else 0
            self.metrics_wrap.columnconfigure(col, weight=1)
            card.grid(row=row, column=col, sticky='nsew', padx=(0, pad_right), pady=(0, pad_bottom))

        self.left_actions.pack_forget()
        self.right_actions.pack_forget()
        if width < 1100:
            self.left_actions.pack(fill='x', pady=(0, 12))
            self.right_actions.pack(fill='x')
            action_cols = 2
        else:
            self.left_actions.pack(side='left', fill='x', expand=True, padx=(0, 10))
            self.right_actions.pack(side='right', fill='y')
            action_cols = 4

        for idx, button in enumerate(self.action_buttons):
            button.grid_forget()
            row = idx // action_cols
            col = idx % action_cols
            self.actions_grid.columnconfigure(col, weight=1)
            button.grid(row=row, column=col, sticky='ew', padx=(0, 10) if col < action_cols - 1 else 0, pady=6)

    def get_logged_account_id(self) -> str:
        return '' if self.app.logged_account_id is None else str(self.app.logged_account_id)

    def get_logged_account(self):
        return self.app.bank_service.get_account(self.get_logged_account_id())

    def refresh_recent_transactions(self) -> None:
        for item_id in self.transaction_tree.get_children():
            self.transaction_tree.delete(item_id)
        account_id = self.get_logged_account_id()
        if account_id == '':
            return
        history = self.app.bank_service.get_transaction_history(account_id)
        for transaction in history[:5]:
            note_text = str(transaction.note).strip() if str(transaction.note).strip() != '' else '-'
            self.transaction_tree.insert('', 'end', values=(transaction.time_text, get_transaction_type_display(transaction.transaction_type), format_money_vnd(transaction.amount), note_text))
        if len(history) == 0:
            self.transaction_tree.insert('', 'end', values=('-', '-', '-', 'Chưa có giao dịch nào'))

    def refresh_information(self) -> None:
        account = self.get_logged_account()
        if account is None:
            self.welcome_label.configure(text='Chưa có người dùng đăng nhập.')
            self.info_line_label.configure(text='Hãy quay lại màn hình đăng nhập để truy cập dashboard.')
            for label in [self.account_id_value, self.balance_value, self.transaction_count_value, self.savings_count_value]:
                label.configure(text='--')
            self.refresh_recent_transactions()
            return

        history = self.app.bank_service.get_transaction_history(account.account_id)
        savings_summary = self.app.bank_service.get_savings_summary(account.account_id)
        self.welcome_label.configure(text=f'Xin chào, {account.owner_name}!')
        self.info_line_label.configure(
            text=(
                f'Tài khoản {account.account_id} • Ngày tạo {account.created_at} • '
                f'Đang gửi tiết kiệm: {savings_summary["active_count"]} sổ '
                f'({format_money_vnd(savings_summary["total_principal"])})'
            )
        )
        self.account_id_value.configure(text=account.account_id)
        self.balance_value.configure(text=format_money_vnd(account.balance))
        self.transaction_count_value.configure(text=str(len(history)))
        self.savings_count_value.configure(text=str(savings_summary['active_count']))
        self.refresh_recent_transactions()
        self.app.set_status('Đã làm mới thông tin tài khoản.')

    def on_show(self) -> None:
        self.refresh_information()

    def copy_account_id(self) -> None:
        account = self.get_logged_account()
        if account is None:
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(str(account.account_id))
            self.app.set_status('Đã copy số tài khoản vào clipboard.')
            messagebox.showinfo('Copy', 'Đã copy số tài khoản.', parent=self)
        except Exception:
            messagebox.showwarning('Lỗi', 'Không thể copy vào clipboard.', parent=self)

    def open_register_from_dashboard(self) -> None:
        self.app.show_frame('RegisterFrame')

    def logout(self) -> None:
        confirm = messagebox.askyesno('Xác nhận', 'Bạn muốn đăng xuất?', parent=self)
        if not confirm:
            return
        self.app.logged_account_id = None
        self.app.set_status('Đã đăng xuất khỏi tài khoản hiện tại.')
        self.app.show_frame('StartFrame')

    def open_deposit(self) -> None:
        account = self.get_logged_account()
        if account is None:
            return

        def submit(amount: int, note: str):
            ok, message = self.app.bank_service.deposit_money(account.account_id, amount, note)
            if ok:
                self.app.save_data()
                self.refresh_information()
                self.app.set_status(f'Đã nạp {format_money_vnd(amount)} vào tài khoản {account.account_id}.')
            return ok, message

        MoneyDialog(self, 'Nạp tiền', account.balance, submit)

    def open_withdraw(self) -> None:
        account = self.get_logged_account()
        if account is None:
            return

        def submit(amount: int, note: str):
            ok, message = self.app.bank_service.withdraw_money(account.account_id, amount, note)
            if ok:
                self.app.save_data()
                self.refresh_information()
                self.app.set_status(f'Đã rút {format_money_vnd(amount)} từ tài khoản {account.account_id}.')
            return ok, message

        MoneyDialog(self, 'Rút tiền', account.balance, submit)

    def open_transfer(self) -> None:
        account = self.get_logged_account()
        if account is None:
            return

        def after_transfer():
            self.app.save_data()
            self.refresh_information()
            self.app.set_status(f'Đã cập nhật sau khi chuyển khoản từ {account.account_id}.')

        TransferDialog(self, self.app.bank_service, account.account_id, after_transfer)

    def open_history(self) -> None:
        account_id = self.get_logged_account_id()
        if account_id == '':
            return
        HistoryWindow(self, self.app.bank_service, account_id)

    def open_savings(self) -> None:
        account_id = self.get_logged_account_id()
        if account_id == '':
            return
        SavingsWindow(self, self.app.bank_service, account_id, save_callback=self.app.save_data, refresh_callback=self.refresh_information)
