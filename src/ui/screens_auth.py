import re
import tkinter as tk
from tkinter import ttk, messagebox

from src.ui.ui_helpers import ScrollableContent, is_pin_format_valid, read_non_negative_integer


class RegisterFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style='App.TFrame')
        self.app = app
        self.scrollable = ScrollableContent(self, frame_style='App.TFrame')
        self.scrollable.pack(fill='both', expand=True)
        self.page = self.scrollable.body

        ttk.Label(self.page, text='Mở tài khoản mới', style='HeaderTitle.TLabel').pack(anchor='w', pady=(0, 14))

        self.body = ttk.Frame(self.page, style='App.TFrame')
        self.body.pack(fill='both', expand=True)

        self.form_card = ttk.Frame(self.body, style='Card.TFrame', padding=(24, 20))
        ttk.Label(self.form_card, text='Biểu mẫu đăng ký', style='SectionTitle.TLabel').pack(anchor='w')
        self.form_intro = ttk.Label(
            self.form_card,
            text='Điền đầy đủ thông tin để tạo tài khoản mới. Giao diện đã được nâng cấp theo hướng giống ứng dụng ngân hàng số.',
            style='Surface.TLabel',
            wraplength=620,
            justify='left',
        )
        self.form_intro.pack(anchor='w', pady=(8, 18))

        form_grid = ttk.Frame(self.form_card, style='Card.TFrame')
        form_grid.pack(fill='x')
        form_grid.columnconfigure(1, weight=1)

        ttk.Label(form_grid, text='Tên chủ tài khoản', style='Surface.TLabel').grid(row=0, column=0, sticky='w', pady=8)
        self.owner_name_entry = ttk.Entry(form_grid, width=38)
        self.owner_name_entry.grid(row=0, column=1, sticky='ew', pady=8)

        ttk.Label(form_grid, text='PIN (4–6 chữ số)', style='Surface.TLabel').grid(row=1, column=0, sticky='w', pady=8)
        self.pin_code_entry = ttk.Entry(form_grid, width=38, show='*')
        self.pin_code_entry.grid(row=1, column=1, sticky='ew', pady=8)
        ttk.Checkbutton(form_grid, text='Hiện PIN', command=self.toggle_register_pin, style='Surface.TCheckbutton').grid(row=1, column=2, padx=(10, 0))

        ttk.Label(form_grid, text='Số dư ban đầu (VNĐ)', style='Surface.TLabel').grid(row=2, column=0, sticky='w', pady=8)
        self.initial_balance_entry = ttk.Entry(form_grid, width=38)
        self.initial_balance_entry.grid(row=2, column=1, sticky='ew', pady=8)
        self.initial_balance_entry.insert(0, '0')

        self.register_feedback_label = ttk.Label(self.form_card, text='Nhập thông tin để bắt đầu.', style='Muted.TLabel')
        self.register_feedback_label.pack(anchor='w', pady=(14, 8))

        preview_box = ttk.LabelFrame(self.form_card, text='Xem trước', style='Card.TLabelframe')
        preview_box.pack(fill='x', pady=(2, 16))
        self.preview_label = ttk.Label(preview_box, text='Thông tin xem trước: chưa có dữ liệu.', style='Surface.TLabel', wraplength=610, justify='left')
        self.preview_label.pack(anchor='w')

        button_row = ttk.Frame(self.form_card, style='Card.TFrame')
        button_row.pack(anchor='w')
        ttk.Button(button_row, text='Tạo tài khoản', command=self.create_account, style='Primary.TButton').grid(row=0, column=0, padx=(0, 10), pady=4)
        ttk.Button(button_row, text='Làm trống', command=self.clear_inputs, style='Secondary.TButton').grid(row=0, column=1, padx=(0, 10), pady=4)
        ttk.Button(button_row, text='Sang đăng nhập', command=self.go_to_login, style='Light.TButton').grid(row=0, column=2, padx=(0, 10), pady=4)
        ttk.Button(button_row, text='Quay lại', command=self.go_back, style='Light.TButton').grid(row=0, column=3, pady=4)

        self.right_card = ttk.Frame(self.body, style='Card.TFrame', padding=(24, 20))
        ttk.Label(self.right_card, text='Hướng dẫn nhanh', style='SectionTitle.TLabel').pack(anchor='w')
        self.help_items = []
        for text in [
            '• Tên chủ tài khoản không được bỏ trống.',
            '• PIN chỉ gồm chữ số, độ dài từ 4 đến 6.',
            '• Số dư ban đầu có thể nhập 0 hoặc giá trị lớn hơn.',
            '• Sau khi tạo thành công, hệ thống tự chuyển sang màn hình đăng nhập.',
        ]:
            label = ttk.Label(self.right_card, text=text, style='Surface.TLabel', wraplength=320, justify='left')
            label.pack(anchor='w', pady=4)
            self.help_items.append(label)
        ttk.Label(self.right_card, text='Mô phỏng giống ứng dụng thật', style='CardTitle.TLabel').pack(anchor='w', pady=(16, 4))
        self.help_desc = ttk.Label(
            self.right_card,
            text='Biểu mẫu chia rõ từng trường, có gợi ý realtime và hộp xem trước để học sinh hiểu ngay dữ liệu nào sẽ được ghi xuống hệ thống.',
            style='Surface.TLabel',
            wraplength=320,
            justify='left',
        )
        self.help_desc.pack(anchor='w')

        self.owner_name_entry.bind('<KeyRelease>', self.on_register_input_change)
        self.pin_code_entry.bind('<KeyRelease>', self.on_register_input_change)
        self.initial_balance_entry.bind('<KeyRelease>', self.on_register_input_change)
        self.initial_balance_entry.bind('<FocusOut>', self.on_balance_focus_out)
        self.owner_name_entry.bind('<Return>', lambda event: self.create_account())
        self.pin_code_entry.bind('<Return>', lambda event: self.create_account())
        self.initial_balance_entry.bind('<Return>', lambda event: self.create_account())

        self.page.bind('<Configure>', self.on_resize)
        self.on_resize()

    def on_resize(self, event=None) -> None:
        width = self.page.winfo_width() or self.winfo_width() or 1200
        narrow = width < 980
        form_wrap = max(420, width - 260)
        side_wrap = max(280, min(420, width - 140))
        self.form_intro.configure(wraplength=max(380, form_wrap - 120))
        self.preview_label.configure(wraplength=max(360, form_wrap - 130))
        for label in self.help_items:
            label.configure(wraplength=side_wrap)
        self.help_desc.configure(wraplength=side_wrap)

        self.form_card.grid_forget()
        self.right_card.grid_forget()
        if narrow:
            self.body.columnconfigure(0, weight=1)
            self.form_card.grid(row=0, column=0, sticky='nsew', pady=(0, 12))
            self.right_card.grid(row=1, column=0, sticky='nsew')
        else:
            self.body.columnconfigure(0, weight=3)
            self.body.columnconfigure(1, weight=2)
            self.form_card.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
            self.right_card.grid(row=0, column=1, sticky='nsew')

    def toggle_register_pin(self) -> None:
        self.pin_code_entry.configure(show='*' if self.pin_code_entry.cget('show') == '' else '')

    def parse_initial_balance_relaxed(self, text: str) -> int:
        raw = str(text).strip()
        if raw == '':
            return -1
        raw = re.sub(r'[\s\.,_]', '', raw)
        return read_non_negative_integer(raw)

    def on_balance_focus_out(self, event=None) -> None:
        value = self.parse_initial_balance_relaxed(self.initial_balance_entry.get())
        if value != -1:
            self.initial_balance_entry.delete(0, tk.END)
            self.initial_balance_entry.insert(0, f'{value:,}'.replace(',', '.'))

    def on_register_input_change(self, event=None) -> None:
        owner_name = self.owner_name_entry.get().strip()
        pin_code = self.pin_code_entry.get().strip()
        balance = self.parse_initial_balance_relaxed(self.initial_balance_entry.get())

        if owner_name == '':
            feedback_text, feedback_color = 'Gợi ý: nhập tên chủ tài khoản.', '#6e7f93'
        elif not is_pin_format_valid(pin_code):
            feedback_text, feedback_color = 'Gợi ý: PIN cần 4 đến 6 chữ số.', '#d07b00'
        elif balance == -1:
            feedback_text, feedback_color = 'Gợi ý: số dư ban đầu phải là số nguyên không âm.', '#d07b00'
        else:
            feedback_text, feedback_color = 'Thông tin hợp lệ, có thể tạo tài khoản.', '#12805c'

        self.register_feedback_label.configure(text=feedback_text, foreground=feedback_color)
        display_name = owner_name if owner_name else '(chưa nhập tên)'
        display_pin = '*' * len(pin_code) if pin_code else '(chưa nhập PIN)'
        display_balance = 'không hợp lệ' if balance == -1 else f'{balance:,} VNĐ'.replace(',', '.')
        self.preview_label.configure(text=f'Thông tin xem trước: {display_name} | PIN: {display_pin} | Số dư: {display_balance}')

    def go_to_login(self) -> None:
        self.app.show_frame('LoginFrame')

    def go_to_register(self) -> None:
        self.clear_inputs()
        self.app.show_frame('RegisterFrame')

    def go_back(self) -> None:
        self.clear_inputs()
        self.app.show_frame('StartFrame')

    def clear_inputs(self) -> None:
        self.owner_name_entry.delete(0, 'end')
        self.pin_code_entry.delete(0, 'end')
        self.initial_balance_entry.delete(0, 'end')
        self.initial_balance_entry.insert(0, '0')
        self.register_feedback_label.configure(text='Nhập thông tin để bắt đầu.', foreground='#6e7f93')
        self.preview_label.configure(text='Thông tin xem trước: chưa có dữ liệu.')
        self.owner_name_entry.focus_set()

    def on_show(self) -> None:
        self.owner_name_entry.focus_set()
        self.on_register_input_change()

    def create_account(self) -> None:
        owner_name = self.owner_name_entry.get().strip()
        pin_code = self.pin_code_entry.get().strip()
        initial_balance = self.parse_initial_balance_relaxed(self.initial_balance_entry.get())

        if owner_name == '':
            messagebox.showwarning('Lỗi nhập liệu', 'Tên chủ tài khoản không được để trống.', parent=self)
            return
        if not is_pin_format_valid(pin_code):
            messagebox.showwarning('Lỗi nhập liệu', 'PIN phải gồm 4 đến 6 chữ số.', parent=self)
            return
        if initial_balance == -1:
            messagebox.showwarning('Lỗi nhập liệu', 'Số dư ban đầu phải là số nguyên không âm.', parent=self)
            return

        ok, message, account_id = self.app.bank_service.create_account(owner_name, pin_code, initial_balance)
        if ok:
            self.app.last_created_account_id = str(account_id)
            self.app.save_data()
            self.app.set_status(f'Tạo tài khoản thành công: {account_id}')
            messagebox.showinfo('Thành công', f'{message}\nBạn có thể dùng tài khoản này để đăng nhập ngay.', parent=self)
            self.clear_inputs()
            self.app.show_frame('LoginFrame')
        else:
            messagebox.showwarning('Không thành công', message, parent=self)


