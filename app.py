import streamlit as st
from playwright.sync_api import sync_playwright
import os
import subprocess

# Browser install လုပ်ရန် (App စဖွင့်ချင်း တစ်ခါပဲ လုပ်ဖို့လိုတယ်)
@st.cache_resource
def install_browsers():
    subprocess.run(["playwright", "install", "chromium"])
    subprocess.run(["playwright", "install-deps"])

install_browsers()


# Playwright Browser တွေကို install လုပ်ဖို့ command
#os.system("playwright install chromium")

st.title("Cloudflare Cookie Solver (Cloud Version)")

target_url = st.text_input("Target URL", "https://satoshifaucet.io")
proxy_server = st.text_input("Proxy (IP:Port)", "")

if st.button("Solve & Get Cookie"):
    with sync_playwright() as p:
        # Streamlit Cloud ပေါ်မှာမို့လို့ headless=True ပဲ သုံးရပါမယ်
        browser = p.chromium.launch(headless=True, proxy={"server": proxy_server} if proxy_server else None)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        
        with st.spinner("Solving Cloudflare..."):
            try:
                page.goto(target_url)
                page.wait_for_timeout(8000) # Challenge ကျော်ဖို့ စောင့်ချိန်
                cookies = context.cookies()
                st.write("Cookies Found:", cookies)
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                browser.close()
