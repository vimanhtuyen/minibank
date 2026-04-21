import json
import os
from typing import Dict, Any


DEFAULT_BANK_DATA = {
    "next_account_id": 100001,
    "next_transaction_number": 1,
    "next_saving_deposit_number": 1,
    "accounts": [],
    "transactions": [],
    "saving_deposits": [],
}


def ensure_folder_exists(file_path: str) -> None:
    folder_path = os.path.dirname(file_path)
    if folder_path and not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)


def load_bank_data(file_path: str) -> Dict[str, Any]:
    """
    Đọc dữ liệu ngân hàng từ file JSON.
    - Nếu file chưa tồn tại: tạo dữ liệu mặc định.
    - Nếu file bị lỗi: đổi tên file lỗi và tạo dữ liệu mới.
    """
    if not os.path.exists(file_path):
        ensure_folder_exists(file_path)
        save_bank_data(file_path, DEFAULT_BANK_DATA)
        return dict(DEFAULT_BANK_DATA)

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        for key, value in DEFAULT_BANK_DATA.items():
            if key not in data:
                data[key] = value

        data["next_account_id"] = int(data.get("next_account_id", 100001))
        data["next_transaction_number"] = int(data.get("next_transaction_number", 1))
        data["next_saving_deposit_number"] = int(data.get("next_saving_deposit_number", 1))

        if not isinstance(data.get("accounts"), list):
            data["accounts"] = []
        if not isinstance(data.get("transactions"), list):
            data["transactions"] = []
        if not isinstance(data.get("saving_deposits"), list):
            data["saving_deposits"] = []

        return data

    except Exception:
        try:
            os.replace(file_path, file_path + ".broken")
        except Exception:
            pass

        ensure_folder_exists(file_path)
        save_bank_data(file_path, DEFAULT_BANK_DATA)
        return dict(DEFAULT_BANK_DATA)


def save_bank_data(file_path: str, data: Dict[str, Any]) -> None:
    """Ghi dữ liệu ngân hàng ra file JSON."""
    ensure_folder_exists(file_path)
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