class LoginFrame(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, style='App.TFrame')
        self.app = app
        self.scrollable = ScrollableContent(self, frame_style='App.TFrame')
        self.scrollable.pack(fill='both', expand=True)
        self.page = self.scrollable.body

        ttk.Label(self.page, text='Đăng nhập tài khoản', style='HeaderTitle.TLabel').pack(anchor='w', pady=(0, 14))

        self.body = ttk.Frame(self.page, style='App.TFrame')
        self.body.pack(fill='both', expand=True)

        self.form_card = ttk.Frame(self.body, style='Card.TFrame', padding=(24, 20))
        ttk.Label(self.form_card, text='Xác thực người dùng', style='SectionTitle.TLabel').pack(anchor='w')
        self.form_intro = ttk.Label(
            self.form_card,
            text='Nhập số tài khoản và PIN để truy cập bảng điều khiển. Nếu vừa tạo tài khoản, bạn có thể dùng nút điền nhanh.',
            style='Surface.TLabel',
            wraplength=620,
            justify='left',
        )
        self.form_intro.pack(anchor='w', pady=(8, 18))

        form_grid = ttk.Frame(self.form_card, style='Card.TFrame')
        form_grid.pack(fill='x')
        form_grid.columnconfigure(1, weight=1)

        ttk.Label(form_grid, text='Số tài khoản', style='Surface.TLabel').grid(row=0, column=0, sticky='w', pady=8)
        self.account_id_entry = ttk.Entry(form_grid, width=38)
        self.account_id_entry.grid(row=0, column=1, sticky='ew', pady=8)

        ttk.Label(form_grid, text='PIN', style='Surface.TLabel').grid(row=1, column=0, sticky='w', pady=8)
        self.pin_code_entry = ttk.Entry(form_grid, width=38, show='*')
        self.pin_code_entry.grid(row=1, column=1, sticky='ew', pady=8)
        ttk.Checkbutton(form_grid, text='Hiện PIN', command=self.toggle_login_pin, style='Surface.TCheckbutton').grid(row=1, column=2, padx=(10, 0))

        self.login_feedback_label = ttk.Label(self.form_card, text='Nhập thông tin để tiếp tục.', style='Muted.TLabel')
        self.login_feedback_label.pack(anchor='w', pady=(14, 8))
        self.recent_account_label = ttk.Label(self.form_card, text='Tài khoản gần nhất: chưa có dữ liệu.', style='Strong.TLabel')
        self.recent_account_label.pack(anchor='w', pady=(0, 16))

        button_row = ttk.Frame(self.form_card, style='Card.TFrame')
        button_row.pack(anchor='w')
        ttk.Button(button_row, text='Đăng nhập', command=self.login, style='Primary.TButton').grid(row=0, column=0, padx=(0, 10), pady=4)
        ttk.Button(button_row, text='Dùng tài khoản vừa tạo', command=self.prefill_recent_account, style='Secondary.TButton').grid(row=0, column=1, padx=(0, 10), pady=4)
        ttk.Button(button_row, text='Mở tài khoản mới', command=self.go_to_register, style='Secondary.TButton').grid(row=0, column=2, padx=(0, 10), pady=4)
        ttk.Button(button_row, text='Quay lại', command=self.go_back, style='Light.TButton').grid(row=0, column=3, pady=4)

        self.right_card = ttk.Frame(self.body, style='Card.TFrame', padding=(24, 20))
        ttk.Label(self.right_card, text='Tại sao giao diện này dễ dạy?', style='SectionTitle.TLabel').pack(anchor='w')
        self.right_intro = ttk.Label(
            self.right_card,
            text='Màn hình chia rõ khu vực nhập liệu, gợi ý trạng thái và hành động. Học sinh dễ nhìn thấy luồng dữ liệu từ login sang dashboard.',
            style='Surface.TLabel',
            wraplength=320,
            justify='left',
        )
        self.right_intro.pack(anchor='w', pady=(8, 14))
        self.right_items = []
        for text in [
            '• Có thể điền nhanh tài khoản vừa tạo.',
            '• Gợi ý realtime khi thiếu thông tin.',
            '• Đăng nhập xong chuyển ngay vào bảng điều khiển.',
            '• Thanh tiêu đề đổi theo trạng thái người dùng.',
        ]:
            label = ttk.Label(self.right_card, text=text, style='Surface.TLabel', wraplength=320, justify='left')
            label.pack(anchor='w', pady=4)
            self.right_items.append(label)

        self.account_id_entry.bind('<KeyRelease>', self.on_login_input_change)
        self.pin_code_entry.bind('<KeyRelease>', self.on_login_input_change)
        self.account_id_entry.bind('<Return>', lambda event: self.login())
        self.pin_code_entry.bind('<Return>', lambda event: self.login())

        self.page.bind('<Configure>', self.on_resize)
        self.on_resize()

    def on_resize(self, event=None) -> None:
        width = self.page.winfo_width() or self.winfo_width() or 1200
        narrow = width < 980
        form_wrap = max(420, width - 260)
        side_wrap = max(280, min(420, width - 140))
        self.form_intro.configure(wraplength=max(380, form_wrap - 120))
        self.right_intro.configure(wraplength=side_wrap)
        for label in self.right_items:
            label.configure(wraplength=side_wrap)

        self.form_card.grid_forget()
        self.right_card.grid_forget()
        if narrow:
            self.body.columnconfigure(0, weight=1)
            self.form_card.grid(row=0, column=0, sticky='nsew', pady=(0, 12))
            self.right_card.grid(row=1, column=0, sticky='nsew')
        else:
            self.body.columnconfigure(0, weight=3)
            self.body.columnconfigure(1, weight=2)
            self.form_card.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
            self.right_card.grid(row=0, column=1, sticky='nsew')

    def toggle_login_pin(self) -> None:
        self.pin_code_entry.configure(show='*' if self.pin_code_entry.cget('show') == '' else '')

    def prefill_recent_account(self) -> None:
        recent_account_id = str(self.app.last_created_account_id).strip()
        if recent_account_id == '':
            messagebox.showinfo('Thông báo', 'Chưa có tài khoản vừa tạo trong phiên làm việc này.', parent=self)
            return
        self.account_id_entry.delete(0, tk.END)
        self.account_id_entry.insert(0, recent_account_id)
        self.pin_code_entry.focus_set()
        self.on_login_input_change()

    def on_login_input_change(self, event=None) -> None:
        account_id = self.account_id_entry.get().strip()
        pin_code = self.pin_code_entry.get().strip()
        if account_id == '':
            self.login_feedback_label.configure(text='Gợi ý: nhập số tài khoản cần đăng nhập.', foreground='#6e7f93')
        elif pin_code == '':
            self.login_feedback_label.configure(text='Gợi ý: nhập mã PIN của tài khoản.', foreground='#d07b00')
        else:
            self.login_feedback_label.configure(text='Đã đủ thông tin, nhấn Đăng nhập để tiếp tục.', foreground='#12805c')

    def update_recent_account_label(self) -> None:
        recent_account_id = str(self.app.last_created_account_id).strip()
        if recent_account_id == '':
            self.recent_account_label.configure(text='Tài khoản gần nhất: chưa có dữ liệu.')
        else:
            self.recent_account_label.configure(text=f'Tài khoản gần nhất vừa tạo: {recent_account_id}')

    def go_to_register(self) -> None:
        self.clear_inputs()
        self.app.show_frame('RegisterFrame')

    def go_back(self) -> None:
        self.clear_inputs()
        self.app.show_frame('StartFrame')

    def clear_inputs(self) -> None:
        self.account_id_entry.delete(0, 'end')
        self.pin_code_entry.delete(0, 'end')
        self.login_feedback_label.configure(text='Nhập thông tin để tiếp tục.', foreground='#6e7f93')
        self.account_id_entry.focus_set()

    def on_show(self) -> None:
        self.update_recent_account_label()
        self.account_id_entry.delete(0, tk.END)
        if str(self.app.last_created_account_id).strip() != '':
            self.account_id_entry.insert(0, str(self.app.last_created_account_id))
        self.pin_code_entry.focus_set()
        self.on_login_input_change()

    def login(self) -> None:
        account_id = self.account_id_entry.get().strip()
        pin_code = self.pin_code_entry.get().strip()
        if account_id == '':
            messagebox.showwarning('Lỗi nhập liệu', 'Số tài khoản không được để trống.', parent=self)
            return
        if pin_code == '':
            messagebox.showwarning('Lỗi nhập liệu', 'PIN không được để trống.', parent=self)
            return
        ok, message = self.app.bank_service.authenticate_login(account_id, pin_code)
        if ok:
            self.app.logged_account_id = account_id
            self.app.last_login_account_id = account_id
            self.app.set_status(f'Đăng nhập thành công: {account_id}')
            self.clear_inputs()
            self.app.show_frame('DashboardFrame')
        else:
            messagebox.showwarning('Không thành công', message, parent=self)
