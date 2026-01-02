from playwright.sync_api import Page
import datetime
import time
import re

def perform_booking(page: Page, center_name: str, target_time: str = "07:00 AM"):
    print(f"\n[BOOKING] Starting process for center: {center_name}")
    
    # 1. Navigate to Class Booking
    target_url = "https://www.cult.fit/cult/classbooking?pageFrom=cultCLP&pageType=classbooking"
    
    if page.url != target_url:
        print(f"Navigating to {target_url}...")
        page.goto(target_url, wait_until="load")
        time.sleep(3) # Wait for page structure
    
    # 2. Check Login / Session
    print("Checking session status...")
    # Trigger for center search acts as a good proxy for 'page loaded' and 'logged in' (mostly)
    # The trigger is usually the city name or 'Location' text.
    trigger = page.locator("div[class*='location-text'], .city-name, div:has-text('Bangalore')").first
    
    if not trigger.is_visible(timeout=5000):
        # Fallback: maybe the search bar is already open?
        search_input = page.get_by_placeholder("Search for center")
        if not search_input.is_visible():
            print("[WARNING] neither location trigger nor search bar found. Potential Login Issue?")
            # We continue anyway, hoping for the best or that selectors are just latent
    else:
        print("Page loaded. Location trigger found.")

    # 3. Select Center (Handle Popup)
    print(f"Selecting center: {center_name}...")
    try:

        # Check if the modal is ALREADY open (common on fresh load)
        modal_visible = False
        search_input = page.locator("input[placeholder='Search for names']")
        
        # Also check for the generic "Select A Center" header which implies modal is open
        if page.get_by_text("Select A Center").is_visible():
            print("Detected 'Select A Center' modal is open.")
            modal_visible = True
        
        if not modal_visible:
            # Check if likely already selected in the trigger
            # We use a specific locator for the header location name to avoid false positives from other text
            # Usually .style-prefix-.... name, but let's try the trigger area.
            
            # If trigger is visible and contains name
            if trigger.is_visible() and trigger.filter(has_text=center_name).count() > 0:
                  print(f"Center '{center_name}' seems to be already selected (trigger validation).")
                  # Ensure modal is definitely NOT blocking us
                  if not page.get_by_text("Select A Center").is_visible():
                      return # Success
            
            # If we are here, we need to open the modal
            print("Clicking location/center trigger to open popup...")
            if trigger.is_visible():
                trigger.click()
                time.sleep(1)
            else:
                 print("[WARNING] Trigger not visible. Assuming modal might open or we are stuck.")
        
        # Now operate on the modal
        if search_input.is_visible(timeout=5000):
            print("Search bar visible. Entering center name...")
            search_input.click()
            search_input.fill("") 
            search_input.type(center_name, delay=100) 
            
            time.sleep(3) # Wait for results
            
            print("Selecting from results...")
            
            # User instruction: "u need to select first option , scroll and then SELECT option shows"
            # Reverting to get_by_text as it was proven to work in Step 212
            
            # Use get_by_text but ensure we get the result item, not the header/input
            # The result is usually the last occurrence or distinct from the input
            candidate_results = page.get_by_text(center_name, exact=False)
            
            # Wait for at least one candidate (search result)
            try:
                candidate_results.first.wait_for(state="visible", timeout=10000)
            except:
                 print("[ERROR] Search results (text match) did not appear in time.")
                 page.screenshot(path="search_results_timeout_text.png")
                 raise

            # Heuristic: The result in the list is likely the last one found or one that is a div
            # We iterate to find the most likely result item (e.g. clickable)
            count = candidate_results.count()
            print(f"Found {count} elements with center name text.")
            
            # Usually the first valid text node that is visible and interactable in the list
            # We pick the first one provided it's checking out.
            first_result_data = candidate_results.first
            if count > 1:
                 # If input and result both have text, result is likely second
                 first_result_data = candidate_results.nth(1)

            print("Interaction sequence: Scroll -> Click Card -> Click SELECT.")

            # 3. Scroll into view & Hover
            first_result_data.scroll_into_view_if_needed()
            first_result_data.hover()
            
            # 4. Click the card itself first ("select first option")
            first_result_data.click()
            print("Clicked the result card/text.")
            time.sleep(1) # Allow UI to react (expand/show button)

            # 5. Look for the "SELECT" button
            # It might be separate now.
            # Look for "SELECT" anywhere in the modal/page that is visible
            # Note: 110+ "SELECT" text elements exist. We MUST use .first to pick the one corresponding to our first result
            # or scope it to the result container.
            
            print("Looking for 'SELECT' button (targeting the first one)...")
            
            # Scoped attempt: Look inside the parent/grandparent of the text we clicked
            # This is safer than global .first
            select_btn_scoped = first_result_data.locator("..").locator("..").get_by_text("SELECT", exact=True)
            
            if select_btn_scoped.first.is_visible(timeout=2000):
                 print(f"Found scoped SELECT button. Clicking...")
                 select_btn_scoped.first.click()
            else:
                 print("Scoped SELECT not found. Trying global visible SELECT button...")
                 # Fallback to global first visible "SELECT"
                 # We filter by visibility to avoid clicking hidden ones
                 select_btn_global = page.get_by_text("SELECT", exact=True).filter(has=page.locator("visible=true"))
                 
                 if select_btn_global.first.is_visible(timeout=3000):
                      print("Found global meaningful SELECT button. Clicking...")
                      select_btn_global.first.click()
                 else:
                      print("[WARNING] Could not find a visible 'SELECT' button even globally.")
            
            time.sleep(3) # Wait for modal to close
        else:
             print("[ERROR] Search input not found (modal interactions failed).")




    except Exception as e:
        print(f"[ERROR] Center selection failed: {e}")

    # 4. Date Navigation (4th day)
    # 4. Date Navigation (4th day from today)
    print("\nNavigating to the 4th day...")
    try:
        # Wait for date tabs to be visible. 
        print("Waiting for date tabs to load...")
        time.sleep(5)
        
        # DOM Strategy based on User Input:
        # <div class="booking-date-widget"><div class="booking-date-container">...<div class="booking-cell">
        date_tabs = page.locator(".booking-cell")
        
        count = date_tabs.count()
        print(f"Found {count} date tabs.")

        if count == 0:
             print("[DEBUG] Taking screenshot for inspection: no_dates_found.png")
             page.screenshot(path="no_dates_found.png")
        
        if count >= 4:
            # Click the 4th tab (index 3)
            # DOM shows: W, T, F, S ... so 4th one is index 3.
            target_tab = date_tabs.nth(3)
            print("Clicking the 4th date tab...")
            target_tab.click()
            time.sleep(3) # Wait for slots to reload
        else:
            print("[WARNING] Less than 4 date tabs found. Clicking the last one.")
            if count > 0:
                date_tabs.last.click()
                time.sleep(3)

    except Exception as e:
        print(f"[ERROR] Date navigation error: {e}")

    # 5. Select Class (07:00 AM)
    # 5. Select Class (Dynamic Time)
    print(f"\nLooking for {target_time} class...")
    try:
        # Find the row that contains the specific time
        not_found_action = lambda: page.screenshot(path="no_slot_found.png")
        
        # We need to target the row specifically to ensure we get the class *in that row*
        # Use .first to avoid strict mode violation if multiple rows match (though theoretically shouldn't happen for same time)
        time_slot_row = page.locator(".booking-time-row-cell").filter(has=page.locator(".time-text", has_text=target_time)).first
        
        # Wait for it to be attached
        try:
            time_slot_row.wait_for(state="attached", timeout=5000)
        except:
            print(f"[WARNING] Timeout waiting for {target_time} row attachment.")

        if time_slot_row.count() > 0:
            print(f"Found {target_time} time slot row.")
            
            # Now find the class cell within this row
            # Use .first in case there are multiple classes at the same time slot (rare but possible) or weird DOM nesting
            class_card = time_slot_row.locator(".class-cell").first
            
            if class_card.count() > 0:
                # Check if available (optional logging, but we try to click anyway or handle specifically)
                class_class_attr = class_card.get_attribute("class") or ""
                print(f"Class card found. Classes: {class_class_attr}")
                
                if "unavailable-theme" in class_class_attr:
                    print(f"[WARNING] The {target_time} class appears to be UNAVAILABLE (full or past). attempting to click anyway only for verification...")
                
                class_card.click()
                print(f"Clicked {target_time} class card.")
                
                # Check for "Book" button in the popup/modal that usually appears
                # NOTE: The provided DOM was for the *list*. Clicking usually opens a bottom sheet with "Book" button.
                # Use a specific text selector for "Book" or "Join"
                print("Waiting for booking confirmation/action button...")
                
                # Broad selector for book button just in case
                book_btn = page.locator("button").filter(has_text=re.compile(r"Book|Join", re.IGNORECASE))
                
                try:
                    book_btn.wait_for(state="visible", timeout=5000)
                    book_btn.first.click()
                    print("Clicked 'Book/Join' button.")
                except Exception:
                    print("No explicit 'Book' button found immediately after clicking class card. Checking if booking is already processed or different flow...")

            else:
                print(f"[ERROR] {target_time} row found, but no '.class-cell' inside it.")
                page.screenshot(path="row_found_no_class.png")
        else:
            print(f"[ERROR] {target_time} time slot row NOT found.")
            not_found_action()
            
    except Exception as e:
        print(f"[ERROR] Class booking error: {e}")
        page.screenshot(path="booking_error.png")
            
    except Exception as e:
        print(f"[ERROR] Class booking error: {e}")
        page.screenshot(path="booking_error.png")


    # 6. Final Confirmation
    print("\nChecking for final confirmation...")
    try:
        # User Feedback: "another pop up occurs on top of booking pop up... close the pop up and then behind it , confirm and book button exists"
        # Strategy: 1. Check for overlapping "App" popup or generic modal close buttons. 2. Use JS click.
        
        # Check if the "App" popup is present
        try:
            if page.get_by_text("Complete your booking on the cult app").is_visible():
             print("Detected 'App Booking' popup. Proceed to book in app...")
             # We do not close the popup as it is the intended flow now
             
        # Fallback closure logic if it was a DIFFERENT popup, but for now we assume if that text is there, we are done/blocked.
        # If we wanted to support other popups we would separate the checks. 
        # For this specific request: "update the log to book in app".

        
        # Common selectors: .close, button.close, [aria-label='Close'], or svg inside a button in the modal
            # close_btn = page.locator(".close, .close-icon, button[aria-label='Close'], .modal-close").first
            # if close_btn.is_visible():
            #     close_btn.click()
            #     print("Closed overlapping popup.")
            #     time.sleep(2)
        except Exception as e:
            print(f"[WARNING] Could not close popup (ignoring and proceeding to force click): {e}")

        # Regex to match variants like "CONFIRM & BOOK", "CONFIRM", "PAY"
        confirm_pattern = re.compile(r"CONFIRM|PAY|BOOK", re.IGNORECASE)
        
        # Priority 1: Button role with matching name
        confirm_btn = page.get_by_role("button", name=confirm_pattern)
        
        if not confirm_btn.first.is_visible(timeout=3000):
             print("Button role not found/visible. Trying generic text match...")
             # Priority 2: Generic text match (filtered to likely clickable elements or just text)
             confirm_btn = page.get_by_text(confirm_pattern)
        
        # Use .first to handle potential duplicates (e.g. one in modal, one behind)
        final_btn = confirm_btn.first
        
        if final_btn.is_visible(timeout=3000):
            btn_text = final_btn.text_content() or "Unknown"
            print(f"Final Confirmation button visible: '{btn_text.strip()}'. Clicking via JS (Direct)...")
            
            # Debug: See what's on screen before we click
            page.screenshot(path="pre_confirm_js.png")
            
            # Use JS Click to force interaction even if covered/obscured
            final_btn.evaluate("el => el.click()")
            
            print("[SUCCESS] Clicked final confirmation (JS).")
            time.sleep(5) # Wait for booking to process
            page.screenshot(path="post_confirm_js.png")
        else:
            print("No 'CONFIRM/BOOK/PAY' button found. Might be already booked or different flow.")

    except Exception as e:
        print(f"[WARNING] Final confirmation check failed regex: {e}")
        
    print("\n[FINISH] Booking flow completed.")
