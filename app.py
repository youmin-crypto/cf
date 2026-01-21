import streamlit as st
from playwright.sync_api import sync_playwright
import subprocess
import os

@st.cache_resource
def install_playwright_browser():
    try:
        # Browser သွင်းတာကို ပိုသေချာအောင် လုပ်မယ်
        subprocess.run(["playwright", "install", "chromium"], check=True)
    except Exception as e:
        st.error(f"Installation Error: {e}")

install_playwright_browser()

st.title("Cloudflare Cookie Solver (Final Debug)")

target_url = st.text_input("Target URL", "https://satoshifaucet.io")
proxy_input = st.text_input("Proxy (http://user:pass@ip:port)", "")

if st.button("Solve & Get Cookie"):
    if not target_url:
        st.warning("Please enter a Target URL")
    else:
        with sync_playwright() as p:
            try:
                # Proxy protocol ကို အော်တိုပြင်ပေးမယ်
                final_proxy = proxy_input.replace("https://", "http://") if proxy_input else None
                
                # Launch options ကို ပိုပြီး robust ဖြစ်အောင် ပြင်မယ်
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox", 
                        "--disable-setuid-sandbox",
                        "--disable-dev-shm-usage", # RAM error သက်သာအောင်
                        "--disable-blink-features=AutomationControlled"
                    ],
                    proxy={"server": final_proxy} if final_proxy else None
                )
                
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    viewport={'width': 1280, 'height': 800}
                )
                
                page = context.new_page()
                # Automation စစ်တာကို ကျော်ဖို့ script ထည့်မယ်
                page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

                with st.spinner("Loading page and solving Cloudflare..."):
                    # wait_until ကို 'networkidle' ပြန်ပြောင်းလိုက်ပါတယ်
                    response = page.goto(target_url, wait_until="networkidle", timeout=90000)
                    
                    # Page load ပြီးသွားရင် ခဏစောင့်မယ်
                    st.info(f"Page loaded. Status: {response.status if response else 'No Response'}")
                    page.wait_for_timeout(10000) 
                    
                    # Screenshot ရိုက်တာကို ပိုသေချာအောင် လုပ်မယ်
                    try:
                        screenshot_bytes = page.screenshot(full_page=False)
                        st.image(screenshot_bytes, caption="Browser Screenshot")
                    except:
                        st.warning("Could not capture screenshot.")

                    cookies = context.cookies()
                    if cookies:
                        st.success(f"Found {len(cookies)} cookies!")
                        st.write(cookies)
                    else:
                        st.error("No cookies found. Site might be blocking this IP.")
                
                browser.close()
            except Exception as e:
                st.error(f"Runtime Error: {e}")
