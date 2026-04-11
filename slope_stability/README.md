# ⛰️ 智慧邊坡穩定評估與動態視覺化模擬系統

Intelligent Slope Stability Assessment & Dynamic Visualization System

## 功能

- **Simplified Bishop Method** 疊代法計算安全係數 Fs
- **即時互動滑桿**：凝聚力 c、內摩擦角 φ、地下水位等參數即時更新
- **邊坡剖面圖**：含土條切片、圓弧滑動面、地下水位視覺化
- **敏感度分析**：地下水位、凝聚力個別分析 + Tornado 多參數比較圖
- **情境模擬**：豪雨（+30% 孔隙壓）、地震（kh=0.15g）
- **安全警示**：Fs 顏色分級 + 文字建議（安全/注意/警戒/即刻撤離）
- **分析報告**：含切片資料表，可下載 .md 格式

## 安裝與執行

```bash
# 1. 建立虛擬環境（建議）
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. 安裝套件
pip install -r requirements.txt

# 3. 啟動應用
streamlit run app.py
```

瀏覽器自動開啟 `http://localhost:8501`

## 安全係數判斷標準

| Fs 範圍 | 狀態 | 顏色 |
|---------|------|------|
| ≥ 1.5 | 安全 | 綠色 |
| 1.2 ~ 1.5 | 注意 | 黃色 |
| 1.0 ~ 1.2 | 警戒 | 橙色 |
| < 1.0 | 即刻撤離 | 紅色 |

## 檔案結構

```
slope_stability/
├── app.py              # 主程式（Streamlit UI）
├── requirements.txt    # 套件需求
├── utils/
│   ├── bishop.py       # Bishop 疊代法計算核心
│   └── plots.py        # Plotly 視覺化函式
└── README.md
```

## 使用角色

- **水土保持工程師**：初步設計階段評估不同土層參數對穩定性影響
- **防災相關科系學生**：透過互動工具理解切片法力學原理
- **坡地監測人員**：豪雨或地震後輸入現地觀測數據進行即時風險預判
