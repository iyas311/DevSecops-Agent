"""
CISA Frontend — Sidebar Component
AWS connection status, profile selector, quick actions, and session management.
"""

import os
import configparser
from pathlib import Path

import streamlit as st
import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BACKEND_URL = "http://localhost:8000"
HEALTH_ENDPOINT = f"{BACKEND_URL}/health"
AWS_CREDENTIALS_PATH = Path.home() / ".aws" / "credentials"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _check_backend_health() -> bool:
    """Return True if the backend /health endpoint responds successfully."""
    try:
        resp = requests.get(HEALTH_ENDPOINT, timeout=3)
        return resp.status_code == 200
    except Exception:
        return False


def _load_aws_profiles() -> list[str]:
    """Parse ~/.aws/credentials and return available profile names."""
    profiles: list[str] = []
    if AWS_CREDENTIALS_PATH.exists():
        config = configparser.ConfigParser()
        try:
            config.read(str(AWS_CREDENTIALS_PATH))
            profiles = config.sections()
        except Exception:
            pass
    # Also try AWS_CONFIG_FILE / ~/.aws/config
    aws_config_path = Path.home() / ".aws" / "config"
    if aws_config_path.exists():
        config = configparser.ConfigParser()
        try:
            config.read(str(aws_config_path))
            for section in config.sections():
                name = section.replace("profile ", "")
                if name not in profiles:
                    profiles.append(name)
        except Exception:
            pass
    return profiles if profiles else ["default"]


# ---------------------------------------------------------------------------
# Main render function
# ---------------------------------------------------------------------------
def render_sidebar() -> None:
    """Render the CISA sidebar with all controls."""

    with st.sidebar:
        # ── Logo / Title ─────────────────────────────────────────────────
        st.markdown(
            """
            <div class="sidebar-logo">
                <span class="icon">🛡️</span>
                <span class="title">CISA</span>
                <div class="sub">Cloud Identity Security Assistant</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # ── AWS Connection Status ────────────────────────────────────────
        st.markdown(
            '<div class="section-label">Backend Status</div>',
            unsafe_allow_html=True,
        )

        is_connected = _check_backend_health()
        if is_connected:
            st.markdown(
                '<span class="status-dot connected"></span> '
                '<span style="color:#22c55e;font-size:.85rem;font-weight:500;">'
                "Connected</span>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<span class="status-dot disconnected"></span> '
                '<span style="color:#ef4444;font-size:.85rem;font-weight:500;">'
                "Disconnected</span>",
                unsafe_allow_html=True,
            )

        st.markdown("---")

        # ── AWS Profile Selector ─────────────────────────────────────────
        st.markdown(
            '<div class="section-label">AWS Profile</div>',
            unsafe_allow_html=True,
        )

        profiles = _load_aws_profiles()

        # Manual input toggle
        use_manual = st.checkbox("Enter profile manually", value=False, key="aws_manual_toggle")

        if use_manual:
            manual_profile = st.text_input(
                "Profile name",
                value=st.session_state.get("aws_profile", "default"),
                key="aws_profile_manual_input",
                label_visibility="collapsed",
                placeholder="e.g. prod-readonly",
            )
            st.session_state.aws_profile = manual_profile
        else:
            current_idx = 0
            current_profile = st.session_state.get("aws_profile")
            if current_profile and current_profile in profiles:
                current_idx = profiles.index(current_profile)

            selected = st.selectbox(
                "Select AWS profile",
                options=profiles,
                index=current_idx,
                key="aws_profile_select",
                label_visibility="collapsed",
            )
            st.session_state.aws_profile = selected

        st.markdown("---")

        # ── Quick Actions ────────────────────────────────────────────────
        st.markdown(
            '<div class="section-label">Quick Actions</div>',
            unsafe_allow_html=True,
        )

        quick_actions = [
            ("🔍 Run IAM Audit", "Run a comprehensive IAM security audit on my AWS account"),
            ("👥 List IAM Users", "List all IAM users in my AWS account with their details"),
            ("🔑 Check MFA Status", "Check MFA status for all IAM users"),
            ("📋 Show Credential Report", "Generate and show the IAM credential report"),
        ]

        for label, message in quick_actions:
            if st.button(label, key=f"qa_{label}", use_container_width=True):
                st.session_state.quick_action_message = message

        st.markdown("---")

        # ── Session Management ───────────────────────────────────────────
        st.markdown(
            '<div class="section-label">Session</div>',
            unsafe_allow_html=True,
        )

        if st.button("🗑️ Clear Chat", key="clear_chat_btn", use_container_width=True):
            st.session_state.messages = []
            st.session_state.pop("quick_action_message", None)
            st.rerun()

        session_id = st.session_state.get("session_id", "N/A")
        short_id = session_id[:8] if len(session_id) > 8 else session_id
        st.markdown(
            f'<div style="margin-top:.4rem;">'
            f'<span class="section-label">Session ID</span><br>'
            f'<span class="session-badge">{short_id}…</span>'
            f"</div>",
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # ── About ────────────────────────────────────────────────────────
        with st.expander("ℹ️ About CISA"):
            st.markdown(
                """
                **CISA** — Cloud Identity Security Assistant

                An AI-powered cybersecurity tool that analyzes
                AWS IAM configurations, detects security risks,
                and provides actionable recommendations.

                **Capabilities:**
                - IAM user & role analysis
                - Policy evaluation
                - MFA compliance checks
                - Credential rotation auditing
                - Security best-practice scoring

                Built with ❤️ for DevSecOps teams.
                """,
            )
