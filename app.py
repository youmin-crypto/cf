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

st.title("Cloudflare Cookie Solver (Auto-Clicker)")

target_url = st.text_input("Target URL", "https://satoshifaucet.io")
proxy_input = st.text_input("Proxy (http://user:pass@ip:port)", "")

if st.button("Solve & Get Cookie"):
    with sync_playwright() as p:
        try:
            # Proxy cleaning
            final_proxy = proxy_input.replace("https://", "http://") if proxy_input else None

            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-blink-features=AutomationControlled"],
                proxy={"server": final_proxy} if final_proxy else None
            )
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            with st.spinner("Attempting to bypass Cloudflare Checkbox..."):
                # Timeout ကို 90s အထိ တိုးလိုက်တယ် (Proxy အတွက်)
                try:
                    page.goto(target_url, wait_until="domcontentloaded", timeout=90000)
                except Exception as e:
                    st.warning(f"Initial load timeout, but continuing to look for checkbox...")

                # Checkbox ရှိတဲ့ Iframe ကို ရှာပြီး နှိပ်ဖို့ ကြိုးစားမယ်
                page.wait_for_timeout(5000)
                st.info("Searching for Checkbox...")
                
                # Cloudflare Checkbox ကို ရှာဖွေပြီး နှိပ်ခြင်း
                try:
                    # Cloudflare ရဲ့ checkbox က iframe ထဲမှာ ရှိတတ်လို့ အဲဒါကို ရှာနှိပ်တာပါ
                    checkbox = page.frame_locator("iframe[src*='cloudflare']").locator("input[type='checkbox']")
                    if checkbox.is_visible():
                        checkbox.click()
                        st.success("Checkbox clicked!")
                    else:
                        # တခါတလေ တစ်ခြား selector တွေနဲ့ လာတတ်လို့
                        page.click("input[type='checkbox']", timeout=5000)
                except:
                    st.info("Manual click not needed or not found. Waiting for auto-resolve...")

                # Challenge ပြေလည်ဖို့ စောင့်မယ်
                page.wait_for_timeout(15000) 
                
                # နောက်ဆုံး အခြေအနေကို ပုံရိုက်မယ်
                shot = page.screenshot()
                st.image(shot, caption="Final Page State")

                cookies = context.cookies()
                if cookies:
                    # cf_clearance ပါမပါ စစ်မယ်
                    cf_present = any(c['name'] == 'cf_clearance' for c in cookies)
                    if cf_present:
                        st.success("Bypass Successful! cf_clearance found.")
                    st.write(cookies)
                else:
                    st.error("Could not retrieve cookies.")
            
            browser.close()
        except Exception as e:
            st.error(f"Error: {e}")
