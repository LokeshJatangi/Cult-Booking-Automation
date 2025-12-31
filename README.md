# Cult.fit Booking Automation

A Python-based automation tool using [Playwright](https://playwright.dev/python/) to automate class bookings on [Cult.fit](https://www.cult.fit/).

## ⚠️ Important Note
**Status**: Partial Success / Deprecated.
While this tool successfully automates the entire flow (Login -> Center Selection -> Date Selection -> Class Selection -> Confirmation Click), Cult.fit often restricts the final booking confirmation step to their **Mobile App**. You may encounter a popup saying "Complete your booking on the cult app!" at the final step.

## Features
*   **Persistent Sessions**: Logs in once and saves the browser state (cookies/local storage) to `./user_data`, avoiding repeated OTP logins.
*   **Robust Selectors**: Handles dynamic class names and complex DOM structures.
*   **CLI Arguments**: Configurable center name and class time.
*   **Resilience**: customized logic to handle overlapping popups and force-click actions.

## Prerequisites
*   Python 3.10+
*   Playwright

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <your-repo-url>
    cd cult-booking-automation
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    # OR using uv
    uv sync
    ```

3.  **Install Playwright browsers**:
    ```bash
    playwright install chromium
    ```

## Usage

### 1. First Run: Login
Run with the `--login` flag to open a headed browser, enter your phone number and OTP manually. The session will be saved automatically.
```bash
python main.py --login
```
*Wait for the login to complete, then press Ctrl+C to exit and save the session.*

### 2. Schedule a Booking
Once logged in, run the script to book a class.

**Default (07:00 AM at Cult Basavanagudi):**
```bash
python main.py
```

**Custom Time:**
```bash
python main.py --time "07:00 PM"
```

**Custom Center:**
```bash
python main.py --center "Indiranagar 100ft Road"
```

## Troubleshooting
*   **"No slots found"**: Ensure the center name is exact.
*   **"TargetClosedError"**: Do not close the browser window manually mid-script.
*   **Strict Mode Errors**: If you see "resolved to N elements", checking `booking.py` for `.first` calls usually fixes this.

## Scheduling (Linux Cron)
To run this script automatically every day at **10:00 PM** (likely when slots open):

1.  Open your crontab:
    ```bash
    crontab -e
    ```

2.  Add the following line (adjust paths if necessary):
    ```cron
    0 22 * * * cd /home/kakashi/EAG/cult-booking-automation && /home/kakashi/EAG/cult-booking-automation/.venv/bin/python main.py --headless
    ```

    *   `0 22 * * *`: Runs at 22:00 (10 PM) every day.
    *   `cd ...`: Switches to the project directory so it can find `user_data`.
    *   `--headless`: Important for running in the background without a visible UI.

## License
MIT
