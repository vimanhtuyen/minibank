from typing import Optional, Tuple  
from src.storage.json_storage import load_bank_data, save_bank_data
from src.core.bank_service import BankService
from src.ui.ui_helpers import format_money_vnd, is_pin_format_valid  
import re  


DATA_FILE_PATH = "data/bank_data.json"


def parse_money_text(text: str) -> Optional[int]:  
    """Parse số tiền cho CLI.
    Cho phép nhập 100000 hoặc 100.000 hoặc 100,000 hoặc '100 000'.
    Trả về None nếu không hợp lệ.
    """  
    raw = str(text).strip()  
    if raw == "":  
        return None  
    raw = re.sub(r"[\s\.,_]", "", raw)  
    if not raw.isdigit():  
        return None  
    value = int(raw)  
    if value <= 0:  
        return None  
    return value  


def wait_for_enter() -> None:
    input("\nNhấn Enter để tiếp tục...")


def run_application() -> None:
    bank_data = load_bank_data(DATA_FILE_PATH)
    bank_service = BankService(bank_data)

    while True:
        print("\n" + "=" * 60)
        print("MINI BANK")
        print("=" * 60)
        print("1) Tạo tài khoản mới")
        print("2) Đăng nhập")
        print("3) Thoát")

        choice = input("Chọn chức năng: ").strip()

        if choice == "1":
            create_account_screen(bank_service)
            save_bank_data(DATA_FILE_PATH, bank_service.build_snapshot_data())

        elif choice == "2":
            account_id = login_screen(bank_service)
            if account_id is not None:
                session_menu(bank_service, account_id)
                save_bank_data(DATA_FILE_PATH, bank_service.build_snapshot_data())

        elif choice == "3":
            save_bank_data(DATA_FILE_PATH, bank_service.build_snapshot_data())
            print("Đã lưu dữ liệu. Tạm biệt.")
            return

        else:
            print("Lựa chọn không hợp lệ.")
            wait_for_enter()


def read_non_empty(prompt: str) -> str:  
    while True:  
        value = input(prompt).strip()  
        if value != "":  
            return value  
        print("Không được để trống. Vui lòng nhập lại.")  


def read_valid_pin(prompt: str) -> str:  
    while True:  
        pin_code = input(prompt).strip()  
        if is_pin_format_valid(pin_code):  
            return pin_code  
        print("PIN không hợp lệ. Yêu cầu 4–6 chữ số.")  


def read_optional_initial_balance(prompt: str) -> int:  
    while True:  
        text = input(prompt).strip()  
        if text == "":  
            return 0  
        raw = re.sub(r"[\s\.,_]", "", text)  
        if raw.isdigit():  
            return int(raw)  
        print("Số dư ban đầu không hợp lệ. Ví dụ hợp lệ: 0, 100000, 100.000")  


def create_account_screen(bank_service: BankService) -> None:
    print("\n--- TẠO TÀI KHOẢN ---")
    owner_name = read_non_empty("Tên chủ tài khoản: ")  
    pin_code = read_valid_pin("PIN (4–6 chữ số): ")  

    initial_balance = read_optional_initial_balance("Số dư ban đầu (VNĐ, Enter nếu 0): ")  

    ok, message, account_id = bank_service.create_account(owner_name, pin_code, initial_balance)
    print(message)

    if ok and account_id is not None:
        ok_balance, _, balance = bank_service.get_balance(account_id)
        if ok_balance and balance is not None:
            print("Số dư hiện tại:", format_money_vnd(balance))

    wait_for_enter()


def login_screen(bank_service: BankService) -> Optional[str]:
    print("\n--- ĐĂNG NHẬP ---")
    account_id = input("Số tài khoản: ").strip()
    pin_code = input("PIN: ").strip()

    ok, message = bank_service.authenticate_login(account_id, pin_code)
    print(message)

    if not ok:
        wait_for_enter()
        return None
    return account_id


