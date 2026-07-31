"""
server_beta.py — Real-time Financial Budget Dashboard Server for Beta Solutions
================================================================================
• Đọc dữ liệu từ file sample-data/ngan_sach_phong_ban.xlsx (500 bản ghi).
• Đọc qua file tạm thời (tempfile copy) để không bị khóa khi file mở trong Excel.
• Cung cấp API /api/data hỗ trợ lọc thời gian thực & làm mới tự động mỗi 2s.
• Chạy server HTTP tại port 9091 và mở tự động trên trình duyệt.
"""

import json
import os
import sys
import time
import socket
import shutil
import tempfile
import threading
import webbrowser
import logging
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 9091
BASE_DIR = Path(__file__).resolve().parent
EXCEL_PATH = BASE_DIR / "sample-data" / "ngan_sach_phong_ban.xlsx"
HTML_PATH = BASE_DIR / "dashboard_beta.html"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("BetaServer")

_data_lock = threading.Lock()
_live_cache = {}
_last_mtime = 0.0

def parse_excel(path: Path) -> dict:
    if not path.exists():
        log.warning(f"File not found: {path}")
        return {"records": [], "summary": {}}

    try:
        import openpyxl
    except ImportError:
        log.error("Missing openpyxl. Install via pip install openpyxl")
        return {"records": [], "summary": {}}

    # Safe read via temp file copy
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        tmp_path = Path(tmp.name)
    try:
        shutil.copy2(path, tmp_path)
        wb = openpyxl.load_workbook(tmp_path, read_only=True, data_only=True)
    finally:
        try:
            tmp_path.unlink(missing_ok=True)
        except Exception:
            pass

    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()

    if not rows or len(rows) <= 1:
        return {"records": [], "summary": {}}

    headers = [str(cell).strip() if cell is not None else "" for cell in rows[0]]
    
    # Map header names
    idx_map = {}
    for i, h in enumerate(headers):
        h_lower = h.lower()
        if "mã" in h_lower: idx_map["ma_gd"] = i
        elif "ngày" in h_lower: idx_map["ngay"] = i
        elif "quý" in h_lower: idx_map["quy"] = i
        elif "tháng" in h_lower: idx_map["thang"] = i
        elif "phòng" in h_lower: idx_map["phong_ban"] = i
        elif "hạng" in h_lower: idx_map["hang_muc"] = i
        elif "ngân sách" in h_lower: idx_map["ngan_sach"] = i
        elif "thực chi" in h_lower: idx_map["thuc_chi"] = i
        elif "chênh" in h_lower: idx_map["chenh_lech"] = i
        elif "trạng" in h_lower: idx_map["trang_thai"] = i
        elif "người" in h_lower: idx_map["nguoi_duyet"] = i

    records = []
    total_budget = 0.0
    total_expense = 0.0
    overrun_count = 0
    overrun_total = 0.0

    for r in rows[1:]:
        if not r or r[0] is None:
            continue
        
        def get_val(key, default=""):
            idx = idx_map.get(key)
            if idx is not None and idx < len(r) and r[idx] is not None:
                return r[idx]
            return default

        try:
            budget = float(get_val("ngan_sach", 0))
            expense = float(get_val("thuc_chi", 0))
        except (ValueError, TypeError):
            budget = 0.0
            expense = 0.0

        chenh_lech = expense - budget
        is_overrun = expense > budget

        total_budget += budget
        total_expense += expense
        if is_overrun:
            overrun_count += 1
            overrun_total += chenh_lech

        rec = {
            "ma_gd": str(get_val("ma_gd")),
            "ngay": str(get_val("ngay")),
            "quy": str(get_val("quy")),
            "thang": str(get_val("thang")),
            "phong_ban": str(get_val("phong_ban")),
            "hang_muc": str(get_val("hang_muc")),
            "ngan_sach": budget,
            "thuc_chi": expense,
            "chenh_lech": chenh_lech,
            "trang_thai": "Vượt ngân sách" if is_overrun else "Trong ngân sách",
            "nguoi_duyet": str(get_val("nguoi_duyet"))
        }
        records.append(rec)

    return {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "mtime": path.stat().st_mtime if path.exists() else 0,
        "summary": {
            "total_budget": total_budget,
            "total_expense": total_expense,
            "overrun_count": overrun_count,
            "overrun_total": overrun_total,
            "total_records": len(records)
        },
        "records": records
    }

def bg_excel_watcher():
    global _live_cache, _last_mtime
    log.info(f"Starting Excel file watcher for: {EXCEL_PATH}")
    while True:
        try:
            if EXCEL_PATH.exists():
                curr_mtime = EXCEL_PATH.stat().st_mtime
                if curr_mtime != _last_mtime or not _live_cache:
                    log.info("Excel change detected, reloading dataset...")
                    parsed = parse_excel(EXCEL_PATH)
                    with _data_lock:
                        _live_cache = parsed
                        _last_mtime = curr_mtime
                    log.info(f"Loaded {len(parsed.get('records', []))} records successfully.")
        except Exception as e:
            log.error(f"Error reading Excel: {e}")
        time.sleep(2.0)

class BetaHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silence default HTTP access logs for clean stdout
        pass

    def do_GET(self):
        path_str = self.path.split("?")[0]

        if path_str == "/api/data":
            with _data_lock:
                payload = json.dumps(_live_cache, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            self.wfile.write(payload)
            return

        # Serve static file (HTML, CSS, JS)
        if path_str == "/" or path_str == "/dashboard_beta.html":
            target_path = HTML_PATH
        else:
            target_path = BASE_DIR / path_str.lstrip("/")

        if target_path.exists() and target_path.is_file():
            content_type = "text/html; charset=utf-8"
            if target_path.suffix == ".css": content_type = "text/css"
            elif target_path.suffix == ".js": content_type = "application/javascript"
            elif target_path.suffix == ".json": content_type = "application/json"

            with open(target_path, "rb") as f:
                content = f.read()

            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"404 Not Found")

def run_server():
    # Initial load
    global _live_cache, _last_mtime
    _live_cache = parse_excel(EXCEL_PATH)
    if EXCEL_PATH.exists():
        _last_mtime = EXCEL_PATH.stat().st_mtime

    # Start watcher thread
    watcher_thread = threading.Thread(target=bg_excel_watcher, daemon=True)
    watcher_thread.start()

    server_address = ("0.0.0.0", PORT)
    httpd = HTTPServer(server_address, BetaHTTPHandler)
    url = f"http://localhost:{PORT}/dashboard_beta.html"
    log.info(f"==================================================")
    log.info(f"BETA SOLUTIONS BUDGET DASHBOARD SERVER IS READY!")
    log.info(f"Server URL: {url}")
    log.info(f"==================================================")

    # Auto open browser after 1 second
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        log.info("Server stopped by user.")

if __name__ == "__main__":
    run_server()
