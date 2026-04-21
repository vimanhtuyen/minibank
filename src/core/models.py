from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


def get_current_datetime() -> datetime:
    return datetime.now()


def get_current_time_text() -> str:
    """Trả về thời gian hiện tại theo định dạng dễ đọc."""
    return get_current_datetime().strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class Account:
    """Thông tin một tài khoản ngân hàng."""
    account_id: str
    owner_name: str
    pin_code: str
    balance: int
    created_at: str

    def to_dictionary(self) -> Dict[str, Any]:
        return {
            "account_id": self.account_id,
            "owner_name": self.owner_name,
            "pin_code": self.pin_code,
            "balance": self.balance,
            "created_at": self.created_at,
        }

    @staticmethod
    def from_dictionary(data: Dict[str, Any]) -> "Account":
        return Account(
            account_id=str(data["account_id"]),
            owner_name=str(data["owner_name"]),
            pin_code=str(data["pin_code"]),
            balance=int(data.get("balance", 0)),
            created_at=str(data.get("created_at", get_current_time_text())),
        )


@dataclass
class Transaction:
    """Thông tin một giao dịch."""
    transaction_id: str
    transaction_type: str  # DEPOSIT, WITHDRAW, TRANSFER_IN, TRANSFER_OUT, SAVINGS_OPEN, SAVINGS_CLOSE
    amount: int
    time_text: str
    note: str
    from_account_id: Optional[str]
    to_account_id: Optional[str]

    def to_dictionary(self) -> Dict[str, Any]:
        return {
            "transaction_id": self.transaction_id,
            "transaction_type": self.transaction_type,
            "amount": self.amount,
            "time_text": self.time_text,
            "note": self.note,
            "from_account_id": self.from_account_id,
            "to_account_id": self.to_account_id,
        }

    @staticmethod
    def from_dictionary(data: Dict[str, Any]) -> "Transaction":
        return Transaction(
            transaction_id=str(data["transaction_id"]),
            transaction_type=str(data["transaction_type"]),
            amount=int(data["amount"]),
            time_text=str(data.get("time_text", get_current_time_text())),
            note=str(data.get("note", "")),
            from_account_id=data.get("from_account_id"),
            to_account_id=data.get("to_account_id"),
        )


@dataclass
class SavingDeposit:
    """Thông tin một sổ tiết kiệm."""
    deposit_id: str
    account_id: str
    principal_amount: int
    annual_interest_rate: float
    term_months: int
    opened_at: str
    maturity_at: str
    status: str
    note: str
    settled_at: Optional[str] = None
    interest_earned: int = 0
    maturity_amount: int = 0

    def to_dictionary(self) -> Dict[str, Any]:
        return {
            "deposit_id": self.deposit_id,
            "account_id": self.account_id,
            "principal_amount": self.principal_amount,
            "annual_interest_rate": self.annual_interest_rate,
            "term_months": self.term_months,
            "opened_at": self.opened_at,
            "maturity_at": self.maturity_at,
            "status": self.status,
            "note": self.note,
            "settled_at": self.settled_at,
            "interest_earned": self.interest_earned,
            "maturity_amount": self.maturity_amount,
        }

    @staticmethod
    def from_dictionary(data: Dict[str, Any]) -> "SavingDeposit":
        principal_amount = int(data.get("principal_amount", 0))
        annual_interest_rate = float(data.get("annual_interest_rate", 0.0))
        term_months = int(data.get("term_months", 0))
        interest_earned = int(data.get("interest_earned", 0))
        maturity_amount = int(data.get("maturity_amount", principal_amount + interest_earned))
        return SavingDeposit(
            deposit_id=str(data["deposit_id"]),
            account_id=str(data["account_id"]),
            principal_amount=principal_amount,
            annual_interest_rate=annual_interest_rate,
            term_months=term_months,
            opened_at=str(data.get("opened_at", get_current_time_text())),
            maturity_at=str(data.get("maturity_at", get_current_time_text())),
            status=str(data.get("status", "ACTIVE")),
            note=str(data.get("note", "")),
            settled_at=data.get("settled_at"),
            interest_earned=interest_earned,
            maturity_amount=maturity_amount,
        )
