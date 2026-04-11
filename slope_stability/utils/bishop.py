# -*- coding: utf-8 -*-
import numpy as np

def bishop_fs(c, phi, gamma, beta, H, gw_ratio, rain=False, quake=False, n=10):
    # 角度轉弧度
    beta_rad = np.radians(beta)
    phi_rad = np.radians(phi)
    
    # 豪雨與地震修正
    u_multiplier = 1.3 if rain else 1.0
    kh = 0.15 if quake else 0.0
    
    # 建立切片數據
    dx = (H / np.tan(beta_rad)) / n
    slices = []
    total_driving_moment = 0
    
    for i in range(n):
        x = (i + 0.5) * dx
        h = H - x * np.tan(beta_rad)
        if h < 0: h = 0
        W = gamma * h * dx
        alpha = np.arctan((H/n)/dx) # 簡化圓弧假設
        
        # 孔隙壓計算
        u = gamma * (h * gw_ratio) * u_multiplier
        slices.append({'W': W, 'alpha_rad': alpha, 'alpha_deg': np.degrees(alpha), 'u': u, 'width': dx, 'height': h})

    # Bishop 疊代尋找 Fs
    fs = 1.5
    for _ in range(50):
        numerator = 0
        denominator = 0
        for s in slices:
            m_alpha = np.cos(s['alpha_rad']) + (np.sin(s['alpha_rad']) * np.tan(phi_rad) / fs)
            numerator += (c * s['width'] + (s['W'] - s['u'] * s['width']) * np.tan(phi_rad)) / m_alpha
            denominator += s['W'] * np.sin(s['alpha_rad']) + (kh * s['W']) # 考慮地震力
        
        new_fs = numerator / denominator
        if abs(new_fs - fs) < 0.001: break
        fs = new_fs
    
    # 計算有效正應力 N' 用於報告
    for s in slices:
        s['N_eff'] = (s['W'] - s['u'] * s['width']) / np.cos(s['alpha_rad'])

    return {"Fs": fs, "ru": (gw_ratio * 0.5 * u_multiplier), "iterations": _, "slices": slices}