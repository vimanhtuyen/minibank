# Mini Bank Web - Deploy lên PythonAnywhere

## 1) Tạo virtualenv và cài package
```bash
cd ~/mini_bank_web
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2) Chạy thử local trong Bash console
```bash
export SECRET_KEY='doi-secret-key-nay'
python app.py
```

## 3) Tạo web app trên PythonAnywhere
- Vào **Web**
- Chọn **Add a new web app**
- Chọn **Manual configuration**
- Chọn Python **3.10** hoặc phiên bản bạn đang dùng trên tài khoản

## 4) Sửa file WSGI
Mở file WSGI mà PythonAnywhere tạo sẵn và thay bằng:

```python
import sys
path = '/home/yourusername/mini_bank_web'
if path not in sys.path:
    sys.path.insert(0, path)

from app import app as application
```

## 5) Khai báo virtualenv
Tại tab **Web**, mục **Virtualenv**:
```text
/home/yourusername/mini_bank_web/.venv
```

## 6) Static files
Tạo mapping:
- URL: `/static/`
- Directory: `/home/yourusername/mini_bank_web/static/`

## 7) Environment variable
Trong file WSGI, thêm trước dòng import app:

```python
import os
os.environ['SECRET_KEY'] = 'doi-secret-key-that-kho-doan'
```

## 8) Reload
Bấm **Reload** trên tab Web.

## Ghi chú
- File dữ liệu đang lưu ở `data/bank_data.json`
- Vì đang dùng JSON file chung, đây phù hợp demo/học tập, chưa phù hợp production nhiều người dùng cùng lúc.
- Nếu muốn bản tốt hơn, nên đổi sang SQLite.
