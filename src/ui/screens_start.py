from tkinter import ttk, messagebox

from src.ui.ui_helpers import ScrollableContent, format_money_vnd


class StartFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style='App.TFrame')
        self.app = app
        self.scrollable = ScrollableContent(self, frame_style='App.TFrame')
        self.scrollable.pack(fill='both', expand=True)
        self.page = self.scrollable.body

        self.hero = ttk.Frame(self.page, style='Hero.TFrame', padding=(28, 28))
        self.hero.pack(fill='x', pady=(0, 18))

        self.hero_left = ttk.Frame(self.hero, style='Hero.TFrame')
        self.hero_left.pack(side='left', fill='both', expand=True)
        ttk.Label(self.hero_left, text='Ngân hàng số Mini Bank', style='HeroTitle.TLabel').pack(anchor='w')
        self.hero_desc = ttk.Label(
            self.hero_left,
            text='',
            style='HeroText.TLabel',
            wraplength=620,
            justify='left',
        )
        self.hero_desc.pack(anchor='w', pady=(10, 16))

        self.action_bar = ttk.Frame(self.hero_left, style='Hero.TFrame')
        self.action_bar.pack(anchor='w')
        ttk.Button(self.action_bar, text='Mở tài khoản ngay', command=self.open_register, style='Primary.TButton').grid(row=0, column=0, padx=(0, 10), pady=4)
        ttk.Button(self.action_bar, text='Đăng nhập', command=self.open_login, style='Light.TButton').grid(row=0, column=1, padx=(0, 10), pady=4)
        ttk.Button(self.action_bar, text='Thoát ứng dụng', command=self.app.on_window_close, style='Light.TButton').grid(row=0, column=2, pady=4)

        self.hero_right = ttk.Frame(self.hero, style='Surface.TFrame', padding=(22, 18))
        self.hero_right.pack(side='right', padx=(22, 0), fill='y')
        ttk.Label(self.hero_right, text='Điểm nổi bật', style='CardTitle.TLabel').pack(anchor='w')
        for line in [
            '• Tạo tài khoản nhanh với PIN 4–6 số',
            '• Nạp, rút, chuyển khoản ngay trên giao diện',
            '• Lịch sử giao dịch lọc và tìm kiếm rõ ràng',
            '• Dữ liệu lưu nhanh chóng',
        ]:
            ttk.Label(self.hero_right, text=line, style='Surface.TLabel').pack(anchor='w', pady=3)

        self.metrics_wrap = ttk.Frame(self.page, style='App.TFrame')
        self.metrics_wrap.pack(fill='x', pady=(0, 18))
        self.account_card, self.account_value = self._create_metric_card(self.metrics_wrap, 'Tổng số tài khoản')
        self.transaction_card, self.transaction_value = self._create_metric_card(self.metrics_wrap, 'Tổng số giao dịch')
        self.balance_card, self.balance_value = self._create_metric_card(self.metrics_wrap, 'Tổng số dư toàn hệ thống')

        self.bottom_grid = ttk.Frame(self.page, style='App.TFrame')
        self.bottom_grid.pack(fill='both', expand=True)

        self.left_card = ttk.Frame(self.bottom_grid, style='Card.TFrame', padding=(22, 18))
        ttk.Label(self.left_card, text='', style='SectionTitle.TLabel').pack(anchor='w')
        self.practice_label = ttk.Label(
            self.left_card,
            text='',
            style='Surface.TLabel',
            wraplength=620,
            justify='left',
        )
        self.practice_label.pack(anchor='w', pady=(8, 14))
        for line in [
        ]:
            ttk.Label(self.left_card, text=line, style='Surface.TLabel').pack(anchor='w', pady=4)
        button_row = ttk.Frame(self.left_card, style='Card.TFrame')
        button_row.pack(anchor='w', pady=(16, 0))
        ttk.Button(button_row, text='Làm mới số liệu', command=self.refresh_summary, style='Secondary.TButton').grid(row=0, column=0, padx=(0, 10), pady=4)
        ttk.Button(button_row, text='Giới thiệu dự án', command=self.show_project_info, style='Light.TButton').grid(row=0, column=1, pady=4)

        self.right_card = ttk.Frame(self.bottom_grid, style='Card.TFrame', padding=(22, 18))
        ttk.Label(self.right_card, text='Thông tin gần nhất', style='SectionTitle.TLabel').pack(anchor='w')
        self.recent_info_label = ttk.Label(self.right_card, text='Đang cập nhật...', style='Surface.TLabel', wraplength=320, justify='left')
        self.recent_info_label.pack(anchor='w', pady=(10, 14))
        ttk.Label(self.right_card, text='Mẹo thao tác', style='CardTitle.TLabel').pack(anchor='w')
        self.tip_label = ttk.Label(
            self.right_card,
            text='Tạo tài khoản trước, sau đó bấm “Đăng nhập” để vào bảng điều khiển. Trong dashboard, nhấn đúp vào bảng giao dịch để mở lịch sử đầy đủ.',
            style='Surface.TLabel',
            wraplength=320,
            justify='left',
        )
        self.tip_label.pack(anchor='w', pady=(8, 10))
        ttk.Label(self.right_card, text='', style='CardTitle.TLabel').pack(anchor='w', pady=(10, 0))
        ttk.Label(
            self.right_card,
            text='',
            style='Surface.TLabel',
            justify='left',
        ).pack(anchor='w', pady=(8, 0))

        self.page.bind('<Configure>', self.on_resize)
        self.on_resize()

    def _create_metric_card(self, parent, title: str):
        card = ttk.Frame(parent, style='Card.TFrame', padding=(18, 16))
        ttk.Label(card, text=title, style='CardTitle.TLabel').pack(anchor='w')
        value_label = ttk.Label(card, text='0', style='MetricValue.TLabel')
        value_label.pack(anchor='w', pady=(12, 2))
        ttk.Label(card, text='Cập nhật theo dữ liệu hiện tại', style='MetricCaption.TLabel').pack(anchor='w')
        return card, value_label

    def on_resize(self, event=None) -> None:
        width = self.page.winfo_width() or self.winfo_width() or 1200
        narrow = width < 980
        wrap_main = max(420, width - 180)
        wrap_side = max(280, min(420, width - 140))
        self.hero_desc.configure(wraplength=max(360, wrap_main - 160))
        self.practice_label.configure(wraplength=max(360, wrap_main - 180))
        self.recent_info_label.configure(wraplength=wrap_side)
        self.tip_label.configure(wraplength=wrap_side)

        self.hero_left.pack_forget()
        self.hero_right.pack_forget()
        if narrow:
            self.hero_left.pack(fill='both', expand=True)
            self.hero_right.pack(fill='x', pady=(18, 0))
        else:
            self.hero_left.pack(side='left', fill='both', expand=True)
            self.hero_right.pack(side='right', padx=(22, 0), fill='y')

        for index, card in enumerate([self.account_card, self.transaction_card, self.balance_card]):
            card.grid_forget()
            if narrow:
                card.grid(row=index, column=0, sticky='ew', pady=(0, 10) if index < 2 else 0)
                self.metrics_wrap.columnconfigure(0, weight=1)
            else:
                card.grid(row=0, column=index, sticky='nsew', padx=(0, 10) if index < 2 else 0)
                self.metrics_wrap.columnconfigure(index, weight=1)

        self.left_card.grid_forget()
        self.right_card.grid_forget()
        if narrow:
            self.bottom_grid.columnconfigure(0, weight=1)
            self.left_card.grid(row=0, column=0, sticky='nsew', pady=(0, 12))
            self.right_card.grid(row=1, column=0, sticky='nsew')
        else:
            self.bottom_grid.columnconfigure(0, weight=3)
            self.bottom_grid.columnconfigure(1, weight=2)
            self.left_card.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
            self.right_card.grid(row=0, column=1, sticky='nsew')

    def refresh_summary(self) -> None:
        account_count = len(self.app.bank_service.accounts_by_id)
        transaction_count = len(self.app.bank_service.transaction_list)
        total_balance = sum(int(account.balance) for account in self.app.bank_service.accounts_by_id.values())
        self.account_value.configure(text=str(account_count))
        self.transaction_value.configure(text=str(transaction_count))
        self.balance_value.configure(text=format_money_vnd(total_balance))

        last_created = str(self.app.last_created_account_id).strip() or 'Chưa có'
        last_login = str(self.app.last_login_account_id).strip() or 'Chưa có'
        self.recent_info_label.configure(
            text=(
                f'Tài khoản vừa tạo gần nhất: {last_created}\n'
                f'Tài khoản đăng nhập gần nhất: {last_login}\n\n'
                'Bạn có thể dùng nút “Đăng nhập” ở phía trên để chuyển sang màn hình xác thực.'
            )
        )
        self.app.set_status('Đã cập nhật thông tin ở màn hình bắt đầu.')

    def on_show(self) -> None:
        self.refresh_summary()

    def show_project_info(self) -> None:
        messagebox.showinfo(
            'Giới thiệu dự án',
            'Mini Bank là dự án thực hành Python Tkinter dành cho học sinh.\n\n'
            'Nội dung phù hợp để dạy:\n'
            '- Chia giao diện thành nhiều màn hình\n'
            '- Kiểm tra dữ liệu nhập\n'
            '- Gọi lớp nghiệp vụ xử lý giao dịch\n'
            '- Cập nhật dữ liệu và lưu xuống JSON',
            parent=self,
        )

    def open_register(self) -> None:
        self.app.show_frame('RegisterFrame')

    def open_login(self) -> None:
        self.app.show_frame('LoginFrame')
