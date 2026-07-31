import sys
import os
import site

user_site = site.getusersitepackages()
if user_site not in sys.path:
    sys.path.append(user_site)

import streamlit as st
import pandas as pd
import numpy as np
import re
import io
import requests
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------------------------
# Page Configuration & Styling (Tone Màu Đỏ Chủ Đạo Premium)
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Lead Scoring Dashboard - Bất Động Sản",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Red Theme Glassmorphism Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700;800&display=swap');
    
    /* Global Styling */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .stApp {
        background: radial-gradient(circle at top right, #2a0812 0%, #110509 45%, #070204 100%);
        color: #fff1f2;
    }

    /* Main Header Container */
    .main-header {
        background: linear-gradient(135deg, rgba(225, 29, 72, 0.25) 0%, rgba(136, 19, 55, 0.45) 50%, rgba(15, 23, 42, 0.7) 100%);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(244, 63, 94, 0.3);
        padding: 28px 32px;
        border-radius: 20px;
        margin-bottom: 28px;
        box-shadow: 0 15px 35px -10px rgba(225, 29, 72, 0.35);
    }
    
    .main-header h1 {
        background: linear-gradient(90deg, #ffffff 0%, #fecdd3 50%, #fda4af 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        margin: 0 0 10px 0;
        font-size: 2.3rem;
        letter-spacing: -0.02em;
    }
    
    .main-header p {
        color: #fecdd3;
        font-size: 1.1rem;
        margin: 0;
        opacity: 0.9;
    }

    /* Metric Cards */
    .metric-card {
        background: linear-gradient(145deg, rgba(39, 16, 25, 0.75), rgba(20, 7, 13, 0.85));
        backdrop-filter: blur(12px);
        border: 1px solid rgba(244, 63, 94, 0.25);
        border-radius: 16px;
        padding: 20px 18px;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 8px 20px -6px rgba(0, 0, 0, 0.5);
    }
    
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(244, 63, 94, 0.6);
        box-shadow: 0 12px 28px -6px rgba(225, 29, 72, 0.4);
    }
    
    .metric-value {
        font-size: 2.3rem;
        font-weight: 800;
        margin: 4px 0;
        letter-spacing: -0.03em;
    }
    
    .metric-label {
        font-size: 0.82rem;
        color: #fda4af;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 700;
    }

    .metric-sub {
        font-size: 0.78rem;
        color: #fb7185;
        margin-top: 4px;
        font-weight: 500;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: rgba(30, 10, 18, 0.6);
        padding: 8px;
        border-radius: 14px;
        border: 1px solid rgba(244, 63, 94, 0.2);
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre;
        border-radius: 10px;
        color: #fecdd3;
        font-weight: 600;
        font-size: 0.98rem;
        border: none;
        padding: 0 24px;
        transition: all 0.2s ease;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #e11d48 0%, #9f1239 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(225, 29, 72, 0.4);
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #e11d48 0%, #be123c 100%);
        color: white;
        font-weight: 700;
        border: none;
        border-radius: 12px;
        padding: 10px 24px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 14px rgba(225, 29, 72, 0.35);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(225, 29, 72, 0.5);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #12060a;
        border-right: 1px solid rgba(244, 63, 94, 0.15);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Knowledge Base Loader
# ---------------------------------------------------------
KNOWLEDGE_FILE_PATH = os.path.join("knowledge-base", "tieu_chi_cham_diem.txt")

@st.cache_data(ttl=60)
def load_knowledge_base():
    """Đọc file tieu_chi_cham_diem.txt từ thư mục knowledge-base"""
    if os.path.exists(KNOWLEDGE_FILE_PATH):
        try:
            with open(KNOWLEDGE_FILE_PATH, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Lỗi đọc file Knowledge Base: {e}"
    return "Không tìm thấy file tieu_chi_cham_diem.txt trong thư mục knowledge-base."

# ---------------------------------------------------------
# AI Lead Scoring Engine
# ---------------------------------------------------------
def score_single_lead(description: str) -> dict:
    """
    Hàm chấm điểm Lead dựa trên quy tắc trong tieu_chi_cham_diem.txt
    """
    if not isinstance(description, str) or not description.strip():
        return {
            'score': 0,
            'category': 'COLD',
            'reasons': 'Mô tả trống'
        }
    
    desc_lower = description.lower()
    score = 0
    positive_reasons = []
    negative_reasons = []

    # 1. TIÊU CHÍ TRỪ 50 ĐIỂM (KHÁCH RÁC / KHÔNG TIỀM NĂNG)
    if ("quận 1" in desc_lower or "q1" in desc_lower or "trung tâm" in desc_lower) and \
       re.search(r'\b(1|2|vài trăm)\s*(tỷ|triệu)\b', desc_lower):
        score -= 50
        negative_reasons.append("Trừ 50đ: Mua BĐS Q1/Trung tâm giá phi thực tế (1-2 tỷ/vài trăm triệu)")

    if any(k in desc_lower for k in ["nhầm số", "không có nhu cầu", "dữ liệu cũ", "nhầm ngành"]):
        score -= 50
        negative_reasons.append("Trừ 50đ: Khách nhầm số / Không có nhu cầu")

    if any(k in desc_lower for k in ["hỏi giá cho vui", "chưa có ý định mua", "thái độ không hợp tác", "đóng máy ngang"]):
        score -= 50
        negative_reasons.append("Trừ 50đ: Hỏi giá cho vui / Không hợp tác")

    if any(k in desc_lower for k in ["bảo hiểm", "vay vốn", "quảng cáo", "mời chào", "chứng khoán", "spam"]):
        score -= 50
        negative_reasons.append("Trừ 50đ: Spam / Quảng cáo dịch vụ khác")

    if any(k in desc_lower for k in ["thuê bao", "không bắt máy", "không phản hồi zalo", "gọi nhiều lần không"]):
        score -= 50
        negative_reasons.append("Trừ 50đ: Liên lạc lỗi / Thuê bao / Không phản hồi")

    # 2. TIÊU CHÍ CỘNG 50 ĐIỂM (KHÁCH VIP / TIỀM NĂNG CAO)
    budget_match = re.search(r'(\d+)\s*(tỷ|tỉ)', desc_lower)
    is_big_budget = False
    if budget_match:
        amount = int(budget_match.group(1))
        if amount >= 20:
            is_big_budget = True
            positive_reasons.append(f"Cộng 50đ: Ngân sách lớn ({amount} tỷ >= 20 tỷ)")
    
    if not is_big_budget and any(k in desc_lower for k in ["tài chính mạnh", "không thành vấn đề", "tài chính sẵn sàng"]):
        positive_reasons.append("Cộng 50đ: Tài chính mạnh / không thành vấn đề")
        is_big_budget = True

    luxury_types = ["biệt thự", "penthouse", "shophouse", "đất công nghiệp", "sàn văn phòng"]
    found_types = [t for t in luxury_types if t in desc_lower]
    if found_types:
        positive_reasons.append(f"Cộng 50đ: BĐS cao cấp ({', '.join(found_types).title()})")

    prime_locations = ["quận 1", "ven sông", "vinhomes ocean park", "phú mỹ hưng", "vinhomes"]
    found_locs = [l for l in prime_locations if l in desc_lower]
    if found_locs and "giá 1" not in desc_lower and "giá 2" not in desc_lower:
        positive_reasons.append(f"Cộng 50đ: Vị trí đắc địa ({', '.join(found_locs).title()})")

    vip_personas = ["chủ doanh nghiệp", "nhà đầu tư", "mua sỉ", "mua số lượng lớn", "chủ cty"]
    found_vip = [v for v in vip_personas if v in desc_lower]
    if found_vip:
        positive_reasons.append(f"Cộng 50đ: Chân dung VIP ({', '.join(found_vip).title()})")

    urgent_keywords = ["pháp lý chuẩn", "sổ hồng riêng", "gặp trực tiếp chủ đầu tư", "muốn gặp trực tiếp", "cần mua gấp"]
    found_urgent = [u for u in urgent_keywords if u in desc_lower]
    if found_urgent:
        positive_reasons.append(f"Cộng 50đ: Cấp thiết / Pháp lý chuẩn ({', '.join(found_urgent)})")

    if positive_reasons and not negative_reasons:
        score += 50 * min(len(positive_reasons), 2)
    elif positive_reasons and negative_reasons:
        score += 50 * len(positive_reasons)

    # 3. TRƯỜNG HỢP TRUNG TRÍNH
    if not positive_reasons and not negative_reasons:
        if any(k in desc_lower for k in ["căn hộ", "chung cư", "nhà phố", "vay ngân hàng", "tư vấn"]):
            score = 20
            positive_reasons.append("Cộng 20đ: Nhu cầu nhà ở/căn hộ tầm trung")
        else:
            score = 10
            positive_reasons.append("Cộng 10đ: Nhu cầu cơ bản")

    all_reasons = positive_reasons + negative_reasons
    reason_str = " | ".join(all_reasons) if all_reasons else "Nhu cầu bình thường"

    if score >= 50:
        category = "HOT"
    elif score >= 0:
        category = "WARM"
    elif score > -50:
        category = "COLD"
    else:
        category = "JUNK"

    return {
        'score': score,
        'category': category,
        'reasons': reason_str
    }

# ---------------------------------------------------------
# Data Loader
# ---------------------------------------------------------
DEFAULT_SHEET_URL = "https://docs.google.com/spreadsheets/d/1DyN6I3_5hVfMpszVom4enaKu2ZKxHInwf6RXrkTg1uo/export?format=csv&gid=1542775777"

def generate_sample_fallback_leads():
    """Tạo bộ dữ liệu 20 mẫu Lead BĐS thực tế làm dự phòng khi Google Sheets bị khóa quyền (401)"""
    sample_data = [
        {"ID": 1, "Họ và tên": "Phan Văn Hoa", "SĐT": "0901234567", "Mô tả chi tiết": "Đang tìm thuê mặt bằng kinh doanh spa tại Quận 1, diện tích khoảng 80-100m2. Giá thuê dưới 50 triệu/tháng."},
        {"ID": 2, "Họ và tên": "Hồ Hồng Linh", "SĐT": "0912345678", "Mô tả chi tiết": "Khách hàng nhầm số, không có nhu cầu về bất động sản. Có vẻ là dữ liệu cũ từ ngành khác."},
        {"ID": 3, "Họ và tên": "Lý Đức Cường", "SĐT": "0987654321", "Mô tả chi tiết": "Quan tâm căn hộ 2PN tại Quận 7 cho gia đình trẻ. Tài chính khoảng 4-5 tỷ, cần hỗ trợ vay ngân hàng 70%."},
        {"ID": 4, "Họ và tên": "Lê Anh Lan", "SĐT": "0933445566", "Mô tả chi tiết": "Tìm mua Penthouse diện tích lớn, có hồ bơi riêng. Ngân sách không thành vấn đề, quan trọng đẳng cấp."},
        {"ID": 5, "Họ và tên": "Ngô Anh Mai", "SĐT": "0977889900", "Mô tả chi tiết": "Tìm nhà phố liền kề nội thành, gần trường học bệnh viện. Ngân sách 8-10 tỷ. Cần tư vấn chiết khấu."},
        {"ID": 6, "Họ và tên": "Đặng Hoàng Dũng", "SĐT": "0966554433", "Mô tả chi tiết": "Số điện thoại hay bị thuê bao, gọi nhiều lần không bắt máy. Nhắn tin Zalo không phản hồi."},
        {"ID": 7, "Họ và tên": "Phạm Minh Lan", "SĐT": "0944332211", "Mô tả chi tiết": "Cần mua đất nền vùng ven (Long An, Đồng Nai) đầu tư dài hạn. Tài chính 2-3 tỷ. Yêu cầu sổ hồng riêng."},
        {"ID": 8, "Họ và tên": "Trần Quốc Tuấn", "SĐT": "0922110099", "Mô tả chi tiết": "Mua Shophouse mặt đường lớn tại Phú Mỹ Hưng. Ngân sách 25 tỷ tài chính sẵn sàng, muốn gặp trực tiếp CĐT."},
        {"ID": 9, "Họ và tên": "Bùi Thị Tuyết", "SĐT": "0911009988", "Mô tả chi tiết": "Hỏi giá cho vui, chưa có ý định mua trong năm nay. Đóng máy ngang khi tư vấn."},
        {"ID": 10, "Họ và tên": "Vũ Văn Nam", "SĐT": "0900998877", "Mô tả chi tiết": "Gọi điện đến quảng cáo dịch vụ bảo hiểm và vay vốn ngân hàng. Không có nhu cầu mua BĐS."},
        {"ID": 11, "Họ và tên": "Hoàng Minh Trí", "SĐT": "0988776655", "Mô tả chi tiết": "Chủ doanh nghiệp cần mua Quỹ đất công nghiệp 2-5 ha tại Bình Dương. Tài chính mạnh, pháp lý chuẩn 100%."},
        {"ID": 12, "Họ và tên": "Nguyễn Thị Ngọc", "SĐT": "0977665544", "Mô tả chi tiết": "Tìm mua Biệt thự đơn lập tại Vinhomes Ocean Park. Yêu cầu căn góc ven sông, cần mua gấp trong tháng."},
        {"ID": 13, "Họ và tên": "Đỗ Quang Liêm", "SĐT": "0966554422", "Mô tả chi tiết": "Tìm mua nhà mặt tiền Quận 1 giá 1,5 tỷ để ở. Không thương lượng thêm."},
        {"ID": 14, "Họ và tên": "Trịnh Kim Chi", "SĐT": "0955443322", "Mô tả chi tiết": "Nhà đầu tư chuyên nghiệp mua sỉ 5 căn hộ cao cấp khu vực trung tâm. Cần gặp đàm phán chính sách sỉ."},
        {"ID": 15, "Họ và tên": "Phùng Đức Thắng", "SĐT": "0944332200", "Mô tả chi tiết": "Thuê sàn văn phòng diện tích lớn 500m2 tại Quận 1. Ngân sách 200 triệu/tháng. Hợp đồng 5 năm."}
    ]
    return pd.DataFrame(sample_data)

def load_data_from_private_sheet(source_url):
    """Nạp dữ liệu từ Google Sheet Riêng Tư (Private) bằng Service Account Token trong st.secrets"""
    try:
        if "gcp_service_account" in st.secrets:
            from google.oauth2 import service_account
            from google.auth.transport.requests import Request

            creds_dict = dict(st.secrets["gcp_service_account"])
            if "private_key" in creds_dict:
                creds_dict["private_key"] = str(creds_dict["private_key"]).replace("\\n", "\n")

            scopes = [
                'https://www.googleapis.com/auth/spreadsheets.readonly',
                'https://www.googleapis.com/auth/drive.readonly'
            ]
            credentials = service_account.Credentials.from_service_account_info(creds_dict, scopes=scopes)
            credentials.refresh(Request())
            
            headers = {
                'Authorization': f'Bearer {credentials.token}'
            }
            res = requests.get(source_url, headers=headers, timeout=12)
            if res.status_code == 200:
                return pd.read_csv(io.StringIO(res.text))
    except Exception as e:
        pass
    return None

def load_data(source_url):
    df = None
    
    # 1. Thử xác thực Service Account từ st.secrets cho Private Google Sheet (bọc try-except an toàn)
    has_gcp_secret = False
    try:
        if "gcp_service_account" in st.secrets:
            has_gcp_secret = True
    except Exception:
        has_gcp_secret = False

    if has_gcp_secret:
        df = load_data_from_private_sheet(source_url)
        
    # 2. Nếu chưa thành công, thử tải trực tiếp
    if df is None:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            res = requests.get(source_url, headers=headers, timeout=10)
            if res.status_code == 200:
                df = pd.read_csv(io.StringIO(res.text))
            elif res.status_code == 401 or res.status_code == 403:
                st.warning("""
                🔒 **Google Sheet đang ở chế độ Riêng Tư (Private/401 Unauthorized)**:
                - **Để kết nối Google Sheet Riêng Tư này với Service Account**: 
                  Mở Google Sheet ➔ Bấm **Chia sẻ (Share)** ➔ Thêm email Service Account làm Người xem (Viewer):
                  `lead-scoring-robot@agenticday7.iam.gserviceaccount.com`
                - **Tạm thời**: Hệ thống đang hiển thị **Bộ Dữ Liệu Mẫu** bên dưới!
                """)
                df = generate_sample_fallback_leads()
            else:
                df = pd.read_csv(source_url)
        except Exception as e:
            st.warning(f"⚠️ Không thể nạp từ Google Sheets ({e}). Đang nạp dữ liệu mẫu dự phòng...")
            df = generate_sample_fallback_leads()

    if df is not None:
        column_mapping = {
            'id': 'ID',
            'ten_khach': 'Họ và tên',
            'sdt': 'SĐT',
            'nhu_cau_mo_ta': 'Mô tả chi tiết',
            'Email': 'Email',
            'Nhu cầu BĐS': 'Nhu cầu BĐS',
            'Khu vực quan tâm': 'Khu vực quan tâm',
            'Ngân sách (Tỷ)': 'Ngân sách (Tỷ)'
        }
        df = df.rename(columns=column_mapping)
        
        if 'ID' not in df.columns:
            df['ID'] = range(1, len(df) + 1)
        if 'Họ và tên' not in df.columns:
            df['Họ và tên'] = 'Khách hàng'
        if 'SĐT' not in df.columns:
            df['SĐT'] = 'N/A'
        if 'Mô tả chi tiết' not in df.columns and 'nhu_cau_mo_ta' in df.columns:
            df['Mô tả chi tiết'] = df['nhu_cau_mo_ta']
            
        df['SĐT'] = df['SĐT'].fillna('').astype(str)
        df['Họ và tên'] = df['Họ và tên'].fillna('Khách hàng').astype(str)
        df['Mô tả chi tiết'] = df['Mô tả chi tiết'].fillna('').astype(str)

        if 'AI Scoring' not in df.columns:
            df['AI Scoring'] = np.nan
        if 'Phân loại' not in df.columns:
            df['Phân loại'] = 'Chưa phân loại'
        if 'Lý do AI' not in df.columns:
            df['Lý do AI'] = ''
        if 'Duyệt' not in df.columns:
            df['Duyệt'] = 'Chờ duyệt'
        if 'Ghi chú Sales' not in df.columns:
            df['Ghi chú Sales'] = ''
            
        return df
    return None

# ---------------------------------------------------------
# Sidebar Setup
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0;">
        <h2 style="color: #f43f5e; font-weight: 800; margin:0;">👑 REAL ESTATE</h2>
        <p style="color: #fda4af; font-size: 0.85rem; margin:0;">AI Lead Intelligence System</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    st.subheader("⚙️ Cấu Hình Nguồn Dữ Liệu")
    sheet_url_input = st.text_input(
        "Link Google Sheets CSV Export:",
        value=DEFAULT_SHEET_URL,
        help="Định dạng export CSV từ Google Sheets"
    )
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔄 Tải lại", use_container_width=True):
            st.session_state.pop('leads_df', None)
            st.rerun()
            
    with col_btn2:
        if st.button("🗑️ Reset", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    st.markdown("---")
    st.subheader("📚 Quy Tắc Knowledge Base")
    kb_content = load_knowledge_base()
    with st.expander("📖 Xem tieu_chi_cham_diem.txt", expanded=False):
        st.text_area("Nội dung tieu_chi_cham_diem.txt", value=kb_content, height=220, disabled=True)

    st.markdown("---")
    st.caption("Developed by Antigravity AI • Premium Crimson Edition")

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if 'leads_df' not in st.session_state:
    with st.spinner("Đang kết nối & nạp dữ liệu từ Google Sheets..."):
        loaded_df = load_data(sheet_url_input)
        if loaded_df is not None:
            st.session_state.leads_df = loaded_df
        else:
            st.session_state.leads_df = generate_sample_fallback_leads()

df = st.session_state.leads_df

# ---------------------------------------------------------
# Header Section
# ---------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>👑 DASHBOARD BÁO CÁO & AI LEAD SCORING</h1>
    <p>Hệ thống AI tự động phân tích nhu cầu, chấm điểm Lead Real Estate và quản trị phê duyệt trực quan.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Top KPI Metric Cards (Visual Stats)
# ---------------------------------------------------------
total_leads = len(df)
scored_leads = df['AI Scoring'].notna().sum()
hot_leads = (df['Phân loại'] == 'HOT').sum()
warm_leads = (df['Phân loại'] == 'WARM').sum()
cold_leads = (df['Phân loại'] == 'COLD').sum()
junk_leads = (df['Phân loại'] == 'JUNK').sum()
approved_leads = (df['Duyệt'] == 'Đã duyệt').sum()
pending_approval = (df['Duyệt'] == 'Chờ duyệt').sum()

pct_hot = (hot_leads / total_leads * 100) if total_leads > 0 else 0
pct_junk = (junk_leads / total_leads * 100) if total_leads > 0 else 0

m1, m2, m3, m4, m5, m6 = st.columns(6)

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Tổng Lead</div>
        <div class="metric-value" style="color: #ffffff;">{total_leads}</div>
        <div class="metric-sub">Đã nạp từ Sheets</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card" style="border-color: rgba(244, 63, 94, 0.7);">
        <div class="metric-label">🌟 KHÁCH VIP (HOT)</div>
        <div class="metric-value" style="color: #f43f5e;">{hot_leads}</div>
        <div class="metric-sub">{pct_hot:.1f}% trên tổng số</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🟡 WARM (Tiềm Năng)</div>
        <div class="metric-value" style="color: #fbbf24;">{warm_leads}</div>
        <div class="metric-sub">Cần chăm sóc chuẩn</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🔵 COLD (Ít Tiềm Năng)</div>
        <div class="metric-value" style="color: #60a5fa;">{cold_leads}</div>
        <div class="metric-sub">Nuôi dưỡng tự động</div>
    </div>
    """, unsafe_allow_html=True)

with m5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🔴 JUNK (Khách Rác)</div>
        <div class="metric-value" style="color: #94a3b8;">{junk_leads}</div>
        <div class="metric-sub">{pct_junk:.1f}% lọc bỏ</div>
    </div>
    """, unsafe_allow_html=True)

with m6:
    st.markdown(f"""
    <div class="metric-card" style="border-color: rgba(168, 85, 247, 0.5);">
        <div class="metric-label">⏳ Chờ Duyệt</div>
        <div class="metric-value" style="color: #c084fc;">{pending_approval}</div>
        <div class="metric-sub">Đã duyệt: {approved_leads}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# TABBED NAVIGATION (Dashboard Visual vs Data Editor)
# ---------------------------------------------------------
tab_analytics, tab_management, tab_knowledge = st.tabs([
    "📊 DASHBOARD THỐNG KÊ VISUAL",
    "📋 QUẢN LÝ LEAD & AI AGENT",
    "📚 TIÊU CHÍ KNOWLEDGE BASE"
])

# =========================================================
# TAB 1: DASHBOARD THỐNG KÊ VISUAL
# =========================================================
with tab_analytics:
    st.markdown("<h3 style='color: #fda4af; font-weight: 700;'>📈 Báo Cáo & Biểu Đồ Thống Kê Trực Quan</h3>", unsafe_allow_html=True)
    
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        # Donut Chart Phân Loại Lead
        cat_counts = df['Phân loại'].value_counts().reset_index()
        cat_counts.columns = ['Phân loại', 'Số lượng']
        
        color_map = {
            'HOT': '#e11d48',       # Crimson Red
            'WARM': '#f59e0b',      # Amber
            'COLD': '#3b82f6',      # Blue
            'JUNK': '#64748b',      # Slate
            'Chưa phân loại': '#334155'
        }
        
        fig_donut = px.pie(
            cat_counts,
            names='Phân loại',
            values='Số lượng',
            hole=0.55,
            title="<b>Tỷ Lệ Phân Loại Khách Hàng (Lead Quality)</b>",
            color='Phân loại',
            color_discrete_map=color_map
        )
        fig_donut.update_traces(
            textposition='inside',
            textinfo='percent+label',
            marker=dict(line=dict(color='#1e1b1e', width=2))
        )
        fig_donut.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#fecdd3', family='Outfit'),
            title_font=dict(size=18, color='#ffffff'),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with col_chart2:
        # Bar Chart Trạng Thái Duyệt Lead
        approval_counts = df['Duyệt'].value_counts().reset_index()
        approval_counts.columns = ['Trạng thái', 'Số lượng']
        
        app_color_map = {
            'Đã duyệt': '#10b981',    # Emerald Green
            'Chờ duyệt': '#e11d48',   # Crimson Red
            'Từ chối': '#64748b'     # Gray
        }
        
        fig_bar = px.bar(
            approval_counts,
            x='Trạng thái',
            y='Số lượng',
            text='Số lượng',
            color='Trạng thái',
            title="<b>Thống Kê Trạng Thái Duyệt Lead</b>",
            color_discrete_map=app_color_map
        )
        fig_bar.update_traces(
            textposition='outside',
            marker_line_color='#ffffff',
            marker_line_width=1.5,
            opacity=0.9
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#fecdd3', family='Outfit'),
            title_font=dict(size=18, color='#ffffff'),
            xaxis=dict(showgrid=False, title=""),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title="Số lượng Lead")
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_chart3, col_chart4 = st.columns([3, 2])
    
    with col_chart3:
        # Phân bố Điểm số AI (Score Distribution Histogram)
        scored_df = df[df['AI Scoring'].notna()].copy()
        if len(scored_df) > 0:
            fig_hist = px.histogram(
                scored_df,
                x='AI Scoring',
                nbins=20,
                title="<b>Phân Bổ Phổ Điểm AI Scoring (-50 đến +100)</b>",
                color_discrete_sequence=['#e11d48']
            )
            fig_hist.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#fecdd3', family='Outfit'),
                title_font=dict(size=18, color='#ffffff'),
                xaxis=dict(title="Điểm AI (Score)", showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
                yaxis=dict(title="Số lượng Lead", showgrid=True, gridcolor='rgba(255,255,255,0.1)')
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("Chưa có dữ liệu điểm AI. Hãy bấm 'TỰ ĐỘNG CHẤM ĐIỂM TẤT CẢ LEAD' tại Tab Quản Lý để tạo biểu đồ!")

    with col_chart4:
        # Thống kê tổng quan KPI bổ sung
        avg_score = scored_df['AI Scoring'].mean() if len(scored_df) > 0 else 0
        max_score = scored_df['AI Scoring'].max() if len(scored_df) > 0 else 0
        auto_approved = (scored_df['AI Scoring'] >= 100).sum() if len(scored_df) > 0 else 0
        
        st.markdown(f"""
        <div style="background: rgba(39, 16, 25, 0.6); border: 1px solid rgba(244, 63, 94, 0.3); border-radius: 16px; padding: 24px; margin-top: 25px;">
            <h4 style="color: #fda4af; margin-top: 0;">⚡ Chỉ Số AI Intelligence</h4>
            <hr style="border-color: rgba(244, 63, 94, 0.2);">
            <p style="font-size: 1.1rem; color: #ffffff;"><b>• Tỷ lệ đã chấm điểm:</b> <span style="color: #f43f5e; font-weight: bold;">{scored_leads}/{total_leads} ({scored_leads/total_leads*100:.1f}%)</span></p>
            <p style="font-size: 1.1rem; color: #ffffff;"><b>• Điểm AI Trung bình:</b> <span style="color: #fbbf24; font-weight: bold;">{avg_score:.1f} điểm</span></p>
            <p style="font-size: 1.1rem; color: #ffffff;"><b>• Điểm AI Cao nhất:</b> <span style="color: #34d399; font-weight: bold;">{max_score:.0f} điểm</span></p>
            <p style="font-size: 1.1rem; color: #ffffff;"><b>• Số Lead Tự động Duyệt (>=100đ):</b> <span style="color: #a78bfa; font-weight: bold;">{auto_approved} lead</span></p>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# TAB 2: QUẢN LÝ LEAD & AI AGENT
# =========================================================
with tab_management:
    st.markdown("<h3 style='color: #fda4af; font-weight: 700;'>⚡ AI Scoring Agent & Quản Lý Duyệt Lead</h3>", unsafe_allow_html=True)
    
    # Action Buttons Bar
    col_action1, col_action2, col_action3 = st.columns([3, 3, 2])

    with col_action1:
        if st.button("⚡ TỰ ĐỘNG CHẤM ĐIỂM TẤT CẢ LEAD (500 Leads)", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            total_rows = len(df)
            auto_approved_count = 0
            for idx in range(total_rows):
                desc = str(df.at[idx, 'Mô tả chi tiết'])
                res = score_single_lead(desc)
                df.at[idx, 'AI Scoring'] = res['score']
                df.at[idx, 'Phân loại'] = res['category']
                df.at[idx, 'Lý do AI'] = res['reasons']
                
                if res['score'] >= 100:
                    df.at[idx, 'Duyệt'] = 'Đã duyệt'
                    auto_approved_count += 1
                
                if (idx + 1) % 50 == 0 or idx == total_rows - 1:
                    progress_bar.progress((idx + 1) / total_rows)
                    status_text.text(f"Đã xử lý {idx + 1}/{total_rows} leads...")
                    
            st.session_state.leads_df = df
            status_text.success(f"✅ Đã hoàn tất chấm điểm 500 leads! (Tự động duyệt {auto_approved_count} lead VIP >= 100đ)")
            st.rerun()

    with col_action2:
        if st.button("🎯 Chấm điểm Lead Chưa Có Điểm", use_container_width=True):
            unscored_mask = df['AI Scoring'].isna()
            unscored_indices = df[unscored_mask].index
            
            if len(unscored_indices) == 0:
                st.toast("Tất cả leads đều đã được chấm điểm!", icon="ℹ️")
            else:
                auto_approved_count = 0
                for idx in unscored_indices:
                    desc = str(df.at[idx, 'Mô tả chi tiết'])
                    res = score_single_lead(desc)
                    df.at[idx, 'AI Scoring'] = res['score']
                    df.at[idx, 'Phân loại'] = res['category']
                    df.at[idx, 'Lý do AI'] = res['reasons']
                    
                    if res['score'] >= 100:
                        df.at[idx, 'Duyệt'] = 'Đã duyệt'
                        auto_approved_count += 1
                        
                st.session_state.leads_df = df
                st.success(f"✅ Đã chấm điểm cho {len(unscored_indices)} leads mới! (Tự động duyệt {auto_approved_count} lead VIP)")
                st.rerun()

    with col_action3:
        csv_buffer = io.BytesIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        csv_buffer.seek(0)
        st.download_button(
            label="📥 Tải Bảng Dữ Liệu (CSV)",
            data=csv_buffer,
            file_name="lead_scoring_results.csv",
            mime="text/csv",
            use_container_width=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Filters Bar
    f_col1, f_col2, f_col3 = st.columns([2, 2, 3])

    with f_col1:
        filter_category = st.multiselect(
            "Lọc Phân Loại AI:",
            options=["HOT", "WARM", "COLD", "JUNK", "Chưa phân loại"],
            default=[]
        )

    with f_col2:
        filter_approval = st.multiselect(
            "Lọc Trạng Thái Duyệt:",
            options=["Chờ duyệt", "Đã duyệt", "Từ chối"],
            default=[]
        )

    with f_col3:
        search_keyword = st.text_input(
            "🔎 Tìm kiếm (Họ tên, SĐT, Mô tả):",
            placeholder="Nhập từ khóa tìm kiếm..."
        )

    filtered_df = df.copy()

    if filter_category:
        filtered_df = filtered_df[filtered_df['Phân loại'].isin(filter_category)]

    if filter_approval:
        filtered_df = filtered_df[filtered_df['Duyệt'].isin(filter_approval)]

    if search_keyword:
        kw = search_keyword.lower()
        mask = (
            filtered_df['Họ và tên'].astype(str).str.lower().str.contains(kw) |
            filtered_df['SĐT'].astype(str).str.lower().str.contains(kw) |
            filtered_df['Mô tả chi tiết'].astype(str).str.lower().str.contains(kw)
        )
        filtered_df = filtered_df[mask]

    st.caption(f"Hiển thị **{len(filtered_df)}** / **{len(df)}** leads")

    # Interactive Data Table with st.data_editor
    desired_columns = ['ID', 'Họ và tên', 'SĐT', 'Mô tả chi tiết', 'AI Scoring', 'Phân loại', 'Lý do AI', 'Duyệt', 'Ghi chú Sales']
    existing_columns = [col for col in desired_columns if col in filtered_df.columns]

    edited_df = st.data_editor(
        filtered_df[existing_columns],
        key="lead_data_editor",
        use_container_width=True,
        num_rows="dynamic",
        height=550,
        column_config={
            "ID": st.column_config.NumberColumn("ID", disabled=True, width="small"),
            "Họ và tên": st.column_config.TextColumn("Họ & Tên", width="medium"),
            "SĐT": st.column_config.TextColumn("SĐT", width="small"),
            "Mô tả chi tiết": st.column_config.TextColumn("Nhu Cầu Mô Tả", width="large"),
            "AI Scoring": st.column_config.NumberColumn(
                "Điểm AI",
                help="Điểm đánh giá từ AI (-50 đến +100)",
                format="%d",
                width="small"
            ),
            "Phân loại": st.column_config.SelectboxColumn(
                "Phân Loại",
                options=["HOT", "WARM", "COLD", "JUNK", "Chưa phân loại"],
                width="small"
            ),
            "Lý do AI": st.column_config.TextColumn("Lý Do / Chi Tiết Điểm", width="large", disabled=True),
            "Duyệt": st.column_config.SelectboxColumn(
                "Duyệt Trạng Thái",
                options=["Chờ duyệt", "Đã duyệt", "Từ chối"],
                required=True,
                width="medium"
            ),
            "Ghi chú Sales": st.column_config.TextColumn("Ghi Chú Sales", width="medium")
        }
    )

    if not edited_df.equals(filtered_df[existing_columns]):
        for index, row in edited_df.iterrows():
            lead_id = row['ID']
            original_idx = df[df['ID'] == lead_id].index
            if len(original_idx) > 0:
                idx = original_idx[0]
                df.at[idx, 'AI Scoring'] = row['AI Scoring']
                df.at[idx, 'Phân loại'] = row['Phân loại']
                
                if not pd.isna(row['AI Scoring']) and float(row['AI Scoring']) >= 100:
                    df.at[idx, 'Duyệt'] = 'Đã duyệt'
                else:
                    df.at[idx, 'Duyệt'] = row['Duyệt']
                    
                df.at[idx, 'Ghi chú Sales'] = row['Ghi chú Sales']
        st.session_state.leads_df = df
        st.toast("✅ Đã lưu chỉnh sửa & tự động cập nhật duyệt!", icon="💾")

# =========================================================
# TAB 3: TIÊU CHÍ KNOWLEDGE BASE
# =========================================================
with tab_knowledge:
    st.markdown("<h3 style='color: #fda4af; font-weight: 700;'>📚 Chi Tiết Bộ Quy Tắc Knowledge Base</h3>", unsafe_allow_html=True)
    
    col_kb1, col_kb2 = st.columns(2)
    
    with col_kb1:
        st.markdown("""
        <div style="background: rgba(39, 16, 25, 0.7); border: 1px solid rgba(244, 63, 94, 0.4); border-radius: 16px; padding: 20px;">
            <h4 style="color: #f43f5e; margin-top: 0;">🔥 Tiêu Chí CỘNG 50 ĐIỂM (VIP)</h4>
            <ul>
                <li><b>Ngân sách lớn:</b> Từ 20 tỷ trở lên hoặc "tài chính mạnh", "không thành vấn đề".</li>
                <li><b>Loại hình cao cấp:</b> Biệt thự đơn lập, Penthouse, Shophouse lớn, Đất công nghiệp.</li>
                <li><b>Vị trí đắc địa:</b> Quận 1, Ven sông, Vinhomes Ocean Park, Phú Mỹ Hưng.</li>
                <li><b>Chân dung VIP:</b> Chủ doanh nghiệp, Nhà đầu tư chuyên nghiệp, Mua sỉ.</li>
                <li><b>Cấp thiết & Pháp lý:</b> Sổ hồng riêng, Pháp lý chuẩn 100%, Gặp trực tiếp CĐT.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_kb2:
        st.markdown("""
        <div style="background: rgba(39, 16, 25, 0.7); border: 1px solid rgba(148, 163, 184, 0.4); border-radius: 16px; padding: 20px;">
            <h4 style="color: #94a3b8; margin-top: 0;">⛔ Tiêu Chí TRỪ 50 ĐIỂM (Khách Rác)</h4>
            <ul>
                <li><b>Yêu cầu phi thực tế:</b> Nhà Q1 / Trung tâm giá 1-2 tỷ hoặc vài trăm triệu.</li>
                <li><b>Không nhu cầu:</b> Nhầm số, Không nhu cầu, Dữ liệu cũ, Nhầm ngành.</li>
                <li><b>Thiếu thiện chí:</b> Hỏi giá cho vui, Chưa ý định mua, Không hợp tác.</li>
                <li><b>Spam/Quảng cáo:</b> Bảo hiểm, Vay vốn, Mời chào dịch vụ khác.</li>
                <li><b>Liên lạc lỗi:</b> Thuê bao, Gọi nhiều lần không bắt máy, Không Zalo.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown("<p style='text-align: center; color: #fda4af; font-size: 0.88rem;'>🏢 Real Estate AI Lead Scoring System • Red Premium UI Edition</p>", unsafe_allow_html=True)
