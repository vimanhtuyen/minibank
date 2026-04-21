from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

from src.storage.json_storage import load_bank_data, save_bank_data
from src.core.bank_service import BankService
from src.ui.screens_start import StartFrame
from src.ui.screens_auth import RegisterFrame, LoginFrame
from src.ui.screens_dashboard import DashboardFrame
from src.ui.ui_helpers import (
    BIDV_BACKGROUND,
    BIDV_BLUE,
    BIDV_BORDER,
    BIDV_DARK_BLUE,
    BIDV_LIGHT_BLUE,
    BIDV_MUTED,
    BIDV_RED,
    BIDV_SURFACE,
    BIDV_TEXT,
    clamp_window_size,
    center_window,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_FILE_PATH = str(PROJECT_ROOT / 'data' / 'bank_data.json')


class MiniBankApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Mini Bank | Giao diện phong cách BIDV')
        self.configure(bg=BIDV_BACKGROUND)
        width, height = clamp_window_size(self, 1320, 860, min_width=980, min_height=680, margin_x=60, margin_y=80)
        self.geometry(f'{width}x{height}')
        self.minsize(980, 680)
        self.resizable(True, True)
        self.is_fullscreen = False

        self.last_created_account_id = ''
        self.last_login_account_id = ''
        self.logged_account_id = None
        self.current_frame_name = 'StartFrame'

        self.setup_style()
        self.setup_menu()

        bank_data = load_bank_data(DATA_FILE_PATH)
        self.bank_service = BankService(bank_data)

        self.build_shell_layout()
        self.frames = {}
        self.create_frames()
        self.build_status_bar()

        self.update_quick_summary()
        self.show_frame('StartFrame')
        center_window(self, width=width, height=height)

        self.bind_all('<Control-s>', lambda event: self.save_data())
        self.bind_all('<F5>', lambda event: self.refresh_current_frame())
        self.bind_all('<F11>', lambda event: self.toggle_fullscreen())
        self.bind_all('<Escape>', self._handle_escape)
        self.bind_all('<Control-m>', lambda event: self.toggle_maximize())
        self.protocol('WM_DELETE_WINDOW', self.on_window_close)

    def setup_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except Exception:
            pass

        style.configure('TFrame', background=BIDV_BACKGROUND)
        style.configure('App.TFrame', background=BIDV_BACKGROUND)
        style.configure('Surface.TFrame', background=BIDV_SURFACE)
        style.configure('Card.TFrame', background=BIDV_SURFACE, relief='flat')
        style.configure('AppBar.TFrame', background=BIDV_DARK_BLUE)
        style.configure('Hero.TFrame', background=BIDV_BLUE)
        style.configure('Strip.TFrame', background=BIDV_RED)
        style.configure('Footer.TFrame', background=BIDV_DARK_BLUE)

        style.configure('TLabel', background=BIDV_BACKGROUND, foreground=BIDV_TEXT, font=('Segoe UI', 10))
        style.configure('Surface.TLabel', background=BIDV_SURFACE, foreground=BIDV_TEXT)
        style.configure('Muted.TLabel', background=BIDV_SURFACE, foreground=BIDV_MUTED)
        style.configure('BrandTitle.TLabel', background=BIDV_DARK_BLUE, foreground='white', font=('Segoe UI', 20, 'bold'))
        style.configure('BrandSub.TLabel', background=BIDV_DARK_BLUE, foreground='#d5e6fb', font=('Segoe UI', 10))
        style.configure('HeaderTitle.TLabel', background=BIDV_BACKGROUND, foreground=BIDV_DARK_BLUE, font=('Segoe UI', 21, 'bold'))
        style.configure('SectionTitle.TLabel', background=BIDV_SURFACE, foreground=BIDV_DARK_BLUE, font=('Segoe UI', 13, 'bold'))
        style.configure('CardTitle.TLabel', background=BIDV_SURFACE, foreground=BIDV_DARK_BLUE, font=('Segoe UI', 11, 'bold'))
        style.configure('Strong.TLabel', background=BIDV_SURFACE, foreground=BIDV_TEXT, font=('Segoe UI', 11, 'bold'))
        style.configure('HeroTitle.TLabel', background=BIDV_BLUE, foreground='white', font=('Segoe UI', 24, 'bold'))
        style.configure('HeroText.TLabel', background=BIDV_BLUE, foreground='#e5f1ff', font=('Segoe UI', 11))
        style.configure('MetricValue.TLabel', background=BIDV_SURFACE, foreground=BIDV_DARK_BLUE, font=('Segoe UI', 16, 'bold'))
        style.configure('MetricCaption.TLabel', background=BIDV_SURFACE, foreground=BIDV_MUTED, font=('Segoe UI', 9))
        style.configure('Status.TLabel', background=BIDV_DARK_BLUE, foreground='white', font=('Segoe UI', 9))
        style.configure('StatusDim.TLabel', background=BIDV_DARK_BLUE, foreground='#dbe9f9', font=('Segoe UI', 9))

        style.configure('Card.TLabelframe', background=BIDV_SURFACE, bordercolor=BIDV_BORDER, borderwidth=1, relief='solid', padding=14)
        style.configure('Card.TLabelframe.Label', background=BIDV_SURFACE, foreground=BIDV_DARK_BLUE, font=('Segoe UI', 11, 'bold'))

        style.configure('TEntry', padding=8, fieldbackground='white', foreground=BIDV_TEXT, bordercolor=BIDV_BORDER)
        style.map('TEntry', bordercolor=[('focus', BIDV_BLUE)])
        style.configure('TCombobox', padding=6, fieldbackground='white', foreground=BIDV_TEXT, bordercolor=BIDV_BORDER)
        style.map('TCombobox', bordercolor=[('focus', BIDV_BLUE)])
        style.configure('Surface.TCheckbutton', background=BIDV_SURFACE, foreground=BIDV_TEXT, font=('Segoe UI', 10))
        style.map('Surface.TCheckbutton', background=[('active', BIDV_SURFACE)])

        style.configure('Primary.TButton', background=BIDV_RED, foreground='white', borderwidth=0, padding=(18, 10), font=('Segoe UI', 10, 'bold'))
        style.map('Primary.TButton', background=[('active', '#bf1820'), ('pressed', '#a7141b')])
        style.configure('Secondary.TButton', background=BIDV_BLUE, foreground='white', borderwidth=0, padding=(16, 10), font=('Segoe UI', 10, 'bold'))
        style.map('Secondary.TButton', background=[('active', '#004f93'), ('pressed', '#00457f')])
        style.configure('Light.TButton', background='white', foreground=BIDV_DARK_BLUE, borderwidth=1, bordercolor=BIDV_BORDER, padding=(16, 10), font=('Segoe UI', 10, 'bold'))
        style.map('Light.TButton', background=[('active', BIDV_LIGHT_BLUE), ('pressed', '#dfeaf7')])
        style.configure('Danger.TButton', background='#fff2f3', foreground=BIDV_RED, borderwidth=1, bordercolor='#f2b8bc', padding=(16, 10), font=('Segoe UI', 10, 'bold'))
        style.map('Danger.TButton', background=[('active', '#ffdfe1')])

        style.configure('Treeview', background='white', fieldbackground='white', foreground=BIDV_TEXT, rowheight=31, bordercolor=BIDV_BORDER, font=('Segoe UI', 10))
        style.configure('Treeview.Heading', background=BIDV_DARK_BLUE, foreground='white', relief='flat', font=('Segoe UI', 10, 'bold'))
        style.map('Treeview.Heading', background=[('active', BIDV_BLUE)])

    def setup_menu(self) -> None:
        menu_bar = tk.Menu(self)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label='Lưu dữ liệu', command=self.save_data)
        file_menu.add_command(label='Làm mới màn hình', command=self.refresh_current_frame)
        file_menu.add_separator()
        file_menu.add_command(label='Thoát', command=self.on_window_close)
        menu_bar.add_cascade(label='Tệp', menu=file_menu)

        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label='Phóng to cửa sổ', command=self.maximize_window)
        view_menu.add_command(label='Khôi phục kích thước', command=self.restore_window)
        view_menu.add_command(label='Toàn màn hình (F11)', command=self.toggle_fullscreen)
        menu_bar.add_cascade(label='Hiển thị', menu=view_menu)

        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label='Hướng dẫn', command=self.show_help)
        help_menu.add_command(label='Giới thiệu', command=self.show_about)
        menu_bar.add_cascade(label='Trợ giúp', menu=help_menu)

        self.config(menu=menu_bar)

    def build_shell_layout(self) -> None:
        self.main_shell = ttk.Frame(self, style='App.TFrame')
        self.main_shell.pack(fill='both', expand=True)

        red_strip = ttk.Frame(self.main_shell, style='Strip.TFrame', height=5)
        red_strip.pack(fill='x')
        red_strip.pack_propagate(False)

        app_bar = ttk.Frame(self.main_shell, style='AppBar.TFrame', padding=(24, 18))
        app_bar.pack(fill='x')

        left_bar = ttk.Frame(app_bar, style='AppBar.TFrame')
        left_bar.pack(side='left', fill='x', expand=True)
        ttk.Label(left_bar, text='MINI BANK', style='BrandTitle.TLabel').pack(anchor='w')
        ttk.Label(left_bar, text='Giao diện nâng cấp theo phong cách ngân hàng số xanh – đỏ, bố cục hiện đại và rõ ràng.', style='BrandSub.TLabel').pack(anchor='w', pady=(2, 0))

        right_bar = ttk.Frame(app_bar, style='AppBar.TFrame')
        right_bar.pack(side='right')
        self.page_title_var = tk.StringVar(value='Trang chủ')
        self.current_user_var = tk.StringVar(value='Chưa đăng nhập')
        ttk.Label(right_bar, textvariable=self.page_title_var, style='BrandTitle.TLabel', font=('Segoe UI', 15, 'bold')).pack(anchor='e')
        ttk.Label(right_bar, textvariable=self.current_user_var, style='BrandSub.TLabel').pack(anchor='e', pady=(2, 0))

        self.content_area = ttk.Frame(self.main_shell, style='App.TFrame', padding=(22, 18, 22, 12))
        self.content_area.pack(fill='both', expand=True)

        self.container = ttk.Frame(self.content_area, style='App.TFrame')
        self.container.pack(fill='both', expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

    def build_status_bar(self) -> None:
        footer = ttk.Frame(self.main_shell, style='Footer.TFrame', padding=(18, 10))
        footer.pack(fill='x', side='bottom')

        self.status_text = tk.StringVar(value='Sẵn sàng.')
        self.quick_summary_text = tk.StringVar(value='')
        ttk.Label(footer, textvariable=self.status_text, style='Status.TLabel').pack(side='left', fill='x', expand=True)
        ttk.Label(footer, textvariable=self.quick_summary_text, style='StatusDim.TLabel').pack(side='right')

    def show_help(self) -> None:
        text = (
            '1) Tạo tài khoản với tên, PIN và số dư ban đầu.\n'
            '2) Đăng nhập bằng số tài khoản và PIN.\n'
            '3) Trong bảng điều khiển, bạn có thể nạp tiền, rút tiền, chuyển khoản, gửi tiết kiệm và xem lịch sử.\n'
            '4) Có thể kéo giãn cửa sổ, phóng to hoặc nhấn F11 để toàn màn hình.\n'
            '5) Dữ liệu được lưu khi thao tác thành công hoặc khi thoát chương trình.\n'
            '6) Phím tắt: Ctrl+S để lưu, F5 để làm mới, Ctrl+M để phóng to, F11 để toàn màn hình.'
        )
        messagebox.showinfo('Hướng dẫn nhanh', text, parent=self)

    def show_about(self) -> None:
        messagebox.showinfo(
            'Mini Bank',
            'Mini Bank - bản nâng cấp giao diện phong cách BIDV.\n'
            'Dự án giữ nguyên lõi nghiệp vụ nhưng thay mới giao diện, bảng điều khiển và các hộp thoại giao dịch.\n\n'
            f'Tệp dữ liệu hiện dùng:\n{DATA_FILE_PATH}',
            parent=self,
        )

    def set_status(self, text: str) -> None:
        self.status_text.set(str(text))

    def update_header_context(self) -> None:
        page_map = {
            'StartFrame': 'Trang chủ',
            'RegisterFrame': 'Mở tài khoản',
            'LoginFrame': 'Đăng nhập',
            'DashboardFrame': 'Tổng quan tài khoản',
        }
        self.page_title_var.set(page_map.get(self.current_frame_name, self.current_frame_name))
        if self.logged_account_id is None:
            self.current_user_var.set('Chưa đăng nhập')
        else:
            account = self.bank_service.get_account(self.logged_account_id)
            if account is None:
                self.current_user_var.set(f'Tài khoản {self.logged_account_id}')
            else:
                self.current_user_var.set(f'{account.owner_name} • {account.account_id}')

    def update_quick_summary(self) -> None:
        account_count = len(self.bank_service.accounts_by_id)
        transaction_count = len(self.bank_service.transaction_list)
        saving_count = len(self.bank_service.saving_deposits)
        self.quick_summary_text.set(f'Tài khoản: {account_count} | Giao dịch: {transaction_count} | Sổ tiết kiệm: {saving_count}')
        self.update_header_context()

    def maximize_window(self) -> None:
        try:
            self.state('zoomed')
        except Exception:
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            self.geometry(f'{screen_width}x{screen_height}+0+0')
        self.set_status('Đã phóng to cửa sổ.')

    def restore_window(self) -> None:
        self.attributes('-fullscreen', False)
        self.is_fullscreen = False
        try:
            self.state('normal')
        except Exception:
            pass
        width, height = clamp_window_size(self, 1320, 860, min_width=980, min_height=680, margin_x=60, margin_y=80)
        center_window(self, width=width, height=height)
        self.set_status('Đã khôi phục kích thước cửa sổ.')

    def toggle_maximize(self) -> None:
        if self.attributes('-fullscreen'):
            return
        try:
            if self.state() == 'zoomed':
                self.restore_window()
            else:
                self.maximize_window()
        except Exception:
            self.maximize_window()

    def toggle_fullscreen(self) -> None:
        self.is_fullscreen = not bool(self.is_fullscreen)
        self.attributes('-fullscreen', self.is_fullscreen)
        self.set_status('Đã bật toàn màn hình.' if self.is_fullscreen else 'Đã tắt toàn màn hình.')

    def _handle_escape(self, event=None):
        if self.is_fullscreen:
            self.toggle_fullscreen()
            return 'break'
        return None
    
    def create_frames(self) -> None:
        self.frames['StartFrame'] = StartFrame(self.container, self)
        self.frames['RegisterFrame'] = RegisterFrame(self.container, self)
        self.frames['LoginFrame'] = LoginFrame(self.container, self)
        self.frames['DashboardFrame'] = DashboardFrame(self.container, self)

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky='nsew')
    
    def show_frame(self, frame_name: str) -> None:
        frame = self.frames.get(frame_name)
        if frame is None:
            return
        self.current_frame_name = frame_name
        if hasattr(frame, 'on_show'):
            frame.on_show()
        if frame_name == 'DashboardFrame' and hasattr(frame, 'refresh_information'):
            frame.refresh_information()
        frame.tkraise()
        self.update_header_context()
        self.update_quick_summary()
        self.set_status(f'Đang ở màn hình: {self.page_title_var.get()}')
    
    def refresh_current_frame(self) -> None:
        current_frame = self.frames.get(self.current_frame_name)
        if current_frame is not None and hasattr(current_frame, 'refresh_information'):
            current_frame.refresh_information()
            self.set_status('Đã làm mới dữ liệu trên màn hình.')
        if current_frame is not None and hasattr(current_frame, 'on_show'):
            current_frame.on_show()
        
        self.update_quick_summary()
        self.set_status('Đã làm mới màn hình hiện tại.')

    def save_data(self) -> None:
        try:
            save_bank_data(DATA_FILE_PATH, self.bank_service.build_snapshot_data())
            self.update_quick_summary()
            self.set_status('Dữ liệu đã được lưu thành công.')
        except Exception as e:
            messagebox.showerror('Lỗi lưu dữ liệu', f'Đã xảy ra lỗi khi lưu dữ liệu:\n{str(e)}', parent=self)
            self.set_status('Lỗi: Không thể lưu dữ liệu.')
    
    def on_window_close(self) -> None:
        self.save_data()
        self.destroy()
        
def run_application() -> None:
    app = MiniBankApplication()
    app.mainloop()
