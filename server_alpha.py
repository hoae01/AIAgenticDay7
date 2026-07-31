"""
server_alpha.py — Dashboard Server cho Công Ty TNHH Alpha
=========================================================
• Đọc dữ liệu CHÍNH XÁC từ file DEMO_sales_data.xlsx.
• Theo dõi mtime của file Excel mỗi 2 giây:
  - Nếu bạn SỬA HOẶC LƯU FILE EXCEL -> Server lập tức nạp lại dữ liệu mới và cập nhật lên Dashboard.
  - Nếu KHÔNG thay đổi file Excel -> Dữ liệu giữ nguyên chuẩn xác từ file Excel (không phát sinh dữ liệu giả).
• Dual-Stack IPv4/IPv6 tại port 9090.
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
from collections import defaultdict
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

# ──────────────────────────────────────────────
# CẤU HÌNH
# ──────────────────────────────────────────────
PORT         = 9090
POLL_SEC     = 2
BASE_DIR     = Path(__file__).resolve().parent
EXCEL_PATH   = BASE_DIR / "sample-data" / "DEMO_sales_data.xlsx"
HTML_PATH    = BASE_DIR / "dashboard_alpha.html"
OPEN_DELAY   = 1.0

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("AlphaServer")

# ──────────────────────────────────────────────
# GLOBAL STATE
# ──────────────────────────────────────────────
_data_lock   = threading.Lock()
_live_data   = {}
_last_mtime  = 0.0

TRIEU = 1_000_000

# ──────────────────────────────────────────────
# PARSE EXCEL
# ──────────────────────────────────────────────
def parse_excel(path: Path) -> dict:
    """Đọc và tổng hợp chính xác dữ liệu từ file Excel."""
    try:
        import openpyxl
    except ImportError:
        log.error("Thiếu thư viện openpyxl. Hãy chạy: pip install openpyxl")
        sys.exit(1)

    # Đọc thông qua file tạm để tránh bị khóa khi đang mở file trong Microsoft Excel
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

    if not rows:
        return {}

    data = rows[1:]

    IDX_THANG    = 2
    IDX_KHU_VUC  = 4
    IDX_DANH_MUC = 8
    IDX_DT       = 13
    IDX_CP       = 18
    IDX_LN       = 19

    total_dt = total_cp = total_ln = 0.0
    total_don_hang = len(data)

    month_dt = defaultdict(float)
    month_cp = defaultdict(float)
    month_ln = defaultdict(float)

    cat_dt = defaultdict(float)
    cat_cp = defaultdict(float)
    cat_ln = defaultdict(float)

    region_dt = defaultdict(float)

    for row in data:
        dt = float(row[IDX_DT] or 0)
        cp = float(row[IDX_CP] or 0)
        ln = float(row[IDX_LN] or 0)
        thang    = str(row[IDX_THANG] or "")
        khu_vuc  = str(row[IDX_KHU_VUC] or "")
        danh_muc = str(row[IDX_DANH_MUC] or "")

        total_dt += dt
        total_cp += cp
        total_ln += ln

        if thang:
            month_dt[thang] += dt
            month_cp[thang] += cp
            month_ln[thang] += ln

        if danh_muc:
            cat_dt[danh_muc] += dt
            cat_cp[danh_muc] += cp
            cat_ln[danh_muc] += ln

        if khu_vuc:
            region_dt[khu_vuc] += dt

    sorted_months = sorted(month_dt.keys())
    labels_months = ["T" + str(int(m.split("-")[1])) if "-" in m else m for m in sorted_months]

    cat_alias = {
        "Thuc Pham":  "Thực Phẩm",
        "Thoi Trang": "Thời Trang",
        "Dien Tu":    "Điện Tử",
        "Gia Dung":   "Gia Dụng",
    }
    sorted_cats = sorted(cat_dt.keys(), key=lambda k: -cat_dt[k])
    cat_labels  = [cat_alias.get(c, c) for c in sorted_cats]
    cat_rev     = [round(cat_dt[c]  / TRIEU) for c in sorted_cats]
    cat_cost    = [round(cat_cp[c]  / TRIEU) for c in sorted_cats]
    cat_profit  = [round(cat_ln[c]  / TRIEU) for c in sorted_cats]

    region_alias = {
        "Mien Nam":   "Miền Nam",
        "Mien Trung": "Miền Trung",
        "Mien Bac":   "Miền Bắc",
    }
    sorted_regions = sorted(region_dt.keys(), key=lambda k: -region_dt[k])
    reg_labels = [region_alias.get(r, r) for r in sorted_regions]
    reg_rev    = [round(region_dt[r] / TRIEU) for r in sorted_regions]

    return {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "kpi": {
            "doanh_thu": round(total_dt / TRIEU),
            "chi_phi":   round(total_cp / TRIEU),
            "loi_nhuan": round(total_ln / TRIEU),
            "don_hang":  total_don_hang,
        },
        "monthly": {
            "labels":    labels_months,
            "doanh_thu": [round(month_dt[m] / TRIEU) for m in sorted_months],
            "chi_phi":   [round(month_cp[m] / TRIEU) for m in sorted_months],
            "loi_nhuan": [round(month_ln[m] / TRIEU) for m in sorted_months],
        },
        "categories": {
            "labels":  cat_labels,
            "revenue": cat_rev,
            "cost":    cat_cost,
            "profit":  cat_profit,
        },
        "regions": {
            "labels":  reg_labels,
            "revenue": reg_rev,
        },
    }

# ──────────────────────────────────────────────
# POLLING FILE EXCEL REAL-TIME
# ──────────────────────────────────────────────
def polling_loop():
    global _live_data, _last_mtime
    log.info(f"Vòng lặp giám sát file Excel đang chạy (mỗi {POLL_SEC}s)...")

    while True:
        try:
            if EXCEL_PATH.exists():
                mtime = EXCEL_PATH.stat().st_mtime
                if mtime != _last_mtime:
                    log.info("📢 Phát hiện file DEMO_sales_data.xlsx vừa thay đổi! Đang nạp dữ liệu mới...")
                    fresh_data = parse_excel(EXCEL_PATH)
                    with _data_lock:
                        _live_data = fresh_data
                    _last_mtime = mtime
                    log.info(
                        f"✅ Cập nhật thành công từ Excel — "
                        f"Tổng DT: ₫{fresh_data['kpi']['doanh_thu']:,} Tr | "
                        f"Đơn hàng: {fresh_data['kpi']['don_hang']}"
                    )
        except Exception as exc:
            log.error(f"Lỗi khi đọc file Excel: {exc}")

        time.sleep(POLL_SEC)

# ──────────────────────────────────────────────
# DUAL STACK HTTP SERVER
# ──────────────────────────────────────────────
class DualStackHTTPServer(HTTPServer):
    address_family = socket.AF_INET6

    def server_bind(self):
        try:
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        except (AttributeError, OSError):
            pass
        super().server_bind()

class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        msg = fmt % args
        if "/data" not in msg:
            log.info(f"HTTP {self.address_string()} — {msg}")

    def do_GET(self):
        path = self.path.split("?")[0]

        if path in ("/", "/dashboard", "/dashboard_alpha.html"):
            self._serve_html()
        elif path == "/data":
            self._serve_json()
        elif path == "/health":
            self._send(200, "application/json", b'{"status":"ok"}')
        else:
            self._send(404, "text/plain", b"404 Not Found")

    def _serve_html(self):
        try:
            content = HTML_PATH.read_bytes()
            self._send(200, "text/html; charset=utf-8", content)
        except FileNotFoundError:
            self._send(500, "text/plain", b"dashboard_alpha.html not found")

    def _serve_json(self):
        with _data_lock:
            data = json.dumps(_live_data, ensure_ascii=False).encode("utf-8")
        self._send(200, "application/json", data)

    def _send(self, code: int, content_type: str, body: bytes):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(body)

# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────
def main():
    if not EXCEL_PATH.exists() or not HTML_PATH.exists():
        log.error("Thiếu file Excel hoặc HTML!")
        sys.exit(1)

    global _live_data, _last_mtime
    try:
        _live_data = parse_excel(EXCEL_PATH)
        _last_mtime = EXCEL_PATH.stat().st_mtime
        log.info(
            f"Nạp dữ liệu ban đầu từ Excel — "
            f"{_live_data['kpi']['don_hang']} đơn hàng, "
            f"Doanh thu ₫{_live_data['kpi']['doanh_thu']:,} Tr"
        )
    except Exception as e:
        log.error(f"Lỗi đọc Excel: {e}")
        sys.exit(1)

    t = threading.Thread(target=polling_loop, daemon=True, name="PollingThread")
    t.start()

    try:
        server = DualStackHTTPServer(("", PORT), DashboardHandler)
        log.info("Khởi động Dual-Stack IPv4/IPv6 thành công!")
    except Exception:
        server = HTTPServer(("0.0.0.0", PORT), DashboardHandler)
        log.info("Khởi động IPv4 HTTPServer thành công!")

    url_ip = f"http://127.0.0.1:{PORT}"

    log.info(f"🚀 Server chạy tại: {url_ip}")

    def open_browser():
        time.sleep(OPEN_DELAY)
        webbrowser.open(url_ip)

    threading.Thread(target=open_browser, daemon=True, name="BrowserThread").start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        log.info("Đã tắt server.")
        server.shutdown()

if __name__ == "__main__":
    main()
