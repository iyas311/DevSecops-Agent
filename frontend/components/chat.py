"""
CISA Frontend — Chat Component
Renders the conversation area: message bubbles, typing indicator,
backend API integration, and tool-usage tags.
"""

import streamlit as st
import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BACKEND_URL = "http://localhost:8000"
CHAT_ENDPOINT = f"{BACKEND_URL}/api/v1/chat"

WELCOME_HTML = """
<div class="welcome-card">
    <h3>👋 Welcome to CISA</h3>
    <p>
        I'm your Cloud Identity Security Assistant.<br>
        Ask me anything about your AWS IAM configuration, security posture,
        or identity management best practices.
    </p>
    <div class="welcome-features">
        <div class="welcome-feature">
            <div class="feat-icon">🔍</div>
            <div class="feat-title">IAM Auditing</div>
            <div class="feat-desc">Comprehensive analysis of users, roles & policies</div>
        </div>
        <div class="welcome-feature">
            <div class="feat-icon">🔑</div>
            <div class="feat-title">MFA Compliance</div>
            <div class="feat-desc">Verify multi-factor authentication coverage</div>
        </div>
        <div class="welcome-feature">
            <div class="feat-icon">📋</div>
            <div class="feat-title">Credential Reports</div>
            <div class="feat-desc">Access key age, rotation & usage analysis</div>
        </div>
        <div class="welcome-feature">
            <div class="feat-icon">⚡</div>
            <div class="feat-title">Best Practices</div>
            <div class="feat-desc">Actionable recommendations aligned to AWS standards</div>
        </div>
    </div>
</div>
"""

TYPING_HTML = """
<div class="chat-msg assistant">
    <div class="avatar">🤖</div>
    <div class="typing-indicator">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
    </div>
</div>
"""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _render_message(role: str, content: str, tools: list[str] | None = None) -> None:
    """Render a single chat message bubble with optional tools-used tag."""
    avatar = "👤" if role == "user" else "🤖"
    css_class = "user" if role == "user" else "assistant"

    tools_html = ""
    if tools:
        tool_list = ", ".join(tools)
        tools_html = (
            f'<div class="tools-tag">🔧 Tools used: {tool_list}</div>'
        )

    # Escape backticks in content for safe HTML embedding isn't needed —
    # Streamlit's markdown renderer handles the content.  We use st.markdown
    # for the wrapper and let Streamlit handle the inner markdown naturally.

    st.markdown(
        f"""
        <div class="chat-msg {css_class}">
            <div class="avatar">{avatar}</div>
            <div class="bubble">
        """,
        unsafe_allow_html=True,
    )

    # Render actual content via Streamlit markdown (supports code blocks, tables, etc.)
    st.markdown(content, unsafe_allow_html=True)

    if tools_html:
        st.markdown(tools_html, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)


def _send_message_to_backend(
    message: str, session_id: str, aws_profile: str | None
) -> dict:
    """POST the user message to the backend and return the JSON response."""
    payload = {
        "message": message,
        "session_id": session_id,
        "context": {"aws_profile": aws_profile or "default"},
    }
    try:
        resp = requests.post(CHAT_ENDPOINT, json=payload, timeout=120)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        return {
            "error": True,
            "response": (
                "⚠️ **Cannot reach the backend server.**\n\n"
                "Please make sure the CISA backend is running at "
                f"`{BACKEND_URL}` and try again."
            ),
        }
    except requests.exceptions.Timeout:
        return {
            "error": True,
            "response": (
                "⏱️ **Request timed out.**\n\n"
                "The analysis is taking longer than expected. "
                "Please try a simpler query or try again shortly."
            ),
        }
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "?"
        return {
            "error": True,
            "response": (
                f"❌ **Backend error (HTTP {status}).**\n\n"
                "Something went wrong on the server side. "
                "Check the backend logs for details."
            ),
        }
    except Exception as exc:
        return {
            "error": True,
            "response": (
                f"❌ **Unexpected error:** `{exc}`\n\n"
                "Please try again or contact your administrator."
            ),
        }


# ---------------------------------------------------------------------------
# Main render function
# ---------------------------------------------------------------------------
def render_chat() -> None:
    """Render the full chat interface."""

    # ── Header ────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="cisa-header">
            <h1>🛡️ Cloud Identity Security Assistant</h1>
            <div class="tagline">AI-powered AWS IAM analysis &amp; security recommendations</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Chat container ────────────────────────────────────────────────────
    chat_container = st.container()

    with chat_container:
        messages = st.session_state.get("messages", [])

        # Show welcome card if no messages yet
        if not messages:
            st.markdown(WELCOME_HTML, unsafe_allow_html=True)

        # Render existing messages
        for msg in messages:
            _render_message(
                role=msg["role"],
                content=msg["content"],
                tools=msg.get("tools"),
            )

    # ── Process quick-action if triggered from sidebar ────────────────────
    quick_msg = st.session_state.pop("quick_action_message", None)
    if quick_msg:
        _handle_user_input(quick_msg)
        st.rerun()

    # ── Chat input ────────────────────────────────────────────────────────
    user_input = st.chat_input(
        placeholder="Ask about IAM users, roles, policies, MFA status…",
    )

    if user_input:
        _handle_user_input(user_input)
        st.rerun()


def _handle_user_input(message: str) -> None:
    """Append the user message, call the backend, and store the response."""
    # Add user message
    st.session_state.messages.append({"role": "user", "content": message})

    # Call backend
    session_id = st.session_state.get("session_id", "")
    aws_profile = st.session_state.get("aws_profile")

    with st.spinner("🤖 Analyzing…"):
        result = _send_message_to_backend(message, session_id, aws_profile)

    # Parse response
    if isinstance(result, dict):
        is_error = result.get("error", False)
        response_text = result.get("response", "No response received.")
        tools_used = result.get("tools_used") or result.get("tools") or None

        # Normalize tools to a list of strings
        if tools_used and not isinstance(tools_used, list):
            tools_used = [str(tools_used)]
    else:
        response_text = str(result)
        tools_used = None
        is_error = False

    # Store assistant message
    assistant_msg: dict = {"role": "assistant", "content": response_text}
    if tools_used:
        assistant_msg["tools"] = tools_used
    st.session_state.messages.append(assistant_msg)
