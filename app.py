import streamlit as st
from playwright.sync_api import sync_playwright
import subprocess

# ပိုရိုးရှင်းပြီး error ကင်းတဲ့ နည်းလမ်းနဲ့ ပြင်မယ်
@st.cache_resource
def install_playwright_browser():
    try:
        # install-deps ကို ဖြုတ်လိုက်ပါပြီ (packages.txt က အလုပ်လုပ်ပေးမှာမို့လို့ပါ)
        subprocess.run(["playwright", "install", "chromium"], check=True)
    except Exception as e:
        st.error(f"Browser Installation Error: {e}")

install_playwright_browser()

st.title("Cloudflare Cookie Solver (Cloud Version)")

target_url = st.text_input("Target URL", "https://satoshifaucet.io")
proxy_input = st.text_input("Proxy (http://username:password@ip:port)", "")

if st.button("Solve & Get Cookie"):
    if not target_url:
        st.warning("Please enter a Target URL")
    else:
        with sync_playwright() as p:
            try:
                # Linux မှာ Browser ပွင့်ဖို့ sandbox flag တွေက အရေးကြီးပါတယ်
                browser = p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-setuid-sandbox"],
                    proxy={"server": proxy_input} if proxy_input else None
                )
                
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
                )
                
                page = context.new_page()
                
                with st.spinner("Solving Cloudflare..."):
                    # Timeout ကို 60s ထားပါ (Cloud server တွေက နှေးတတ်လို့ပါ)
                    page.goto(target_url, wait_until="networkidle", timeout=60000)
                    page.wait_for_timeout(10000) 
                    
                    cookies = context.cookies()
                    if cookies:
                        st.success("Successfully got cookies!")
                        st.write(cookies)
                    else:
                        st.warning("No cookies found.")
                
                browser.close()
            except Exception as e:
                st.error(f"Runtime Error: {e}")
