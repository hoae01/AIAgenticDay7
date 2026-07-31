---
name: dashboard-html
description: >
  Tạo file HTML dashboard tĩnh hoàn chỉnh theo tiêu chuẩn thiết kế hiện đại:
  Glassmorphism, Dark Mode, KPI layout với hiệu ứng nhảy số real-time,
  chart tương tác, phối màu tương phản chuyên nghiệp. Kích hoạt khi người
  dùng yêu cầu tạo dashboard, báo cáo trực quan, KPI board, hoặc bất kỳ
  yêu cầu nào liên quan đến "dashboard HTML", "tạo dashboard", "KPI visual",
  "báo cáo HTML", "html report", "dashboard glassmorphism".
---

# Skill: Dashboard HTML (Glassmorphism · Dark Mode · KPI · Real-time)

## Mục tiêu
Tạo ra một file HTML **duy nhất, tự chứa** (self-contained) — không cần backend, không cần npm — hiển thị dữ liệu dưới dạng dashboard hiện đại, đẹp mắt, có thể mở ngay trên trình duyệt.

---

## Quy trình bắt buộc

### Bước 1 — Thu thập dữ liệu & yêu cầu
Trước khi viết code, phải xác định:
- **Nguồn dữ liệu**: user cung cấp số liệu inline / file Excel / JSON / CSV.
- **Chủ đề dashboard**: Sales, HR, Finance, Operations, Marketing, v.v.
- **Các KPI chính** cần hiển thị (tối thiểu 4 KPI cards).
- **Loại biểu đồ** phù hợp (Line, Bar, Doughnut, Area, Radar).
- **Brand colors** nếu có (xem file brand guideline nếu user cung cấp).

Nếu user không cung cấp đủ, hãy dùng **dữ liệu demo hợp lý** nhưng ghi chú rõ ràng.

### Bước 2 — Thiết kế trước khi code
Lập kế hoạch layout:
```
[ Header: Logo + Title + Live Clock ]
[ KPI Row: 4-6 cards ngang ]
[ Chart Row: 1 chart lớn + 1-2 chart nhỏ ]
[ Table Row: Data table hoặc Top-N list ]
[ Footer: Timestamp cập nhật ]
```

### Bước 3 — Triển khai HTML
Tạo file HTML duy nhất theo spec bên dưới.

---

## Tiêu chuẩn thiết kế bắt buộc

### 🌑 Dark Mode Foundation
```css
:root {
  --bg-base:    #0a0e1a;   /* nền ngoài cùng */
  --bg-surface: #0f1629;   /* nền card */
  --bg-glass:   rgba(255, 255, 255, 0.05);
  --border-glass: rgba(255, 255, 255, 0.12);
  --text-primary:   #e8eaf6;
  --text-secondary: #90a4c8;
  --text-muted:     #546e8a;
}
body {
  background: var(--bg-base);
  background-image:
    radial-gradient(ellipse at 20% 50%, rgba(99,102,241,0.15) 0%, transparent 50%),
    radial-gradient(ellipse at 80% 20%, rgba(16,185,129,0.10) 0%, transparent 40%);
  min-height: 100vh;
  font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
}
```

### 🪟 Glassmorphism Cards
```css
.glass-card {
  background: var(--bg-glass);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--border-glass);
  border-radius: 16px;
  box-shadow:
    0 8px 32px rgba(0,0,0,0.3),
    inset 0 1px 0 rgba(255,255,255,0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.glass-card:hover {
  transform: translateY(-4px);
  box-shadow:
    0 16px 48px rgba(0,0,0,0.4),
    inset 0 1px 0 rgba(255,255,255,0.15);
}
```

### 📊 Bảng màu KPI — Tương phản cao
Sử dụng 4 màu accent chính, mỗi màu cho 1 nhóm KPI:

| Token            | Hex       | Dùng cho              |
|------------------|-----------|-----------------------|
| --accent-blue    | #6366f1   | Revenue / Primary     |
| --accent-green   | #10b981   | Growth / Positive     |
| --accent-amber   | #f59e0b   | Warning / Attention   |
| --accent-rose    | #f43f5e   | Risk / Negative / Red |
| --accent-cyan    | #06b6d4   | Info / Secondary      |
| --accent-purple  | #a855f7   | Special / Highlight   |

Mỗi KPI card có gradient border matching accent color của nó:
```css
.kpi-card::before {
  content: '';
  position: absolute; inset: 0;
  border-radius: inherit;
  padding: 1px;
  background: linear-gradient(135deg, var(--accent-color), transparent);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask-composite: exclude;
}
```

