import streamlit as st
from playwright.sync_api import sync_playwright
import subprocess
import os

# Playwright Browser ကို ပိုစိတ်ချရတဲ့နည်းနဲ့ install လုပ်မယ်
@st.cache_resource
def install_playwright():
    # Browser တွေ ရှိမရှိ အရင်စစ်မယ်
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True)
        # Linux dependencies တွေ သွင်းဖို့ (streamlit cloud မှာ ဒါက အရေးကြီးတယ်)
        subprocess.run(["playwright", "install-deps"], check=True)
    except Exception as e:
        st.error(f"Installation Error: {e}")

install_playwright()

st.title("Cloudflare Cookie Solver (Cloud Version)")

target_url = st.text_input("Target URL", "https://satoshifaucet.io")
# Proxy format ကို User အတွက် ပိုရှင်းအောင် ပြင်ပေးမယ်
proxy_input = st.text_input("Proxy (http://username:password@ip:port)", "")

if st.button("Solve & Get Cookie"):
    if not target_url:
        st.warning("Please enter a Target URL")
    else:
        with sync_playwright() as p:
            try:
                # Browser launch logic
                browser_args = {
                    "headless": True,
                    "args": ["--no-sandbox", "--disable-setuid-sandbox"] # Linux မှာ လိုအပ်တဲ့ flags တွေ
                }
                
                if proxy_input:
                    browser_args["proxy"] = {"server": proxy_input}
                
                browser = p.chromium.launch(**browser_args)
                
                # Device တွေနဲ့ ပိုတူအောင် emulating လုပ်မယ်
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                
                page = context.new_page()
                
                with st.spinner("Accessing site and solving Cloudflare..."):
                    # Timeout ကို နဲနဲ တိုးပေးမယ်
                    page.goto(target_url, wait_until="networkidle", timeout=60000)
                    
                    # CF challenge ဖြေရှင်းချိန် စောင့်မယ်
                    st.info("Waiting for Cloudflare challenge...")
                    page.wait_for_timeout(10000) 
                    
                    cookies = context.cookies()
                    if cookies:
                        st.success("Successfully got cookies!")
                        st.write(cookies)
                    else:
                        st.warning("No cookies found. Site might have blocked the server IP.")
                
                browser.close()
            except Exception as e:
                st.error(f"Playwright Runtime Error: {e}")
