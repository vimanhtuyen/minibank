from pathlib import Path
from functools import wraps
import os

from flask import Flask, flash, redirect, render_template, request, session, url_for

from src.storage.json_storage import load_bank_data, save_bank_data
from src.core.bank_service import BankService
from web_helpers import (
    format_interest_rate,
    format_money_vnd,
    is_pin_format_valid,
    parse_money_amount,
    transaction_type_display,
)

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE_PATH = str(BASE_DIR / "data" / "bank_data.json")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-change-me-on-pythonanywhere")


def build_bank_service() -> BankService:
    bank_data = load_bank_data(DATA_FILE_PATH)
    return BankService(bank_data)


def persist(bank_service: BankService) -> None:
    save_bank_data(DATA_FILE_PATH, bank_service.build_snapshot_data())


def current_account(bank_service: BankService):
    account_id = session.get("account_id")
    if not account_id:
        return None
    return bank_service.get_account(account_id)


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("account_id"):
            flash("Bạn cần đăng nhập trước.", "error")
            return redirect(url_for("home"))
        return view_func(*args, **kwargs)
    return wrapper


@app.context_processor
def inject_globals():
    return {
        "format_money_vnd": format_money_vnd,
        "format_interest_rate": format_interest_rate,
        "transaction_type_display": transaction_type_display,
    }


@app.get("/")
def home():
    bank_service = build_bank_service()
    account = current_account(bank_service)
    if account:
        return redirect(url_for("dashboard"))
    stats = {
        "account_count": len(bank_service.accounts_by_id),
        "transaction_count": len(bank_service.transaction_list),
        "saving_count": len(bank_service.saving_deposits),
    }
    return render_template("home.html", stats=stats)


@app.post("/register")
def register():
    bank_service = build_bank_service()
    owner_name = request.form.get("owner_name", "").strip()
    pin_code = request.form.get("pin_code", "").strip()
    initial_balance_text = request.form.get("initial_balance", "").strip()

    if not owner_name:
        flash("Tên chủ tài khoản không được để trống.", "error")
        return redirect(url_for("home"))

    if not is_pin_format_valid(pin_code):
        flash("PIN phải gồm 4 đến 6 chữ số.", "error")
        return redirect(url_for("home"))

    if initial_balance_text == "":
        initial_balance = 0
    else:
        raw = initial_balance_text.replace(" ", "").replace(".", "").replace(",", "")
        if not raw.isdigit():
            flash("Số dư ban đầu không hợp lệ.", "error")
            return redirect(url_for("home"))
        initial_balance = int(raw)

    ok, message, account_id = bank_service.create_account(owner_name, pin_code, initial_balance)
    if ok and account_id:
        persist(bank_service)
        flash(f"{message}. Mời bạn đăng nhập.", "success")
    else:
        flash(message, "error")
    return redirect(url_for("home"))


@app.post("/login")
def login():
    bank_service = build_bank_service()
    account_id = request.form.get("account_id", "").strip()
    pin_code = request.form.get("pin_code", "").strip()
    ok, message = bank_service.authenticate_login(account_id, pin_code)
    if ok:
        session["account_id"] = account_id
        flash(message, "success")
        return redirect(url_for("dashboard"))
    flash(message, "error")
    return redirect(url_for("home"))


@app.post("/logout")
@login_required
def logout():
    session.clear()
    flash("Đã đăng xuất.", "success")
    return redirect(url_for("home"))


@app.get("/dashboard")
@login_required
def dashboard():
    bank_service = build_bank_service()
    account = current_account(bank_service)
    if account is None:
        session.clear()
        flash("Phiên đăng nhập không còn hợp lệ.", "error")
        return redirect(url_for("home"))
    transactions = bank_service.get_transaction_history(account.account_id)
    savings = bank_service.get_saving_deposits(account.account_id)
    savings_summary = bank_service.get_savings_summary(account.account_id)
    return render_template(
        "dashboard.html",
        account=account,
        transactions=transactions,
        savings=savings,
        savings_summary=savings_summary,
    )


@app.post("/deposit")
@login_required
def deposit():
    bank_service = build_bank_service()
    account_id = session["account_id"]
    amount = parse_money_amount(request.form.get("amount", ""))
    note = request.form.get("note", "").strip()
    ok, message = bank_service.deposit_money(account_id, amount, note)
    if ok:
        persist(bank_service)
        flash(message, "success")
    else:
        flash(message, "error")
    return redirect(url_for("dashboard"))


@app.post("/withdraw")
@login_required
def withdraw():
    bank_service = build_bank_service()
    account_id = session["account_id"]
    amount = parse_money_amount(request.form.get("amount", ""))
    note = request.form.get("note", "").strip()
    ok, message = bank_service.withdraw_money(account_id, amount, note)
    if ok:
        persist(bank_service)
        flash(message, "success")
    else:
        flash(message, "error")
    return redirect(url_for("dashboard"))


@app.post("/transfer")
@login_required
def transfer():
    bank_service = build_bank_service()
    from_account_id = session["account_id"]
    to_account_id = request.form.get("to_account_id", "").strip()
    amount = parse_money_amount(request.form.get("amount", ""))
    note = request.form.get("note", "").strip()
    ok, message = bank_service.transfer_money(from_account_id, to_account_id, amount, note)
    if ok:
        persist(bank_service)
        flash(message, "success")
    else:
        flash(message, "error")
    return redirect(url_for("dashboard"))


@app.post("/savings/open")
@login_required
def open_savings():
    bank_service = build_bank_service()
    account_id = session["account_id"]
    principal_amount = parse_money_amount(request.form.get("principal_amount", ""))
    note = request.form.get("note", "").strip()
    try:
        annual_interest_rate = float(request.form.get("annual_interest_rate", "0").strip())
    except Exception:
        annual_interest_rate = -1
    try:
        term_months = int(request.form.get("term_months", "0").strip())
    except Exception:
        term_months = -1

    ok, message, _ = bank_service.create_saving_deposit(
        account_id,
        principal_amount,
        annual_interest_rate,
        term_months,
        note,
    )
    if ok:
        persist(bank_service)
        flash(message, "success")
    else:
        flash(message, "error")
    return redirect(url_for("dashboard"))


@app.post("/savings/<deposit_id>/settle")
@login_required
def settle_savings(deposit_id: str):
    bank_service = build_bank_service()
    account_id = session["account_id"]
    ok, message = bank_service.settle_saving_deposit(account_id, deposit_id)
    if ok:
        persist(bank_service)
        flash(message, "success")
    else:
        flash(message, "error")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