### 🔢 Hiệu ứng nhảy số (Counter Animation)
Bắt buộc áp dụng cho mọi giá trị số trong KPI cards:
```javascript
function animateCounter(el, target, duration = 2000, prefix = '', suffix = '', decimals = 0) {
  const start = performance.now();
  const startVal = 0;

  function update(timestamp) {
    const elapsed = timestamp - start;
    const progress = Math.min(elapsed / duration, 1);
    const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
    const current = startVal + (target - startVal) * eased;
    el.textContent = prefix + current.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',') + suffix;
    if (progress < 1) requestAnimationFrame(update);
  }
  requestAnimationFrame(update);
}

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const el = entry.target;
      animateCounter(
        el,
        parseFloat(el.dataset.target),
        2000,
        el.dataset.prefix || '',
        el.dataset.suffix || '',
        parseInt(el.dataset.decimals || 0)
      );
      observer.unobserve(el);
    }
  });
}, { threshold: 0.3 });

document.querySelectorAll('[data-target]').forEach(el => observer.observe(el));
```

Dùng trong HTML:
```html
<span class="kpi-value" data-target="1234567" data-prefix="$" data-decimals="0">$0</span>
<span class="kpi-value" data-target="98.5" data-suffix="%" data-decimals="1">0%</span>
```

### ⏱️ Live Clock & Auto-refresh Timestamp
```javascript
function updateClock() {
  const now = new Date();
  document.getElementById('live-clock').textContent =
    now.toLocaleTimeString('vi-VN', { hour12: false });
  document.getElementById('last-updated').textContent =
    'Cập nhật: ' + now.toLocaleString('vi-VN');
}
setInterval(updateClock, 1000);
updateClock();
```

### 📈 Biểu đồ với Chart.js
Luôn load Chart.js từ CDN:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
```

Cấu hình chart dark-mode mặc định:
```javascript
Chart.defaults.color = '#90a4c8';
Chart.defaults.borderColor = 'rgba(255,255,255,0.06)';
Chart.defaults.font.family = "'Inter', 'Segoe UI', system-ui";

function createGradient(ctx, colorTop, colorBottom) {
  const gradient = ctx.createLinearGradient(0, 0, 0, 300);
  gradient.addColorStop(0, colorTop);
  gradient.addColorStop(1, colorBottom);
  return gradient;
}
```

### 🏗️ Layout Grid Responsive
```css
.dashboard-grid {
  display: grid;
  gap: 20px;
  padding: 24px;
  max-width: 1600px;
  margin: 0 auto;
}
.kpi-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}
.chart-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}
@media (max-width: 1024px) {
  .chart-row { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .kpi-row { grid-template-columns: 1fr 1fr; }
  .dashboard-grid { padding: 12px; gap: 12px; }
}
```

### 🔔 Pulse Badge (Trạng thái Live)
```css
.live-badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 10px;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 999px;
  font-size: 11px; font-weight: 600;
  color: #10b981; letter-spacing: 0.5px;
}
.pulse-dot {
  width: 6px; height: 6px;
  background: #10b981;
  border-radius: 50%;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50%       { opacity: 0.4; transform: scale(1.5); }
}
```

---

## Cấu trúc file HTML bắt buộc

```html
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[TÊN DASHBOARD] | Dashboard</title>
  <meta name="description" content="[Mô tả ngắn]">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
  <style>
    /* === CSS Variables === */
    /* === Reset & Base === */
    /* === Layout === */
    /* === Glass Cards === */
    /* === KPI Cards === */
    /* === Charts === */
    /* === Tables === */
    /* === Animations === */
    /* === Responsive === */
  </style>
</head>
<body>
  <!-- Header -->
  <header class="dashboard-header">...</header>

  <main class="dashboard-grid">
    <!-- KPI Row -->
    <section class="kpi-row" aria-label="Key Performance Indicators">
      <!-- 4-6 .kpi-card elements -->
    </section>

    <!-- Chart Row -->
    <section class="chart-row">
      <!-- Main chart (2/3 width) + Secondary chart (1/3 width) -->
    </section>

    <!-- Data Table / Top List -->
    <section class="data-section">...</section>
  </main>

  <!-- Footer -->
  <footer class="dashboard-footer">
    <span id="last-updated"></span>
  </footer>

  <script>
    /* === Counter Animation === */
    /* === Chart.js Setup === */
    /* === Chart Definitions === */
    /* === Live Clock === */
    /* === IntersectionObserver === */
  </script>
</body>
</html>
```

---

## Checklist trước khi giao file

- [ ] Tất cả số trong KPI có data-target và hiệu ứng nhảy số
- [ ] Có live clock hiển thị giờ thực
- [ ] Có ít nhất 2 loại biểu đồ khác nhau
- [ ] Glassmorphism áp dụng đúng (backdrop-filter)
- [ ] Hover effect trên mọi card
- [ ] Responsive hoạt động ở 320px, 768px, 1280px
- [ ] Không có placeholder text (Lorem ipsum), dữ liệu phải có nghĩa
- [ ] File chạy được khi double-click
- [ ] Màu sắc dùng đúng bảng accent, không dùng màu plain (red, blue, green)
- [ ] Có trend indicator (▲/▼) và % change cho mỗi KPI

---

## Tham khảo thêm
Xem file mẫu trong examples/sample_dashboard.html để có bản triển khai đầy đủ.
Xem references/design_tokens.md để tra cứu toàn bộ design token.
