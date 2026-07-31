# Design Tokens — Dashboard HTML Skill

Tài liệu tra cứu đầy đủ tất cả design token, màu sắc, spacing, typography và animation
được sử dụng trong skill `dashboard-html`.

---

## 1. Color Palette

### Base Colors (Dark Mode Foundation)
| Token              | Value                        | Mô tả                          |
|--------------------|------------------------------|--------------------------------|
| `--bg-base`        | `#0a0e1a`                    | Background ngoài cùng          |
| `--bg-surface`     | `#0f1629`                    | Background card/panel          |
| `--bg-glass`       | `rgba(255,255,255,0.05)`     | Glass morphism fill            |
| `--border-glass`   | `rgba(255,255,255,0.10)`     | Border mặc định glass card     |
| `--border-hover`   | `rgba(255,255,255,0.20)`     | Border khi hover               |

### Text Colors
| Token               | Value       | Dùng cho                          |
|---------------------|-------------|-----------------------------------|
| `--text-primary`    | `#e8eaf6`   | Tiêu đề, số KPI, nội dung quan trọng |
| `--text-secondary`  | `#90a4c8`   | Body text, label phụ              |
| `--text-muted`      | `#546e8a`   | Hint, caption, placeholder        |

### Accent Colors (KPI & Chart)
| Token              | Hex       | RGB                  | Dùng cho                        |
|--------------------|-----------|----------------------|---------------------------------|
| `--accent-blue`    | `#6366f1` | 99, 102, 241         | Revenue / Primary metric        |
| `--accent-green`   | `#10b981` | 16, 185, 129         | Growth / Positive trend         |
| `--accent-amber`   | `#f59e0b` | 245, 158, 11         | Warning / Attention / Rank #1   |
| `--accent-rose`    | `#f43f5e` | 244, 63, 94          | Risk / Negative / Danger        |
| `--accent-cyan`    | `#06b6d4` | 6, 182, 212          | Info / Secondary metric         |
| `--accent-purple`  | `#a855f7` | 168, 85, 247         | Special / Feature / Rank #3     |

### Chart Color Palette (ordered)
```
1. rgba(99, 102, 241, 0.85)   — blue
2. rgba(16, 185, 129, 0.85)   — green
3. rgba(245, 158, 11, 0.85)   — amber
4. rgba(168, 85, 247, 0.85)   — purple
5. rgba(6, 182, 212, 0.85)    — cyan
6. rgba(244, 63, 94, 0.85)    — rose
```

---

## 2. Typography

### Font Stack
```css
font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
```
Import từ Google Fonts:
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
```

### Type Scale
| Role              | Size    | Weight | Color             |
|-------------------|---------|--------|-------------------|
| Dashboard title   | 18px    | 700    | `--text-primary`  |
| Card title        | 15px    | 700    | `--text-primary`  |
| KPI value         | 28-34px | 800    | `--text-primary`  |
| KPI label         | 11px    | 600    | `--text-muted`    |
| Body / table      | 13px    | 400    | `--text-secondary`|
| Caption / badge   | 11px    | 600    | varies            |
| Live clock        | 15px    | 600    | `--text-secondary`|

---

## 3. Spacing & Sizing

| Token          | Value   | Dùng cho                        |
|----------------|---------|---------------------------------|
| Grid gap       | 22px    | Khoảng cách giữa các khu vực   |
| KPI gap        | 18px    | Khoảng cách giữa KPI cards     |
| Card padding   | 22-24px | Padding bên trong card          |
| Border radius  | 16px    | Card, panel                     |
| Border radius  | 8-10px  | Button, badge, icon wrapper     |
| Border radius  | 999px   | Pill badge, trend indicator     |

---

## 4. Shadows

| Context       | Value                                                     |
|---------------|-----------------------------------------------------------|
| Card default  | `0 8px 32px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.08)` |
| Card hover    | `0 20px 60px rgba(0,0,0,0.50), inset 0 1px 0 rgba(255,255,255,0.12)` |

---

## 5. Transitions & Animations

### Transition
```css
transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1),
            box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1),
            border-color 0.3s cubic-bezier(0.4, 0, 0.2, 1);
