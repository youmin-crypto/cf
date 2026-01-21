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

st.title("Cloudflare Cookie Solver (Advanced Bypass)")

target_url = st.text_input("Target URL", "https://satoshifaucet.io")
proxy_input = st.text_input("Proxy (http://user:pass@ip:port)", "")

if st.button("Solve & Get Cookie"):
    with sync_playwright() as p:
        try:
            # Proxy cleaning logic
            clean_proxy = None
            if proxy_input:
                # https ကို http ပြောင်းပြီး space တွေ ဖျက်မယ်
                clean_proxy = proxy_input.strip().replace("https://", "http://")
                if not clean_proxy.startswith("http://"):
                    clean_proxy = "http://" + clean_proxy

            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox", 
                    "--disable-setuid-sandbox",
                    "--disable-blink-features=AutomationControlled"
                ],
                proxy={"server": clean_proxy} if clean_proxy else None
            )
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={'width': 1280, 'height': 800}
            )
            page = context.new_page()

            with st.spinner("Bypassing Cloudflare..."):
                # Navigation timeout ကို ၁ မိနစ်ခွဲအထိ တိုးထားတယ် (Proxy အတွက်)
                try:
                    page.goto(target_url, wait_until="domcontentloaded", timeout=100000)
                except:
                    st.info("Loading taking longer than expected, checking for checkbox...")

                page.wait_for_timeout(7000) # Challenge တက်လာအောင် စောင့်မယ်
                
                # Checkbox နှိပ်ဖို့ ကြိုးစားခြင်း
                st.info("Attempting to solve Turnstile...")
                try:
                    # Cloudflare Iframe ကို ရှာမယ်
                    frames = page.frames
                    for frame in frames:
                        if "cloudflare" in frame.url:
                            # Checkbox ကို တွေ့ရင် နှိပ်မယ်
                            checkbox = frame.locator(".ctp-checkbox-label")
                            if checkbox.is_visible():
                                checkbox.click()
                                st.success("Cloudflare Checkbox Clicked!")
                                page.wait_for_timeout(10000) # Success ဖြစ်ဖို့ စောင့်မယ်
                                break
                except Exception as e:
                    st.warning("Auto-click failed, waiting for potential auto-solve...")

                # နောက်ဆုံး အခြေအနေ ပုံရိုက်မယ်
                page.wait_for_timeout(5000)
                st.image(page.screenshot(), caption="Current State")

                cookies = context.cookies()
                if cookies:
                    st.write("Cookies Retrieved:", cookies)
                    # cf_clearance ပါမပါ စစ်မယ်
                    if any(c['name'] == 'cf_clearance' for c in cookies):
                        st.balloons()
                        st.success("Bypass Complete!")
                else:
                    st.error("Cookie not found. Please check your Proxy or Target URL.")

            browser.close()
        except Exception as e:
            st.error(f"Runtime Error: {e}")
