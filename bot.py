from playwright.sync_api import sync_playwright, TimeoutError
import time

def order_on_amazon(name, street, city, zip_code, test_mode=False):
    PRODUCT_URL = "https://www.amazon.com/AMUFER-Upgraded-Exclusive-Improvement-Mosquito/dp/B0CT4KKSB5?source=ps-sl-shoppingads-lpcontext&ref_=fplfs&psc=1&smid=A3ASA9QYNZUULE&gQT=1"
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state="session.json")
            page = context.new_page()

            page.goto(PRODUCT_URL, timeout=15000)
            page.wait_for_selector("#add-to-cart-button", timeout=5000)
            page.click("#add-to-cart-button")
            time.sleep(2)

            page.goto("https://www.amazon.com/gp/cart/view.html")
            page.wait_for_selector(".a-button-inner a[href*='proceed']")

            if test_mode:
                print("🧪 Test mode active. Stopping before checkout.")
                print(f"Would have proceeded with order for: {name}, {street}, {city}, {zip_code}")
            else:
                page.click(".a-button-inner a[href*='proceed']")
                print(f"✅ Live order flow completed for {name}")
        except TimeoutError as te:
            print(f"[TIMEOUT] Failed to complete order flow: {te}")
            page.screenshot(path="error_screenshot.png")
        except Exception as e:
            print(f"[ERROR] Something went wrong: {e}")
            page.screenshot(path="error_screenshot.png")
        finally:
            browser.close()
