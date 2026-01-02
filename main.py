import argparse
import os
from playwright.sync_api import sync_playwright
from booking import perform_booking

# Directory to store browser profile/session
USER_DATA_DIR = os.path.join(os.getcwd(), "user_data")

def main():
    parser = argparse.ArgumentParser(description="Cult.fit Booking Automation")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--login", action="store_true", help="Run in login mode to capture session")
    parser.add_argument("--center", type=str, default="Cult Whitefield", help="Center name to book")
    parser.add_argument("--time", type=str, default="07:00 AM", help="Class time to book (e.g., '07:00 AM')")
    args = parser.parse_args()

    # Ensure user_data directory exists
    if not os.path.exists(USER_DATA_DIR):
        os.makedirs(USER_DATA_DIR)

    with sync_playwright() as p:
        print(f"Launching browser with persistent profile in: {USER_DATA_DIR}")
        
        # launch_persistent_context combines launch and new_context
        # It maintains cookies, local storage, etc. natively.
        context = p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            headless=False if args.login else args.headless, # Always show browser for login
            slow_mo=1000, 
            args=["--start-maximized"] 
        )
        
        page = context.pages[0] if context.pages else context.new_page()

        try:
            if args.login:
                print(">>> LOGIN MODE <<<")
                print("Navigating to https://www.cult.fit/")
                page.goto("https://www.cult.fit/", wait_until="load")
                
                print("Attempting to open Login modal...")
                try:
                    # Generic selector for the user/profile icon. 
                    # Usually an image with 'user' or 'profile' in src or alt, or an SVG.
                    # Cult.fit header usually has a profile icon on the right.
                    profile_icon = page.locator("img[alt='user_image'], img[src*='user-image'], .user-image, img[src*='profile']").first
                    if profile_icon.is_visible():
                        profile_icon.click()
                        print("Clicked Profile Icon. Please enter your phone number and OTP.")
                    else:
                        print("Could not auto-click Profile Icon. Please click it manually.")
                except Exception as e:
                    print(f"Auto-click failed: {e}. Please click login manually.")

                print("\nAction Required: Log in manually in the browser window.")
                print("Once you are logged in, press Ctrl+C here to save and exit.")
                # Wait indefinitely for user to login
                page.wait_for_timeout(300000) # 5 minutes

            else:
                # Normal Booking Mode
                perform_booking(page, center_name=args.center, target_time=args.time)

        except KeyboardInterrupt:
            print("\nOperation stopped by user (Ctrl+C). Saving session...")
        except Exception as e:
            print(f"\n[CRITICAL ERROR] {e}")
            try:
                page.screenshot(path="error_capture.png")
                print("Screenshot saved to error_capture.png")
            except:
                pass
        finally:
            if not args.headless and not args.login:
                print("\nProcess finished. Closing browser in 10 seconds...")
                page.wait_for_timeout(10000)
            context.close()

if __name__ == "__main__":
    main()
