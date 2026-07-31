---
name: lead-scoring
description: Hướng dẫn AI lấy dữ liệu khách hàng từ Google Sheets và tự động thực hiện chấm điểm Lead Scoring cho ngành Bất động sản theo quy tắc Knowledge base. Kích hoạt khi người dùng yêu cầu chấm điểm lead, đánh giá khách hàng BĐS, xử lý dữ liệu Google Sheet lead scoring, hoặc chạy AI Lead Agent.
---

# SKILL: LEAD SCORING DÀNH CHO NGÀNH BẤT ĐỘNG SẢN

Skill này hướng dẫn AI quy trình kết nối dữ liệu lead từ Google Sheets, phân tích nội dung nhu cầu khách hàng, áp dụng bộ tiêu chí chấm điểm ngành Bất động sản và xuất kết quả phân loại.

---

## 1. NGUỒN DỮ LIỆU GOOGLE SHEETS
- **URL Google Sheet mặc định**: 
  `https://docs.google.com/spreadsheets/d/1DyN6I3_5hVfMpszVom4enaKu2ZKxHInwf6RXrkTg1uo/edit?gid=1542775777#gid=1542775777`
- **Link xuất CSV trực tiếp**: 
  `https://docs.google.com/spreadsheets/d/1DyN6I3_5hVfMpszVom4enaKu2ZKxHInwf6RXrkTg1uo/export?format=csv&gid=1542775777`
- **Cấu trúc dữ liệu chuẩn**:
  - `id`: Mã định danh khách hàng
  - `ten_khach`: Họ và tên
  - `sdt`: Số điện thoại
  - `nhu_cau_mo_ta`: Nội dung ghi chú / chi tiết nhu cầu tìm kiếm BĐS của khách

---

## 2. QUY TẮC CHẤM ĐIỂM (LEAD SCORING RULES)

Dựa trên file Knowledge `knowledge-base/tieu_chi_cham_diem.txt`, AI thực hiện đánh giá theo các nhóm tiêu chí:

### A. Tiêu chí CỘNG 50 ĐIỂM (Khách VIP / Tiềm năng cao)
AI nhận diện các cụm từ & ngữ cảnh sau:
1. **Ngân sách lớn**: Đề cập ngân sách từ **20 tỷ** trở lên, "tài chính mạnh", "không thành vấn đề", "tài chính sẵn sàng".
2. **Loại hình BĐS cao cấp**: "Biệt thự đơn lập", "Penthouse", "Shophouse mặt đường lớn", "Quỹ đất công nghiệp", "Sàn văn phòng diện tích lớn".
3. **Vị trí đắc địa**: "Quận 1", "Ven sông", "Vinhomes Ocean Park", "Phú Mỹ Hưng", "Trung tâm TP".
4. **Chân dung VIP**: "Chủ doanh nghiệp", "Nhà đầu tư chuyên nghiệp", "Mua sỉ", "Mua số lượng lớn".
5. **Cấp thiết & Minh bạch**: "Pháp lý chuẩn 100%", "Sổ hồng riêng", "Muốn gặp trực tiếp chủ đầu tư", "Cần mua gấp trong tháng".

### B. Tiêu chí TRỪ 50 ĐIỂM (Khách Rác / Không tiềm năng)
AI phát hiện các dấu hiệu:
1. **Yêu cầu phi thực tế**: Giá quá thấp vô lý so với khu vực (VD: Nhà Quận 1 giá 1-2 tỷ, biệt thự trung tâm vài trăm triệu).
2. **Không có nhu cầu / Nhầm số**: "Nhầm số", "Không có nhu cầu", "Dữ liệu cũ", "Nhầm ngành".
3. **Thái độ / Không thiện chí**: "Hỏi giá cho vui", "Chưa có ý định mua", "Thái độ không hợp tác", "Đóng máy ngang".
4. **Spam / Quảng cáo**: Mời chào "Bảo hiểm", "Vay vốn", "Tư vấn chứng khoán", dịch vụ ngoài.
5. **Lỗi liên lạc**: "Thuê bao", "Gọi nhiều lần không bắt máy", "Không phản hồi Zalo", "Số không có thật".

### C. Trường hợp CÂN BẰNG (0 đến +20 ĐIỂM)
- Nhu cầu nhà ở tầm trung (Căn hộ, nhà phố 3-10 tỷ).
- Cần vay ngân hàng, tham khảo chính sách thanh toán.
- Nhu cầu thực nhưng cần tư vấn thêm về pháp lý hoặc quy hoạch.

---

## 3. PHÂN LOẠI LEAD (LEAD CLASSIFICATION)

| Tổng điểm | Phân loại | Hành động khuyến nghị cho Sales |
|---|---|---|
| **>= 50** | 🌟 **HOT (VIP)** | Chuyển ngay cho Super Sales / Gặp trực tiếp trong 2 giờ |
| **0 - 49** | 🟡 **WARM** | Chăm sóc chuẩn, gửi bảng giá & tư vấn thêm |
| **-49 - -1** | 🔵 **COLD** | Cho vào luồng Nurturing / Gửi thông tin tự động qua Zalo |
| **<= -50** | 🔴 **JUNK (Rác)** | Lọc bỏ, dừng liên lạc để tiết kiệm tài nguyên |

---

## 4. HƯỚNG DẪN XỬ LÝ TRONG ỨNG DỤNG STREAMLIT (`app_lead_scoring.py`)

1. **Đọc dữ liệu**: Sử dụng pandas đọc từ link export CSV Google Sheet.
2. **Đọc Knowledge**: Nạp nội dung từ `knowledge-base/tieu_chi_cham_diem.txt` làm quy tắc gốc.
3. **AI Agent Logic**: Duyệt từng dòng lead, phân tích văn bản trong `nhu_cau_mo_ta`, tính điểm tổng, liệt kê các lý do (+50 vì sao, -50 vì sao).
4. **Hiển thị & Tương tác**: 
   - Đưa dữ liệu vào `st.data_editor`.
   - Cung cấp các cột: `AI Scoring` (Điểm), `Phân loại`, `Lý do AI`, `Duyệt` (`Chờ duyệt`, `Đã duyệt`, `Từ chối`), `Ghi chú Sales`.
   - Cho phép Sales/Manager xem, lọc theo trạng thái duyệt, chỉnh sửa trực tiếp và xuất file Excel/CSV.
