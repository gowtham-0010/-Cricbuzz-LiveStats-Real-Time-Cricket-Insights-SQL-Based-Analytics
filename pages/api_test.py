import streamlit as st

def show_api_test():
    st.markdown('<h1 class="page-title">🧪 API Testing & Debugging</h1>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Test API connectivity and diagnose connection issues</p>', unsafe_allow_html=True)

    if st.button("🚀 Quick API Test", type="primary"):
        st.success("✅ API connection test would run here")

    st.markdown("### 🎯 Endpoint Testing")
    endpoint = st.selectbox("Select Endpoint:", ["matches/v1/live", "matches/v1/recent"])

    if st.button("🧪 Test Selected Endpoint"):
        st.info("Individual endpoint testing would be implemented here")

if __name__ == "__main__":
    show_api_test()
