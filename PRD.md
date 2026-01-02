# Product Requirements Document (PRD): Cult Class Booking Automation

## 1. Executive Summary
The goal of this project is to build an automated solution for booking Cult.fit classes. The system will automate the user flow from login (cached) to booking confirmation, targeting the 7:00 AM class on the 4th day from the current date. The initial prototype will run in a visible browser for debugging, with the final version running headlessly.

## 2. Problem Statement
Booking popular classes on Cult.fit is competitive, with slots opening at 10 PM IST. Manual booking is slow and prone to missing out. An automated solution is required to secure slots reliably.

## 3. User Stories
- As a user, I want the system to automatically select my preferred center.
- As a user, I want the system to navigate to the booking date (4 days in advance).
- As a user, I want the system to book the 7:00 AM class.
- As a user, I want the system to retry if booking fails.
- As a user, I want to be notified if the booking is successful or failed.

## 4. Functional Requirements

### 4.1 Core Booking Flow
1.  **Center Selection**:
    *   Navigate to `https://www.cult.fit/cult/classbooking?pageFrom=cultCLP&pageType=classbooking`.
    *   Search for "Cult Whitefield".
    *   Select the correct center from the dropdown/list.
2.  **Date Selection**:
    *   Identify the date 4 days from today.
    *   Click/Navigate to the corresponding date tab.
3.  **Class Selection**:
    *   Locate the class scheduled for 7:00 AM.
    *   Click the "Select" or "Book" button.
4.  **Confirmation**:
    *   Handle any confirmation pop-ups.
    *   Verify booking success.

### 4.2 Session Management
*   Store and reuse login session (cookies/local storage) to avoid repeated logins (OTP based).
*   **Initial Setup**: Manual login once to capture session.

### 4.3 Error Handling
*   Detect if the class is full.
*   Detect if the center is not found.
*   Detect network timeouts.

## 5. Technical Architecture

### 5.1 Tech Stack
*   **Language**: Python (recommended for automation ecosystem) or Node.js. *Decision: Python with Playwright/Selenium due to robust browser automation support.*
*   **Browser Automation**: Playwright (preferred for speed and reliability) or Selenium.
*   **Scheduling**: Cron jobs or a task scheduler (e.g., Celery/APScheduler) for 10 PM execution.

### 5.2 Modular Design (for Asynchronous Agents)
To support future asynchronous agent integration, the system will be modularized:
*   **Auth Module**: Handles login and session persistence.
*   **Navigation Module**: Handles URL navigation and center selection.
*   **Booking Module**: Handles date picking and class selection.
*   **Notification Module**: Handles emails/alerts.

## 6. Roadmap

### Phase 1: Prototype (Current Goal)
*   Linear script execution.
*   Visible browser (headed mode).
*   Hardcoded parameters (Center, Time).

### Phase 2: Robustness & Headless
*   Headless browser execution.
*   Robust error handling and retries.
*   Configuration file for user preferences.

### Phase 3: Production & Automation
*   Automated scheduling (10 PM IST).
*   Notification integration.
*   Dockerization for deployment.

## 7. Success Metrics
*   Successful booking of the 7:00 AM class in < 10 seconds from slot opening.
*   Zero manual intervention required after initial login.

## 8. Assumptions & Risks
*   **Assumption**: DOM structure of Cult.fit remains relatively stable.
*   **Risk**: Cult.fit implements CAPTCHA or stricter bot detection.
*   **Risk**: 7:00 AM class might not exist on some days.
