# -*- coding: utf-8 -*-
"""
智慧邊坡穩定評估與動態視覺化模擬系統
Intelligent Slope Stability Assessment & Dynamic Visualization System
"""

import streamlit as st

st.set_page_config(
    page_title="智慧邊坡穩定評估系統",
    page_icon="⛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 套用專業自訂樣式
st.markdown("""
<style>
    .main-header { font-size: 1.6rem; font-weight: 600; color: #1e3a5f; margin-bottom: 0.2rem; }
    .fs-safe    { background:#dcfce7; color:#166534; padding:6px 14px; border-radius:6px; font-weight:600; }
    .fs-danger  { background:#fee2e2; color:#991b1b; padding:6px 14px; border-radius:6px; font-weight:600; }
</style>
""", unsafe_allow_html=True)

from utils.bishop import bishop_fs
from utils.plots import plot_slope, plot_sensitivity, plot_multi_sensitivity

# ── Sidebar 參數輸入面板 ──
with st.sidebar:
    st.markdown("## ⛰️ 參數輸入面板")
    c = st.slider("凝聚力 c (kPa)", 0, 80, 25, 1)
    phi = st.slider("內摩擦角 φ (°)", 5, 45, 30, 1)
    gamma = st.slider("土體單位重 γ (kN/m³)", 14.0, 24.0, 18.0, 0.5)
    beta = st.slider("坡角 β (°)", 10, 70, 35, 1)
    H = st.slider("坡高 H (m)", 3, 30, 10, 1)
    gw_ratio = st.slider("地下水位比 hw/H", 0.0, 1.0, 0.30, 0.05)
    
    st.markdown("### ⚙️ 情境模擬")
    rain = st.toggle("🌧️ 豪雨模擬（+30% 孔隙壓）", value=False)
    quake = st.toggle("⚡ 地震模擬（kh = 0.15g）", value=False)
    num_slices = st.select_slider("切片數量", options=[5, 8, 10, 15, 20], value=10)

# ── 呼叫 Bishop 計算核心 ──
result = bishop_fs(c, phi, gamma, beta, H, gw_ratio, rain, quake, num_slices)
Fs = result["Fs"]

# ── 呈現安全係數結果 ──
st.markdown('<div class="main-header">⛰️ 智慧邊坡穩定評估系統</div>', unsafe_allow_html=True)
st.metric("安全係數 Fs", f"{Fs:.3f}")

if Fs >= 1.5:
    st.markdown('<span class="fs-safe">✅ 安全 SAFE</span>', unsafe_allow_html=True)
else:
    st.markdown('<span class="fs-danger">🚨 建議補強或撤離</span>', unsafe_allow_html=True)

# ── 分頁呈現圖表 ──
tab1, tab2 = st.tabs(["📊 邊坡剖面", "📈 敏感度分析"])
with tab1:
    st.plotly_chart(plot_slope(c, phi, gamma, beta, H, gw_ratio, rain, quake, num_slices, result["slices"], Fs))
with tab2:
    st.plotly_chart(plot_multi_sensitivity(c, phi, gamma, beta, H, gw_ratio, rain, quake, num_slices))