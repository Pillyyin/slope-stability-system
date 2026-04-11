"""
utils/plots.py
Plotly-based visualization functions for slope stability system.
"""

import math
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.bishop import bishop_fs


# ─── Color helpers ────────────────────────────────────────────────────────────
def fs_color(Fs: float) -> str:
    if Fs >= 1.5:
        return "#16a34a"
    elif Fs >= 1.2:
        return "#d97706"
    elif Fs >= 1.0:
        return "#ea580c"
    return "#dc2626"


# ─── Slope cross-section plot ─────────────────────────────────────────────────
def plot_slope(c, phi, gamma, beta, H, gw_ratio, rain, quake,
               n_slices, slices, Fs) -> go.Figure:

    fig = go.Figure()
    beta_rad = math.radians(beta)
    slope_run = H / math.tan(beta_rad)
    total_x = slope_run * 2.4

    base_y = 0.0
    slope_base_x = total_x * 0.22
    slope_top_x = slope_base_x + slope_run
    top_extend_x = slope_top_x + slope_run * 0.65

    # Ground polygon
    ground_x = [0, slope_base_x, slope_top_x, top_extend_x, top_extend_x, 0, 0]
    ground_y = [0, 0, H, H, -H * 0.15, -H * 0.15, 0]
    fig.add_trace(go.Scatter(
        x=ground_x, y=ground_y, fill="toself",
        fillcolor="rgba(196,160,100,0.55)",
        line=dict(color="#8b6914", width=1.5),
        name="土體", hoverinfo="skip"
    ))

    # Groundwater zone
    if gw_ratio > 0:
        gw_y = gw_ratio * H
        fill_color = "rgba(59,130,246,0.30)" if not rain else "rgba(59,130,246,0.50)"
        fig.add_trace(go.Scatter(
            x=[0, slope_base_x, slope_top_x, top_extend_x, top_extend_x, 0],
            y=[0, 0, H, H, gw_y, gw_y],
            fill="toself", fillcolor=fill_color,
            line=dict(color="#3b82f6", width=1.5, dash="dash"),
            name=f"地下水位 ({gw_ratio:.2f}H)", hoverinfo="skip"
        ))
        # GW label
        fig.add_annotation(
            x=slope_base_x * 0.5, y=gw_y + H * 0.04,
            text=f"💧 地下水位 {gw_y:.1f} m",
            showarrow=False, font=dict(size=11, color="#1d4ed8"),
            bgcolor="rgba(219,234,254,0.85)", bordercolor="#93c5fd", borderwidth=1
        )

    # Slip circle arc
    R_px = H * 1.5
    cx = (slope_base_x + slope_top_x) / 2
    cy = -R_px * 0.35
    theta = np.linspace(math.pi * 0.55, math.pi * 1.05, 80)
    arc_x = cx + R_px * np.cos(theta)
    arc_y = cy + R_px * np.sin(theta)
    # Clip to ground interior
    mask = arc_y <= H * 1.05
    fig.add_trace(go.Scatter(
        x=arc_x[mask], y=arc_y[mask],
        mode="lines",
        line=dict(color="#ef4444", width=2.5, dash="dash"),
        name="圓弧滑動面"
    ))

    # Slice columns
    slice_x_start = slope_base_x * 0.55
    slice_x_end = slope_top_x * 0.98
    sw_px = (slice_x_end - slice_x_start) / n_slices

    for i, s in enumerate(slices):
        sx = slice_x_start + i * sw_px
        top_h = s["height"]
        alpha_rad = math.radians(s["alpha_deg"])

        # Slice rectangle
        fig.add_shape(type="rect",
            x0=sx, x1=sx + sw_px * 0.92,
            y0=0, y1=top_h,
            line=dict(color="rgba(180,120,20,0.7)", width=0.8),
            fillcolor="rgba(251,191,36,0.08)"
        )
        # Weight arrow (downward)
        mid_x = sx + sw_px * 0.46
        arr_len = min(top_h * 0.35, H * 0.18)
        fig.add_annotation(
            x=mid_x, y=top_h - arr_len,
            ax=mid_x, ay=top_h * 0.1,
            xref="x", yref="y", axref="x", ayref="y",
            arrowhead=2, arrowsize=0.8,
            arrowcolor="#f59e0b", arrowwidth=1.5,
            showarrow=True, text="",
        )

    # Seismic indicator
    if quake:
        fig.add_annotation(
            x=total_x * 0.05, y=H * 0.95,
            text="⚡ 地震模擬 kh=0.15g",
            showarrow=False, font=dict(size=11, color="#dc2626"),
            bgcolor="rgba(254,226,226,0.9)", bordercolor="#f87171", borderwidth=1
        )

    # Rain indicator
    if rain:
        fig.add_annotation(
            x=total_x * 0.05, y=H * 0.82,
            text="🌧️ 豪雨模擬 +30% 孔隙壓",
            showarrow=False, font=dict(size=11, color="#1d4ed8"),
            bgcolor="rgba(219,234,254,0.9)", bordercolor="#93c5fd", borderwidth=1
        )

    # Fs annotation
    color = fs_color(Fs)
    fig.add_annotation(
        x=total_x * 0.78, y=H * 0.85,
        text=f"<b>Fs = {Fs:.3f}</b>",
        showarrow=False, font=dict(size=18, color=color),
        bgcolor="white", bordercolor=color, borderwidth=2,
        borderpad=8
    )

    # Dimension arrows
    fig.add_annotation(
        x=slope_base_x, y=-H * 0.08, ax=slope_top_x, ay=-H * 0.08,
        xref="x", yref="y", axref="x", ayref="y",
        arrowhead=2, arrowcolor="#6b7280", arrowwidth=1,
        text=f"L = {slope_run:.1f} m", font=dict(size=10, color="#6b7280")
    )
    fig.add_annotation(
        x=slope_top_x + slope_run * 0.08, y=0,
        ax=slope_top_x + slope_run * 0.08, ay=H,
        xref="x", yref="y", axref="x", ayref="y",
        arrowhead=2, arrowcolor="#6b7280", arrowwidth=1,
        text=f"H = {H} m", font=dict(size=10, color="#6b7280"),
        textangle=-90
    )

    fig.update_layout(
        title=dict(text=f"邊坡剖面圖與 Bishop 切片示意（β={beta}°, H={H}m, φ={phi}°, c={c}kPa）",
                   font=dict(size=13), x=0.01),
        xaxis=dict(title="水平距離 (m)", showgrid=True, gridcolor="#f0f0f0",
                   range=[-total_x * 0.05, total_x * 1.05]),
        yaxis=dict(title="高度 (m)", showgrid=True, gridcolor="#f0f0f0",
                   scaleanchor="x", scaleratio=1,
                   range=[-H * 0.25, H * 1.25]),
        legend=dict(orientation="h", y=-0.18, x=0),
        margin=dict(l=50, r=30, t=50, b=50),
        plot_bgcolor="rgba(240,248,255,0.6)",
        paper_bgcolor="white",
        height=420,
    )
    return fig


