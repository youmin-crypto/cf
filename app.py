import streamlit as st
from playwright.sync_api import sync_playwright
import subprocess

@st.cache_resource
def install_playwright_browser():
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True)
    except Exception:
        pass

install_playwright_browser()

st.title("Cloudflare Cookie Solver (Advanced Stealth)")

target_url = st.text_input("Target URL", "https://satoshifaucet.io")
proxy_input = st.text_input("Proxy (http://user:pass@ip:port)", "")

if st.button("Solve & Get Cookie"):
    with sync_playwright() as p:
        try:
            # Proxy cleaning
            proxy_settings = None
            if proxy_input:
                proxy_settings = {"server": proxy_input.replace("https://", "http://")}

            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox", 
                    "--disable-setuid-sandbox",
                    "--disable-blink-features=AutomationControlled", # Automation စစ်တာကို ပိတ်မယ်
                ],
                proxy=proxy_settings
            )
            
            # Browser Context ကို လူအစစ်နဲ့ ပိုတူအောင် လုပ်မယ်
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                viewport={'width': 1280, 'height': 720}
            )
            
            page = context.new_page()
            
            # Webdriver property ကို Javascript နဲ့ ဖျောက်မယ်
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            with st.spinner("Bypassing Cloudflare... This might take 20-30 seconds."):
                # Page ကို သွားမယ်
                page.goto(target_url, wait_until="domcontentloaded", timeout=60000)
                
                # Cloudflare challenge ဖြေရှင်းဖို့ အချိန်အလုံအလောက် ပေးမယ်
                page.wait_for_timeout(60000) 
                
                # Screenshot ရိုက်ကြည့်မယ် (ဘာဖြစ်နေလဲ သိရအောင်)
                st.image(page.screenshot(), caption="Current Page State")

                cookies = context.cookies()
                if cookies:
                    # cf_clearance cookie ပါမပါ စစ်မယ်
                    cf_cookie = [c for c in cookies if c['name'] == 'cf_clearance']
                    if cf_cookie:
                        st.success("Target Cleared! cf_clearance found.")
                    st.write(cookies)
                else:
                    st.error("Access Denied or Timeout. Cloudflare blocked the request.")
            
            browser.close()
        except Exception as e:
            st.error(f"Error: {e}")
