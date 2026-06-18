"""
CISA Frontend — Custom CSS Styles
Premium dark cybersecurity theme with Inter font, cyan/teal accents,
amber warnings, animated indicators, and polished micro-interactions.
"""


def get_custom_css() -> str:
    """Return comprehensive custom CSS for the CISA Streamlit frontend."""
    return """
    <style>
    /* ─────────────────────────────────────────────
       0. GOOGLE FONTS
       ───────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

    /* ─────────────────────────────────────────────
       1. ROOT VARIABLES
       ───────────────────────────────────────────── */
    :root {
        --bg-primary:    #0a0e1a;
        --bg-secondary:  #111827;
        --bg-tertiary:   #1a2332;
        --bg-card:       #111827;
        --bg-card-hover: #162032;
        --accent-cyan:   #06b6d4;
        --accent-teal:   #14b8a6;
        --accent-amber:  #f59e0b;
        --accent-red:    #ef4444;
        --accent-green:  #22c55e;
        --text-primary:  #f1f5f9;
        --text-secondary:#94a3b8;
        --text-muted:    #64748b;
        --border-color:  #1e293b;
        --border-accent: #06b6d420;
        --user-bubble:   #1e2a4a;
        --asst-bubble:   #131c2e;
        --shadow-sm:     0 1px 3px rgba(0,0,0,.4);
        --shadow-md:     0 4px 12px rgba(0,0,0,.5);
        --shadow-glow:   0 0 20px rgba(6,182,212,.15);
        --radius:        10px;
        --transition:    all .25s cubic-bezier(.4,0,.2,1);
    }

    /* ─────────────────────────────────────────────
       2. GLOBAL / BODY
       ───────────────────────────────────────────── */
    html, body, [data-testid="stAppViewContainer"],
    [data-testid="stApp"] {
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    *, *::before, *::after { box-sizing: border-box; }

    /* ─────────────────────────────────────────────
       3. HIDE STREAMLIT DEFAULTS
       ───────────────────────────────────────────── */
    #MainMenu, header[data-testid="stHeader"],
    footer, .stDeployButton,
    [data-testid="stToolbar"] {
        display: none !important;
    }

    div[data-testid="stDecoration"] { display: none !important; }

    /* ─────────────────────────────────────────────
       4. SCROLLBAR
       ───────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb {
        background: var(--text-muted);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: var(--accent-cyan); }

    /* ─────────────────────────────────────────────
       5. SIDEBAR
       ───────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1321 0%, #0a0e1a 100%) !important;
        border-right: 1px solid var(--border-color) !important;
        padding-top: .5rem !important;
    }

    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span,
    section[data-testid="stSidebar"] .stMarkdown label {
        color: var(--text-secondary) !important;
        font-family: 'Inter', sans-serif !important;
    }

    section[data-testid="stSidebar"] hr {
        border-color: var(--border-color) !important;
        margin: .75rem 0 !important;
    }

    /* Sidebar buttons */
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        padding: .55rem 1rem !important;
        font-family: 'Inter', sans-serif !important;
        font-size: .82rem !important;
        font-weight: 500 !important;
        text-align: left !important;
        transition: var(--transition) !important;
        cursor: pointer !important;
    }

    section[data-testid="stSidebar"] .stButton > button:hover {
        background: var(--bg-card-hover) !important;
        border-color: var(--accent-cyan) !important;
        box-shadow: var(--shadow-glow) !important;
        transform: translateY(-1px);
    }

    section[data-testid="stSidebar"] .stButton > button:active {
        transform: translateY(0);
    }

    /* Sidebar selectbox */
    section[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
    }

    /* ─────────────────────────────────────────────
       6. HEADER / GLOWING TITLE
       ───────────────────────────────────────────── */
    .cisa-header {
        text-align: center;
        padding: 1.5rem 0 1rem;
    }

    .cisa-header h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 2rem;
        background: linear-gradient(135deg, #06b6d4 0%, #14b8a6 50%, #06b6d4 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 4s ease-in-out infinite;
        margin: 0;
        letter-spacing: -.02em;
    }

    .cisa-header .tagline {
        color: var(--text-muted);
        font-size: .85rem;
        font-weight: 400;
        margin-top: .25rem;
    }

    @keyframes shimmer {
        0%   { background-position: 0% center; }
        50%  { background-position: 100% center; }
        100% { background-position: 0% center; }
    }

    /* ─────────────────────────────────────────────
       7. CHAT CONTAINER WITH GRADIENT BORDER
       ───────────────────────────────────────────── */
    .chat-container {
        max-width: 860px;
        margin: 0 auto;
        padding: 1rem 0 6rem;
    }

    .chat-container-wrapper {
        position: relative;
        background: var(--bg-primary);
        border-radius: 14px;
        padding: 2px;
        background: linear-gradient(135deg, var(--accent-cyan), transparent 40%, transparent 60%, var(--accent-teal));
    }

    .chat-container-inner {
        background: var(--bg-primary);
        border-radius: 13px;
        padding: 1rem;
    }

    /* ─────────────────────────────────────────────
       8. CHAT BUBBLES
       ───────────────────────────────────────────── */
    .chat-msg {
        display: flex;
        gap: .75rem;
        margin-bottom: 1.25rem;
        animation: fadeSlideIn .35s ease-out both;
    }

    @keyframes fadeSlideIn {
        from { opacity: 0; transform: translateY(12px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .chat-msg .avatar {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        flex-shrink: 0;
        margin-top: 2px;
    }

    .chat-msg.user .avatar {
        background: linear-gradient(135deg, #2563eb, #3b82f6);
    }

    .chat-msg.assistant .avatar {
        background: linear-gradient(135deg, #06b6d4, #14b8a6);
    }

    .chat-msg .bubble {
        flex: 1;
        padding: .85rem 1.1rem;
        border-radius: var(--radius);
        font-size: .9rem;
        line-height: 1.65;
        transition: var(--transition);
        max-width: 100%;
        overflow-x: auto;
    }

    .chat-msg.user .bubble {
        background: var(--user-bubble);
        border: 1px solid #1e3a5f;
        color: var(--text-primary);
    }

    .chat-msg.assistant .bubble {
        background: var(--asst-bubble);
        border: 1px solid var(--border-color);
        border-left: 3px solid var(--accent-cyan);
        color: var(--text-primary);
    }

    .chat-msg .bubble:hover {
        box-shadow: var(--shadow-sm);
    }

    /* ─────────────────────────────────────────────
       9. TOOLS USED TAG
       ───────────────────────────────────────────── */
    .tools-tag {
        display: inline-flex;
        align-items: center;
        gap: .35rem;
        margin-top: .5rem;
        padding: .3rem .7rem;
        background: rgba(6, 182, 212, .08);
        border: 1px solid rgba(6, 182, 212, .2);
        border-radius: 6px;
        font-size: .72rem;
        color: var(--accent-cyan);
        font-weight: 500;
        font-family: 'Inter', sans-serif;
    }

    /* ─────────────────────────────────────────────
       10. TYPING INDICATOR
       ───────────────────────────────────────────── */
    .typing-indicator {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: .6rem 1rem;
        background: var(--asst-bubble);
        border: 1px solid var(--border-color);
        border-left: 3px solid var(--accent-cyan);
        border-radius: var(--radius);
    }

    .typing-indicator .dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--accent-cyan);
        animation: typingBounce 1.4s ease-in-out infinite;
    }

    .typing-indicator .dot:nth-child(2) { animation-delay: .2s; }
    .typing-indicator .dot:nth-child(3) { animation-delay: .4s; }

    @keyframes typingBounce {
        0%, 60%, 100% { transform: translateY(0); opacity: .4; }
        30%            { transform: translateY(-6px); opacity: 1; }
    }

    /* ─────────────────────────────────────────────
       11. STATUS INDICATOR (PULSE)
       ───────────────────────────────────────────── */
    .status-dot {
        display: inline-block;
        width: 9px;
        height: 9px;
        border-radius: 50%;
        margin-right: 6px;
        vertical-align: middle;
    }

    .status-dot.connected {
        background: var(--accent-green);
        box-shadow: 0 0 6px var(--accent-green);
        animation: pulse 2s ease-in-out infinite;
    }

    .status-dot.disconnected {
        background: var(--accent-red);
        box-shadow: 0 0 6px var(--accent-red);
        animation: pulse 1.5s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50%      { opacity: .6; transform: scale(1.15); }
    }

    /* ─────────────────────────────────────────────
       12. CODE BLOCKS
       ───────────────────────────────────────────── */
    .chat-msg .bubble pre {
        background: #0d1117 !important;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1rem;
        overflow-x: auto;
        position: relative;
        margin: .5rem 0;
    }

    .chat-msg .bubble pre code {
        font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
        font-size: .82rem !important;
        line-height: 1.6 !important;
        color: #e6edf3 !important;
    }

    .chat-msg .bubble code {
        font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
        background: rgba(6,182,212,.1) !important;
        color: var(--accent-cyan) !important;
        padding: .15rem .4rem !important;
        border-radius: 4px !important;
        font-size: .82rem !important;
    }

    .chat-msg .bubble pre code {
        background: transparent !important;
        padding: 0 !important;
    }

    /* Streamlit code blocks */
    [data-testid="stCode"], .stCodeBlock {
        background: #0d1117 !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
    }

    /* ─────────────────────────────────────────────
       13. TABLES
       ───────────────────────────────────────────── */
    .chat-msg .bubble table {
        width: 100%;
        border-collapse: collapse;
        margin: .5rem 0;
        font-size: .82rem;
    }

    .chat-msg .bubble table th {
        background: var(--bg-tertiary);
        color: var(--accent-cyan);
        padding: .6rem .8rem;
        text-align: left;
        font-weight: 600;
        border-bottom: 2px solid var(--accent-cyan);
        font-size: .78rem;
        text-transform: uppercase;
        letter-spacing: .04em;
    }

    .chat-msg .bubble table td {
        padding: .55rem .8rem;
        border-bottom: 1px solid var(--border-color);
        color: var(--text-secondary);
    }

    .chat-msg .bubble table tr:nth-child(even) td {
        background: rgba(17, 24, 39, .5);
    }

    .chat-msg .bubble table tr:hover td {
        background: rgba(6, 182, 212, .05);
    }

    /* Streamlit dataframes */
    [data-testid="stDataFrame"] {
        background: var(--bg-secondary) !important;
        border-radius: 8px !important;
    }

    /* ─────────────────────────────────────────────
       14. DETAILS / EXPANDABLE SECTIONS
       ───────────────────────────────────────────── */
    .chat-msg .bubble details {
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: .5rem .75rem;
        margin: .5rem 0;
        background: var(--bg-tertiary);
        transition: var(--transition);
    }

    .chat-msg .bubble details[open] {
        border-color: var(--accent-cyan);
    }

    .chat-msg .bubble details summary {
        cursor: pointer;
        font-weight: 600;
        color: var(--accent-cyan);
        font-size: .85rem;
        padding: .25rem 0;
        user-select: none;
    }

    .chat-msg .bubble details summary:hover {
        color: var(--accent-teal);
    }

    /* ─────────────────────────────────────────────
       15. MAIN AREA INPUTS
       ───────────────────────────────────────────── */
    [data-testid="stChatInput"] {
        background: var(--bg-secondary) !important;
        border-color: var(--border-color) !important;
    }

    [data-testid="stChatInput"] textarea {
        color: var(--text-primary) !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* Text inputs */
    .stTextInput input, .stTextArea textarea {
        background: var(--bg-tertiary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        font-family: 'Inter', sans-serif !important;
        transition: var(--transition) !important;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--accent-cyan) !important;
        box-shadow: 0 0 0 2px rgba(6,182,212,.15) !important;
    }

    /* Select boxes */
    [data-testid="stSelectbox"] > div > div {
        background: var(--bg-tertiary) !important;
        border: 1px solid var(--border-color) !important;
        color: var(--text-primary) !important;
    }

    /* ─────────────────────────────────────────────
       16. BUTTONS (MAIN AREA)
       ───────────────────────────────────────────── */
    .stButton > button {
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
        transition: var(--transition) !important;
    }

    /* ─────────────────────────────────────────────
       17. STREAMLIT CHAT MESSAGES
       ───────────────────────────────────────────── */
    [data-testid="stChatMessage"] {
        background: transparent !important;
        border: none !important;
        padding: .5rem 0 !important;
    }

    /* ─────────────────────────────────────────────
       18. SPINNER
       ───────────────────────────────────────────── */
    .stSpinner > div {
        border-top-color: var(--accent-cyan) !important;
    }

    /* ─────────────────────────────────────────────
       19. EXPANDER (Streamlit)
       ───────────────────────────────────────────── */
    [data-testid="stExpander"] {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
    }

    [data-testid="stExpander"] summary span {
        color: var(--text-secondary) !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* ─────────────────────────────────────────────
       20. RESPONSIVE LAYOUT
       ───────────────────────────────────────────── */
    @media (max-width: 768px) {
        .cisa-header h1 { font-size: 1.5rem; }
        .chat-msg .bubble { padding: .65rem .85rem; font-size: .85rem; }
        .chat-msg .avatar { width: 30px; height: 30px; font-size: .9rem; }
    }

    /* ─────────────────────────────────────────────
       21. SIDEBAR LOGO AREA
       ───────────────────────────────────────────── */
    .sidebar-logo {
        text-align: center;
        padding: .75rem 0 .5rem;
    }

    .sidebar-logo .icon {
        font-size: 2.4rem;
        display: block;
        margin-bottom: .2rem;
    }

    .sidebar-logo .title {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 1.55rem;
        letter-spacing: .06em;
        background: linear-gradient(135deg, #06b6d4, #14b8a6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .sidebar-logo .sub {
        color: var(--text-muted);
        font-size: .7rem;
        font-weight: 400;
        letter-spacing: .03em;
    }

    /* ─────────────────────────────────────────────
       22. SECTION LABELS
       ───────────────────────────────────────────── */
    .section-label {
        font-family: 'Inter', sans-serif;
        font-size: .68rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: .08em;
        color: var(--text-muted);
        margin-bottom: .4rem;
    }

    /* ─────────────────────────────────────────────
       23. WELCOME CARD
       ───────────────────────────────────────────── */
    .welcome-card {
        background: linear-gradient(135deg, rgba(6,182,212,.08), rgba(20,184,166,.04));
        border: 1px solid rgba(6,182,212,.15);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        text-align: center;
    }

    .welcome-card h3 {
        color: var(--accent-cyan);
        margin: 0 0 .5rem;
        font-weight: 700;
    }

    .welcome-card p {
        color: var(--text-secondary);
        font-size: .88rem;
        margin: 0;
        line-height: 1.6;
    }

    .welcome-features {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: .75rem;
        margin-top: 1rem;
        text-align: left;
    }

    .welcome-feature {
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: .75rem;
        transition: var(--transition);
    }

    .welcome-feature:hover {
        border-color: var(--accent-cyan);
        box-shadow: var(--shadow-glow);
    }

    .welcome-feature .feat-icon {
        font-size: 1.2rem;
        margin-bottom: .25rem;
    }

    .welcome-feature .feat-title {
        font-size: .8rem;
        font-weight: 600;
        color: var(--text-primary);
    }

    .welcome-feature .feat-desc {
        font-size: .72rem;
        color: var(--text-muted);
        margin-top: .15rem;
    }

    /* ─────────────────────────────────────────────
       24. ERROR CARD
       ───────────────────────────────────────────── */
    .error-card {
        background: rgba(239, 68, 68, .08);
        border: 1px solid rgba(239, 68, 68, .25);
        border-left: 3px solid var(--accent-red);
        border-radius: 8px;
        padding: .85rem 1rem;
        margin: .5rem 0;
        color: #fca5a5;
        font-size: .85rem;
    }

    /* ─────────────────────────────────────────────
       25. SESSION INFO BADGE
       ───────────────────────────────────────────── */
    .session-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: .65rem;
        color: var(--text-muted);
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: 6px;
        padding: .3rem .6rem;
        display: inline-block;
        word-break: break-all;
    }
    </style>
    """
