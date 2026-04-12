# -*- coding: utf-8 -*-
"""
utils/plots.py
負責所有圖表的繪製，使用 Plotly 產生互動式圖形
"""

import math
import numpy as np
import plotly.graph_objects as go
from utils.bishop import bishop_fs


# ─────────────────────────────────────────────
# 輔助函式：根據安全係數回傳對應顏色
# Fs >= 1.5 綠色(安全) / >= 1.2 黃色(注意)
# >= 1.0 橘色(警戒) / < 1.0 紅色(危險)
# ─────────────────────────────────────────────
def fs_color(Fs):
    if Fs >= 1.5: return "#16a34a"   # 綠色
    elif Fs >= 1.2: return "#d97706" # 黃色
    elif Fs >= 1.0: return "#ea580c" # 橘色
    return "#dc2626"                 # 紅色


# ─────────────────────────────────────────────
# 函式一：繪製邊坡剖面圖
# 包含：土體、地下水位、圓弧滑動面、土條切片
# ─────────────────────────────────────────────
def plot_slope(c, phi, gamma, beta, H, gw_ratio, rain, quake, n_slices, slices, Fs):
    fig = go.Figure()

    # 計算邊坡幾何尺寸
    beta_rad = math.radians(beta)       # 坡角轉換為弧度
    slope_run = H / math.tan(beta_rad)  # 坡面水平投影長度
    total_x = slope_run * 2.4           # 圖形總寬度

    # 定義坡腳、坡頂、延伸點的 x 座標
    slope_base_x = total_x * 0.22
    slope_top_x = slope_base_x + slope_run
    top_extend_x = slope_top_x + slope_run * 0.65

    # ── 繪製土體填充區域 ──
    ground_x = [0, slope_base_x, slope_top_x, top_extend_x, top_extend_x, 0, 0]
    ground_y = [0, 0, H, H, -H*0.15, -H*0.15, 0]
    fig.add_trace(go.Scatter(
        x=ground_x, y=ground_y,
        fill="toself",                          # 填滿封閉區域
        fillcolor="rgba(196,160,100,0.55)",     # 土黃色
        line=dict(color="#8b6914", width=1.5),  # 邊框深棕色
        name="soil", hoverinfo="skip"))

    # ── 繪製地下水位區域（只有 gw_ratio > 0 才繪製）──
    if gw_ratio > 0:
        gw_y = gw_ratio * H  # 地下水位高度
        # 豪雨時水色更深
        fill_color = "rgba(59,130,246,0.50)" if rain else "rgba(59,130,246,0.30)"
        fig.add_trace(go.Scatter(
            x=[0, slope_base_x, slope_top_x, top_extend_x, top_extend_x, 0],
            y=[0, 0, H, H, gw_y, gw_y],
            fill="toself", fillcolor=fill_color,
            line=dict(color="#3b82f6", width=1.5, dash="dash"),  # 藍色虛線
            name=f"GW ({gw_ratio:.2f}H)", hoverinfo="skip"))
        # 地下水位標籤
        fig.add_annotation(
            x=slope_base_x*0.5, y=gw_y+H*0.04,
            text=f"Groundwater {gw_y:.1f} m",
            showarrow=False,
            font=dict(size=11, color="#1d4ed8"),
            bgcolor="rgba(219,234,254,0.85)", bordercolor="#93c5fd", borderwidth=1)

    # ── 繪製圓弧滑動面 ──
    R_px = H * 1.5                              # 滑動圓弧半徑
    cx = (slope_base_x + slope_top_x) / 2      # 圓心 x（坡面中點）
    cy = -R_px * 0.35                           # 圓心 y（坡面下方）
    theta = np.linspace(math.pi*0.55, math.pi*1.05, 80)  # 角度範圍
    arc_x = cx + R_px * np.cos(theta)           # 圓弧 x 座標
    arc_y = cy + R_px * np.sin(theta)           # 圓弧 y 座標
    mask = arc_y <= H * 1.05                    # 只顯示土體範圍內的弧線
    fig.add_trace(go.Scatter(
        x=arc_x[mask], y=arc_y[mask],
        mode="lines",
        line=dict(color="#ef4444", width=2.5, dash="dash"),  # 紅色虛線
        name="Slip Circle"))

    # ── 繪製 Bishop 土條切片 ──
    slice_x_start = slope_base_x * 0.55
    slice_x_end = slope_top_x * 0.98
    sw_px = (slice_x_end - slice_x_start) / n_slices  # 每個切片的寬度（像素）

    for i, s in enumerate(slices):
        sx = slice_x_start + i * sw_px  # 切片左邊界 x
        top_h = s["height"]             # 切片頂部高度

        # 畫切片矩形框
        fig.add_shape(
            type="rect",
            x0=sx, x1=sx+sw_px*0.92,
            y0=0, y1=top_h,
            line=dict(color="rgba(180,120,20,0.7)", width=0.8),
            fillcolor="rgba(251,191,36,0.08)")  # 淡黃色填充

        # 畫重量箭頭（向下）
        mid_x = sx + sw_px * 0.46
        arr_len = min(top_h * 0.35, H * 0.18)
        fig.add_annotation(
            x=mid_x, y=top_h-arr_len,
            ax=mid_x, ay=top_h*0.1,
            xref="x", yref="y", axref="x", ayref="y",
            arrowhead=2, arrowsize=0.8,
            arrowcolor="#f59e0b", arrowwidth=1.5,
            showarrow=True, text="")

    # ── 情境模擬標籤 ──
    if quake:
        fig.add_annotation(
            x=total_x*0.05, y=H*0.95,
            text="Seismic kh=0.15g",
            showarrow=False,
            font=dict(size=11, color="#dc2626"),
            bgcolor="rgba(254,226,226,0.9)", bordercolor="#f87171", borderwidth=1)
    if rain:
        fig.add_annotation(
            x=total_x*0.05, y=H*0.82,
            text="Heavy Rain +30% Pore Pressure",
            showarrow=False,
            font=dict(size=11, color="#1d4ed8"),
            bgcolor="rgba(219,234,254,0.9)", bordercolor="#93c5fd", borderwidth=1)

    # ── 安全係數標示（右上角）──
    color = fs_color(Fs)
    fig.add_annotation(
        x=total_x*0.78, y=H*0.85,
        text=f"<b>Fs = {Fs:.3f}</b>",
        showarrow=False,
        font=dict(size=18, color=color),
        bgcolor="white", bordercolor=color, borderwidth=2, borderpad=8)

    # ── 圖表版面設定 ──
    fig.update_layout(
        title=dict(
            text=f"Slope Profile (beta={beta}, H={H}m, phi={phi}, c={c}kPa)",
            font=dict(size=13), x=0.01),
        xaxis=dict(title="Horizontal Distance (m)", showgrid=True,
                   gridcolor="#f0f0f0", range=[-total_x*0.05, total_x*1.05]),
        yaxis=dict(title="Height (m)", showgrid=True, gridcolor="#f0f0f0",
                   scaleanchor="x", scaleratio=1, range=[-H*0.25, H*1.25]),
        legend=dict(orientation="h", y=-0.22, x=0), # 稍微下調避免擋到標籤
        
        # --- 新增標籤設定，解決重疊問題 ---
        annotations=[
            # Fs=1.5 Safe (放線的右上方)
            dict(x=total_x, y=1.5, text="Fs=1.5 Safe", showarrow=False, 
                 xanchor="right", yanchor="bottom", yshift=5, font=dict(color="green", size=11)),
            
            # Fs=1.2 Warning (放線的右下方，避免擠在同一高度)
            dict(x=total_x, y=1.2, text="Fs=1.2 Warning", showarrow=False, 
                 xanchor="right", yanchor="top", yshift=-5, font=dict(color="orange", size=11)),
            
            # Fs=1.0 Danger (再往下移一點)
            dict(x=total_x, y=1.0, text="Fs=1.0 Alert/Danger", showarrow=False, 
                 xanchor="right", yanchor="top", yshift=-25, font=dict(color="red", size=11))
        ],
        # ----------------------------

        margin=dict(l=50, r=30, t=50, b=80), # 底部 margin 增加，給 legend 更多空間
        plot_bgcolor="rgba(240,248,255,0.6)",
        paper_bgcolor="white",
        height=450) # 高度稍微增加一點，看起來比較不擠
    
    return fig


