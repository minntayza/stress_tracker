/**
 * charts.js - Trends page grouped bar charts with period filters and clear metadata.
 */

(function () {
    "use strict";

    let chartInstance = null;
    let currentDays = 7;

    function cssVar(name, fallback) {
        const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
        return value || fallback;
    }

    const PALETTE = {
        stress: cssVar("--chart-secondary", "#c76d2b"),
        stressAvg: cssVar("--chart-soft", "#d9b99b"),
        instability: cssVar("--chart-primary", "#102a2a"),
    };

    function getSeriesState() {
        const checks = document.querySelectorAll("[data-series]");
        return Array.from(checks).map((c) => c.checked);
    }

    function hasAnySeriesData(series) {
        if (!series) return false;
        const allValues = []
            .concat(series.stress || [])
            .concat(series.stress_ma7 || [])
            .concat(series.instability || []);
        return allValues.some((v) => v !== null && v !== undefined);
    }

    function countValidPoints(values) {
        return (values || []).filter((v) => v !== null && v !== undefined).length;
    }

    function getValidPoints(values) {
        return (values || [])
            .map((v, i) => ({ x: i, y: v }))
            .filter((point) => point.y !== null && point.y !== undefined);
    }

    function calculateTrendMeta(series) {
        const points = getValidPoints(series?.stress || []);
        if (points.length < 2) {
            return {
                label: "Trend not available yet",
                tone: "muted",
                delta: null,
            };
        }

        const first = points[0].y;
        const last = points[points.length - 1].y;
        const delta = Number((last - first).toFixed(1));

        if (delta <= -5) {
            return { label: `Improving trend (${Math.abs(delta).toFixed(1)} pts down)`, tone: "good", delta };
        }
        if (delta >= 5) {
            return { label: `Rising stress trend (${delta.toFixed(1)} pts up)`, tone: "bad", delta };
        }
        return { label: `Stable trend (Δ ${delta.toFixed(1)} pts)`, tone: "muted", delta };
    }

    function updateStats(entries, series) {
        const stressScores = entries.map((e) => e.stress_score).filter((v) => v != null);
        const sleepVals = entries.map((e) => e.sleep).filter((v) => v != null);
        const avgStress = stressScores.length ? stressScores.reduce((a, b) => a + b, 0) / stressScores.length : null;
        const avgSleep = sleepVals.length ? sleepVals.reduce((a, b) => a + b, 0) / sleepVals.length : null;
        const trendMeta = calculateTrendMeta(series || {});

        const setText = (id, value) => {
            const el = document.getElementById(id);
            if (el) el.textContent = value;
        };

        setText("avgStress", avgStress !== null ? avgStress.toFixed(1) : "-");
        setText("stressDelta", trendMeta.delta !== null ? `${trendMeta.delta > 0 ? "+" : ""}${trendMeta.delta.toFixed(1)}` : "-");
        setText("avgSleep", avgSleep !== null ? `${avgSleep.toFixed(1)}h` : "-");
        setText("entryCount", entries.length);

        const deltaEl = document.getElementById("stressDelta");
        if (deltaEl) {
            deltaEl.classList.remove("text-danger", "text-success", "text-muted");
            if (trendMeta.delta === null) {
                deltaEl.classList.add("text-muted");
            } else if (trendMeta.delta > 0) {
                deltaEl.classList.add("text-danger");
            } else if (trendMeta.delta < 0) {
                deltaEl.classList.add("text-success");
            } else {
                deltaEl.classList.add("text-muted");
            }
        }
    }

    function renderInsights(insights) {
        const container = document.getElementById("insightsContainer");
        if (!container) return;
        container.innerHTML = "";
        (insights || []).forEach((text) => {
            const div = document.createElement("div");
            div.className = "insight-callout";
            div.textContent = text;
            container.appendChild(div);
        });
    }

    function updatePeriodMeta(meta, series) {
        const rangeInfo = document.getElementById("rangeInfo");
        const periodHint = document.getElementById("periodHint");
        const trendSummary = document.getElementById("trendSummary");
        const entryCount = meta.entries_in_period || 0;
        const entryWord = entryCount === 1 ? "entry" : "entries";
        const trendMeta = calculateTrendMeta(series || {});

        if (rangeInfo) {
            rangeInfo.textContent = `Showing ${meta.days} days (${meta.period_start} to ${meta.period_end}) - ${entryCount} saved ${entryWord}`;
        }
        if (periodHint) {
            let hint = meta.period_note || "";
            if (entryCount < 2) {
                const trendHint = `Need at least 2 saved entries in this window to draw a real trend line.`;
                hint = hint ? `${hint} ${trendHint}` : trendHint;
            }
            periodHint.textContent = hint;
        }
        if (trendSummary) {
            trendSummary.textContent = trendMeta.label;
            trendSummary.classList.remove("text-success", "text-danger", "text-muted");
            if (trendMeta.tone === "good") trendSummary.classList.add("text-success");
            else if (trendMeta.tone === "bad") trendSummary.classList.add("text-danger");
            else trendSummary.classList.add("text-muted");
        }
    }

    function buildChartData(series, seriesState) {
        return {
            labels: series.labels || [],
            datasets: [
                {
                    label: "Stress Score (0-100)",
                    data: series.stress || [],
                    yAxisID: "yStress",
                    borderColor: PALETTE.stress,
                    backgroundColor: PALETTE.stress,
                    borderWidth: 1,
                    hidden: !seriesState[0],
                },
                {
                    label: "Stress Trend (7-day average)",
                    data: series.stress_ma7 || [],
                    yAxisID: "yStress",
                    borderColor: PALETTE.stressAvg,
                    backgroundColor: PALETTE.stressAvg,
                    borderWidth: 1,
                    hidden: !seriesState[1],
                },
                {
                    label: "Lifestyle Instability (0-100)",
                    data: series.instability || [],
                    yAxisID: "yStress",
                    borderColor: PALETTE.instability,
                    backgroundColor: PALETTE.instability,
                    borderWidth: 1,
                    hidden: !seriesState[2],
                },
            ],
        };
    }

    function renderChart(series, seriesState) {
        const canvas = document.getElementById("trendChart");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        const data = buildChartData(series, seriesState);

        const stressBandsPlugin = {
            id: "stressBands",
            beforeDraw(chart) {
                const yScale = chart.scales?.yStress;
                const chartArea = chart.chartArea;
                if (!yScale || !chartArea) return;

                const { ctx } = chart;
                const x = chartArea.left;
                const width = chartArea.right - chartArea.left;

                const ranges = [
                    { min: 0, max: 40, color: "rgba(47, 125, 103, 0.08)" },
                    { min: 40, max: 70, color: "rgba(214, 137, 16, 0.08)" },
                    { min: 70, max: 100, color: "rgba(198, 70, 70, 0.08)" },
                ];

                ctx.save();
                ranges.forEach((range) => {
                    const yTop = yScale.getPixelForValue(range.max);
                    const yBottom = yScale.getPixelForValue(range.min);
                    ctx.fillStyle = range.color;
                    ctx.fillRect(x, yTop, width, yBottom - yTop);
                });
                ctx.restore();
            },
        };

        if (chartInstance) {
            chartInstance.data = data;
            chartInstance.update("active");
            return;
        }

        chartInstance = new Chart(ctx, {
            type: "bar",
            data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: "index", intersect: false },
                plugins: {
                    legend: {
                        position: "top",
                        labels: { usePointStyle: true, padding: 14 }
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const y = context.parsed.y;
                                return `${context.dataset.label}: ${y === null ? "-" : y.toFixed(1)}`;
                            }
                        }
                    }
                },
                scales: {
                    yStress: {
                        type: "linear",
                        position: "left",
                        min: 0,
                        max: 100,
                        ticks: { stepSize: 20 },
                        title: { display: true, text: "Stress / Trend / Instability" },
                        grid: { color: "rgba(0,0,0,0.06)" }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { autoSkip: true, maxTicksLimit: 12 }
                    }
                }
            },
            plugins: [stressBandsPlugin]
        });
    }

    function setNoDataState(isNoData) {
        const canvas = document.getElementById("trendChart");
        const noDataMsg = document.getElementById("noDataMsg");
        const statsRow = document.getElementById("statsRow");

        if (canvas && canvas.parentElement) {
            canvas.parentElement.style.display = isNoData ? "none" : "";
        }
        if (noDataMsg) {
            noDataMsg.style.display = isNoData ? "" : "none";
        }
        if (statsRow) {
            statsRow.style.opacity = isNoData ? "0.4" : "1";
        }
    }

    function fetchAndRender(days, seriesState) {
        fetch(`/history/data?days=${days}`, { cache: "no-store" })
            .then((r) => r.json())
            .then(({ entries, insights, series, meta }) => {
                updatePeriodMeta(meta || {
                    days,
                    period_start: "-",
                    period_end: "-",
                    entries_in_period: 0,
                    period_note: "",
                }, series || {});

                if (!series || !hasAnySeriesData(series)) {
                    setNoDataState(true);
                    renderInsights([]);
                    updateStats([], {});
                    return;
                }

                setNoDataState(false);
                updateStats(entries || [], series || {});
                renderInsights(insights || []);
                renderChart(series, seriesState || [true, true, true]);
            })
            .catch((err) => {
                console.error("History data error:", err);
                setNoDataState(true);
            });
    }

    document.addEventListener("DOMContentLoaded", () => {
        document.querySelectorAll(".btn-filter").forEach((btn) => {
            btn.addEventListener("click", () => {
                document.querySelectorAll(".btn-filter").forEach((b) => b.classList.remove("active"));
                btn.classList.add("active");
                currentDays = parseInt(btn.dataset.days, 10);
                fetchAndRender(currentDays, getSeriesState());
            });
        });

        document.querySelectorAll("[data-series]").forEach((chk) => {
            chk.addEventListener("change", () => {
                if (!chartInstance) return;
                const idx = parseInt(chk.dataset.series, 10);
                chartInstance.data.datasets[idx].hidden = !chk.checked;
                chartInstance.update();
            });
        });

        fetchAndRender(currentDays, getSeriesState());
    });
})();
