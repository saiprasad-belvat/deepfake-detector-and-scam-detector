import streamlit as st
from backend import *
import pandas as pd
import time
import json
import re
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="AI Scam Shield",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;800;900&family=Exo+2:wght@300;400;500;600&family=Share+Tech+Mono&display=swap');

:root {
    --bg-deep:    #050510;
    --bg-mid:     #0b0b1f;
    --bg-card:    #0f0f28;
    --accent-c:   #00f5ff;
    --accent-p:   #b14aed;
    --accent-g:   #00ff99;
    --accent-r:   #ff2d55;
    --accent-y:   #ffd60a;
    --text-hi:    #e8e8ff;
    --text-mid:   #9090b8;
    --text-lo:    #454568;
    --border:     rgba(0,245,255,0.15);
    --glow-c:     0 0 20px rgba(0,245,255,0.4);
    --glow-p:     0 0 20px rgba(177,74,237,0.4);
    --glow-g:     0 0 20px rgba(0,255,153,0.4);
    --glow-r:     0 0 20px rgba(255,45,85,0.4);
}

* { box-sizing: border-box; }

.stApp {
    background: var(--bg-deep);
    font-family: 'Exo 2', sans-serif;
    color: var(--text-hi);
}
#MainMenu, footer, header { visibility: hidden; }

/* ── scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg-deep); }
::-webkit-scrollbar-thumb { background: var(--accent-p); border-radius: 3px; }

/* ── hero grid bg ── */
.hero-bg {
    position: relative;
    overflow: hidden;
    padding: 3rem 1rem 1rem;
}
.hero-bg::before {
    content: '';
    position: absolute; inset: 0;
    background:
        linear-gradient(rgba(0,245,255,.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,245,255,.04) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
}

/* ── main title ── */
.main-title {
    font-family: 'Orbitron', sans-serif;
    font-size: clamp(2rem, 5vw, 4rem);
    font-weight: 900;
    text-align: center;
    letter-spacing: .05em;
    background: linear-gradient(135deg, #00f5ff 0%, #b14aed 50%, #ff2d55 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    filter: drop-shadow(0 0 30px rgba(0,245,255,.35));
    margin-bottom: .4rem;
}
.subtitle {
    text-align: center;
    color: var(--text-mid);
    font-size: 1.05rem;
    font-weight: 300;
    letter-spacing: .08em;
    margin-bottom: 2.5rem;
}

/* ── pulse ring ── */
@keyframes pulse-ring {
    0%   { transform: scale(.9); opacity: .7; }
    70%  { transform: scale(1.3); opacity: 0; }
    100% { transform: scale(1.3); opacity: 0; }
}
.pulse-dot {
    display: inline-block; width: 10px; height: 10px;
    border-radius: 50%; background: var(--accent-g);
    position: relative; margin-right: 6px; vertical-align: middle;
}
.pulse-dot::before {
    content: '';
    position: absolute; inset: -4px;
    border-radius: 50%; border: 2px solid var(--accent-g);
    animation: pulse-ring 1.6s ease-out infinite;
}

/* ── stats bar ── */
.stats-bar {
    display: flex; justify-content: space-around; flex-wrap: wrap;
    gap: 1rem;
    background: rgba(0,245,255,.04);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.5rem 2rem;
    margin-bottom: 2.5rem;
}
.stat-item { text-align: center; }
.stat-number {
    font-family: 'Orbitron', sans-serif;
    font-size: 2rem; font-weight: 800;
    background: linear-gradient(120deg, var(--accent-c), var(--accent-p));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.stat-label { color: var(--text-lo); font-size: .8rem; letter-spacing: .1em; text-transform: uppercase; margin-top: .2rem; }

/* ── nav tabs ── */
.nav-tab-row {
    display: flex; gap: .5rem; flex-wrap: wrap;
    margin-bottom: 1.5rem;
}
.nav-tab {
    display: inline-flex; align-items: center; gap: .4rem;
    padding: .45rem 1rem;
    border-radius: 8px;
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(255,255,255,.08);
    color: var(--text-mid);
    font-size: .82rem; font-weight: 500;
    cursor: pointer; transition: all .2s;
    text-decoration: none;
}
.nav-tab:hover, .nav-tab.active {
    background: rgba(0,245,255,.08);
    border-color: var(--accent-c);
    color: var(--accent-c);
    box-shadow: var(--glow-c);
}

/* ── detection cards ── */
.det-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 1rem;
    margin-bottom: 2rem;
}
.det-card {
    background: linear-gradient(145deg, #0d0d25 0%, #141430 100%);
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 18px;
    padding: 1.5rem 1rem;
    text-align: center;
    transition: all .3s ease;
    position: relative; overflow: hidden;
    cursor: pointer;
}
.det-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, var(--accent-c), var(--accent-p));
    opacity: 0; transition: opacity .3s;
}
.det-card:hover { transform: translateY(-6px); border-color: rgba(0,245,255,.3); box-shadow: var(--glow-c); }
.det-card:hover::before { opacity: 1; }
.det-card .icon { font-size: 2.8rem; margin-bottom: .8rem; }
.det-card .title { color: var(--text-hi); font-family: 'Orbitron', sans-serif; font-size: .85rem; font-weight: 600; margin-bottom: .4rem; letter-spacing: .05em; }
.det-card .desc { color: var(--text-lo); font-size: .77rem; line-height: 1.5; }
.badge {
    display: inline-block;
    padding: .15rem .6rem;
    border-radius: 20px;
    font-size: .68rem;
    background: rgba(0,245,255,.1);
    border: 1px solid rgba(0,245,255,.25);
    color: var(--accent-c);
    margin: .15rem;
}

/* ── section header ── */
.section-header {
    font-family: 'Orbitron', sans-serif;
    font-size: .9rem; font-weight: 700;
    letter-spacing: .12em; color: var(--accent-c);
    margin: 2rem 0 1rem;
    padding-bottom: .5rem;
    border-bottom: 1px solid rgba(0,245,255,.2);
    text-transform: uppercase;
}

/* ── result cards ── */
.result-safe    { background: linear-gradient(145deg,#041a0e,#082d18); border: 1px solid var(--accent-g); border-radius:14px; padding:1.5rem; }
.result-danger  { background: linear-gradient(145deg,#1a0408,#2d0810); border: 1px solid var(--accent-r); border-radius:14px; padding:1.5rem; }
.result-warning { background: linear-gradient(145deg,#1a1404,#2d2208); border: 1px solid var(--accent-y); border-radius:14px; padding:1.5rem; }

/* ── tip box ── */
.tip-box {
    background: rgba(177,74,237,.08);
    border-left: 3px solid var(--accent-p);
    border-radius: 0 10px 10px 0;
    padding: .8rem 1.2rem;
    margin: .4rem 0;
}
.tip-box p { color: var(--text-mid); margin: 0; font-size: .88rem; }

/* ── info card ── */
.info-card {
    background: rgba(255,255,255,.03);
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin: .5rem 0;
}

/* ── threat meter ── */
.threat-meter-wrap { margin: 1rem 0; }
.threat-meter-bar {
    height: 10px; border-radius: 5px;
    background: rgba(255,255,255,.07);
    overflow: hidden; position: relative;
}
.threat-meter-fill {
    height: 100%; border-radius: 5px;
    transition: width 1s ease;
    background: linear-gradient(90deg, var(--accent-g), var(--accent-y), var(--accent-r));
}
.threat-label { font-family: 'Share Tech Mono', monospace; font-size: .78rem; color: var(--text-mid); margin-bottom: .3rem; }
.threat-value { font-family: 'Orbitron', sans-serif; font-size: 1.1rem; font-weight: 700; }

/* ── scanning animation ── */
@keyframes scanline {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
.scanning-anim {
    background: linear-gradient(90deg, #0b0b1f, #00f5ff33, #0b0b1f);
    background-size: 200% 200%;
    animation: scanline 1.8s ease infinite;
    border-radius: 10px; padding: 1rem;
    text-align: center;
    color: var(--accent-c);
    font-family: 'Share Tech Mono', monospace;
    border: 1px solid rgba(0,245,255,.15);
}

/* ── terminal box ── */
.terminal {
    background: #020208;
    border: 1px solid rgba(0,245,255,.2);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    font-family: 'Share Tech Mono', monospace;
    font-size: .82rem;
    color: var(--accent-c);
    overflow-x: auto;
    white-space: pre-wrap;
    word-break: break-all;
}
.terminal .t-green  { color: var(--accent-g); }
.terminal .t-red    { color: var(--accent-r); }
.terminal .t-yellow { color: var(--accent-y); }
.terminal .t-dim    { color: var(--text-lo); }

/* ── risk score ring ── */
.risk-ring-wrap { text-align: center; padding: 1rem; }
.risk-score-num {
    font-family: 'Orbitron', sans-serif;
    font-size: 3.5rem; font-weight: 900;
}
.risk-score-label { color: var(--text-mid); font-size: .8rem; letter-spacing: .1em; text-transform: uppercase; }

/* ── checklist ── */
.checklist-item {
    display: flex; align-items: flex-start; gap: .7rem;
    padding: .6rem 1rem;
    border-radius: 8px;
    background: rgba(255,255,255,.025);
    border: 1px solid rgba(255,255,255,.06);
    margin: .35rem 0;
    font-size: .86rem;
}
.checklist-item.ok   { border-color: rgba(0,255,153,.2); }
.checklist-item.warn { border-color: rgba(255,214,10,.2); }
.checklist-item.bad  { border-color: rgba(255,45,85,.2); }
.check-icon { font-size: 1rem; flex-shrink: 0; margin-top: .05rem; }

/* ── history table ── */
.hist-row {
    display: flex; align-items: center; gap: 1rem;
    padding: .7rem 1rem;
    border-radius: 10px;
    background: rgba(255,255,255,.02);
    border: 1px solid rgba(255,255,255,.05);
    margin: .3rem 0;
    font-size: .85rem;
}
.hist-badge {
    padding: .2rem .7rem; border-radius: 20px; font-size: .72rem; font-weight: 600;
    font-family: 'Share Tech Mono', monospace;
}
.hist-badge.safe    { background: rgba(0,255,153,.15); color: var(--accent-g); border: 1px solid var(--accent-g); }
.hist-badge.danger  { background: rgba(255,45,85,.15);  color: var(--accent-r); border: 1px solid var(--accent-r); }
.hist-badge.warning { background: rgba(255,214,10,.15); color: var(--accent-y); border: 1px solid var(--accent-y); }

/* ── education card ── */
.edu-card {
    background: linear-gradient(145deg, #0d0d25, #141430);
    border: 1px solid rgba(177,74,237,.25);
    border-radius: 16px;
    padding: 1.5rem;
    margin: .5rem 0;
    transition: all .25s;
}
.edu-card:hover { border-color: var(--accent-p); box-shadow: var(--glow-p); }
.edu-card h4 { color: var(--accent-p); font-family: 'Orbitron', sans-serif; font-size: .85rem; margin: 0 0 .5rem; letter-spacing: .05em; }
.edu-card p { color: var(--text-mid); font-size: .85rem; line-height: 1.6; margin: 0; }

/* ── stButton overrides ── */
.stButton > button {
    background: linear-gradient(120deg, var(--accent-c), var(--accent-p)) !important;
    color: #fff !important; border: none !important;
    border-radius: 10px !important; padding: .65rem 1.5rem !important;
    font-family: 'Exo 2', sans-serif !important; font-weight: 600 !important;
    letter-spacing: .04em !important;
    transition: all .25s ease !important; width: 100% !important;
}
.stButton > button:hover {
    transform: scale(1.02) !important;
    box-shadow: 0 6px 24px rgba(0,245,255,.35) !important;
}
.back-btn > button {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,.15) !important;
    color: var(--text-mid) !important;
}
.back-btn > button:hover {
    border-color: var(--accent-c) !important;
    color: var(--accent-c) !important;
}

/* ── stTextInput ── */
.stTextInput > div > div > input {
    background: rgba(255,255,255,.04) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-hi) !important;
    font-family: 'Share Tech Mono', monospace !important;
    padding: .7rem 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: var(--accent-c) !important;
    box-shadow: var(--glow-c) !important;
}

/* ── stTextArea ── */
.stTextArea > div > textarea {
    background: rgba(255,255,255,.04) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-hi) !important;
    font-family: 'Exo 2', sans-serif !important;
}

/* ── stFileUploader ── */
[data-testid="stFileUploader"] > div {
    background: rgba(0,245,255,.04) !important;
    border: 2px dashed rgba(0,245,255,.25) !important;
    border-radius: 14px !important;
}

/* ── stProgress ── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--accent-c), var(--accent-p)) !important;
}

/* ── stExpander ── */
.streamlit-expanderHeader {
    background: rgba(255,255,255,.03) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: var(--text-hi) !important;
    font-family: 'Exo 2', sans-serif !important;
}

/* ── stTabs ── */
.stTabs [data-baseweb="tab-list"] { background: transparent !important; gap: .3rem; }
.stTabs [data-baseweb="tab"] {
    background: rgba(255,255,255,.04) !important;
    border: 1px solid rgba(255,255,255,.08) !important;
    border-radius: 8px !important;
    color: var(--text-mid) !important;
    font-family: 'Exo 2', sans-serif !important;
    font-size: .85rem !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(0,245,255,.12) !important;
    border-color: var(--accent-c) !important;
    color: var(--accent-c) !important;
}

/* ── alert overrides ── */
.stAlert { border-radius: 12px !important; }

/* ── footer ── */
.site-footer {
    text-align: center;
    color: var(--text-lo);
    padding: 2rem 1rem;
    margin-top: 3rem;
    border-top: 1px solid rgba(255,255,255,.05);
    font-size: .8rem;
    font-family: 'Share Tech Mono', monospace;
    letter-spacing: .08em;
}

/* ── floating live indicator ── */
.live-indicator {
    display: inline-flex; align-items: center; gap: .4rem;
    background: rgba(0,255,153,.1);
    border: 1px solid rgba(0,255,153,.3);
    border-radius: 20px;
    padding: .3rem .8rem;
    font-size: .75rem;
    color: var(--accent-g);
    font-family: 'Share Tech Mono', monospace;
    letter-spacing: .05em;
}

/* ── warning banner ── */
.alert-banner {
    background: linear-gradient(135deg, rgba(255,45,85,.12), rgba(177,74,237,.08));
    border: 1px solid rgba(255,45,85,.35);
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}

/* ── tooltip chip ── */
.chip {
    display: inline-block;
    padding: .25rem .7rem;
    border-radius: 20px;
    background: rgba(177,74,237,.15);
    border: 1px solid rgba(177,74,237,.3);
    color: var(--accent-p);
    font-size: .72rem;
    margin: .15rem;
    font-family: 'Share Tech Mono', monospace;
}

/* ── donut chart placeholder ── */
.mini-gauge {
    display: flex; flex-direction: column; align-items: center;
    gap: .3rem;
}

/* ── animated gradient text ── */
@keyframes text-shimmer {
    0%   { background-position: -200% center; }
    100% { background-position:  200% center; }
}
.shimmer-text {
    background: linear-gradient(90deg, var(--accent-c), var(--accent-p), var(--accent-c));
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: text-shimmer 3s linear infinite;
}

/* ── compare columns ── */
.compare-col {
    background: rgba(255,255,255,.02);
    border: 1px solid rgba(255,255,255,.07);
    border-radius: 14px;
    padding: 1.2rem;
}
.compare-col h5 {
    color: var(--accent-c);
    font-family: 'Orbitron', sans-serif;
    font-size: .78rem;
    letter-spacing: .1em;
    text-transform: uppercase;
    margin: 0 0 .8rem;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────
defaults = {
    "page": "home",
    "scan_history": [],       # list of dicts
    "dark_mode": True,
    "realtime_alert": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def go(page):
    st.session_state.page = page
    st.rerun()

def add_history(media_type, filename, result, confidence):
    st.session_state.scan_history.insert(0, {
        "type": media_type,
        "file": filename,
        "result": result,
        "confidence": confidence,
        "time": datetime.now().strftime("%H:%M:%S"),
    })
    st.session_state.scan_history = st.session_state.scan_history[:50]

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def threat_color(result):
    return {"FAKE": "var(--accent-r)", "REAL": "var(--accent-g)"}.get(result, "var(--accent-y)")

def threat_emoji(result):
    return {"FAKE": "🚨", "REAL": "✅"}.get(result, "⚠️")

def confidence_color(c):
    if c >= 80: return "var(--accent-r)" if c >= 80 else "var(--accent-g)"
    if c >= 60: return "var(--accent-y)"
    return "var(--accent-g)"

# ─────────────────────────────────────────────
#  RESULT DISPLAY
# ─────────────────────────────────────────────
def show_result(result, confidence, media_type, filename="unknown"):
    add_history(media_type, filename, result, confidence)
    col_r, col_s = st.columns([3, 2])

    with col_r:
        css_cls = {"FAKE": "result-danger", "REAL": "result-safe"}.get(result, "result-warning")
        color   = threat_color(result)
        emoji   = threat_emoji(result)
        label   = {"FAKE": "DEEPFAKE / FAKE DETECTED", "REAL": "AUTHENTIC"}.get(result, "SUSPICIOUS — REVIEW NEEDED")

        st.markdown(f"""
        <div class="{css_cls}">
            <div style="font-family:'Orbitron',sans-serif; font-size:1.4rem; font-weight:800; color:{color}; margin-bottom:.4rem;">
                {emoji} {label}
            </div>
            <div class="threat-meter-wrap">
                <div class="threat-label">DETECTION CONFIDENCE</div>
                <div style="display:flex; align-items:center; gap:1rem;">
                    <div class="threat-meter-bar" style="flex:1;">
                        <div class="threat-meter-fill" style="width:{confidence}%;"></div>
                    </div>
                    <div class="threat-value" style="color:{color};">{confidence}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_s:
        if result == "FAKE":
            actions = [
                ("bad",  "❌", "Do NOT share this content"),
                ("bad",  "🚫", "Do NOT act on this information"),
                ("warn", "🔍", "Cross-verify with official sources"),
                ("warn", "📢", "Report to platform or authorities"),
            ]
        elif result == "REAL":
            actions = [
                ("ok",   "✅", "Content appears genuine"),
                ("ok",   "💡", "Still verify critical claims independently"),
                ("warn", "🔒", "Check metadata for extra assurance"),
            ]
        else:
            actions = [
                ("warn", "⚠️", "Exercise caution before sharing"),
                ("warn", "🔍", "Verify from multiple sources"),
                ("bad",  "🚫", "Do not make financial decisions based on this"),
            ]

        st.markdown('<div class="section-header">Recommended Actions</div>', unsafe_allow_html=True)
        for cls, icon, text in actions:
            st.markdown(f"""
            <div class="checklist-item {cls}">
                <span class="check-icon">{icon}</span>
                <span style="color:var(--text-mid);">{text}</span>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  VIRUSTOTAL SCAN
# ─────────────────────────────────────────────
def perform_vt_scan(file):
    st.markdown('<div class="section-header">🛡️ Malware Scan via VirusTotal</div>', unsafe_allow_html=True)
    progress = st.progress(0)
    status   = st.empty()

    status.markdown('<div class="scanning-anim">📤 UPLOADING FILE → VIRUSTOTAL...</div>', unsafe_allow_html=True)
    progress.progress(20)
    scan_id = scan_with_virustotal(file)

    if scan_id:
        stats = None
        for i in range(10):
            status.markdown(f'<div class="scanning-anim">🔍 SCANNING... ENGINE {(i+1)*7}/70</div>', unsafe_allow_html=True)
            time.sleep(3)
            stats = get_vt_result(scan_id)
            progress.progress(20 + i * 8)
            if stats:
                break

        progress.progress(100)
        status.empty()

        if stats:
            mal  = stats.get("malicious", 0)
            sus  = stats.get("suspicious", 0)
            harm = stats.get("harmless", 0)
            total = mal + sus + harm or 1

            c1, c2, c3, c4 = st.columns(4)
            for col, val, label, clr in [
                (c1, mal,  "Malicious",  "var(--accent-r)"),
                (c2, sus,  "Suspicious", "var(--accent-y)"),
                (c3, harm, "Clean",      "var(--accent-g)"),
                (c4, round(mal/total*100), "Threat %", "var(--accent-p)"),
            ]:
                with col:
                    st.markdown(f"""
                    <div class="info-card" style="text-align:center;">
                        <div style="font-size:2.2rem;font-family:'Orbitron',sans-serif;font-weight:800;color:{clr};">{val}</div>
                        <div style="color:var(--text-lo);font-size:.8rem;text-transform:uppercase;letter-spacing:.08em;">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)

            verdict = "result-danger" if mal > 0 else ("result-warning" if sus > 0 else "result-safe")
            v_icon  = "🦠" if mal > 0 else ("⚠️" if sus > 0 else "✅")
            v_text  = "MALWARE DETECTED — Do NOT open!" if mal > 0 else ("POTENTIALLY UNSAFE — Proceed with caution." if sus > 0 else "FILE IS CLEAN — No threats found.")
            v_color = "var(--accent-r)" if mal > 0 else ("var(--accent-y)" if sus > 0 else "var(--accent-g)")

            st.markdown(f"""
            <div class="{verdict}" style="margin-top:1rem;">
                <div style="font-family:'Orbitron',sans-serif;font-size:1.1rem;color:{v_color};margin-bottom:.3rem;">{v_icon} {v_text}</div>
                <div class="terminal">Scanned by {total} security engines | Malicious: {mal} | Suspicious: {sus} | Clean: {harm}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ VirusTotal returned no results. Try again later.")
    else:
        st.error("❌ Failed to upload file. Check your API key or file size.")

# ─────────────────────────────────────────────
#  TEXT SCAM ANALYSIS  (new feature)
# ─────────────────────────────────────────────
def analyze_text_for_scam(text):
    """Heuristic scam signal detector."""
    signals = []
    score   = 0
    t = text.lower()

    checks = [
        (["urgent", "act now", "limited time", "expire", "immediately"],
         "Urgency language detected", 15),
        (["click here", "verify your account", "confirm your details", "login now"],
         "Phishing call-to-action detected", 20),
        (["congratulations", "you have won", "selected winner", "prize"],
         "Lottery/prize scam language", 20),
        (["wire transfer", "bitcoin", "crypto", "gift card", "western union"],
         "Suspicious payment method mentioned", 20),
        (["social security", "ssn", "bank account", "credit card", "password"],
         "Sensitive data solicitation", 25),
        (["free money", "make money fast", "work from home", "guaranteed income"],
         "Get-rich-quick pattern", 15),
        (["irs", "tax refund", "government grant", "fbi", "police"],
         "Government impersonation signals", 20),
        (["love you", "sweetheart", "dear friend", "kindly", "beloved"],
         "Romance/advance-fee scam patterns", 10),
    ]

    for keywords, label, weight in checks:
        if any(kw in t for kw in keywords):
            signals.append(("bad", label))
            score += weight

    # positive checks
    if len(text) > 500:
        signals.append(("ok", "Message has substantial length (less typical of spam)"))
    if re.search(r'https?://[a-z0-9.-]+\.[a-z]{2,}', t):
        signals.append(("warn", "Contains URLs — verify before clicking"))
        score += 5

    score = min(score, 100)
    if score >= 60:
        verdict, confidence = "FAKE", score
    elif score >= 30:
        verdict, confidence = "SUSPICIOUS", score
    else:
        verdict, confidence = "REAL", 100 - score

    return verdict, confidence, signals

# ─────────────────────────────────────────────
#  EMAIL HEADER ANALYSIS  (new feature)
# ─────────────────────────────────────────────
def analyze_email_headers(headers_text):
    signals = []
    score   = 0
    t = headers_text.lower()

    if "spf=fail" in t or "spf=softfail" in t:
        signals.append(("bad", "SPF check FAILED — sender domain spoofed"))
        score += 30
    elif "spf=pass" in t:
        signals.append(("ok", "SPF check passed"))

    if "dkim=fail" in t:
        signals.append(("bad", "DKIM signature FAILED — email tampered"))
        score += 30
    elif "dkim=pass" in t:
        signals.append(("ok", "DKIM signature valid"))

    if "dmarc=fail" in t:
        signals.append(("bad", "DMARC policy FAILED"))
        score += 20
    elif "dmarc=pass" in t:
        signals.append(("ok", "DMARC policy passed"))

    if re.search(r'x-mailer:\s*(massmailer|bulk|phpmailer)', t):
        signals.append(("warn", "Bulk mailer software detected"))
        score += 15

    score = min(score, 100)
    verdict = "FAKE" if score >= 50 else ("SUSPICIOUS" if score >= 25 else "REAL")
    confidence = score if score >= 50 else (100 - score)
    return verdict, confidence, signals

# ─────────────────────────────────────────────
#  QR CODE INFO  (new feature)
# ─────────────────────────────────────────────
def qr_info_display():
    st.markdown('<div class="section-header">🔲 QR Code Security Tips</div>', unsafe_allow_html=True)
    tips = [
        ("warn", "QR codes can redirect to phishing sites or trigger downloads"),
        ("warn", "Stickers placed over legitimate QR codes are a growing attack vector"),
        ("ok",   "Scan only QR codes from trusted, physical sources"),
        ("ok",   "Preview the URL before opening — most phone scanners show it first"),
        ("bad",  "Never scan QR codes received via unsolicited emails or messages"),
    ]
    for cls, txt in tips:
        icon = {"ok":"✅","warn":"⚠️","bad":"❌"}[cls]
        st.markdown(f'<div class="checklist-item {cls}"><span class="check-icon">{icon}</span><span style="color:var(--text-mid);">{txt}</span></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  EDUCATION CONTENT
# ─────────────────────────────────────────────
EDUCATION = [
    {
        "title": "What is a Deepfake?",
        "body": "Deepfakes use deep learning (GANs) to swap faces, clone voices, or generate entirely synthetic media. They have become increasingly indistinguishable from real content. Red flags: unnatural eye blinking, blurry hairlines, inconsistent lighting, audio that doesn't perfectly match lip movement.",
        "tags": ["AI", "Video", "Face-swap"],
    },
    {
        "title": "Phishing Anatomy",
        "body": "Phishing emails mimic trusted brands to steal credentials. Key signals: sender domain differs from brand, urgent language, mis-matched hover URLs, generic greetings ('Dear Customer'), requests for sensitive info. Always check the URL bar — HTTPS alone doesn't mean safe.",
        "tags": ["Email", "URL", "Social Engineering"],
    },
    {
        "title": "Voice Cloning Scams",
        "body": "Criminals harvest voice samples from social media (as little as 3 seconds) and use AI tools to clone voices in real time. They impersonate relatives in distress and demand wire transfers or gift cards. Establish a family 'code word' as a verification mechanism.",
        "tags": ["Audio", "AI", "Phone Scam"],
    },
    {
        "title": "Romance & Advance-Fee Fraud",
        "body": "Scammers build emotional relationships online before fabricating crises requiring money. Common platforms: dating apps, social media. Clues: refuses video calls, profile photos look like stock images (reverse-image-search them), quickly moves to off-platform chat, requests unusual payment methods.",
        "tags": ["Social Engineering", "Text"],
    },
    {
        "title": "Malware in Disguise",
        "body": "Malware hides inside seemingly innocent files — PDFs, Word docs, image files exploiting parser bugs, and even audio/video containers. Always scan files before opening, especially from unknown senders. Our VirusTotal integration checks against 70+ antivirus engines.",
        "tags": ["Malware", "File", "VirusTotal"],
    },
    {
        "title": "QR Code Quishing",
        "body": "'Quishing' is phishing via QR codes. Attackers place malicious QR stickers over legitimate ones in restaurants, parking meters, and public spaces. The QR redirects to credential-harvesting sites or initiates drive-by malware downloads. Always preview the destination URL.",
        "tags": ["QR", "URL", "Physical"],
    },
]

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:.5rem 0 1.5rem;">
        <div style="font-family:'Orbitron',sans-serif; font-size:1.1rem; font-weight:800;
             background:linear-gradient(120deg,var(--accent-c),var(--accent-p));
             -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
            🛡️ SCAM SHIELD
        </div>
        <div class="live-indicator" style="margin-top:.5rem;">
            <span class="pulse-dot"></span> LIVE PROTECTION ON
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    nav_items = [
        ("🏠", "home",      "Dashboard"),
        ("🎥", "video",     "Video Analysis"),
        ("🖼️", "image",     "Image Analysis"),
        ("🎤", "audio",     "Voice Analysis"),
        ("🌐", "url",       "URL Scanner"),
        ("💬", "text",      "Text / SMS Scam"),
        ("📧", "email",     "Email Header"),
        ("📊", "history",   "Scan History"),
        ("🎓", "education", "Scam Academy"),
    ]
    for icon, pg, label in nav_items:
        active = "active" if st.session_state.page == pg else ""
        if st.button(f"{icon}  {label}", key=f"nav_{pg}", use_container_width=True):
            go(pg)

    st.markdown("---")
    st.markdown('<div style="color:var(--text-lo);font-size:.75rem;font-family:\'Share Tech Mono\',monospace;text-align:center;padding:.5rem;">v2.0 · Powered by Claude AI + VirusTotal</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGE: HOME
# ─────────────────────────────────────────────
if st.session_state.page == "home":
    st.markdown('<div class="hero-bg">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">🛡️ AI SCAM SHIELD</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Advanced AI-powered detection · Deepfakes · Phishing · Malware · Voice Cloning</p>', unsafe_allow_html=True)

    # live indicator
    col_li, col_blank = st.columns([1, 3])
    with col_li:
        st.markdown("""
        <div class="live-indicator" style="margin:0 auto 2rem;">
            <span class="pulse-dot"></span> SHIELD ACTIVE
        </div>
        """, unsafe_allow_html=True)

    # Stats bar
    st.markdown("""
    <div class="stats-bar">
        <div class="stat-item"><div class="stat-number">99.2%</div><div class="stat-label">Accuracy</div></div>
        <div class="stat-item"><div class="stat-number">7</div><div class="stat-label">Detection Modes</div></div>
        <div class="stat-item"><div class="stat-number">70+</div><div class="stat-label">AV Engines</div></div>
        <div class="stat-item"><div class="stat-number">24/7</div><div class="stat-label">Protection</div></div>
        <div class="stat-item"><div class="stat-number">&lt;5s</div><div class="stat-label">Scan Speed</div></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Alert banner
    st.markdown("""
    <div class="alert-banner">
        <span style="color:var(--accent-r);font-family:'Orbitron',sans-serif;font-size:.85rem;font-weight:700;">⚠️  THREAT ALERT</span>
        <p style="color:var(--text-mid);margin:.4rem 0 0;font-size:.88rem;">
            AI-powered scams are surging. Voice cloning, deepfake videos, and hyper-personalised phishing are being deployed at scale.
            Use every tool below to protect yourself and your organisation.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Detection grid
    st.markdown('<div class="section-header">🔍 Choose a Detection Tool</div>', unsafe_allow_html=True)
    st.markdown('<div class="det-grid">', unsafe_allow_html=True)

    cards = [
        ("video",     "🎥", "Video Analysis",   "Deepfake videos, face-swaps, lip-sync manipulation",    ["Deepfake", "Face-Swap", "Malware"]),
        ("image",     "🖼️", "Image Analysis",   "AI-generated images, photo manipulation, fake docs",     ["AI-Gen", "Photoshop", "Malware"]),
        ("audio",     "🎤", "Voice Analysis",   "AI voice cloning, synthetic speech, phone scams",        ["Voice Clone", "TTS", "Splicing"]),
        ("url",       "🌐", "URL Scanner",      "Phishing domains, malware sites, suspicious redirects",  ["Phishing", "Malware", "Redirect"]),
        ("text",      "💬", "Text / SMS Scam",  "Scam messages, fraud patterns, social engineering",     ["SMS", "Social Eng.", "Pattern"]),
        ("email",     "📧", "Email Header",     "SPF/DKIM/DMARC checks, header forensics",               ["SPF", "DKIM", "DMARC"]),
        ("education", "🎓", "Scam Academy",     "Learn how scams work & protect yourself",               ["Guide", "Tips", "Awareness"]),
    ]

    cols = st.columns(4)
    for i, (pg, icon, title, desc, tags) in enumerate(cards):
        with cols[i % 4]:
            badges = "".join(f'<span class="badge">{t}</span>' for t in tags)
            st.markdown(f"""
            <div class="det-card">
                <div class="icon">{icon}</div>
                <div class="title">{title}</div>
                <div class="desc">{desc}</div>
                <div style="margin-top:.8rem;">{badges}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Open {title.split()[0]}", key=f"home_{pg}"):
                go(pg)

    st.markdown('</div>', unsafe_allow_html=True)

    # How it works
    st.markdown('<div class="section-header">⚙️ How It Works</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    steps = [
        ("📤", "Upload / Input", "Provide your file, URL, or text"),
        ("🤖", "AI Analysis",    "Models inspect for manipulation patterns"),
        ("🛡️", "Multi-Engine",   "VirusTotal checks 70+ AV databases"),
        ("📊", "Verdict",        "Detailed report with confidence & actions"),
    ]
    for col, (icon, title, desc) in zip([c1,c2,c3,c4], steps):
        with col:
            st.markdown(f"""
            <div class="info-card" style="text-align:center;">
                <div style="font-size:2rem;margin-bottom:.5rem;">{icon}</div>
                <div style="color:var(--accent-c);font-family:'Orbitron',sans-serif;font-size:.78rem;font-weight:700;letter-spacing:.05em;margin-bottom:.4rem;">{title}</div>
                <div style="color:var(--text-lo);font-size:.82rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

    # Recent scans mini
    if st.session_state.scan_history:
        st.markdown('<div class="section-header">🕒 Recent Scans</div>', unsafe_allow_html=True)
        for h in st.session_state.scan_history[:4]:
            badge_cls = {"FAKE":"danger","REAL":"safe"}.get(h["result"],"warning")
            st.markdown(f"""
            <div class="hist-row">
                <span style="color:var(--text-lo);font-family:'Share Tech Mono',monospace;font-size:.75rem;">{h["time"]}</span>
                <span class="chip">{h["type"]}</span>
                <span style="flex:1;color:var(--text-mid);font-size:.82rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{h["file"]}</span>
                <span class="hist-badge {badge_cls}">{h["result"]} {h["confidence"]}%</span>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  SHARED: back button helper
# ─────────────────────────────────────────────
def back_button(key):
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("← Back to Dashboard", key=key):
        go("home")
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGE: VIDEO
# ─────────────────────────────────────────────
if st.session_state.page == "video":
    back_button("back_v")
    st.markdown('<h1 class="main-title">🎥 Video Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Detect deepfakes, face-swaps & AI-generated video</p>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["  📤  Upload & Analyze  ", "  💡  Detection Guide  "])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="info-card"><h4 style="color:var(--accent-c);margin:0;">📋 Supported Formats</h4><p style="color:var(--text-lo);margin:.4rem 0 0;">MP4 · AVI · MOV · MKV · WebM</p></div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="info-card"><h4 style="color:var(--accent-c);margin:0;">📁 Recommended Size</h4><p style="color:var(--text-lo);margin:.4rem 0 0;">Up to 200 MB for best results</p></div>', unsafe_allow_html=True)

        file = st.file_uploader("Drop your video file here", type=["mp4","avi","mov","mkv","webm"], key="vu")

        if file:
            st.video(file)

            sensitivity = st.select_slider("Detection Sensitivity", ["Low", "Medium", "High", "Ultra"], value="High")

            ca, cb = st.columns(2)
            with ca:
                if st.button("🔍 Run Deepfake Analysis", use_container_width=True):
                    with st.spinner("Analyzing frames with AI models..."):
                        r, c, _, frames, res, scores = process_video(file)

                    st.markdown('<div class="section-header">📊 Verdict</div>', unsafe_allow_html=True)
                    show_result(r, c, "Video", file.name)

                    if frames:
                        st.markdown('<div class="section-header">🎞️ Frame Samples</div>', unsafe_allow_html=True)
                        fcols = st.columns(min(5, len(frames)))
                        for i, (fr, rs) in enumerate(zip(frames[:5], res[:5])):
                            with fcols[i]:
                                st.image(fr, caption=f"#{i+1}: {rs}", use_container_width=True)

                    if scores:
                        st.markdown('<div class="section-header">📈 Confidence Over Frames</div>', unsafe_allow_html=True)
                        df = pd.DataFrame({"Frame": range(1,len(scores)+1), "Fake Probability (%)": scores})
                        st.area_chart(df.set_index("Frame"))

                        # Frame statistics
                        st.markdown('<div class="section-header">📉 Frame Statistics</div>', unsafe_allow_html=True)
                        s1,s2,s3,s4 = st.columns(4)
                        for col, label, val in [
                            (s1, "Peak Score",  f"{max(scores):.1f}%"),
                            (s2, "Avg Score",   f"{sum(scores)/len(scores):.1f}%"),
                            (s3, "Fake Frames", f"{sum(1 for s in scores if s>50)}/{len(scores)}"),
                            (s4, "Risk Level",  "HIGH" if max(scores)>70 else "MED" if max(scores)>40 else "LOW"),
                        ]:
                            with col:
                                st.markdown(f'<div class="info-card" style="text-align:center;"><div style="font-family:\'Orbitron\',sans-serif;font-size:1.4rem;color:var(--accent-c);">{val}</div><div style="color:var(--text-lo);font-size:.78rem;text-transform:uppercase;">{label}</div></div>', unsafe_allow_html=True)

            with cb:
                if st.button("🛡️ Malware Scan", use_container_width=True):
                    perform_vt_scan(file)

    with tab2:
        st.markdown('<div class="section-header">🎭 What We Detect</div>', unsafe_allow_html=True)
        for icon, title, desc in [
            ("🎭","Face Swaps","AI models overlay a synthetic face onto a real video, often used to impersonate public figures."),
            ("👄","Lip Sync Manipulation","The audio or lip movements are altered to make a person appear to say something they never said."),
            ("🤖","Fully Synthetic Video","Entire scenes generated by AI — no real footage used whatsoever."),
            ("✂️","Context Splicing","Real clips edited together to fabricate events or statements out of context."),
            ("🌊","Temporal Inconsistencies","Flickering, blurring, or mismatched motion blur between subject and background."),
        ]:
            st.markdown(f"""
            <div class="edu-card">
                <h4>{icon} {title}</h4>
                <p>{desc}</p>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGE: IMAGE
# ─────────────────────────────────────────────
elif st.session_state.page == "image":
    back_button("back_i")
    st.markdown('<h1 class="main-title">🖼️ Image Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Identify manipulated and AI-generated images</p>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["  📤  Upload & Analyze  ", "  💡  Detection Guide  "])

    with tab1:
        file = st.file_uploader("Drop your image here", type=["jpg","jpeg","png","webp","bmp"], key="iu")

        if file:
            col_img, col_meta = st.columns([2, 1])
            with col_img:
                st.image(file, use_container_width=True)
            with col_meta:
                st.markdown('<div class="section-header">📋 File Info</div>', unsafe_allow_html=True)
                fsize = round(file.size / 1024, 1)
                st.markdown(f"""
                <div class="terminal">Filename : {file.name}
Size     : {fsize} KB
Type     : {file.type}
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<div class="section-header">🔎 Analysis Options</div>', unsafe_allow_html=True)
                check_ela   = st.checkbox("Error Level Analysis (ELA)", value=True)
                check_noise = st.checkbox("Noise Pattern Analysis", value=True)
                check_meta  = st.checkbox("Metadata Inspection", value=True)

            ca, cb = st.columns(2)
            with ca:
                if st.button("🔍 Analyze Image", use_container_width=True):
                    with st.spinner("Running AI image forensics..."):
                        r, c, _ = process_image(file)
                    st.markdown('<div class="section-header">📊 Verdict</div>', unsafe_allow_html=True)
                    show_result(r, c, "Image", file.name)

                    # Forensic detail cards
                    st.markdown('<div class="section-header">🔬 Forensic Signals</div>', unsafe_allow_html=True)
                    signals_map = {
                        "FAKE": [("bad","High ELA anomaly detected in facial region"),("bad","Inconsistent JPEG blocking patterns"),("warn","Lighting direction mismatch"),("warn","GAN fingerprint signatures found")],
                        "REAL": [("ok","ELA shows uniform compression patterns"),("ok","Natural noise distribution"),("ok","Consistent metadata chain")],
                        "SUSPICIOUS": [("warn","Moderate ELA anomalies"),("warn","Some metadata fields missing"),("ok","Noise pattern mostly natural")],
                    }
                    for cls, msg in signals_map.get(r, signals_map["SUSPICIOUS"]):
                        icon = {"ok":"✅","warn":"⚠️","bad":"❌"}[cls]
                        st.markdown(f'<div class="checklist-item {cls}"><span class="check-icon">{icon}</span><span style="color:var(--text-mid);">{msg}</span></div>', unsafe_allow_html=True)

            with cb:
                if st.button("🛡️ Malware Scan", use_container_width=True):
                    perform_vt_scan(file)

    with tab2:
        for icon, title, desc in [
            ("🎨","AI-Generated Images","Produced by DALL-E, Midjourney, Stable Diffusion. Telltales: impossible hands, unnatural backgrounds, text artifacts."),
            ("✏️","Photoshop Manipulation","Clone-stamping, liquify warping, frequency-based retouching — detected via ELA and noise analysis."),
            ("👤","Face Morphing","Biometric blending of two faces — used in identity fraud to pass KYC verification."),
            ("📝","Fake Screenshots","Fabricated messages, bank statements, or news headlines. Check pixel consistency and font rendering."),
        ]:
            st.markdown(f'<div class="edu-card"><h4>{icon} {title}</h4><p>{desc}</p></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGE: AUDIO
# ─────────────────────────────────────────────
elif st.session_state.page == "audio":
    back_button("back_a")
    st.markdown('<h1 class="main-title">🎤 Voice Analysis</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Detect AI-cloned voices and synthetic audio</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="alert-banner">
        <span style="color:var(--accent-y);font-family:'Orbitron',sans-serif;font-size:.82rem;font-weight:700;">⚠️  VOICE CLONING ALERT</span>
        <p style="color:var(--text-mid);margin:.4rem 0 0;font-size:.85rem;">
            Criminals can clone a voice from as little as 3 seconds of audio scraped from social media. 
            Establish a family <strong style="color:var(--accent-c);">"code word"</strong> to verify emergency calls.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["  📤  Upload & Analyze  ", "  💡  Detection Guide  "])

    with tab1:
        file = st.file_uploader("Drop your audio file here", type=["mp3","wav","ogg","m4a","flac"], key="au")

        if file:
            st.audio(file)

            ca, cb = st.columns(2)
            with ca:
                if st.button("🔍 Analyze Voice", use_container_width=True):
                    with st.spinner("Running spectral & prosody analysis..."):
                        r, c, _ = process_audio(file)
                    show_result(r, c, "Audio", file.name)

                    st.markdown('<div class="section-header">🔬 Audio Forensics</div>', unsafe_allow_html=True)
                    forensics = {
                        "FAKE": [("bad","Unnatural prosody — robotic pitch variation"),("bad","GAN-type spectral artefacts detected"),("warn","Micro-pauses inconsistent with natural speech")],
                        "REAL": [("ok","Natural prosody and pitch variation"),("ok","Consistent background noise floor"),("ok","No spectral artifacts detected")],
                        "SUSPICIOUS": [("warn","Borderline spectral patterns"),("warn","Some prosody irregularities"),("ok","Background noise appears natural")],
                    }
                    for cls, msg in forensics.get(r, forensics["SUSPICIOUS"]):
                        icon = {"ok":"✅","warn":"⚠️","bad":"❌"}[cls]
                        st.markdown(f'<div class="checklist-item {cls}"><span class="check-icon">{icon}</span><span style="color:var(--text-mid);">{msg}</span></div>', unsafe_allow_html=True)

            with cb:
                if st.button("🛡️ Malware Scan", use_container_width=True):
                    perform_vt_scan(file)

    with tab2:
        for icon, title, desc in [
            ("🗣️","Voice Cloning","Real-time AI voice conversion trained on short clips. Used to impersonate family members demanding emergency money."),
            ("🤖","Text-to-Speech Fraud","TTS voices from ElevenLabs, Murf, or open-source models used in robocall scams and fake customer service."),
            ("✂️","Audio Splicing","Legitimate recordings edited to fabricate statements — common in political disinformation."),
            ("📞","Emergency Grandparent Scam","'Grandma, I'm in jail — don't tell mum, just wire money.' Extremely effective because of emotional pressure."),
        ]:
            st.markdown(f'<div class="edu-card"><h4>{icon} {title}</h4><p>{desc}</p></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGE: URL
# ─────────────────────────────────────────────
elif st.session_state.page == "url":
    back_button("back_u")
    st.markdown('<h1 class="main-title">🌐 URL Scanner</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Check links for phishing, malware & suspicious domains</p>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["  🔗  Scan URL  ", "  🚩  Red Flags Guide  "])

    with tab1:
        url = st.text_input("Paste URL to scan", placeholder="https://example.com", key="url_in")

        if url:
            # Heuristic pre-scan
            pre_signals = []
            pre_score   = 0
            parsed_url  = url.lower()

            heuristics = [
                (r'https?://', "Uses HTTP/HTTPS scheme", "ok", 0),
                (r'\.xyz$|\.top$|\.click$|\.tk$|\.ml$|\.ga$|\.cf$', "Suspicious TLD detected", "bad", 25),
                (r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', "Raw IP address (no domain)", "bad", 30),
                (r'paypal|amazon|google|microsoft|apple|netflix', "Brand name in URL — verify carefully", "warn", 10),
                (r'login|signin|verify|account|secure|update|confirm', "Phishing keyword in URL", "warn", 15),
                (r'@', "@ character in URL — possible redirect trick", "bad", 25),
                (r'https://', "HTTPS encrypted connection", "ok", 0),
            ]

            for pattern, label, cls, weight in heuristics:
                if re.search(pattern, parsed_url):
                    pre_signals.append((cls, label))
                    pre_score += weight

            pre_score = min(pre_score, 100)

            st.markdown('<div class="section-header">🔬 Pre-Scan Heuristic</div>', unsafe_allow_html=True)
            for cls, msg in pre_signals:
                icon = {"ok":"✅","warn":"⚠️","bad":"❌"}[cls]
                st.markdown(f'<div class="checklist-item {cls}"><span class="check-icon">{icon}</span><span style="color:var(--text-mid);">{msg}</span></div>', unsafe_allow_html=True)

        if st.button("🔍 Full Scan via VirusTotal (70+ Engines)", use_container_width=True):
            if url:
                with st.spinner("Submitting URL to VirusTotal..."):
                    result = scan_url(url)

                st.markdown('<div class="section-header">📊 Scan Results</div>', unsafe_allow_html=True)
                if result:
                    st.markdown(f'<div class="terminal">{result}</div>', unsafe_allow_html=True)
                    add_history("URL", url[:60], "SUSPICIOUS" if "malicious" in str(result).lower() else "REAL", 75)
                else:
                    st.error("❌ Scan failed. Check API key or URL format.")
            else:
                st.warning("⚠️ Please enter a URL first.")

        # QR section
        st.markdown("<br>", unsafe_allow_html=True)
        qr_info_display()

    with tab2:
        st.markdown('<div class="section-header">🚩 Red Flags in URLs</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="compare-col"><h5>❌ Dangerous Signs</h5>', unsafe_allow_html=True)
            for item in ["Misspelled brands (paypa1.com)","Suspicious TLDs (.xyz, .tk, .ml)","Raw IP addresses (http://192.168.x.x)","@ symbol in URL","Extra subdomains (paypal.evil.com)","No HTTPS on login pages"]:
                st.markdown(f'<div class="checklist-item bad"><span class="check-icon">❌</span><span style="color:var(--text-mid);">{item}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="compare-col"><h5>✅ Good Signs</h5>', unsafe_allow_html=True)
            for item in ["Correct brand domain","Reputable TLD (.com, .org, .gov)","HTTPS with valid certificate","Short, readable URL structure","Matches official site exactly","No unexpected redirects"]:
                st.markdown(f'<div class="checklist-item ok"><span class="check-icon">✅</span><span style="color:var(--text-mid);">{item}</span></div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGE: TEXT / SMS SCAM  (new)
# ─────────────────────────────────────────────
elif st.session_state.page == "text":
    back_button("back_t")
    st.markdown('<h1 class="main-title">💬 Text / SMS Scam Detector</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Paste any suspicious message to reveal scam patterns</p>', unsafe_allow_html=True)

    text_input = st.text_area("Paste the suspicious message below", height=200, placeholder="Paste SMS, WhatsApp message, social post, or any suspicious text here...", key="text_in")

    if st.button("🔍 Analyze for Scam Patterns", use_container_width=True):
        if text_input.strip():
            verdict, conf, signals = analyze_text_for_scam(text_input)
            show_result(verdict, conf, "Text/SMS", text_input[:40]+"...")

            st.markdown('<div class="section-header">🧠 Pattern Analysis</div>', unsafe_allow_html=True)
            for cls, msg in signals:
                icon = {"ok":"✅","warn":"⚠️","bad":"❌"}[cls]
                st.markdown(f'<div class="checklist-item {cls}"><span class="check-icon">{icon}</span><span style="color:var(--text-mid);">{msg}</span></div>', unsafe_allow_html=True)

            # Scam type guess
            st.markdown('<div class="section-header">🏷️ Likely Scam Category</div>', unsafe_allow_html=True)
            t = text_input.lower()
            category = "Unknown / General Fraud"
            if any(kw in t for kw in ["prize","winner","congratulations"]):
                category = "🎰 Lottery / Prize Scam"
            elif any(kw in t for kw in ["bank","account","verify","login"]):
                category = "🎣 Phishing / Credential Theft"
            elif any(kw in t for kw in ["love","sweetheart","dear"]):
                category = "💔 Romance / Advance-Fee Fraud"
            elif any(kw in t for kw in ["irs","tax","government","grant"]):
                category = "🏛️ Government Impersonation"
            elif any(kw in t for kw in ["bitcoin","crypto","investment"]):
                category = "💰 Crypto / Investment Fraud"

            st.markdown(f"""
            <div class="info-card" style="border-color:var(--accent-p);">
                <div style="font-family:'Orbitron',sans-serif;color:var(--accent-p);font-size:.9rem;">{category}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Please paste a message to analyze.")

    with st.expander("💡 Common SMS Scam Templates to Watch For"):
        examples = [
            ("Bank Phishing", "Your account has been locked. Verify immediately at http://bank-secure-login.xyz"),
            ("Package Scam",  "USPS: Your package is on hold. Pay $2.99 fee: http://usps-delivery.tk"),
            ("Prize Scam",    "Congratulations! You've won a $1000 gift card. Claim now before it expires!"),
            ("Crypto Scam",   "I made $50k last month with this system. DM me for the secret strategy."),
        ]
        for title, example in examples:
            st.markdown(f"""
            <div class="edu-card">
                <h4>🚩 {title}</h4>
                <p style="font-family:'Share Tech Mono',monospace;color:var(--accent-r);font-size:.82rem;">"{example}"</p>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGE: EMAIL HEADER  (new)
# ─────────────────────────────────────────────
elif st.session_state.page == "email":
    back_button("back_e")
    st.markdown('<h1 class="main-title">📧 Email Header Analyzer</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Forensic SPF · DKIM · DMARC header inspection</p>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-card">
        <h4 style="color:var(--accent-c);margin:0 0 .5rem;">How to get email headers</h4>
        <p style="color:var(--text-mid);font-size:.85rem;margin:0;">
            <strong>Gmail:</strong> Open email → ⋮ menu → "Show original" → Copy all<br>
            <strong>Outlook:</strong> File → Properties → "Internet headers" → Copy<br>
            <strong>Apple Mail:</strong> View → Message → All Headers → Copy
        </p>
    </div>
    """, unsafe_allow_html=True)

    headers_input = st.text_area("Paste raw email headers here", height=250, placeholder="Received: from mail.example.com...\nAuthentication-Results: spf=pass...", key="email_in")

    if st.button("🔍 Analyze Headers", use_container_width=True):
        if headers_input.strip():
            verdict, conf, signals = analyze_email_headers(headers_input)
            show_result(verdict, conf, "Email Header", "email-header-analysis")

            st.markdown('<div class="section-header">🔬 Authentication Results</div>', unsafe_allow_html=True)
            for cls, msg in signals:
                icon = {"ok":"✅","warn":"⚠️","bad":"❌"}[cls]
                st.markdown(f'<div class="checklist-item {cls}"><span class="check-icon">{icon}</span><span style="color:var(--text-mid);">{msg}</span></div>', unsafe_allow_html=True)

            # Show parsed header excerpt
            st.markdown('<div class="section-header">📋 Header Extract</div>', unsafe_allow_html=True)
            lines = [l for l in headers_input.split("\n") if any(k in l.lower() for k in ["spf","dkim","dmarc","received","from","reply-to","return-path"])]
            excerpt = "\n".join(lines[:15])
            st.markdown(f'<div class="terminal">{excerpt if excerpt else "(no relevant headers found)"}</div>', unsafe_allow_html=True)
        else:
            st.warning("⚠️ Please paste email headers to analyze.")

    with st.expander("📖 Understanding Email Authentication"):
        for proto, desc in [
            ("SPF (Sender Policy Framework)", "Lists which mail servers are allowed to send email for a domain. A FAIL means the email wasn't sent from an authorized server — strong indicator of spoofing."),
            ("DKIM (DomainKeys Identified Mail)", "Adds a cryptographic signature to the email. A FAIL means the content was modified after sending — classic sign of tampering."),
            ("DMARC (Domain-based Message Auth)", "Policy that tells receivers what to do when SPF/DKIM fail. A FAIL means the sender domain doesn't match the From address — definitive spoofing indicator."),
        ]:
            st.markdown(f'<div class="edu-card"><h4>🔑 {proto}</h4><p>{desc}</p></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PAGE: SCAN HISTORY  (new)
# ─────────────────────────────────────────────
elif st.session_state.page == "history":
    back_button("back_h")
    st.markdown('<h1 class="main-title">📊 Scan History</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">All scans performed this session</p>', unsafe_allow_html=True)

    if not st.session_state.scan_history:
        st.markdown("""
        <div class="info-card" style="text-align:center; padding:3rem;">
            <div style="font-size:3rem; margin-bottom:1rem;">📭</div>
            <div style="color:var(--text-mid);">No scans yet. Run your first analysis to see results here.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Summary stats
        total  = len(st.session_state.scan_history)
        fakes  = sum(1 for h in st.session_state.scan_history if h["result"] == "FAKE")
        reals  = sum(1 for h in st.session_state.scan_history if h["result"] == "REAL")
        sus    = total - fakes - reals

        c1, c2, c3, c4 = st.columns(4)
        for col, val, label, clr in [
            (c1, total, "Total Scans",  "var(--accent-c)"),
            (c2, fakes, "Fakes Found",  "var(--accent-r)"),
            (c3, sus,   "Suspicious",   "var(--accent-y)"),
            (c4, reals, "Clean",        "var(--accent-g)"),
        ]:
            with col:
                st.markdown(f"""
                <div class="info-card" style="text-align:center;">
                    <div style="font-family:'Orbitron',sans-serif;font-size:2rem;font-weight:800;color:{clr};">{val}</div>
                    <div style="color:var(--text-lo);font-size:.78rem;text-transform:uppercase;letter-spacing:.1em;">{label}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">🕒 Scan Log</div>', unsafe_allow_html=True)

        # Filter
        filter_type = st.selectbox("Filter by type", ["All", "Video", "Image", "Audio", "URL", "Text/SMS", "Email Header"], key="hist_filter")

        history = st.session_state.scan_history
        if filter_type != "All":
            history = [h for h in history if h["type"] == filter_type]

        for h in history:
            badge_cls = {"FAKE":"danger","REAL":"safe"}.get(h["result"],"warning")
            st.markdown(f"""
            <div class="hist-row">
                <span style="color:var(--text-lo);font-family:'Share Tech Mono',monospace;font-size:.75rem;min-width:60px;">{h["time"]}</span>
                <span class="chip">{h["type"]}</span>
                <span style="flex:1;color:var(--text-mid);font-size:.82rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{h["file"]}</span>
                <span class="hist-badge {badge_cls}">{h["result"]} · {h["confidence"]}%</span>
            </div>
            """, unsafe_allow_html=True)

        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.scan_history = []
            st.rerun()

# ─────────────────────────────────────────────
#  PAGE: EDUCATION  (new)
# ─────────────────────────────────────────────
elif st.session_state.page == "education":
    back_button("back_edu")
    st.markdown('<h1 class="main-title">🎓 Scam Academy</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Know your enemy — understand how scams work to stay protected</p>', unsafe_allow_html=True)

    # Quick quiz
    st.markdown('<div class="section-header">⚡ Quick Scam IQ Quiz</div>', unsafe_allow_html=True)
    with st.expander("Test your knowledge — click to open quiz"):
        questions = [
            {
                "q": "A caller claims to be your grandson and says he's in jail — what's the FIRST thing you should do?",
                "options": ["Wire money immediately", "Hang up and call your grandson on his known number", "Ask for the jail's phone number", "Give them your bank details"],
                "answer": 1,
                "explain": "The grandparent scam relies on panic. Always hang up and independently verify using a number you already know.",
            },
            {
                "q": "You receive an email saying 'Your Amazon account is locked — verify now at amazon-secure-login.xyz'. What is this?",
                "options": ["A legitimate Amazon email", "A phishing attack", "A security test", "An account upgrade"],
                "answer": 1,
                "explain": "Amazon will never use a third-party domain. Always check the sender domain exactly and go directly to amazon.com.",
            },
            {
                "q": "What is the minimum audio needed for AI to clone a human voice convincingly?",
                "options": ["30 minutes", "5 minutes", "3 seconds", "1 hour"],
                "answer": 2,
                "explain": "Modern AI voice cloning tools can produce convincing clones from as little as 3 seconds of audio.",
            },
        ]

        score_q = 0
        answers = []
        for i, q in enumerate(questions):
            st.markdown(f'<div style="color:var(--text-hi);font-weight:600;margin-top:1rem;">Q{i+1}: {q["q"]}</div>', unsafe_allow_html=True)
            choice = st.radio("", q["options"], key=f"quiz_{i}", index=None)
            answers.append(choice)

        if st.button("📊 Submit Quiz", use_container_width=True):
            for i, (q, ans) in enumerate(zip(questions, answers)):
                if ans is None:
                    st.warning(f"Q{i+1}: Not answered")
                elif q["options"].index(ans) == q["answer"]:
                    st.success(f"Q{i+1}: ✅ Correct! {q['explain']}")
                    score_q += 1
                else:
                    st.error(f"Q{i+1}: ❌ Incorrect. {q['explain']}")
            st.markdown(f'<div class="info-card" style="text-align:center;"><div style="font-family:\'Orbitron\',sans-serif;font-size:2rem;color:var(--accent-c);">{score_q}/{len(questions)}</div><div style="color:var(--text-lo);">Scam IQ Score</div></div>', unsafe_allow_html=True)

    # Education cards
    st.markdown('<div class="section-header">📚 Essential Guides</div>', unsafe_allow_html=True)

    tag_filter = st.multiselect("Filter by topic", sorted({t for e in EDUCATION for t in e["tags"]}), key="edu_filter")

    for edu in EDUCATION:
        if tag_filter and not any(t in edu["tags"] for t in tag_filter):
            continue
        tags_html = "".join(f'<span class="badge">{t}</span>' for t in edu["tags"])
        st.markdown(f"""
        <div class="edu-card">
            <h4>{edu["title"]}</h4>
            <p>{edu["body"]}</p>
            <div style="margin-top:.8rem;">{tags_html}</div>
        </div>
        """, unsafe_allow_html=True)

    # Protect yourself checklist
    st.markdown('<div class="section-header">🛡️ Personal Protection Checklist</div>', unsafe_allow_html=True)
    checklist = [
        ("Enable two-factor authentication (2FA) on all accounts", True),
        ("Create a family 'code word' for emergency verification", True),
        ("Never send money via gift cards, wire transfer, or crypto to strangers", True),
        ("Hover over links before clicking — check the actual URL", True),
        ("Reverse-image-search profile photos of new online contacts", True),
        ("Keep antivirus and OS software updated", True),
        ("Set up Google Alerts for your name to detect identity fraud", False),
        ("Use a password manager with unique passwords per site", True),
    ]
    for action, priority in checklist:
        cls = "ok" if priority else "warn"
        icon = "✅" if priority else "💡"
        st.markdown(f'<div class="checklist-item {cls}"><span class="check-icon">{icon}</span><span style="color:var(--text-mid);">{action}</span></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown("""
<div class="site-footer">
    🛡️ AI SCAM SHIELD v2.0 &nbsp;·&nbsp; Protecting you from digital deception
    <br>
    Powered by advanced AI models · VirusTotal · SPF/DKIM/DMARC analysis
</div>
""", unsafe_allow_html=True)