# ─────────────────────────────────────────────
# 函式二：繪製單一參數敏感度折線圖
# 例如：地下水位從 0 到 1.0，Fs 如何變化
# ─────────────────────────────────────────────
def plot_sensitivity(param_name, param_range, param_key, base_params, current_val):
    fs_list = []

    # 對每個參數值計算對應的 Fs
    for val in param_range:
        p = base_params.copy()
        if param_key == "gw":  p["gw_ratio"] = val
        elif param_key == "c": p["c"] = val
        elif param_key == "phi": p["phi"] = val
        r = bishop_fs(p["c"], p["phi"], p["gamma"], p["beta"], p["H"],
                      p["gw_ratio"], p["rain"], p["quake"], p["n"])
        fs_list.append(r["Fs"])

    # 根據 Fs 值設定各點顏色
    colors = [fs_color(f) for f in fs_list]

    fig = go.Figure()

    # 背景色帶：標示安全等級區間
    fig.add_hrect(y0=0,   y1=1.0, fillcolor="rgba(239,68,68,0.08)",  line_width=0, annotation_text="Danger")
    fig.add_hrect(y0=1.0, y1=1.2, fillcolor="rgba(249,115,22,0.08)", line_width=0, annotation_text="Alert")
    fig.add_hrect(y0=1.2, y1=1.5, fillcolor="rgba(234,179,8,0.08)",  line_width=0, annotation_text="Warning")
    fig.add_hrect(y0=1.5, y1=4.0, fillcolor="rgba(34,197,94,0.05)",  line_width=0, annotation_text="Safe")

    # 水平虛線：Fs 門檻值
    fig.add_hline(y=1.5, line_dash="dot", line_color="#16a34a", line_width=1.2, annotation_text="Fs=1.5")
    fig.add_hline(y=1.2, line_dash="dot", line_color="#d97706", line_width=1.2, annotation_text="Fs=1.2")
    fig.add_hline(y=1.0, line_dash="dot", line_color="#dc2626", line_width=1.2, annotation_text="Fs=1.0")

    # 折線圖：Fs 隨參數變化趨勢
    fig.add_trace(go.Scatter(
        x=param_range, y=fs_list,
        mode="lines+markers",
        line=dict(color="#3b82f6", width=2.5),
        marker=dict(color=colors, size=8, line=dict(color="white", width=1)),
        name="Fs"))

    # 紅色菱形標記：目前參數值對應的 Fs
    cur_fs = bishop_fs(
        base_params["c"], base_params["phi"], base_params["gamma"],
        base_params["beta"], base_params["H"], base_params["gw_ratio"],
        base_params["rain"], base_params["quake"], base_params["n"])["Fs"]
    fig.add_trace(go.Scatter(
        x=[current_val], y=[cur_fs],
        mode="markers",
        marker=dict(color="red", size=12, symbol="diamond"),
        name="Current"))

    fig.update_layout(
        xaxis_title=param_name,
        yaxis_title="Factor of Safety Fs",
        yaxis=dict(range=[0, min(max(fs_list)*1.2, 4.0)]),
        legend=dict(orientation="h", y=-0.25),
        margin=dict(l=40, r=20, t=20, b=40),
        plot_bgcolor="white", paper_bgcolor="white", height=260)
    return fig


