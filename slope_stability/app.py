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

st.markdown("""
<style>
    .main-header { font-size: 1.6rem; font-weight: 600; color: #1e3a5f; margin-bottom: 0.2rem; }
    .sub-header { font-size: 0.85rem; color: #6b7280; margin-bottom: 1.5rem; }
    .fs-safe   { background:#dcfce7; color:#166534; padding:6px 14px; border-radius:6px; font-weight:600; font-size:1.1rem; }
    .fs-warn   { background:#fef9c3; color:#854d0e; padding:6px 14px; border-radius:6px; font-weight:600; font-size:1.1rem; }
    .fs-alert  { background:#ffedd5; color:#9a3412; padding:6px 14px; border-radius:6px; font-weight:600; font-size:1.1rem; }
    .fs-danger { background:#fee2e2; color:#991b1b; padding:6px 14px; border-radius:6px; font-weight:600; font-size:1.1rem; }
    .stMetric label { font-size:0.78rem !important; }
    div[data-testid="stSidebarContent"] { background-color: #f0f4f8; }
</style>
""", unsafe_allow_html=True)

from utils.bishop import bishop_fs
from utils.plots import plot_slope, plot_sensitivity, plot_multi_sensitivity

with st.sidebar:
    st.markdown("## ⛰️ 參數輸入面板")
    st.markdown("---")

    st.markdown("### 🪨 土層物理性質")
    c = st.slider("凝聚力 c (kPa)", 0, 80, 25, 1, help="土體凝聚力，黏土較高，砂土接近 0")
    phi = st.slider("內摩擦角 φ (°)", 5, 45, 30, 1, help="土體內部摩擦角，影響抗滑力")
    gamma = st.slider("土體單位重 γ (kN/m³)", 14.0, 24.0, 18.0, 0.5, help="飽和或濕土的單位重")

    st.markdown("### 📐 邊坡幾何")
    beta = st.slider("坡角 β (°)", 10, 70, 35, 1, help="坡面與水平面的夾角")
    H = st.slider("坡高 H (m)", 3, 30, 10, 1, help="坡頂到坡腳的垂直高度")

    st.markdown("### 💧 水文條件")
    gw_ratio = st.slider("地下水位比 hw/H", 0.0, 1.0, 0.30, 0.05,
                         help="地下水位距坡腳高度 / 坡高，0=無水，1=完全飽和")

    st.markdown("### ⚙️ 情境模擬")
    rain = st.toggle("🌧️ 豪雨模擬（+30% 孔隙壓）", value=False)
    quake = st.toggle("⚡ 地震模擬（kh = 0.15g）", value=False)
    num_slices = st.select_slider("切片數量", options=[5, 8, 10, 15, 20], value=10)

    st.markdown("---")
    st.caption("方法：Simplified Bishop Method\n疊代收斂容差：0.001")

result = bishop_fs(c, phi, gamma, beta, H, gw_ratio, rain, quake, num_slices)
Fs         = result["Fs"]
ru         = result["ru"]
iterations = result["iterations"]
slices     = result["slices"]

st.markdown('<div class="main-header">⛰️ 智慧邊坡穩定評估與動態視覺化模擬系統</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Intelligent Slope Stability Assessment & Dynamic Visualization System ｜ Simplified Bishop Method</div>', unsafe_allow_html=True)

col_fs, col_status, col_advice = st.columns([1, 1, 3])

with col_fs:
    st.metric("安全係數 Fs", f"{Fs:.3f}")
    if Fs >= 1.5:
        st.markdown('<span class="fs-safe">✅ 安全 SAFE</span>', unsafe_allow_html=True)
    elif Fs >= 1.2:
        st.markdown('<span class="fs-warn">⚠️ 注意 WARNING</span>', unsafe_allow_html=True)
    elif Fs >= 1.0:
        st.markdown('<span class="fs-alert">🔶 警戒 ALERT</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="fs-danger">🚨 即刻撤離 EVACUATE</span>', unsafe_allow_html=True)

with col_status:
    st.metric("孔隙壓比 ru", f"{ru:.3f}")
    st.metric("疊代次數", f"{iterations}")
    st.metric("切片數量", f"{num_slices}")

with col_advice:
    st.markdown("#### 📋 系統建議")
    if Fs >= 1.5:
        st.success("邊坡穩定性良好，安全係數 ≥ 1.5。建議定期監測地下水位，維持正常管理作業。")
    elif Fs >= 1.2:
        st.warning("安全係數介於 1.2 ~ 1.5，建議加強監測頻率，降雨期間須特別注意地下水位變化。")
    elif Fs >= 1.0:
        st.error("安全係數偏低（1.0 ~ 1.2），建議暫停坡地作業，立即部署監測儀器並通報主管機關。")
    else:
        st.error("⚠️ 危險！安全係數 < 1.0，請立即撤離危險區域並啟動緊急應變機制！")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["📊 邊坡剖面 & 切片示意", "📈 敏感度分析", "📑 分析報告", "📖 理論基礎"])

