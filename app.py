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

st.title("Cloudflare Cookie Solver (Final Stealth)")

target_url = st.text_input("Target URL", "https://satoshifaucet.io")
proxy_input = st.text_input("Proxy (http://user:pass@ip:port)", "")

if st.button("Solve & Get Cookie"):
    with sync_playwright() as p:
        try:
            # Proxy cleaning
            clean_proxy = None
            if proxy_input:
                clean_proxy = proxy_input.strip().replace("https://", "http://")
                if not clean_proxy.startswith("http://"):
                    clean_proxy = "http://" + clean_proxy

            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--use-fake-ui-for-media-stream",
                    "--window-size=1920,1080"
                ],
                proxy={"server": clean_proxy} if clean_proxy else None
            )
            
            # Browser Context ကို အမြင့်ဆုံး Stealth လုပ်မယ်
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080},
                device_scale_factor=1,
            )
            
            page = context.new_page()

            # Automation detection တွေကို ဖျောက်တဲ့ script အပြည့်အစုံ
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.chrome = { runtime: {} };
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            """)

            with st.spinner("Executing advanced bypass..."):
                try:
                    page.goto(target_url, wait_until="networkidle", timeout=120000)
                except:
                    st.info("Loading slow, attempting to find Turnstile anyway...")

                page.wait_for_timeout(10000)
                
                # Checkbox ကို ရှာဖွေပြီး လူလိုမျိုး ဖြည်းဖြည်းချင်း နှိပ်မယ်
                try:
                    for frame in page.frames:
                        if "cloudflare" in frame.url:
                            # နေရာအတိအကျကို ရှာပြီး mouse နဲ့ နှိပ်မယ်
                            checkbox = frame.locator("input[type='checkbox'], .ctp-checkbox-label").first
                            if checkbox.is_visible():
                                checkbox.scroll_into_view_if_needed()
                                # လူလိုမျိုး mouse နဲ့ သွားနှိပ်တာ
                                checkbox.click(delay=150) 
                                st.success("Target hit! Checkbox clicked with human-like delay.")
                                page.wait_for_timeout(15000)
                                break
                except:
                    st.info("Searching alternative solve methods...")

                # နောက်ဆုံး screenshot နဲ့ cookie ယူမယ်
                st.image(page.screenshot(), caption="Final Browser State")
                cookies = context.cookies()
                
                if cookies:
                    st.write("Cookies Found:", cookies)
                    if any(c['name'] == 'cf_clearance' for c in cookies):
                        st.balloons()
                        st.success("Bypass Successful!")
                else:
                    st.error("Cookie extraction failed.")

            browser.close()
        except Exception as e:
            st.error(f"Runtime Error: {e}")
