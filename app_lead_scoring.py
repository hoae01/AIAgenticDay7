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
import os
import io

# ---------------------------------------------------------
# Page Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Lead Scoring Agent - Bất Động Sản",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Glassmorphism Dark Theme Styling
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Header Container */
    .main-header {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.8));
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }
    
    .main-header h1 {
        color: #38bdf8;
        font-weight: 700;
        margin: 0 0 8px 0;
        font-size: 2.2rem;
    }
    .main-header p {
        color: #94a3b8;
        font-size: 1.05rem;
        margin: 0;
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px 20px;
        text-align: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-3px);
        border-color: rgba(56, 189, 248, 0.4);
    }
    .metric-value {
        font-size: 2.1rem;
        font-weight: 800;
        margin: 6px 0;
    }
    .metric-label {
        font-size: 0.88rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }

    /* Badges */
    .badge-hot { color: #f43f5e; font-weight: bold; }
    .badge-warm { color: #f59e0b; font-weight: bold; }
    .badge-cold { color: #3b82f6; font-weight: bold; }
    .badge-junk { color: #64748b; font-weight: bold; }
    
    /* Knowledge Expander */
    .stExpander {
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        background: rgba(15, 23, 42, 0.5) !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Knowledge Base Loader & Helper
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
# Rule-based AI Scoring Agent Engine
# ---------------------------------------------------------
def score_single_lead(description: str) -> dict:
    """
    Hàm chấm điểm Lead dựa trên quy tắc trong tieu_chi_cham_diem.txt
    Trả về dict: {'score': int, 'category': str, 'reasons': list}
    """
    if not isinstance(description, str) or not description.strip():
        return {
            'score': 0,
            'category': 'COLD',
            'reasons': ['Mô tả trống']
        }
    
    desc_lower = description.lower()
    score = 0
    positive_reasons = []
    negative_reasons = []

    # -----------------------------------------------------
    # 1. TIÊU CHÍ TRỪ 50 ĐIỂM (KHÁCH RÁC / KHÔNG TIỀM NĂNG)
    # -----------------------------------------------------
    # 1.1 Yêu cầu phi thực tế (Giá vô lý)
    if ("quận 1" in desc_lower or "q1" in desc_lower or "trung tâm" in desc_lower) and \
       re.search(r'\b(1|2|vài trăm)\s*(tỷ|triệu)\b', desc_lower):
        score -= 50
        negative_reasons.append("Trừ 50đ: Yêu cầu mua BĐS Quận 1 / Trung tâm với giá phi thực tế (1-2 tỷ/vài trăm triệu)")

    # 1.2 Không có nhu cầu / Nhầm số
    if any(k in desc_lower for k in ["nhầm số", "không có nhu cầu", "dữ liệu cũ", "nhầm ngành"]):
        score -= 50
        negative_reasons.append("Trừ 50đ: Khách nhầm số / Không có nhu cầu BĐS")

    # 1.3 Thiếu thiện chí
    if any(k in desc_lower for k in ["hỏi giá cho vui", "chưa có ý định mua", "thái độ không hợp tác", "đóng máy ngang"]):
        score -= 50
        negative_reasons.append("Trừ 50đ: Hỏi giá cho vui / Chưa có ý định mua / Không hợp tác")

    # 1.4 Spam / Quảng cáo
    if any(k in desc_lower for k in ["bảo hiểm", "vay vốn", "quảng cáo", "mời chào", "chứng khoán", "spam"]):
        score -= 50
        negative_reasons.append("Trừ 50đ: Spam / Quảng cáo dịch vụ khác")

    # 1.5 Lỗi liên lạc
    if any(k in desc_lower for k in ["thuê bao", "không bắt máy", "không phản hồi zalo", "gọi nhiều lần không"]):
        score -= 50
        negative_reasons.append("Trừ 50đ: Thông tin liên lạc lỗi / Thuê bao / Không bắt máy")

    # -----------------------------------------------------
    # 2. TIÊU CHÍ CỘNG 50 ĐIỂM (KHÁCH VIP / TIỀM NĂNG CAO)
    # -----------------------------------------------------
    # 2.1 Ngân sách lớn (>= 20 tỷ hoặc từ khóa tài chính mạnh)
    budget_match = re.search(r'(\d+)\s*(tỷ|tỉ)', desc_lower)
    is_big_budget = False
    if budget_match:
        amount = int(budget_match.group(1))
        if amount >= 20:
            is_big_budget = True
            positive_reasons.append(f"Cộng 50đ: Ngân sách lớn ({amount} tỷ >= 20 tỷ)")
    
    if not is_big_budget and any(k in desc_lower for k in ["tài chính mạnh", "không thành vấn đề", "tài chính sẵn sàng"]):
        positive_reasons.append("Cộng 50đ: Khách đề cập tài chính mạnh / không thành vấn đề")
        is_big_budget = True

    # 2.2 Loại hình cao cấp
    luxury_types = ["biệt thự", "penthouse", "shophouse", "đất công nghiệp", "sàn văn phòng"]
    found_types = [t for t in luxury_types if t in desc_lower]
    if found_types:
        positive_reasons.append(f"Cộng 50đ: Tìm kiếm BĐS cao cấp ({', '.join(found_types).title()})")

    # 2.3 Vị trí đắc địa
    prime_locations = ["quận 1", "ven sông", "vinhomes ocean park", "phú mỹ hưng", "vinhomes"]
    found_locs = [l for l in prime_locations if l in desc_lower]
    if found_locs and "giá 1" not in desc_lower and "giá 2" not in desc_lower: # Loại trừ trường hợp phi thực tế
        positive_reasons.append(f"Cộng 50đ: Vị trí đắc địa ({', '.join(found_locs).title()})")

    # 2.4 Chân dung VIP
    vip_personas = ["chủ doanh nghiệp", "nhà đầu tư", "mua sỉ", "mua số lượng lớn", "chủ cty"]
    found_vip = [v for v in vip_personas if v in desc_lower]
    if found_vip:
        positive_reasons.append(f"Cộng 50đ: Đối tượng khách VIP ({', '.join(found_vip).title()})")

    # 2.5 Cấp thiết & Minh bạch
    urgent_keywords = ["pháp lý chuẩn", "sổ hồng riêng", "gặp trực tiếp chủ đầu tư", "muốn gặp trực tiếp", "cần mua gấp"]
    found_urgent = [u for u in urgent_keywords if u in desc_lower]
    if found_urgent:
        positive_reasons.append(f"Cộng 50đ: Yêu cầu cấp thiết / Minh bạch pháp lý ({', '.join(found_urgent)})")

    # Cộng điểm nếu có lý do tích cực
    if positive_reasons and not negative_reasons:
        score += 50 * min(len(positive_reasons), 2) # Tối đa cộng 100đ
    elif positive_reasons and negative_reasons:
        # Nếu vừa có tích cực vừa có tiêu cực, áp dụng cộng trừ trực tiếp
        score += 50 * len(positive_reasons)

    # -----------------------------------------------------
    # 3. TRƯỜNG HỢP TRUNG TRÍNH (3-10 tỷ, Căn hộ/nhà phố)
    # -----------------------------------------------------
    if not positive_reasons and not negative_reasons:
        if any(k in desc_lower for k in ["căn hộ", "chung cư", "nhà phố", "vay ngân hàng", "tư vấn"]):
            score = 20
            positive_reasons.append("Cộng 20đ: Nhu cầu nhà ở/căn hộ tầm trung (Cần chăm sóc chuẩn)")
        else:
            score = 10
            positive_reasons.append("Cộng 10đ: Nhu cầu cơ bản")

    # Tổng hợp tất cả lý do
    all_reasons = positive_reasons + negative_reasons
    reason_str = " | ".join(all_reasons) if all_reasons else "Nhu cầu bình thường"

    # Phân loại
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

def load_data(source_url):
    try:
        df = pd.read_csv(source_url)
        # Chuẩn hóa tên cột
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
        
        # Đảm bảo các cột cần thiết tồn tại
        if 'ID' not in df.columns:
            df['ID'] = range(1, len(df) + 1)
        if 'Họ và tên' not in df.columns:
            df['Họ và tên'] = 'Khách hàng'
        if 'SĐT' not in df.columns:
            df['SĐT'] = 'N/A'
        if 'Mô tả chi tiết' not in df.columns and 'nhu_cau_mo_ta' in df.columns:
            df['Mô tả chi tiết'] = df['nhu_cau_mo_ta']
            
        # Ép kiểu dữ liệu chuỗi cho SĐT và Mô tả để tương thích với st.data_editor TextColumn
        df['SĐT'] = df['SĐT'].fillna('').astype(str)
        df['Họ và tên'] = df['Họ và tên'].fillna('Khách hàng').astype(str)
        df['Mô tả chi tiết'] = df['Mô tả chi tiết'].fillna('').astype(str)

        # Thêm các cột chấm điểm & quản lý nếu chưa có
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
    except Exception as e:
        st.error(f"Lỗi khi nạp dữ liệu từ Google Sheets: {e}")
        return None

# ---------------------------------------------------------
# Sidebar Setup
# ---------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/building.png", width=70)
    st.title("⚙️ Cấu Hình & Nguồn")
    
    sheet_url_input = st.text_input(
        "Link Google Sheets CSV Export:",
        value=DEFAULT_SHEET_URL,
        help="Định dạng export CSV từ Google Sheets"
    )
    
    col_btn1, col_btn2 = st.sidebar.columns(2)
    with col_btn1:
        if st.button("🔄 Tải lại dữ liệu", use_container_width=True):
            st.session_state.pop('leads_df', None)
            st.rerun()
            
    with col_btn2:
        if st.button("🗑️ Xóa bộ nhớ tạm", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    st.markdown("---")
    st.subheader("📚 Quy tắc Knowledge Base")
    kb_content = load_knowledge_base()
    with st.expander("📖 Xem tiêu chí tieu_chi_cham_diem.txt", expanded=False):
        st.text_area("Nội dung Knowledge Base", value=kb_content, height=250, disabled=True)

    st.markdown("---")
    st.caption("Developed by Antigravity AI Agent • Real Estate Scoring v2.0")

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if 'leads_df' not in st.session_state:
    with st.spinner("Đang kết nối & nạp dữ liệu từ Google Sheets..."):
        loaded_df = load_data(sheet_url_input)
        if loaded_df is not None:
            st.session_state.leads_df = loaded_df
        else:
            st.stop()

df = st.session_state.leads_df

# ---------------------------------------------------------
# Main UI Header
# ---------------------------------------------------------
st.markdown("""
<div class="main-header">
    <h1>🏢 Hệ Thống Quản Lý & AI Lead Scoring Bất Động Sản</h1>
    <p>Tự động quét mô tả khách hàng, áp dụng bộ quy tắc Knowledge Base để chấm điểm, phân loại và duyệt trạng thái lead real-time.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# AI Scoring Agent Action Bar & Metrics
# ---------------------------------------------------------
col_action1, col_action2, col_action3 = st.columns([2, 2, 2])

with col_action1:
    if st.button("⚡ TỰ ĐỘNG CHẤM ĐIỂM TẤT CẢ LEAD (500 Leads)", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        total_rows = len(df)
        for idx in range(total_rows):
            desc = str(df.at[idx, 'Mô tả chi tiết'])
            res = score_single_lead(desc)
            df.at[idx, 'AI Scoring'] = res['score']
            df.at[idx, 'Phân loại'] = res['category']
            df.at[idx, 'Lý do AI'] = res['reasons']
            
            if (idx + 1) % 50 == 0 or idx == total_rows - 1:
                progress_bar.progress((idx + 1) / total_rows)
                status_text.text(f"Đã xử lý {idx + 1}/{total_rows} leads...")
                
        st.session_state.leads_df = df
        status_text.success("✅ Đã hoàn tất chấm điểm toàn bộ Lead!")
        st.rerun()

with col_action2:
    if st.button("🎯 Chấm điểm Lead Chưa Có Điểm", use_container_width=True):
        unscored_mask = df['AI Scoring'].isna()
        unscored_indices = df[unscored_mask].index
        
        if len(unscored_indices) == 0:
            st.toast("Tất cả leads đều đã được chấm điểm!", icon="ℹ️")
        else:
            for idx in unscored_indices:
                desc = str(df.at[idx, 'Mô tả chi tiết'])
                res = score_single_lead(desc)
                df.at[idx, 'AI Scoring'] = res['score']
                df.at[idx, 'Phân loại'] = res['category']
                df.at[idx, 'Lý do AI'] = res['reasons']
            st.session_state.leads_df = df
            st.success(f"✅ Đã chấm điểm cho {len(unscored_indices)} leads mới!")
            st.rerun()

with col_action3:
    # Xuất file CSV / Excel
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

# ---------------------------------------------------------
# KPI Visual Cards
# ---------------------------------------------------------
total_leads = len(df)
scored_leads = df['AI Scoring'].notna().sum()
hot_leads = (df['Phân loại'] == 'HOT').sum()
warm_leads = (df['Phân loại'] == 'WARM').sum()
cold_leads = (df['Phân loại'] == 'COLD').sum()
junk_leads = (df['Phân loại'] == 'JUNK').sum()
pending_approval = (df['Duyệt'] == 'Chờ duyệt').sum()

m1, m2, m3, m4, m5, m6 = st.columns(6)

with m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Tổng Lead</div>
        <div class="metric-value" style="color: #38bdf8;">{total_leads}</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🌟 HOT (VIP)</div>
        <div class="metric-value" style="color: #f43f5e;">{hot_leads}</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🟡 WARM</div>
        <div class="metric-value" style="color: #f59e0b;">{warm_leads}</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🔵 COLD</div>
        <div class="metric-value" style="color: #3b82f6;">{cold_leads}</div>
    </div>
    """, unsafe_allow_html=True)

with m5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🔴 JUNK (Rác)</div>
        <div class="metric-value" style="color: #94a3b8;">{junk_leads}</div>
    </div>
    """, unsafe_allow_html=True)

with m6:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">⏳ Chờ Duyệt</div>
        <div class="metric-value" style="color: #a855f7;">{pending_approval}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Filters Bar
# ---------------------------------------------------------
st.subheader("🔍 Lọc & Quản Lý Dữ Liệu Lead")

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
        placeholder="Nhập từ khóa cần tìm..."
    )

# Áp dụng bộ lọc
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

# ---------------------------------------------------------
# Interactive Data Table with st.data_editor
# ---------------------------------------------------------
# Sắp xếp các cột cho dễ quan sát
desired_columns = ['ID', 'Họ và tên', 'SĐT', 'Mô tả chi tiết', 'AI Scoring', 'Phân loại', 'Lý do AI', 'Duyệt', 'Ghi chú Sales']
existing_columns = [col for col in desired_columns if col in filtered_df.columns]

# Display data_editor
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
            help="Điểm số đánh giá từ AI Agent (-50 đến +100)",
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

# Cập nhật thay đổi từ st.data_editor vào session state
if not edited_df.equals(filtered_df[existing_columns]):
    for index, row in edited_df.iterrows():
        lead_id = row['ID']
        original_idx = df[df['ID'] == lead_id].index
        if len(original_idx) > 0:
            idx = original_idx[0]
            df.at[idx, 'AI Scoring'] = row['AI Scoring']
            df.at[idx, 'Phân loại'] = row['Phân loại']
            df.at[idx, 'Duyệt'] = row['Duyệt']
            df.at[idx, 'Ghi chú Sales'] = row['Ghi chú Sales']
    st.session_state.leads_df = df
    st.toast("✅ Đã lưu chỉnh sửa!", icon="💾")

# ---------------------------------------------------------
# Footer & Help Instructions
# ---------------------------------------------------------
st.markdown("---")
with st.expander("❓ Hướng dẫn sử dụng Hệ thống AI Lead Scoring"):
    st.markdown("""
    ### 📌 Hướng dẫn từng bước:
    1. **Tải Dữ Liệu**: Mặc định ứng dụng tự động lấy dữ liệu từ [Google Sheets](https://docs.google.com/spreadsheets/d/1DyN6I3_5hVfMpszVom4enaKu2ZKxHInwf6RXrkTg1uo/edit?gid=1542775777#gid=1542775777).
    2. **Chạy AI Scoring**: 
       - Bấm **`⚡ TỰ ĐỘNG CHẤM ĐIỂM TẤT CẢ LEAD`** để AI Agent quét mô tả và chấm điểm toàn bộ 500 lead dựa trên tiêu chí Knowledge Base.
    3. **Xem & Duyệt Lead**: 
       - Dùng bộ lọc theo **Phân loại** (`HOT`, `WARM`, `COLD`, `JUNK`) hoặc **Trạng thái duyệt**.
       - Thay đổi cột **Duyệt Trạng Thái** (`Chờ duyệt` ➔ `Đã duyệt` / `Từ chối`) trực tiếp trên bảng `st.data_editor`.
       - Nhập **Ghi chú Sales** cho từng khách hàng.
    4. **Xuất Báo Cáo**: Bấm nút **`📥 Tải Bảng Dữ Liệu (CSV)`** để tải về kết quả làm báo cáo hoặc nhập hệ thống CRM.
    """)