with tab1:
    fig_slope = plot_slope(c, phi, gamma, beta, H, gw_ratio, rain, quake, num_slices, slices, Fs)
    st.plotly_chart(fig_slope, use_container_width=True)

with tab2:
    st.markdown("#### 參數對安全係數影響分析")
    sens_col1, sens_col2 = st.columns(2)

    with sens_col1:
        st.markdown("**地下水位 vs Fs**")
        fig_gw = plot_sensitivity(
            param_name="地下水位比 hw/H",
            param_range=[round(x * 0.1, 1) for x in range(11)],
            param_key="gw",
            base_params=dict(c=c, phi=phi, gamma=gamma, beta=beta, H=H,
                             gw_ratio=gw_ratio, rain=rain, quake=quake, n=num_slices),
            current_val=gw_ratio
        )
        st.plotly_chart(fig_gw, use_container_width=True)

    with sens_col2:
        st.markdown("**凝聚力 c vs Fs**")
        fig_c = plot_sensitivity(
            param_name="凝聚力 c (kPa)",
            param_range=list(range(0, 81, 8)),
            param_key="c",
            base_params=dict(c=c, phi=phi, gamma=gamma, beta=beta, H=H,
                             gw_ratio=gw_ratio, rain=rain, quake=quake, n=num_slices),
            current_val=c
        )
        st.plotly_chart(fig_c, use_container_width=True)

    st.markdown("**多參數綜合敏感度**")
    fig_multi = plot_multi_sensitivity(c, phi, gamma, beta, H, gw_ratio, rain, quake, num_slices)
    st.plotly_chart(fig_multi, use_container_width=True)

with tab3:
    st.markdown("#### 📄 邊坡穩定性分析報告")
    import datetime
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    report_md = f"""
| 項目 | 數值 |
|------|------|
| 分析時間 | {now} |
| 分析方法 | Simplified Bishop Method |
| 安全係數 Fs | **{Fs:.4f}** |
| 穩定狀態 | {"✅ 安全" if Fs>=1.5 else "⚠️ 注意" if Fs>=1.2 else "🔶 警戒" if Fs>=1.0 else "🚨 危險"} |

**輸入參數**

| 參數 | 值 | 單位 |
|------|----|------|
| 凝聚力 c | {c} | kPa |
| 內摩擦角 φ | {phi} | ° |
| 土體單位重 γ | {gamma} | kN/m³ |
| 坡角 β | {beta} | ° |
| 坡高 H | {H} | m |
| 地下水位比 hw/H | {gw_ratio:.2f} | — |
| 孔隙壓比 ru | {ru:.4f} | — |
| 豪雨模擬 | {"是" if rain else "否"} | — |
| 地震模擬 (kh) | {"0.15g" if quake else "無"} | — |
| 切片數量 | {num_slices} | 片 |
| 疊代次數 | {iterations} | 次 |

**切片資料**

| 切片 | 寬度(m) | 高度(m) | 底角(°) | 有效正應力N'(kN) | 重量W(kN) |
|------|---------|---------|---------|-----------------|----------|
"""
    for i, s in enumerate(slices):
        report_md += f"| {i+1} | {s['width']:.2f} | {s['height']:.2f} | {s['alpha_deg']:.1f} | {s['N_eff']:.2f} | {s['W']:.2f} |\n"

    st.markdown(report_md)
    st.download_button(
        label="⬇️ 下載分析報告 (.md)",
        data=report_md,
        file_name=f"slope_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.md",
        mime="text/markdown"
    )
with tab4:
    st.markdown("### 1. 簡化畢夏普法 (Simplified Bishop Method)")
    st.write("本系統採用簡化畢夏普法進行圓弧滑動面分析，其安全係數 $F_s$ 的定義如下：")
    
    # 主要公式
    st.latex(r"F_s = \frac{\sum \left[ \frac{c' \cdot b + (W - u \cdot b) \tan \phi'}{m_\alpha} \right]}{\sum (W \cdot \sin \alpha + k_h \cdot W \cdot \cos \alpha)}")
    
    st.write("其中疊代係數 $m_\alpha$ 為：")
    st.latex(r"m_\alpha = \cos \alpha + \frac{\tan \phi' \cdot \sin \alpha}{F_s}")

    st.markdown("---")
    st.markdown("### 2. 公式符號講解")
    st.markdown(r"""
| 符號 | 物理意義 | 單位 |
| :--- | :--- | :--- |
| **$F_s$** | 安全係數 (Factor of Safety) | — |
| **$c'$** | 有效凝聚力 (Effective Cohesion) | $kPa$ |
| **$\phi'$** | 有效內摩擦角 (Effective Friction Angle) | 度 ($deg$) |
| **$W$** | 土條切片總重量 | $kN$ |
| **$u$** | 孔隙水壓力 (Pore Water Pressure) | $kPa$ |
| **$b$** | 切片寬度 | $m$ |
| **$\alpha$** | 切片底面傾角 | 度 ($deg$) |
| **$k_h$** | 水平地震力係數 | — |
""")

    st.info("💡 **提示**：由於 $F_s$ 同時出現在等號兩側，系統會透過疊代法（Iteration）計算至收斂值為止（誤差 < 0.001）。")