```

### Hover — Card lift
```css
transform: translateY(-4px);
```

### Fade-in-up (entry animation)
```css
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(24px); }
  to   { opacity: 1; transform: translateY(0); }
}
/* Stagger delays: nth-child +0.05s each */
```

### Pulse (Live badge dot)
```css
@keyframes pulse-anim {
  0%, 100% { opacity: 1; transform: scale(1); box-shadow: 0 0 0 0 rgba(16,185,129,0.6); }
  50%       { opacity: 0.6; transform: scale(1.4); box-shadow: 0 0 0 4px rgba(16,185,129,0); }
}
animation: pulse-anim 2s ease-in-out infinite;
```

### Counter animation easing — easeOutExpo
```javascript
const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
```
Recommended duration: **2000–2400ms**

---

## 6. Layout Grid

### Dashboard Container
```css
max-width: 1600px;
margin: 0 auto;
padding: 28px;
display: grid;
gap: 22px;
```

### KPI Row
```css
grid-template-columns: repeat(4, 1fr);   /* desktop */
grid-template-columns: repeat(2, 1fr);   /* tablet  */
grid-template-columns: repeat(2, 1fr);   /* mobile  */
```

### Chart Row
```css
grid-template-columns: 2fr 1fr;   /* desktop: main + secondary */
grid-template-columns: 1fr;       /* tablet/mobile: stack     */
```

### Bottom Row (Table + Stats)
```css
grid-template-columns: 3fr 2fr;   /* desktop */
grid-template-columns: 1fr;       /* tablet/mobile */
```

### Breakpoints
| Breakpoint | Max-width | Change                          |
|------------|-----------|---------------------------------|
| Desktop    | > 1200px  | Full 4-col KPI, 2:1 chart       |
| Tablet     | ≤ 1200px  | 2-col KPI, stacked charts       |
| Mobile     | ≤ 640px   | 2-col KPI, tighter padding      |

---

## 7. Glassmorphism Recipe

```css
background: rgba(255, 255, 255, 0.05);
backdrop-filter: blur(20px) saturate(180%);
-webkit-backdrop-filter: blur(20px) saturate(180%);
border: 1px solid rgba(255, 255, 255, 0.10);
border-radius: 16px;
box-shadow: 0 8px 32px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.08);
```

> **Lưu ý**: backdrop-filter hoạt động khi có background đủ phức tạp (gradient/image) phía sau.
> Luôn dùng radial-gradient background cho body.

---

## 8. Chart.js Dark Mode Config

```javascript
Chart.defaults.color        = '#90a4c8';          // axis text
Chart.defaults.borderColor  = 'rgba(255,255,255,0.06)'; // gridlines
Chart.defaults.font.family  = "'Inter', 'Segoe UI', system-ui";
Chart.defaults.font.size    = 12;

// Tooltip
tooltip: {
  backgroundColor : 'rgba(15,22,41,0.95)',
  borderColor     : 'rgba(255,255,255,0.12)',
  borderWidth     : 1,
  padding         : 12,
}

// Gridline override per chart
scales.x.grid.color = 'rgba(255,255,255,0.04)';
scales.y.grid.color = 'rgba(255,255,255,0.04)';
```

---

## 9. CDN Dependencies

| Library    | Version | CDN URL                                                          |
|------------|---------|------------------------------------------------------------------|
| Chart.js   | 4.4.0   | `https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js` |
| Google Fonts (Inter) | — | `https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap` |

---

## 10. KPI Card Color Mapping

| Metric type               | Accent class  | Hex       |
|---------------------------|---------------|-----------|
| Revenue / Sales           | `.blue`       | `#6366f1` |
| Growth / New customers    | `.green`      | `#10b981` |
| Warning / Conversion rate | `.amber`      | `#f59e0b` |
| Churn / Risk / Cost       | `.rose`       | `#f43f5e` |
| Visits / Impressions      | `.cyan`       | `#06b6d4` |
| Premium / Featured        | `.purple`     | `#a855f7` |
