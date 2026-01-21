# Charting Pattern: Chart.js + SVG Sparklines

A lightweight, coordinated approach to data visualization that balances rich interactivity with performance.

## The Pattern

| Use Case | Solution | Why |
|----------|----------|-----|
| Full charts (bar, line, pie) | Chart.js | Responsive, tooltips, animations, legends |
| Inline sparklines | Hand-rolled SVG | Lightweight, no library overhead, fast |

## Chart.js Setup

Include via CDN or npm:

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

### Basic Chart Template

```javascript
const ctx = document.getElementById('my-chart');

const chart = new Chart(ctx, {
    type: 'line',  // or 'bar', 'pie', 'doughnut', etc.
    data: {
        labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
        datasets: [{
            label: 'Signups',
            data: [12, 19, 8, 15, 22],
            borderColor: '#10b981',           // emerald-500
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            fill: true,
            tension: 0.4,                     // smooth curves
            pointRadius: 3
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false }        // hide if only one dataset
        },
        scales: {
            y: {
                beginAtZero: true,
                grid: { color: 'rgba(148, 163, 184, 0.1)' }  // subtle grid
            },
            x: {
                grid: { display: false }
            }
        }
    }
});
```

### Destroying and Recreating Charts

When updating chart data (e.g., changing time periods), destroy the old instance first:

```javascript
let myChart = null;

function updateChart(newData) {
    if (myChart) {
        myChart.destroy();
    }

    const ctx = document.getElementById('my-chart');
    myChart = new Chart(ctx, { /* config */ });
}
```

## SVG Sparklines (No Library)

For small inline trend indicators, raw SVG is faster and lighter than a full charting library.

### Sparkline Function

```javascript
function renderSparkline(container, values, color = '#8b5cf6') {
    if (!values || values.length === 0) {
        container.innerHTML = '<span class="text-xs text-slate-400">No data</span>';
        return;
    }

    const width = container.offsetWidth || 100;
    const height = container.offsetHeight || 32;
    const padding = 2;

    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min || 1;

    // Calculate SVG points
    const points = values.map((v, i) => {
        const x = padding + (i / (values.length - 1 || 1)) * (width - 2 * padding);
        const y = height - padding - ((v - min) / range) * (height - 2 * padding);
        return `${x},${y}`;
    });

    // Render SVG with line and end dot
    container.innerHTML = `
        <svg width="${width}" height="${height}" class="sparkline">
            <polyline
                fill="none"
                stroke="${color}"
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
                points="${points.join(' ')}"
            />
            <circle
                cx="${points[points.length - 1].split(',')[0]}"
                cy="${points[points.length - 1].split(',')[1]}"
                r="2"
                fill="${color}"
            />
        </svg>
    `;
}
```

### Usage

```html
<div id="sparkline-users" class="w-24 h-8"></div>
```

```javascript
const last14Days = [12, 15, 11, 18, 22, 19, 25, 23, 28, 30, 27, 32, 35, 38];
renderSparkline(
    document.getElementById('sparkline-users'),
    last14Days,
    '#10b981'  // emerald
);
```

## Color Coordination with Tailwind

Keep chart colors consistent with your UI by using Tailwind's color palette:

```javascript
const CHART_COLORS = {
    violet:  '#8b5cf6',  // violet-500
    emerald: '#10b981',  // emerald-500
    blue:    '#3b82f6',  // blue-500
    cyan:    '#06b6d4',  // cyan-500
    amber:   '#f59e0b',  // amber-500
    rose:    '#f43f5e',  // rose-500
    slate:   '#64748b',  // slate-500
};

// With transparency for fills
const withAlpha = (hex, alpha) => {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};

// Usage
backgroundColor: withAlpha(CHART_COLORS.emerald, 0.1)
```

## Dark Mode Support

Chart.js doesn't auto-detect dark mode. Handle it manually:

```javascript
const isDark = document.documentElement.classList.contains('dark');

const gridColor = isDark
    ? 'rgba(148, 163, 184, 0.1)'   // lighter on dark
    : 'rgba(148, 163, 184, 0.2)';  // darker on light

const textColor = isDark ? '#e2e8f0' : '#334155';
```

## Formatting Helpers

```javascript
function formatNumber(num) {
    return new Intl.NumberFormat('en-US').format(num);
}

function formatCurrency(num) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(num);
}

function formatPercent(num) {
    return `${num.toFixed(1)}%`;
}
```

## When to Use Which

| Scenario | Recommendation |
|----------|----------------|
| Dashboard KPI with trend | Sparkline (SVG) |
| Detailed analytics chart | Chart.js |
| Comparison across categories | Chart.js bar chart |
| Time series deep dive | Chart.js line chart with tooltips |
| Inline table cell trend | Sparkline (SVG) |
| Mobile-first, many charts | Sparklines to reduce bundle size |

## File Organization

```
assets/
├── js/
│   ├── charts/
│   │   ├── sparkline.js      # Reusable sparkline function
│   │   └── chart-config.js   # Shared Chart.js defaults
│   ├── dashboard-overview.js  # Page-specific chart logic
│   └── analytics.js
```

---

*This pattern prioritizes performance (sparklines for small stuff) while keeping rich interactivity where it matters (Chart.js for detailed views).*
