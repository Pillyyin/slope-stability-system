
"""
utils/bishop.py
Simplified Bishop Method for slope stability analysis.
"""

import math


def bishop_fs(c: float, phi_deg: float, gamma: float, beta_deg: float,
              H: float, gw_ratio: float, rain: bool, quake: bool,
              n_slices: int = 10) -> dict:
    """
    Compute Factor of Safety using the Simplified Bishop Method.

    Parameters
    ----------
    c         : cohesion (kPa)
    phi_deg   : friction angle (degrees)
    gamma     : unit weight (kN/m³)
    beta_deg  : slope angle (degrees)
    H         : slope height (m)
    gw_ratio  : groundwater ratio hw/H  (0 – 1)
    rain      : if True, add 30% excess pore pressure
    quake     : if True, add horizontal seismic coefficient kh = 0.15
    n_slices  : number of slices

    Returns
    -------
    dict with keys: Fs, ru, iterations, slices
    """
    phi = math.radians(phi_deg)
    beta = math.radians(beta_deg)
    kh = 0.15 if quake else 0.0

    # Pore pressure ratio
    ru = gw_ratio * 0.5
    if rain:
        ru = min(ru + 0.15, 0.5)

    # Critical slip circle geometry
    # Radius set to 1.5*H; circle center above midpoint of slope
    R = H * 1.5
    slice_width = H / n_slices

    # Bishop iteration
    Fs = 1.5
    iterations = 0
    for _ in range(60):
        iterations += 1
        numerator = 0.0
        denominator = 0.0

        for i in range(n_slices):
            progress = (i + 0.5) / n_slices
            # Approximate slice height using sinusoidal distribution
            h_slice = max(0.05, math.sin(progress * math.pi) * 0.85) * H * progress * 1.9
            h_slice = min(h_slice, H)

            # Base inclination angle (varies across slip circle)
            alpha = math.atan2((progress - 0.5) * H, R) * beta_deg / 35.0
            alpha = max(-math.pi / 3, min(math.pi / 3, alpha))

            W = gamma * h_slice * slice_width              # slice weight (kN/m)
            u = ru * gamma * h_slice                       # pore pressure (kPa)
            b = slice_width

            # mα term
            m_alpha = math.cos(alpha) + (math.tan(phi) * math.sin(alpha)) / Fs
            m_alpha = max(m_alpha, 0.05)

            # Effective normal force at slice base
            N_eff = (W - u * b * math.cos(alpha)) / m_alpha

            # Resisting moment contribution
            numerator += (c * b + N_eff * math.tan(phi)) / m_alpha

            # Driving moment contribution (weight + seismic)
            driving = W * math.sin(alpha) + kh * W * math.cos(alpha)
            denominator += driving

        denominator = max(denominator, 0.01)
        Fs_new = numerator / denominator
        Fs_new = max(0.3, Fs_new)

        if abs(Fs_new - Fs) < 0.001:
            Fs = Fs_new
            break
        Fs = Fs_new

    # Build slice detail list for report
    slices_data = []
    for i in range(n_slices):
        progress = (i + 0.5) / n_slices
        h_slice = max(0.05, math.sin(progress * math.pi) * 0.85) * H * progress * 1.9
        h_slice = min(h_slice, H)
        alpha = math.atan2((progress - 0.5) * H, R) * beta_deg / 35.0
        alpha = max(-math.pi / 3, min(math.pi / 3, alpha))
        b = slice_width
        W = gamma * h_slice * b
        u = ru * gamma * h_slice
        m_alpha = math.cos(alpha) + (math.tan(phi) * math.sin(alpha)) / Fs
        m_alpha = max(m_alpha, 0.05)
        N_eff = (W - u * b * math.cos(alpha)) / m_alpha
        slices_data.append({
            "index": i + 1,
            "width": b,
            "height": round(h_slice, 3),
            "alpha_deg": round(math.degrees(alpha), 2),
            "W": round(W, 3),
            "N_eff": round(N_eff, 3),
            "u": round(u, 3),
        })

    return {
        "Fs": round(Fs, 4),
        "ru": round(ru, 4),
        "iterations": iterations,
        "slices": slices_data,
    }
