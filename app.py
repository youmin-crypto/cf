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

st.title("Cloudflare Cookie Solver (Pro Version)")

target_url = st.text_input("Target URL", "https://satoshifaucet.io")
proxy_input = st.text_input("Proxy (http://user:pass@ip:port)", "")

if st.button("Solve & Get Cookie"):
    with sync_playwright() as p:
        try:
            # Stealth ဖြစ်စေမယ့် args များ
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox", 
                    "--disable-setuid-sandbox",
                    "--disable-blink-features=AutomationControlled", # Automation ဖြစ်နေတာကို ဖျောက်ရန်
                ],
                proxy={"server": proxy_input} if proxy_input else None
            )
            
            # Browser Fingerprint အစစ်နဲ့ တူအောင်လုပ်ခြင်း
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = context.new_page()
            
            # Webdriver property ကို ဖျောက်ခြင်း (Stealth mode)
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            with st.spinner("Solving... Please wait up to 30 seconds"):
                # လမ်းကြောင်းကို နည်းနည်း ပိုစောင့်ခိုင်းမယ်
                response = page.goto(target_url, wait_until="commit", timeout=90000)
                
                # Cloudflare challenge ကို ကျော်ဖို့ ၁၅ စက္ကန့် စောင့်မယ်
                page.wait_for_timeout(15000) 
                
                # အကယ်၍ Captcha box ပေါ်နေရင် screenshot ရိုက်ကြည့်လို့ရတယ် (Debug အတွက်)
                # st.image(page.screenshot()) 

                cookies = context.cookies()
                if cookies:
                    # Cloudflare cookie ပါမပါ စစ်မယ် (cf_clearance)
                    has_cf = any(c['name'] == 'cf_clearance' for c in cookies)
                    if has_cf:
                        st.success("Cloudflare Bypass Success!")
                    st.write(cookies)
                else:
                    st.warning("No cookies found. Try using a Residential Proxy.")
            
            browser.close()
        except Exception as e:
            st.error(f"Error: {e}")
