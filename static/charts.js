/**
 * charts.js - Trends page line charts with period filters and clear metadata.
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
        sleep: cssVar("--chart-tertiary", "#4f6f64"),
        screen: cssVar("--chart-muted", "#8b7f73"),
        mood: cssVar("--success-color", "#2f7d67"),
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
            .concat(series.instability || [])
            .concat(series.sleep || [])
            .concat(series.screen_time || [])
            .concat(series.mood || []);
        return allValues.some((v) => v !== null && v !== undefined);
    }

    function countValidPoints(values) {
        return (values || []).filter((v) => v !== null && v !== undefined).length;
    }

    function updateStats(entries) {
        const stressScores = entries.map((e) => e.stress_score).filter((v) => v != null);
        const sleepVals = entries.map((e) => e.sleep).filter((v) => v != null);
        const avgStress = stressScores.length ? stressScores.reduce((a, b) => a + b, 0) / stressScores.length : null;
        const peakStress = stressScores.length ? Math.max(...stressScores) : null;
        const avgSleep = sleepVals.length ? sleepVals.reduce((a, b) => a + b, 0) / sleepVals.length : null;

        const setText = (id, value) => {
            const el = document.getElementById(id);
            if (el) el.textContent = value;
        };

        setText("avgStress", avgStress !== null ? avgStress.toFixed(1) : "-");
        setText("peakStress", peakStress !== null ? peakStress.toFixed(1) : "-");
        setText("avgSleep", avgSleep !== null ? `${avgSleep.toFixed(1)}h` : "-");
        setText("entryCount", entries.length);
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

    function updatePeriodMeta(meta) {
        const rangeInfo = document.getElementById("rangeInfo");
        const periodHint = document.getElementById("periodHint");
        const entryCount = meta.entries_in_period || 0;
        const entryWord = entryCount === 1 ? "entry" : "entries";

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
    }

    function buildChartData(series, seriesState) {
        const stressLine = countValidPoints(series.stress) >= 2;
        const stressAvgLine = countValidPoints(series.stress_ma7) >= 2;
        const instabilityLine = countValidPoints(series.instability) >= 2;
        const sleepLine = countValidPoints(series.sleep) >= 2;
        const screenLine = countValidPoints(series.screen_time) >= 2;
        const moodLine = countValidPoints(series.mood) >= 2;

        return {
            labels: series.labels || [],
            datasets: [
                {
                    label: "Stress Score (0-100)",
                    data: series.stress || [],
                    yAxisID: "yStress",
                    borderColor: PALETTE.stress,
                    backgroundColor: "transparent",
                    borderWidth: 2.5,
                    tension: 0.3,
                    pointRadius: stressLine ? 4 : 5,
                    pointHoverRadius: 5,
                    pointBackgroundColor: PALETTE.stress,
                    pointBorderColor: "#fff",
                    pointBorderWidth: 1.5,
                    spanGaps: false,
                    showLine: stressLine,
                    hidden: !seriesState[0],
                },
                {
                    label: "Stress Trend (7-day average)",
                    data: series.stress_ma7 || [],
                    yAxisID: "yStress",
                    borderColor: PALETTE.stressAvg,
                    backgroundColor: "transparent",
                    borderDash: [4, 4],
                    borderWidth: 2,
                    tension: 0.3,
                    pointRadius: stressAvgLine ? 3.5 : 5,
                    pointHoverRadius: 5,
                    pointBackgroundColor: PALETTE.stressAvg,
                    pointBorderColor: "#fff",
                    pointBorderWidth: 1.5,
                    spanGaps: false,
                    showLine: stressAvgLine,
                    hidden: !seriesState[1],
                },
                {
                    label: "Lifestyle Instability (0-100)",
                    data: series.instability || [],
                    yAxisID: "yStress",
                    borderColor: PALETTE.instability,
                    backgroundColor: "transparent",
                    borderDash: [6, 4],
                    borderWidth: 2,
                    tension: 0.3,
                    pointRadius: instabilityLine ? 4 : 5,
                    pointHoverRadius: 5,
                    pointBackgroundColor: PALETTE.instability,
                    pointBorderColor: "#fff",
                    pointBorderWidth: 1.5,
                    spanGaps: false,
                    showLine: instabilityLine,
                    hidden: !seriesState[2],
                },
                {
                    label: "Sleep (hours)",
                    data: series.sleep || [],
                    yAxisID: "yFactor",
                    borderColor: PALETTE.sleep,
                    backgroundColor: "transparent",
                    borderWidth: 2,
                    tension: 0.3,
                    pointRadius: sleepLine ? 4 : 5,
                    pointHoverRadius: 5,
                    pointBackgroundColor: PALETTE.sleep,
                    pointBorderColor: "#fff",
                    pointBorderWidth: 1.5,
                    spanGaps: false,
                    showLine: sleepLine,
                    hidden: !seriesState[3],
                },
                {
                    label: "Screen Time (hours)",
                    data: series.screen_time || [],
                    yAxisID: "yFactor",
                    borderColor: PALETTE.screen,
                    backgroundColor: "transparent",
                    borderWidth: 2,
                    tension: 0.3,
                    pointRadius: screenLine ? 4 : 5,
                    pointHoverRadius: 5,
                    pointBackgroundColor: PALETTE.screen,
                    pointBorderColor: "#fff",
                    pointBorderWidth: 1.5,
                    spanGaps: false,
                    showLine: screenLine,
                    hidden: !seriesState[4],
                },
                {
                    label: "Mood (1-10)",
                    data: series.mood || [],
                    yAxisID: "yFactor",
                    borderColor: PALETTE.mood,
                    backgroundColor: "transparent",
                    borderWidth: 2,
                    tension: 0.3,
                    pointRadius: moodLine ? 4 : 5,
                    pointHoverRadius: 5,
                    pointBackgroundColor: PALETTE.mood,
                    pointBorderColor: "#fff",
                    pointBorderWidth: 1.5,
                    spanGaps: false,
                    showLine: moodLine,
                    hidden: !seriesState[5],
                },
            ],
        };
    }

    function renderChart(series, seriesState) {
        const canvas = document.getElementById("trendChart");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        const data = buildChartData(series, seriesState);

        if (chartInstance) {
            chartInstance.data = data;
            chartInstance.update("active");
            return;
        }

        chartInstance = new Chart(ctx, {
            type: "line",
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
                        title: { display: true, text: "Stress / Instability" },
                        grid: { color: "rgba(0,0,0,0.06)" }
                    },
                    yFactor: {
                        type: "linear",
                        position: "right",
                        min: 0,
                        max: 24,
                        ticks: { stepSize: 4 },
                        title: { display: true, text: "Sleep / Screen / Mood" },
                        grid: { drawOnChartArea: false }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { autoSkip: true, maxTicksLimit: 12 }
                    }
                }
            }
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
                });

                if (!series || !hasAnySeriesData(series)) {
                    setNoDataState(true);
                    renderInsights([]);
                    updateStats([]);
                    return;
                }

                setNoDataState(false);
                updateStats(entries || []);
                renderInsights(insights || []);
                renderChart(series, seriesState || [true, true, true, false, false, false]);
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
