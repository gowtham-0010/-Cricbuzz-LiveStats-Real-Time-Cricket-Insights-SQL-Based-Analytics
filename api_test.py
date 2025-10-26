import streamlit as st
import requests
import json

def show_api_test():
    st.title("🧪 API Testing & Debugging")
    st.markdown("### Diagnose API connection issues")

    if st.button("🚀 Quick Test", type="primary"):
        quick_test()

    st.markdown("---")

    endpoint = st.selectbox("Test Endpoint:", [
        "matches/v1/live",
        "matches/v1/recent",
        "matches/v1/upcoming"
    ])

    if st.button("🧪 Test Selected"):
        test_endpoint(endpoint)

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🌐 Internet Test"):
            test_internet()

    with col2:
        if st.button("📦 Package Check"):
            check_packages()

def quick_test():
    st.markdown("### 🚀 Quick API Test")

    headers = {
        "X-RapidAPI-Key": "1d62c1ee99mshd5e1b5c8f929104p1d316ejsn84c4fbff4cc5",
        "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
    }

    try:
        response = requests.get(
            "https://cricbuzz-cricket.p.rapidapi.com/matches/v1/live",
            headers=headers,
            timeout=5
        )

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Status", response.status_code)
        with col2:
            st.metric("Size", f"{len(response.content)} bytes")

        if response.status_code == 200:
            st.success("🎉 API working!")
            with st.expander("Sample Data"):
                try:
                    data = response.json()
                    st.json(data)
                except:
                    st.text(response.text[:200])

        elif response.status_code == 429:
            st.error("🚫 Rate limit exceeded")
            st.info("Wait a few minutes and try again")

        elif response.status_code == 403:
            st.error("🔑 Authentication failed")
            st.info("Check your API key")

        else:
            st.error(f"❌ Failed: {response.status_code}")

    except requests.exceptions.Timeout:
        st.error("⏱️ Request timeout")
    except Exception as e:
        st.error(f"💥 Error: {str(e)}")

def test_endpoint(endpoint):
    st.markdown(f"### Testing: {endpoint}")

    headers = {
        "X-RapidAPI-Key": "f0beadeebbmsh58a7273cdf0621bp1187dejsnc7cb81759c22",
        "X-RapidAPI-Host": "cricbuzz-cricket.p.rapidapi.com"
    }

    try:
        url = f"https://cricbuzz-cricket.p.rapidapi.com/{endpoint}"
        response = requests.get(url, headers=headers, timeout=5)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Status", response.status_code)
        with col2:
            st.metric("Size", f"{len(response.content)} B")

        if response.status_code == 200:
            st.success("✅ Working!")
        else:
            st.error(f"❌ Failed: {response.status_code}")

    except Exception as e:
        st.error(f"Error: {str(e)}")

def test_internet():
    st.markdown("### 🌐 Internet Test")

    sites = [("Google", "https://www.google.com")]

    for name, url in sites:
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                st.success(f"✅ {name} - OK")
            else:
                st.warning(f"⚠️ {name} - {response.status_code}")
        except:
            st.error(f"❌ {name} - Failed")

def check_packages():
    st.markdown("### 📦 Package Check")

    packages = ["streamlit", "requests", "pandas"]

    for pkg in packages:
        try:
            __import__(pkg)
            st.success(f"✅ {pkg} - OK")
        except:
            st.error(f"❌ {pkg} - Missing")

if __name__ == "__main__":
    show_api_test()