# ─── Single-parameter sensitivity plot ───────────────────────────────────────
def plot_sensitivity(param_name, param_range, param_key, base_params, current_val) -> go.Figure:

    fs_list = []
    for val in param_range:
        p = base_params.copy()
        if param_key == "gw":
            p["gw_ratio"] = val
        elif param_key == "c":
            p["c"] = val
        elif param_key == "phi":
            p["phi"] = val
        r = bishop_fs(p["c"], p["phi"], p["gamma"], p["beta"], p["H"],
                      p["gw_ratio"], p["rain"], p["quake"], p["n"])
        fs_list.append(r["Fs"])

    colors = [fs_color(f) for f in fs_list]

    fig = go.Figure()

    # Safety threshold bands
    fig.add_hrect(y0=0, y1=1.0, fillcolor="rgba(239,68,68,0.08)", line_width=0, annotation_text="危險")
    fig.add_hrect(y0=1.0, y1=1.2, fillcolor="rgba(249,115,22,0.08)", line_width=0, annotation_text="警戒")
    fig.add_hrect(y0=1.2, y1=1.5, fillcolor="rgba(234,179,8,0.08)", line_width=0, annotation_text="注意")
    fig.add_hrect(y0=1.5, y1=4.0, fillcolor="rgba(34,197,94,0.05)", line_width=0, annotation_text="安全")

    fig.add_hline(y=1.5, line_dash="dot", line_color="#16a34a", line_width=1.2, annotation_text="Fs=1.5")
    fig.add_hline(y=1.2, line_dash="dot", line_color="#d97706", line_width=1.2, annotation_text="Fs=1.2")
    fig.add_hline(y=1.0, line_dash="dot", line_color="#dc2626", line_width=1.2, annotation_text="Fs=1.0")

    fig.add_trace(go.Scatter(
        x=param_range, y=fs_list,
        mode="lines+markers",
        line=dict(color="#3b82f6", width=2.5),
        marker=dict(color=colors, size=8, line=dict(color="white", width=1)),
        name="Fs"
    ))

    # Current value marker
    cur_fs = bishop_fs(
        base_params["c"], base_params["phi"], base_params["gamma"],
        base_params["beta"], base_params["H"],
        base_params["gw_ratio"], base_params["rain"], base_params["quake"],
        base_params["n"]
    )["Fs"]
    fig.add_trace(go.Scatter(
        x=[current_val], y=[cur_fs],
        mode="markers",
        marker=dict(color="red", size=12, symbol="diamond"),
        name="當前值"
    ))

    fig.update_layout(
        xaxis_title=param_name,
        yaxis_title="安全係數 Fs",
        yaxis=dict(range=[0, min(max(fs_list) * 1.2, 4.0)]),
        legend=dict(orientation="h", y=-0.25),
        margin=dict(l=40, r=20, t=20, b=40),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=260,
    )
    return fig


