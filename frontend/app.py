import streamlit as st

st.set_page_config(
    page_title="AI DevSecOps Platform",
    page_icon="🛡️",
    layout="wide",
)

st.title("AI DevSecOps Platform")
st.markdown("""
Welcome to the AI DevSecOps Platform. Select an assistant from the sidebar to get started:

- **[CISA] Cloud Identity Security Assistant**: Analyze IAM resources, identify security risks, and apply least privilege.
- **[CSGA] Cloud Security & Governance Assistant**: Monitor security services, detect threats, and assess cloud governance.
""")

st.sidebar.success("Select a page above.")
