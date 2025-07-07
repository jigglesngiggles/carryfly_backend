from playwright.sync_api import sync_playwright, TimeoutError
import time

def order_on_amazon(name, street, city, state, zip_code, test_mode=False):
    PRODUCT_URL = "https://www.amazon.com/AMUFER-Upgraded-Exclusive-Improvement-Mosquito/dp/B0CT4KKSB5"
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(storage_state="session.json")
            page = context.new_page()

            page.goto(PRODUCT_URL, timeout=15000)
            page.wait_for_selector("#add-to-cart-button", timeout=5000)
            page.click("#add-to-cart-button")
            time.sleep(2)

            # Go to cart
            page.goto("https://www.amazon.com/gp/cart/view.html")
            page.wait_for_selector(".a-button-inner a[href*='proceed']")
            page.click(".a-button-inner a[href*='proceed']")

            # Wait for address selection / add address form
            time.sleep(2)
            if page.query_selector("a[data-testid='ship-to-another-address-link']"):
                print("🔄 Selecting different address...")
                page.click("a[data-testid='ship-to-another-address-link']")
                page.wait_for_selector("form[name='addressForm']", timeout=10000)

                page.fill("input[name='address-ui-widgets-enterAddressFullName']", name)
                page.fill("input[name='address-ui-widgets-enterAddressLine1']", street)
                page.fill("input[name='address-ui-widgets-enterAddressCity']", city)
                page.fill("input[name='address-ui-widgets-enterAddressStateOrRegion']", state)
                page.fill("input[name='address-ui-widgets-enterAddressPostalCode']", zip_code)
                page.click("input[type='submit']")

            if test_mode:
                print("🧪 Test mode active. Stopping before placing final order.")
                print(f"Would have placed order for {name}, {street}, {city}, {state}, {zip_code}")
            else:
                page.wait_for_selector("input[name='placeYourOrder1']", timeout=10000)
                page.click("input[name='placeYourOrder1']")
                print(f"💸 Order submitted for {name}")
        except TimeoutError as te:
            print(f"[TIMEOUT] Failed to complete order flow: {te}")
            page.screenshot(path="error_screenshot.png")
        except Exception as e:
            print(f"[ERROR] Something went wrong: {e}")
            page.screenshot(path="error_screenshot.png")
        finally:
            browser.close()
