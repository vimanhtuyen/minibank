from calendar import monthrange
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

from src.core.models import Account, SavingDeposit, Transaction, get_current_datetime, get_current_time_text


class BankService:
    """
    Lớp xử lý nghiệp vụ Mini Bank:
    - Tạo tài khoản
    - Xác thực đăng nhập
    - Nạp / Rút / Chuyển khoản
    - Gửi tiết kiệm theo lãi suất
    - Lấy số dư và lịch sử giao dịch
    """

    def __init__(self, bank_data: Dict[str, Any]):
        self.bank_data = bank_data

        self.accounts_by_id: Dict[str, Account] = {}
        self.transaction_list: List[Transaction] = []
        self.saving_deposits: List[SavingDeposit] = []

        for account_dict in self.bank_data.get("accounts", []):
            account = Account.from_dictionary(account_dict)
            self.accounts_by_id[account.account_id] = account

        for transaction_dict in self.bank_data.get("transactions", []):
            transaction = Transaction.from_dictionary(transaction_dict)
            self.transaction_list.append(transaction)

        for saving_dict in self.bank_data.get("saving_deposits", []):
            saving_deposit = SavingDeposit.from_dictionary(saving_dict)
            self.saving_deposits.append(saving_deposit)

    # -------------------------
    # Các hàm kiểm tra dữ liệu
    # -------------------------
    def is_pin_code_valid(self, pin_code: str) -> bool:
        if not pin_code.isdigit():
            return False
        if len(pin_code) < 4 or len(pin_code) > 6:
            return False
        return True

    def is_amount_valid(self, amount: int) -> bool:
        if not isinstance(amount, int):
            return False
        if amount <= 0:
            return False
        return True

    def is_interest_rate_valid(self, annual_interest_rate: float) -> bool:
        try:
            rate = float(annual_interest_rate)
        except Exception:
            return False
        return 0 < rate <= 100

    def is_term_months_valid(self, term_months: int) -> bool:
        return isinstance(term_months, int) and term_months > 0

    # -------------------------
    # Hàm tiện ích cho tiết kiệm
    # -------------------------
    def parse_time_text(self, time_text: str) -> datetime:
        return datetime.strptime(str(time_text), "%Y-%m-%d %H:%M:%S")

    def add_months(self, time_text: str, months: int) -> str:
        base_time = self.parse_time_text(time_text)
        total_month = base_time.month - 1 + int(months)
        target_year = base_time.year + total_month // 12
        target_month = total_month % 12 + 1
        target_day = min(base_time.day, monthrange(target_year, target_month)[1])
        target_time = base_time.replace(year=target_year, month=target_month, day=target_day)
        return target_time.strftime("%Y-%m-%d %H:%M:%S")

    def calculate_saving_interest(self, principal_amount: int, annual_interest_rate: float, term_months: int) -> int:
        interest_value = int(round(int(principal_amount) * float(annual_interest_rate) * int(term_months) / 1200))
        return max(interest_value, 0)

    def is_saving_matured(self, saving_deposit: SavingDeposit) -> bool:
        return get_current_datetime() >= self.parse_time_text(saving_deposit.maturity_at)

    def get_saving_settlement_preview(self, saving_deposit: SavingDeposit) -> Dict[str, Any]:
        if self.is_saving_matured(saving_deposit):
            interest_earned = int(saving_deposit.interest_earned)
            payout_amount = int(saving_deposit.maturity_amount)
            return {
                "is_matured": True,
                "interest_earned": interest_earned,
                "payout_amount": payout_amount,
                "settlement_type": "ON_TIME",
                "message": "Sổ đã đến hạn, sẽ nhận cả gốc và lãi.",
            }
        return {
            "is_matured": False,
            "interest_earned": 0,
            "payout_amount": int(saving_deposit.principal_amount),
            "settlement_type": "EARLY",
            "message": "Sổ chưa đến hạn, tất toán trước hạn chỉ nhận lại tiền gốc.",
        }

    # -------------------------
    # Tạo ID
    # -------------------------
    def create_new_account_id(self) -> str:
        new_id = str(int(self.bank_data["next_account_id"]))
        self.bank_data["next_account_id"] = int(self.bank_data["next_account_id"]) + 1
        return new_id

    def create_new_transaction_id(self) -> str:
        number = int(self.bank_data["next_transaction_number"])
        self.bank_data["next_transaction_number"] = number + 1
        return f"TRANSACTION_{number:08d}"

    def create_new_saving_deposit_id(self) -> str:
        number = int(self.bank_data["next_saving_deposit_number"])
        self.bank_data["next_saving_deposit_number"] = number + 1
        return f"STK_{number:06d}"

    # -------------------------
    # Đồng bộ dữ liệu để lưu file
    # -------------------------
    def build_snapshot_data(self) -> Dict[str, Any]:
        self.bank_data["accounts"] = [account.to_dictionary() for account in self.accounts_by_id.values()]
        self.bank_data["transactions"] = [transaction.to_dictionary() for transaction in self.transaction_list]
        self.bank_data["saving_deposits"] = [saving.to_dictionary() for saving in self.saving_deposits]
        return self.bank_data

    # -------------------------
    # API chính
    # -------------------------
    def create_account(self, owner_name: str, pin_code: str, initial_balance: int) -> Tuple[bool, str, Optional[str]]:
        owner_name = owner_name.strip()

        if owner_name == "":
            return False, "Tên chủ tài khoản không được để trống.", None

        if not self.is_pin_code_valid(pin_code):
            return False, "PIN không hợp lệ. PIN phải gồm 4 đến 6 chữ số.", None

        if initial_balance < 0:
            return False, "Số dư ban đầu không được âm.", None

        account_id = self.create_new_account_id()
        new_account = Account(
            account_id=account_id,
            owner_name=owner_name,
            pin_code=pin_code,
            balance=int(initial_balance),
            created_at=get_current_time_text(),
        )
        self.accounts_by_id[account_id] = new_account

        if initial_balance > 0:
            self.add_transaction(
                transaction_type="DEPOSIT",
                amount=int(initial_balance),
                note="Nạp tiền ban đầu",
                from_account_id=None,
                to_account_id=account_id,
            )

        return True, f"Tạo tài khoản thành công. Số tài khoản: {account_id}", account_id

    def authenticate_login(self, account_id: str, pin_code: str) -> Tuple[bool, str]:
        account = self.accounts_by_id.get(str(account_id))
        if account is None:
            return False, "Không tồn tại số tài khoản."
        if account.pin_code != str(pin_code):
            return False, "PIN không đúng."
        return True, "Đăng nhập thành công."

    def get_account(self, account_id: str) -> Optional[Account]:
        return self.accounts_by_id.get(str(account_id))

    def get_balance(self, account_id: str) -> Tuple[bool, str, Optional[int]]:
        account = self.get_account(account_id)
        if account is None:
            return False, "Không tồn tại số tài khoản.", None
        return True, "OK", account.balance

    def add_transaction(
        self,
        transaction_type: str,
        amount: int,
        note: str,
        from_account_id: Optional[str],
        to_account_id: Optional[str],
    ) -> None:
        transaction = Transaction(
            transaction_id=self.create_new_transaction_id(),
            transaction_type=transaction_type,
            amount=int(amount),
            time_text=get_current_time_text(),
            note=note.strip(),
            from_account_id=from_account_id,
            to_account_id=to_account_id,
        )
        self.transaction_list.append(transaction)

    def deposit_money(self, account_id: str, amount: int, note: str) -> Tuple[bool, str]:
        account = self.get_account(account_id)
        if account is None:
            return False, "Không tồn tại số tài khoản."

        if not self.is_amount_valid(amount):
            return False, "Số tiền nạp phải là số nguyên dương."

        account.balance = account.balance + int(amount)

        self.add_transaction(
            transaction_type="DEPOSIT",
            amount=int(amount),
            note=note,
            from_account_id=None,
            to_account_id=account.account_id,
        )
        return True, "Nạp tiền thành công."

    def withdraw_money(self, account_id: str, amount: int, note: str) -> Tuple[bool, str]:
        account = self.get_account(account_id)
        if account is None:
            return False, "Không tồn tại số tài khoản."

        if not self.is_amount_valid(amount):
            return False, "Số tiền rút phải là số nguyên dương."

        if int(amount) > account.balance:
            return False, "Không đủ số dư để rút."

        account.balance = account.balance - int(amount)

        self.add_transaction(
            transaction_type="WITHDRAW",
            amount=int(amount),
            note=note,
            from_account_id=account.account_id,
            to_account_id=None,
        )
        return True, "Rút tiền thành công."

    def transfer_money(self, from_account_id: str, to_account_id: str, amount: int, note: str) -> Tuple[bool, str]:
        from_account = self.get_account(from_account_id)
        if from_account is None:
            return False, "Tài khoản chuyển không tồn tại."

        to_account = self.get_account(to_account_id)
        if to_account is None:
            return False, "Tài khoản nhận không tồn tại."

        if str(from_account_id) == str(to_account_id):
            return False, "Không thể chuyển khoản cho chính mình."

        if not self.is_amount_valid(amount):
            return False, "Số tiền chuyển phải là số nguyên dương."

        if int(amount) > from_account.balance:
            return False, "Không đủ số dư để chuyển."

        money = int(amount)
        from_account.balance = from_account.balance - money
        to_account.balance = to_account.balance + money

        self.add_transaction(
            transaction_type="TRANSFER_OUT",
            amount=money,
            note=note,
            from_account_id=from_account.account_id,
            to_account_id=to_account.account_id,
        )
        self.add_transaction(
            transaction_type="TRANSFER_IN",
            amount=money,
            note=note,
            from_account_id=from_account.account_id,
            to_account_id=to_account.account_id,
        )

        return True, "Chuyển khoản thành công."

    def create_saving_deposit(
        self,
        account_id: str,
        principal_amount: int,
        annual_interest_rate: float,
        term_months: int,
        note: str,
    ) -> Tuple[bool, str, Optional[str]]:
        account = self.get_account(account_id)
        if account is None:
            return False, "Không tồn tại số tài khoản.", None

        if not self.is_amount_valid(principal_amount):
            return False, "Số tiền gửi tiết kiệm phải là số nguyên dương.", None

        if not self.is_interest_rate_valid(annual_interest_rate):
            return False, "Lãi suất phải lớn hơn 0 và không vượt quá 100%/năm.", None

        if not self.is_term_months_valid(term_months):
            return False, "Kỳ hạn phải là số nguyên dương theo tháng.", None

        if int(principal_amount) > account.balance:
            return False, "Không đủ số dư để mở sổ tiết kiệm.", None

        opened_at = get_current_time_text()
        maturity_at = self.add_months(opened_at, int(term_months))
        interest_earned = self.calculate_saving_interest(principal_amount, annual_interest_rate, term_months)
        maturity_amount = int(principal_amount) + int(interest_earned)
        deposit_id = self.create_new_saving_deposit_id()

        account.balance = int(account.balance) - int(principal_amount)

        saving_deposit = SavingDeposit(
            deposit_id=deposit_id,
            account_id=str(account_id),
            principal_amount=int(principal_amount),
            annual_interest_rate=float(annual_interest_rate),
            term_months=int(term_months),
            opened_at=opened_at,
            maturity_at=maturity_at,
            status="ACTIVE",
            note=note.strip(),
            settled_at=None,
            interest_earned=int(interest_earned),
            maturity_amount=int(maturity_amount),
        )
        self.saving_deposits.append(saving_deposit)

        open_note = note.strip()
        if open_note == "":
            open_note = f"Mở sổ {deposit_id} | {term_months} tháng | {annual_interest_rate:.2f}%/năm"
        else:
            open_note = f"{open_note} | {deposit_id} | {term_months} tháng | {annual_interest_rate:.2f}%/năm"

        self.add_transaction(
            transaction_type="SAVINGS_OPEN",
            amount=int(principal_amount),
            note=open_note,
            from_account_id=account.account_id,
            to_account_id=None,
        )
        return True, f"Mở sổ tiết kiệm thành công: {deposit_id}", deposit_id

    def get_saving_deposit(self, account_id: str, deposit_id: str) -> Optional[SavingDeposit]:
        for saving_deposit in self.saving_deposits:
            if saving_deposit.account_id == str(account_id) and saving_deposit.deposit_id == str(deposit_id):
                return saving_deposit
        return None

    def get_saving_deposits(self, account_id: str, only_active: bool = False) -> List[SavingDeposit]:
        result = []
        for saving_deposit in self.saving_deposits:
            if saving_deposit.account_id != str(account_id):
                continue
            if only_active and str(saving_deposit.status).upper() != "ACTIVE":
                continue
            result.append(saving_deposit)
        result.sort(key=lambda item: item.opened_at, reverse=True)
        return result

    def settle_saving_deposit(self, account_id: str, deposit_id: str) -> Tuple[bool, str]:
        account = self.get_account(account_id)
        if account is None:
            return False, "Không tồn tại số tài khoản."

        saving_deposit = self.get_saving_deposit(account_id, deposit_id)
        if saving_deposit is None:
            return False, "Không tìm thấy sổ tiết kiệm."

        if str(saving_deposit.status).upper() != "ACTIVE":
            return False, "Sổ tiết kiệm này đã được tất toán trước đó."

        preview = self.get_saving_settlement_preview(saving_deposit)
        payout_amount = int(preview["payout_amount"])
        interest_earned = int(preview["interest_earned"])
        settlement_type = str(preview["settlement_type"])

        account.balance = int(account.balance) + payout_amount
        saving_deposit.status = "CLOSED"
        saving_deposit.settled_at = get_current_time_text()
        saving_deposit.interest_earned = interest_earned
        saving_deposit.maturity_amount = payout_amount

        if settlement_type == "ON_TIME":
            note = (
                f"Tất toán {saving_deposit.deposit_id} đúng hạn | "
                f"gốc {saving_deposit.principal_amount} | lãi {interest_earned}"
            )
        else:
            note = f"Tất toán {saving_deposit.deposit_id} trước hạn | chỉ nhận lại tiền gốc"

        self.add_transaction(
            transaction_type="SAVINGS_CLOSE",
            amount=payout_amount,
            note=note,
            from_account_id=None,
            to_account_id=account.account_id,
        )

        if settlement_type == "ON_TIME":
            return True, "Tất toán sổ tiết kiệm thành công. Bạn đã nhận cả gốc và lãi."
        return True, "Tất toán trước hạn thành công. Bạn chỉ nhận lại tiền gốc."

    def get_savings_summary(self, account_id: str) -> Dict[str, int]:
        active_deposits = self.get_saving_deposits(account_id, only_active=True)
        total_principal = sum(int(item.principal_amount) for item in active_deposits)
        total_interest = sum(int(item.interest_earned) for item in active_deposits)
        total_maturity = sum(int(item.maturity_amount) for item in active_deposits)
        return {
            "active_count": len(active_deposits),
            "total_principal": total_principal,
            "total_interest": total_interest,
            "total_maturity": total_maturity,
        }

    def get_transaction_history(self, account_id: str) -> List[Transaction]:
        account_id_text = str(account_id)
        history: List[Transaction] = []

        for transaction in self.transaction_list:
            if transaction.from_account_id == account_id_text or transaction.to_account_id == account_id_text:
                history.append(transaction)

        history.sort(key=lambda item: item.time_text, reverse=True)
        return history
