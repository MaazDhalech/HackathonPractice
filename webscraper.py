from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# Initialize Selenium WebDriver
def init_driver():
    options = Options()
    options.add_argument("--headless")  # Ensure headless mode is set
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--remote-debugging-port=9222")  # Enable remote debugging

    driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"), options=options)
    return driver


def scrape_menu():
    driver = init_driver()

    print("Navigating to menu page...")
    driver.get("https://dining.berkeley.edu/menus/")
    time.sleep(2)  # Reduced initial wait time

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    print("Parsed page source with BeautifulSoup")

    # Find all meal items
    meal_items = soup.find_all('li', class_='recip')
    print(f"Found {len(meal_items)} meal items")

    # To store the halal meals
    halal_meals = []

    for meal_item in meal_items:
        # Extract meal name (span tag)
        meal_name_tag = meal_item.find('span')
        if meal_name_tag:
            meal_name = meal_name_tag.text.strip()
        else:
            meal_name = "Unknown Meal"

        # Skip meals that are unlikely to be halal based on certain categories (optional optimization)
        # You can add more conditions based on your specific knowledge of the meals
        if 'vegetarian' in meal_name.lower() or 'dessert' in meal_name.lower():
            continue

        # Simulate clicking to reveal the ingredients
        data_id = meal_item['data-id']

        try:
            # Wait for the element to be clickable and click using JavaScript
            ingredient_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f'li.recip[data-id="{data_id}"]'))
            )
            # Scroll into view and click using JavaScript
            driver.execute_script("arguments[0].scrollIntoView();", ingredient_button)
            driver.execute_script("arguments[0].click();", ingredient_button)

        except Exception as e:
            continue

        # Decreased wait time after clicking
        time.sleep(1)

        # Extract ingredients using BeautifulSoup after click
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        ingredients_section = soup.find('div', class_='ingredients sec')
        if ingredients_section:
            ingredients_tag = ingredients_section.find('span', class_='content')
            if ingredients_tag:
                ingredients = ingredients_tag.text.strip().lower()

                # Check if 'halal' is in the ingredients
                if 'halal' in ingredients:
                    halal_meals.append(meal_name)

    driver.quit()

    # Output only the halal meals
    if halal_meals:
        print("\nList of halal meals found:")
        for halal_meal in halal_meals:
            print(f"- {halal_meal}")
    else:
        print("No halal meals found.")

# Scrape the menu
scrape_menu()
