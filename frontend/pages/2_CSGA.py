"""
CSGA – Cloud Security & Governance Assistant
Streamlit Frontend with:
  - Live activity feed during analysis
  - Persistent conversation memory (history.json)
  - Security score widget in sidebar
  - Exportable markdown report
  - AWS profile dropdown from credentials file
"""
import streamlit as st
import requests
import json
import uuid
import os
from datetime import datetime
from pathlib import Path

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CSGA – Cloud Security & Governance Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Constants ────────────────────────────────────────────────────────────────
BACKEND = "http://localhost:8000/api/v1"
HISTORY_FILE = Path(__file__).parent / "chat_history_csga.json"

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background: #f8fafc; color: #0f172a; min-height: 100vh; }
header, footer, [data-testid="stToolbar"] { visibility: hidden !important; height: 0 !important; }

/* Sidebar */
[data-testid="stSidebar"] { background: #f1f5f9 !important; border-right: 1px solid #cbd5e1; }
[data-testid="stSidebar"] > div:first-child { padding: 1.25rem 1rem !important; }

/* Sidebar logo */
.sidebar-logo { display:flex;align-items:center;gap:10px;padding:0.4rem 0 1rem;border-bottom:1px solid #cbd5e1;margin-bottom:1rem; }
.sidebar-logo-text h2 { font-size:1.1rem;font-weight:700;color:#0f172a;margin:0; }
.sidebar-logo-text p  { font-size:0.68rem;color:#475569;margin:1px 0 0; }

/* Section labels */
.sidebar-section { font-size:0.62rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#475569;margin:1rem 0 0.45rem; }

/* Buttons */
.stButton > button {
    background: #ffffff !important;
    color:#475569 !important; border:1px solid #cbd5e1 !important;
    border-radius:8px !important; font-size:0.8rem !important;
    font-weight:500 !important; transition:all 0.18s ease !important;
}
.stButton > button:hover {
    background:#f8fafc !important;
    border-color:#3b82f6 !important; color:#0284c7 !important;
    transform:translateY(-1px); box-shadow:0 4px 14px rgba(59,130,246,0.12) !important;
}

/* Score widget */
.score-box {
    text-align:center; padding:1rem 0.5rem; border-radius:12px; margin:0.5rem 0;
    border:1px solid; background: #ffffff;
}
.score-number { font-size:2.2rem; font-weight:800; line-height:1; }
.score-label  { font-size:0.68rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; margin-top:4px; }

/* Inputs */
.stTextInput input, .stSelectbox div[data-baseweb="select"] {
    background:#ffffff !important; border:1px solid #cbd5e1 !important;
    border-radius:8px !important; color:#0f172a !important; font-size:0.82rem !important;
}
.stTextInput label, .stSelectbox label { font-size:0.75rem !important; color:#475569 !important; }

/* Chat input */
[data-testid="stChatInput"],
[data-testid="stChatInputContainer"],
div[data-baseweb="textarea"],
div[data-baseweb="base-input"] {
    background:#ffffff !important; border:1px solid #cbd5e1 !important; border-radius:12px !important;
}
[data-testid="stChatInput"] textarea,
[data-baseweb="textarea"] textarea,
div[data-baseweb="base-input"] textarea {
    background:#ffffff !important; color:#0f172a !important; font-size:0.9rem !important;
}
.stBottom, [data-testid="stBottom"] { background:#f8fafc !important; border-top:1px solid #cbd5e1 !important; }

/* Message layout */
.msg-user-header { display:flex;align-items:center;gap:8px;margin:1.1rem 0 3px;justify-content:flex-end; }
.msg-user-body {
    background:#ffffff; border:1px solid #e2e8f0;
    border-radius:12px 4px 12px 12px; padding:0.7rem 1rem;
    margin-bottom:3px; color:#0f172a !important;
    font-size:0.9rem !important; line-height:1.6 !important; margin-left:12%;
}
.msg-cisa-header { display:flex;align-items:center;gap:8px;margin:1.1rem 0 3px; }
.msg-cisa-body {
    border-left:3px solid #0ea5e9;
    background:linear-gradient(135deg,#f0f9ff,#e0f2fe);
    border-radius:0 12px 12px 12px; padding:0.7rem 1rem;
    margin-bottom:3px; margin-right:5%;
}
.msg-cisa-body p,.msg-cisa-body li,.msg-cisa-body span { color:#334155 !important; font-size:0.88rem !important; }
.msg-cisa-body strong,.msg-cisa-body b { color:#0f172a !important; }
.msg-cisa-body h1,.msg-cisa-body h2,.msg-cisa-body h3 { color:#0f172a !important; }
.msg-cisa-body table { border-collapse:collapse; width:100%; margin-top:6px; }
.msg-cisa-body th { background:#e2e8f0; color:#475569 !important; padding:6px 10px; font-size:0.78rem; }
.msg-cisa-body td { border-bottom:1px solid #e2e8f0; color:#334155 !important; padding:5px 10px; font-size:0.82rem; }
.msg-cisa-body code { background:#e2e8f0; color:#0284c7 !important; padding:1px 5px; border-radius:3px; font-size:0.8rem; }
.msg-avatar-sm { width:24px;height:24px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:0.72rem; }
.avatar-user { background:#e2e8f0; }
.avatar-cisa { background:linear-gradient(135deg,#38bdf8,#3b82f6); color:white; }
.msg-label-inline { font-size:0.63rem !important; font-weight:700 !important; letter-spacing:0.1em !important; text-transform:uppercase !important; color:#64748b !important; }
.cisa-label { color:#0ea5e9 !important; }

/* Activity feed */
.feed-row { display:flex;align-items:center;gap:10px;padding:7px 12px;margin:3px 0;border-radius:8px;font-size:0.81rem;border:1px solid #cbd5e1;background:#ffffff;color:#475569; }
.feed-done { background:#f0fdf4;border-color:#bbf7d0;color:#166534; }
.feed-running { background:#eff6ff;border-color:#bfdbfe;color:#1d4ed8;animation:pulse 1.4s ease-in-out infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.55} }

/* Main header */
.main-header { padding:1.2rem 0 0.9rem; border-bottom:1px solid #cbd5e1; margin-bottom:1.2rem; }
.main-title { font-size:1.4rem;font-weight:700;background:linear-gradient(135deg,#0ea5e9,#4f46e5);-webkit-background-clip:text;-webkit-text-fill-color:transparent; }
.main-subtitle { font-size:0.78rem;color:#64748b;margin-top:2px; }

/* Status container */
[data-testid="stStatusWidget"] { background:#ffffff !important; border:1px solid #cbd5e1 !important; border-radius:10px !important; }
</style>
""", unsafe_allow_html=True)

# ─── Tool metadata ────────────────────────────────────────────────────────────
TOOL_META = {
    "get_guardduty_findings":   ("🛡️", "Checking GuardDuty"),
    "get_securityhub_findings": ("🚨", "Checking Security Hub"),
    "list_public_s3_buckets":   ("🪣", "Finding public S3 buckets"),
    "check_backup_status":      ("💾", "Checking backups"),
    "query_knowledge_base":     ("📚", "Querying Knowledge Base"),
    "lookup_cloudtrail_events": ("🔎", "Searching CloudTrail"),
    "query_cloudwatch_logs":    ("📊", "Querying CloudWatch Logs"),
    "check_kms_configuration":  ("🔑", "Checking KMS Config"),
    "get_config_compliance":    ("📋", "Checking AWS Config"),
}
def get_tool_meta(name): return TOOL_META.get(name, ("⚙️", f"Running {name}"))

# ─── Conversation persistence ─────────────────────────────────────────────────
def load_history():
    if HISTORY_FILE.exists():
        try:
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []

def save_history(messages):
    try:
        HISTORY_FILE.write_text(json.dumps(messages, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        st.warning(f"Could not save history: {e}")

# ─── AWS profiles ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def fetch_profiles():
    try:
        r = requests.get(f"{BACKEND}/profiles", timeout=5)
        return r.json().get("profiles", ["default"])
    except Exception:
        return ["default"]

# ─── Security score helpers ───────────────────────────────────────────────────
def score_color(s):
    if s >= 80: return "#22c55e", "#071a12", "#166534"   # green
    if s >= 55: return "#f59e0b", "#1a1400", "#92400e"   # amber
    return "#ef4444", "#1a0000", "#7f1d1d"               # red

def score_label(s):
    if s >= 80: return "SECURE"
    if s >= 55: return "AT RISK"
    return "CRITICAL"

# ─── Report builder ───────────────────────────────────────────────────────────
def build_report(messages):
    lines = [f"# CSGA Security Report\n_Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n\n---\n"]
    for m in messages:
        role = "**You**" if m["role"] == "user" else "**CSGA**"
        lines.append(f"### {role}\n{m['content']}\n")
        if m.get("tools"):
            lines.append(f"_Tools used: {', '.join(m['tools'])}_\n")
        lines.append("---\n")
    return "\n".join(lines)

# ─── Session state ────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = load_history()
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "aws_profile" not in st.session_state:
    st.session_state.aws_profile = "default"
if "security_score" not in st.session_state:
    st.session_state.security_score = None

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
      <span style="font-size:2rem;line-height:1">🛡️</span>
      <div class="sidebar-logo-text">
        <h2>CSGA</h2>
        <p>Cloud Security & Governance Assistant</p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Security score widget ─────────────────────────────────────────────────
    if st.session_state.security_score is not None:
        s = st.session_state.security_score
        fg, bg, border = score_color(s)
        label = score_label(s)
        st.markdown(f"""
        <div class="score-box" style="background:{bg};border-color:{border}">
          <div class="score-number" style="color:{fg}">{s}</div>
          <div class="score-label" style="color:{fg}">Security Score — {label}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="sidebar-section"></div>', unsafe_allow_html=True)

    # ── AWS Profile ───────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section">AWS Configuration</div>', unsafe_allow_html=True)
    profiles = fetch_profiles()
    try:
        default_idx = profiles.index(st.session_state.aws_profile)
    except ValueError:
        default_idx = 0
    chosen = st.selectbox(
        "AWS Profile",
        options=profiles,
        index=default_idx,
        label_visibility="collapsed",
        key="profile_select"
    )
    st.session_state.aws_profile = chosen

    # ── Quick Actions ─────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section">Quick Actions</div>', unsafe_allow_html=True)
    if st.button("🔍 Assess Security Posture", use_container_width=True, key="btn_audit"):
        st.session_state.trigger_msg = (
            "Analyze my AWS security posture across GuardDuty, Security Hub, S3, Backup, and configuration management."
        )
    if st.button("👥 List S3 Buckets", use_container_width=True, key="btn_s3"):
        st.session_state.trigger_msg = "Find all public S3 buckets in my account."
    if st.button("🔎 Check CloudTrail Activity", use_container_width=True, key="btn_ct"):
        st.session_state.trigger_msg = "Look up recent CloudTrail management events."

    # ── Export Report ─────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section">Export</div>', unsafe_allow_html=True)
    if st.session_state.messages:
        report_md = build_report(st.session_state.messages)
        st.download_button(
            label="📥 Download Report",
            data=report_md.encode("utf-8"),
            file_name=f"cisa_report_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
            use_container_width=True,
            key="btn_download"
        )

    # ── Session ───────────────────────────────────────────────────────────────
    st.markdown('<div class="sidebar-section">Session</div>', unsafe_allow_html=True)
    if st.button("🗑️ Clear Chat", use_container_width=True, key="btn_clear"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.security_score = None
        if HISTORY_FILE.exists():
            HISTORY_FILE.unlink()
        st.rerun()
    st.markdown(
        f"<p style='font-size:0.62rem;color:#334155;margin-top:8px'>Session: {st.session_state.session_id[:12]}…</p>",
        unsafe_allow_html=True
    )

# ─── Main layout ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <div class="main-title">🔒 CSGA</div>
  <div class="main-subtitle">AI-powered AWS Cloud Security & Governance Assistant</div>
</div>
""", unsafe_allow_html=True)

# Display conversation history
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="msg-user-header"><span class="msg-label-inline">YOU</span>'
            f'<span class="msg-avatar-sm avatar-user">👤</span></div>',
            unsafe_allow_html=True
        )
        st.markdown(f'<div class="msg-user-body">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="msg-cisa-header"><span class="msg-avatar-sm avatar-cisa">🤖</span>'
            f'<span class="msg-label-inline cisa-label">CSGA</span></div>',
            unsafe_allow_html=True
        )
        st.markdown('<div class="msg-cisa-body">', unsafe_allow_html=True)
        st.markdown(msg["content"])
        if msg.get("tools"):
            st.caption("🔧 Tools: " + " · ".join(f"`{t}`" for t in msg["tools"]))
        st.markdown('</div>', unsafe_allow_html=True)

# ─── Chat input ───────────────────────────────────────────────────────────────
prompt = st.chat_input("Ask about your AWS security and governance…")
if "trigger_msg" in st.session_state:
    prompt = st.session_state.trigger_msg
    del st.session_state.trigger_msg

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(
        f'<div class="msg-user-header"><span class="msg-label-inline">YOU</span>'
        f'<span class="msg-avatar-sm avatar-user">👤</span></div>',
        unsafe_allow_html=True
    )
    st.markdown(f'<div class="msg-user-body">{prompt}</div>', unsafe_allow_html=True)

    # Build history (exclude current message)
    history = [
        {"role": m["role"], "content": [{"text": m["content"]}]}
        for m in st.session_state.messages[:-1]
    ]

    tools_used = []
    full_text = ""

    with st.status("🤖 CSGA is analysing…", expanded=True) as status_box:
        feed = st.empty()
        completed_html = ""

        try:
            resp = requests.post(
                f"{BACKEND}/chat/stream",
                json={
                    "message": prompt,
                    "session_id": st.session_state.session_id,
                    "agent": "csga",
                    "aws_profile": st.session_state.aws_profile if st.session_state.aws_profile != "default" else None,
                    "conversation_history": history,
                },
                stream=True,
                timeout=180,
            )
            resp.raise_for_status()

            for line in resp.iter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line.decode("utf-8"))
                except json.JSONDecodeError:
                    continue

                if data.get("type") == "tool_status":
                    tool = data["tool"]
                    tools_used.append(tool)
                    icon, label = get_tool_meta(tool)
                    completed_html += f'<div class="feed-row feed-done"><span>{icon}</span><span>{label}</span><span style="margin-left:auto;font-size:0.7rem">✓ done</span></div>'
                    feed.markdown(
                        completed_html + '<div class="feed-row feed-running"><span>⏳</span><span>Processing…</span></div>',
                        unsafe_allow_html=True,
                    )

                elif data.get("type") == "security_score":
                    st.session_state.security_score = data["score"]

                elif data.get("type") == "message":
                    full_text = data["content"]

                elif data.get("type") == "error":
                    full_text = f"⚠️ {data.get('content', 'Unknown error')}"

            feed.markdown(
                completed_html + '<div class="feed-row" style="background:#071a12;border-color:#166534;color:#86efac"><span>✅</span><span>Done</span></div>',
                unsafe_allow_html=True,
            )
            status_box.update(label="✅ Analysis complete", state="complete", expanded=False)

        except requests.exceptions.Timeout:
            feed.markdown(
                completed_html + '<div class="feed-row" style="background:#1a0000;border-color:#7f1d1d;color:#fca5a5"><span>⏱️</span><span>Request timed out. Please try again.</span></div>',
                unsafe_allow_html=True,
            )
            status_box.update(label="⏱️ Timed out", state="error", expanded=True)
            full_text = "Sorry, the request timed out. Please try again."

        except Exception as e:
            feed.markdown(
                completed_html + f'<div class="feed-row" style="background:#1a0000;border-color:#7f1d1d;color:#fca5a5"><span>❌</span><span>Error: {e}</span></div>',
                unsafe_allow_html=True,
            )
            status_box.update(label="❌ Failed", state="error", expanded=True)
            full_text = f"Sorry, I encountered an error: {e}"

    # Save assistant response and persist history
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_text,
        "tools": list(dict.fromkeys(tools_used)),
    })
    save_history(st.session_state.messages)
    st.rerun()
