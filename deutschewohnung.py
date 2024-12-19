from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time


def fetch_room_data(url):
    print(f"[INFO] Setting up Selenium WebDriver to fetch: {url}...")
    options = Options()
    options.add_argument("--headless")  # Run in headless mode
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    rooms = []  # Store all room data
    try:
        driver.get(url)
        time.sleep(3)  # Wait for JavaScript to load
        print(f"[DEBUG] Page loaded successfully.")

        # Find all room listings on the page
        room_elements = driver.find_elements(By.CSS_SELECTOR, "li.object-list__item")
        print(f"[INFO] Found {len(room_elements)} potential room elements.")

        # Collect data for this page
        for i, room in enumerate(room_elements, start=1):
            # Validate room data
            try:
                room_name_element = room.find_element(By.CSS_SELECTOR, "h2.object-list__headline")
                room_name = room_name_element.text.strip()
            except Exception:
                room_name = None

            try:
                address_element = room.find_element(By.CSS_SELECTOR, "div.object-list__address p")
                address = address_element.text.replace("\n", ", ").strip()
            except Exception:
                address = None

            if room_name and address:
                # Add valid room data to the list
                room_data = f"{room_name} - {address}"
                rooms.append(room_data)
                print(f"[DEBUG] Valid room found: {room_data}")
            else:
                print(f"[WARNING] Incomplete or invalid room data, element {i}.")

    except Exception as e:
        print(f"[ERROR] An error occurred while processing: {e}")

    finally:
        print("[INFO] Closing WebDriver...")
        driver.quit()
        print("[INFO] WebDriver closed.")

    return rooms


def monitor_changes(new_rooms, all_rooms):
    """
    Compare new rooms with the current list of all rooms to detect changes.
    """
    new_set = set(new_rooms)
    all_set = set(all_rooms)

    added = new_set - all_set
    removed = all_set - new_set

    return list(added), list(removed)


def scrape_and_monitor(base_url, total_pages):
    all_rooms = []  # Keep track of all rooms found across all pages
    while True:
        print("\n[INFO] Starting a new monitoring cycle...")

        current_rooms = []  # Collect rooms found during this scrape

        # Scrape each page
        for page in range(1, total_pages + 1):
            # Construct the URL for each page
            url = base_url.replace("page=1", f"page={page}")
            print(f"\n[INFO] Scraping page {page}...")

            # Fetch data for the current page
            page_rooms = fetch_room_data(url)

            # Add rooms from this page to the current list
            current_rooms.extend(page_rooms)

        # Monitor for changes compared to the previous run
        added, removed = monitor_changes(current_rooms, all_rooms)

        # Update the master list of all rooms
        all_rooms = current_rooms.copy()

        # Print monitoring results
        print("\n[INFO] Monitoring results:")
        if added:
            print(f"[INFO] New rooms added: {len(added)}")
            for room in added:
                print(f"- {room}")
        else:
            print("[INFO] No new rooms added.")

        if removed:
            print(f"[INFO] Rooms removed: {len(removed)}")
            for room in removed:
                print(f"- {room}")
        else:
            print("[INFO] No rooms removed.")

        # Wait before the next monitoring cycle
        print("[INFO] Monitoring cycle complete. Waiting for the next cycle...\n")
        time.sleep(60)  # Adjust the interval as needed


if __name__ == "__main__":
    # Base URL for the first page
    base_url = "https://www.deutsche-wohnen.com/immobilienangebote#page=1&locale=de&commercializationType=rent&utilizationType=flat,retirement&location=Berlin"

    # Define the total number of pages to scrape
    total_pages = 5  # Adjust based on your requirements

    # Start scraping and monitoring
    scrape_and_monitor(base_url, total_pages)
