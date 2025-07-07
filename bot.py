from playwright.sync_api import sync_playwright, TimeoutError
import time

def order_on_amazon(name, street, city, state, zip_code, test_mode=False):
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
            page.click(".a-button-inner a[href*='proceed']")
            time.sleep(3)

            # === Address Entry Page ===
            try:
                page.wait_for_selector('input[name="address-ui-widgets-enterAddressFullName"]', timeout=5000)
                print("📝 Entering shipping address...")

                page.fill('input[name="address-ui-widgets-enterAddressFullName"]', name)
                page.fill('input[name="address-ui-widgets-enterAddressLine1"]', street)
                page.fill('input[name="address-ui-widgets-enterAddressCity"]', city)
                page.select_option('select[name="address-ui-widgets-enterAddressStateOrRegion"]', state)
                page.fill('input[name="address-ui-widgets-enterAddressPostalCode"]', zip_code)
                time.sleep(1)

                page.click('input.a-button-input[name="shipToThisAddress"]')
                page.wait_for_timeout(2000)
            except TimeoutError:
                print("✅ Address already saved or skipped (likely a returning session).")

            if test_mode:
                print("🧪 Test mode: Halting before payment.")
                print(f"Would have ordered for {name}, {street}, {city}, {state}, {zip_code}")
                return

            # === Delivery Selection ===
            try:
                page.wait_for_selector('input.a-button-input[name="continue-top"]', timeout=5000)
                page.click('input.a-button-input[name="continue-top"]')
                time.sleep(2)
            except TimeoutError:
                print("⚠️ Skipping delivery selection — maybe auto-selected.")

            # === Payment Method ===
            try:
                page.wait_for_selector('input.a-button-input[name="ppw-widgetEvent:SetPaymentPlanSelectContinueEvent"]', timeout=5000)
                page.click('input.a-button-input[name="ppw-widgetEvent:SetPaymentPlanSelectContinueEvent"]')
                time.sleep(2)
            except TimeoutError:
                print("⚠️ Skipping payment selection — maybe auto-selected.")

            # === Final Checkout Button ===
            print("🛒 Placing order...")
            page.wait_for_selector('input.place-your-order-button, #bottomSubmitOrderButtonId', timeout=7000)
            try:
                page.click('input.place-your-order-button')
            except:
                page.click('#bottomSubmitOrderButtonId')

            print(f"🎉 Order placed for {name}")

        except TimeoutError as te:
            print(f"[TIMEOUT] Failed to complete order flow: {te}")
            page.screenshot(path="error_screenshot.png")
        except Exception as e:
            print(f"[ERROR] Something went wrong: {e}")
            page.screenshot(path="error_screenshot.png")
        finally:
            browser.close()
