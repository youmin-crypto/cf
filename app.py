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

st.title("Cloudflare Cookie Solver (Debug Mode)")

target_url = st.text_input("Target URL", "https://satoshifaucet.io")
# Proxy ထည့်တဲ့နေရာမှာ http:// သုံးဖို့ သတိပေးထားမယ်
proxy_input = st.text_input("Proxy (http://username:password@ip:port)", "")

if st.button("Solve & Get Cookie"):
    with sync_playwright() as p:
        try:
            # Proxy string ထဲက https ကို http ပြောင်းပေးမယ့် logic လေး ထည့်ထားပေးတယ်
            final_proxy = proxy_input.replace("https://", "http://") if proxy_input else None
            
            browser = p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-blink-features=AutomationControlled"],
                proxy={"server": final_proxy} if final_proxy else None
            )
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            with st.spinner("Checking Cloudflare..."):
                page.goto(target_url, wait_until="commit")
                
                # ၁၅ စက္ကန့် စောင့်နေတုန်းမှာ ဘာဖြစ်နေလဲ ကြည့်ဖို့
                st.info("Taking a look at the page...")
                page.wait_for_timeout(15000) 
                
                # Screenshot ရိုက်ပြီး Streamlit မှာ ပြမယ်
                shot = page.screenshot()
                st.image(shot, caption="Current Browser View")

                cookies = context.cookies()
                if cookies:
                    st.write("Cookies Found:", cookies)
                else:
                    st.warning("No cookies found yet.")
            
            browser.close()
        except Exception as e:
            st.error(f"Error: {e}")