# ─────────────────────────────────────────────
# 函式三：繪製多參數 Tornado 敏感度比較圖
# 同時比較所有參數對 Fs 的影響大小
# 藍色 = 參數增加讓 Fs 上升
# 紅色 = 參數增加讓 Fs 下降
# ─────────────────────────────────────────────
def plot_multi_sensitivity(c, phi, gamma, beta, H, gw_ratio, rain, quake, n_slices):
    # 計算基準 Fs（目前參數下的安全係數）
    base = bishop_fs(c, phi, gamma, beta, H, gw_ratio, rain, quake, n_slices)["Fs"]

    # 定義每個參數的名稱、基準值、擾動量
    params = {
        "Cohesion c":   ("c",        c,        c*0.2),       # 凝聚力 ±20%
        "Friction phi": ("phi",      phi,      phi*0.2),     # 內摩擦角 ±20%
        "Unit weight":  ("gamma",    gamma,    gamma*0.1),   # 單位重 ±10%
        "Slope angle":  ("beta",     beta,     beta*0.15),   # 坡角 ±15%
        "Slope height": ("H",        H,        H*0.2),       # 坡高 ±20%
        "GW ratio":     ("gw_ratio", gw_ratio, 0.15),        # 水位比 ±0.15
    }

    names, lows, highs = [], [], []

    for label, (key, val, delta) in params.items():
        # 計算參數增加時的 Fs
        p_hi = dict(c=c, phi=phi, gamma=gamma, beta=beta, H=H, gw_ratio=gw_ratio)
        p_lo = dict(c=c, phi=phi, gamma=gamma, beta=beta, H=H, gw_ratio=gw_ratio)
        p_hi[key] = min(val + delta, 1.0) if key == "gw_ratio" else val + delta
        p_lo[key] = max(val - delta, 0.0) if key == "gw_ratio" else max(val - delta, 0.01)

        fs_hi = bishop_fs(p_hi["c"], p_hi["phi"], p_hi["gamma"], p_hi["beta"],
                          p_hi["H"], p_hi["gw_ratio"], rain, quake, n_slices)["Fs"]
        fs_lo = bishop_fs(p_lo["c"], p_lo["phi"], p_lo["gamma"], p_lo["beta"],
                          p_lo["H"], p_lo["gw_ratio"], rain, quake, n_slices)["Fs"]

        names.append(label)
        lows.append(round(min(fs_hi, fs_lo) - base, 4))   # 最低變化量
        highs.append(round(max(fs_hi, fs_lo) - base, 4))  # 最高變化量

    # 依敏感度由小到大排序（最敏感的參數在最上方）
    sensitivity = [abs(h - l) for h, l in zip(highs, lows)]
    order = sorted(range(len(names)), key=lambda i: sensitivity[i])
    names  = [names[i]  for i in order]
    lows   = [lows[i]   for i in order]
    highs  = [highs[i]  for i in order]

    fig = go.Figure()

    # 藍色長條：參數變化讓 Fs 上升的範圍
    fig.add_trace(go.Bar(
        name="Positive sensitivity",
        y=names, x=highs, orientation="h",
        marker_color="#3b82f6", opacity=0.85))

    # 紅色長條：參數變化讓 Fs 下降的範圍
    fig.add_trace(go.Bar(
        name="Negative sensitivity",
        y=names, x=lows, orientation="h",
        marker_color="#f87171", opacity=0.85))

    # 中心線（ΔFs = 0）
    fig.add_vline(x=0, line_color="#374151", line_width=1.5)

    fig.update_layout(
        barmode="overlay",
        title=dict(
            text=f"Parameter Sensitivity (Base Fs={base:.3f})",
            font=dict(size=13), x=0.01),
        xaxis_title="Delta Fs",
        yaxis_title="",
        legend=dict(orientation="h", y=-0.2),
        margin=dict(l=120, r=30, t=45, b=60),
        plot_bgcolor="white", paper_bgcolor="white", height=320)
    return fig