def session_menu(bank_service: BankService, account_id: str) -> None:
    while True:
        account = bank_service.get_account(account_id)
        if account is None:
            print("Không tìm thấy tài khoản. Không thể là do dữ liệu bị lỗi.")
            wait_for_enter()
            return

        print("\n" + "-" * 60)
        print("TÀI KHOẢN:", account.account_id, "| CHỦ TÀI KHOẢN:", account.owner_name)
        print("SỐ DƯ:", format_money_vnd(account.balance))
        print("-" * 60)
        print("1) Nạp tiền")
        print("2) Rút tiền")
        print("3) Chuyển khoản")
        print("4) Xem số dư")
        print("5) Xem lịch sử giao dịch")
        print("6) Đăng xuất")

        choice = input("Chọn chức năng: ").strip()

        if choice == "1":
            deposit_screen(bank_service, account_id)
            save_bank_data(DATA_FILE_PATH, bank_service.build_snapshot_data())

        elif choice == "2":
            withdraw_screen(bank_service, account_id)
            save_bank_data(DATA_FILE_PATH, bank_service.build_snapshot_data())

        elif choice == "3":
            transfer_screen(bank_service, account_id)
            save_bank_data(DATA_FILE_PATH, bank_service.build_snapshot_data())

        elif choice == "4":
            ok, _, balance = bank_service.get_balance(account_id)
            if ok and balance is not None:
                print("Số dư hiện tại:", format_money_vnd(balance))
            wait_for_enter()

        elif choice == "5":
            show_history_screen(bank_service, account_id)
            wait_for_enter()

        elif choice == "6":
            print("Đã đăng xuất.")
            return

        else:
            print("Lựa chọn không hợp lệ.")
            wait_for_enter()


def deposit_screen(bank_service: BankService, account_id: str) -> None:
    print("\n--- NẠP TIỀN ---")
    amount_text = input("Số tiền nạp (VNĐ): ")  
    amount = parse_money_text(amount_text)  
    if amount is None:
        print("Số tiền không hợp lệ. Ví dụ: 50000 hoặc 50.000")
        wait_for_enter()
        return

    note = input("Ghi chú (Enter nếu bỏ qua): ").strip()
    ok, message = bank_service.deposit_money(account_id, amount, note)
    print(message)
    wait_for_enter()


def withdraw_screen(bank_service: BankService, account_id: str) -> None:
    print("\n--- RÚT TIỀN ---")
    amount_text = input("Số tiền rút (VNĐ): ")  
    amount = parse_money_text(amount_text)  
    if amount is None:
        print("Số tiền không hợp lệ. Ví dụ: 50000 hoặc 50.000")
        wait_for_enter()
        return

    note = input("Ghi chú (Enter nếu bỏ qua): ").strip()
    ok, message = bank_service.withdraw_money(account_id, amount, note)
    print(message)
    wait_for_enter()


def transfer_screen(bank_service: BankService, from_account_id: str) -> None:
    print("\n--- CHUYỂN KHOẢN ---")
    to_account_id = input("Số tài khoản nhận: ").strip()

    to_account = bank_service.get_account(to_account_id)  
    if to_account is None:  
        print("Tài khoản nhận không tồn tại.")  
        wait_for_enter()  
        return  
    print(f"Người nhận: {to_account.owner_name}")  

    amount_text = input("Số tiền chuyển (VNĐ): ")  
    amount = parse_money_text(amount_text)  
    if amount is None:
        print("Số tiền không hợp lệ. Ví dụ: 100000 hoặc 100.000")
        wait_for_enter()
        return

    note = input("Ghi chú (Enter nếu bỏ qua): ").strip()

    confirm = input(f"Xác nhận chuyển {format_money_vnd(amount)} đến {to_account_id}? (y/n): ").strip().lower()  
    if confirm not in ("y", "yes"):  
        print("Đã hủy chuyển khoản.")  
        wait_for_enter()  
        return  

    ok, message = bank_service.transfer_money(from_account_id, to_account_id, amount, note)
    print(message)
    wait_for_enter()


def show_history_screen(bank_service: BankService, account_id: str) -> None:
    print("\n--- LỊCH SỬ GIAO DỊCH (mới nhất trước) ---")
    history = bank_service.get_transaction_history(account_id)

    if len(history) == 0:
        print("Chưa có giao dịch.")
        return

    limit_text = input("Xem bao nhiêu giao dịch? (Enter = 10): ").strip()
    if limit_text == "":
        limit = 10
    elif limit_text.isdigit():
        limit = int(limit_text)
    else:
        limit = 10

    if limit < 1:
        limit = 10

    show_list = history[:limit]
    for index, transaction in enumerate(show_list, start=1):
        line = (
            f"{index:02d}) {transaction.time_text} | {transaction.transaction_id} | "
            f"{transaction.transaction_type} | {format_money_vnd(transaction.amount)}"
        )

        if transaction.transaction_type.startswith("TRANSFER"):
            line += f" | {transaction.from_account_id} -> {transaction.to_account_id}"

        if transaction.note != "":
            line += f" | Ghi chú: {transaction.note}"

        print(line)