# ─── Multi-parameter sensitivity (radar/bar) ──────────────────────────────────
def plot_multi_sensitivity(c, phi, gamma, beta, H, gw_ratio, rain, quake, n_slices) -> go.Figure:
    """
    Show how +/-20% change in each parameter affects Fs (tornado chart).
    """
    base = bishop_fs(c, phi, gamma, beta, H, gw_ratio, rain, quake, n_slices)["Fs"]

    params = {
        "凝聚力 c":     ("c",        c,        c * 0.2,    False),
        "內摩擦角 φ":   ("phi",      phi,      phi * 0.2,  False),
        "土體單位重 γ": ("gamma",    gamma,    gamma * 0.1,True),
        "坡角 β":       ("beta",     beta,     beta * 0.15,True),
        "坡高 H":       ("H",        H,        H * 0.2,    True),
        "地下水位比":   ("gw_ratio", gw_ratio, 0.15,        True),
    }

    names, lows, highs = [], [], []

    for label, (key, val, delta, higher_is_worse) in params.items():
        def _fs(**kw):
            kw.setdefault("c", c); kw.setdefault("phi", phi)
            kw.setdefault("gamma", gamma); kw.setdefault("beta", beta)
            kw.setdefault("H", H); kw.setdefault("gw_ratio", gw_ratio)
            return bishop_fs(kw["c"], kw["phi"], kw["gamma"], kw["beta"],
                             kw["H"], kw["gw_ratio"], rain, quake, n_slices)["Fs"]

        val_hi = max(val + delta, 0.01)
        val_lo = max(val - delta, 0.01)
        if key == "gw_ratio":
            val_hi = min(val_hi, 1.0)
            val_lo = max(val_lo, 0.0)

        fs_hi = _fs(**{key: val_hi})
        fs_lo = _fs(**{key: val_lo})

        names.append(label)
        lows.append(round(min(fs_hi, fs_lo) - base, 4))
        highs.append(round(max(fs_hi, fs_lo) - base, 4))

    # Sort by sensitivity (absolute range)
    sensitivity = [abs(h - l) for h, l in zip(highs, lows)]
    order = sorted(range(len(names)), key=lambda i: sensitivity[i])
    names = [names[i] for i in order]
    lows  = [lows[i]  for i in order]
    highs = [highs[i] for i in order]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="正向敏感度（參數增加）",
        y=names, x=highs, orientation="h",
        marker_color="#3b82f6", opacity=0.85
    ))
    fig.add_trace(go.Bar(
        name="負向敏感度（參數減少）",
        y=names, x=lows, orientation="h",
        marker_color="#f87171", opacity=0.85
    ))
    fig.add_vline(x=0, line_color="#374151", line_width=1.5)

    fig.update_layout(
        barmode="overlay",
        title=dict(text=f"各參數敏感度分析（相對基準 Fs={base:.3f} 的變化量）",
                   font=dict(size=13), x=0.01),
        xaxis_title="ΔFs（相對基準）",
        yaxis_title="",
        legend=dict(orientation="h", y=-0.2),
        margin=dict(l=100, r=30, t=45, b=60),
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=320,
    )
    return fig
