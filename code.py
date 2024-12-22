!pip install selenium
import os
print("Current Working Directory:", os.getcwd())
import time
import csv
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("user-agent=Mozilla/5.0")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
        Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined
        })
        """
    })
    return driver


def amazon_login(driver, email, password):
    try:
        driver.get("https://www.amazon.in/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.in%2Flog-in%2Fs%3Fk%3Dlog%2Bin%26ref_%3Dnav_custrec_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=inflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_email"))
        ).send_keys(email, Keys.RETURN)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ap_password"))
        ).send_keys(password, Keys.RETURN)

       
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "nav-logo-sprites"))
        )
        print("Login successful!")
    except TimeoutException:
        print("Login failed. Solve CAPTCHA if prompted.")
        input("Press Enter after solving CAPTCHA manually...")


    driver.get("https://www.amazon.in/gp/bestsellers/")
    if "not a functioning page" in driver.page_source:
        raise Exception("Blocked or invalid access to Best Sellers page.")



def scrape_category(driver, category_url, max_products=1500):
    driver.get(category_url)
    scraped_products = []

    while len(scraped_products) < max_products:
        try:
            products = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".zg-grid-general-faceout"))
            )

            for product in products:
                if len(scraped_products) >= max_products:
                    break

                try:
                    name = product.find_element(By.CSS_SELECTOR, ".p13n-sc-truncated").text
                    price = product.find_element(By.CSS_SELECTOR, ".p13n-sc-price").text
                    rating = product.find_element(By.CSS_SELECTOR, ".a-icon-alt").get_attribute("textContent")
                    seller = product.find_element(By.CSS_SELECTOR, ".a-row.a-size-small").text

                  
                    scraped_products.append({
                        "Product Name": name,
                        "Price": price,
                        "Rating": rating,
                        "Seller": seller
                    })
                except NoSuchElementException:
                    continue

            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".a-pagination .a-last a"))
                )
                next_button.click()
                time.sleep(2)  
            except TimeoutException:
                break  

        except TimeoutException:
            print("Error loading category page. Moving to next category...")
            break

    return scraped_products

# Save data to CSV
def save_to_csv(data, filename):
    if data:
        keys = data[0].keys()
        with open(filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)


def save_to_json(data, filename):
    if data:
        with open(filename, "w", encoding="utf-8") as jsonfile:
            json.dump(data, jsonfile, indent=4)

# Main function
def main():
    email =input("Enter your email: ") 
    password =input("Enter your password: ")    

    categories = [
        "https://www.amazon.in/gp/bestsellers/kitchen/ref=zg_bs_nav_kitchen_0",     
    "https://www.amazon.in/gp/bestsellers/shoes/ref=zg_bs_nav_shoes_0",          
    "https://www.amazon.in/gp/bestsellers/computers/ref=zg_bs_nav_computers_0",  
    "https://www.amazon.in/gp/bestsellers/electronics/ref=zg_bs_nav_electronics_0",  
    "https://www.amazon.in/gp/bestsellers/books/ref=zg_bs_nav_books_0",           
    "https://www.amazon.in/gp/bestsellers/beauty/ref=zg_bs_nav_beauty_0",        
    "https://www.amazon.in/gp/bestsellers/fashion/ref=zg_bs_nav_fashion_0",      
    "https://www.amazon.in/gp/bestsellers/sports/ref=zg_bs_nav_sports_0",        
    "https://www.amazon.in/gp/bestsellers/garden/ref=zg_bs_nav_garden_0",       
    "https://www.amazon.in/gp/bestsellers/health/ref=zg_bs_nav_health_0",  
    ]

    driver = initialize_driver()
    amazon_login(driver, email, password)

    all_products = []

    for category_url in categories:
        print(f"Scraping category: {category_url}")
        products = scrape_category(driver, category_url)
        all_products.extend(products)
        print(f"Scraped {len(products)} products from {category_url}")

  
    save_to_csv(all_products, "amazon_best_sellers.csv") 
    if os.path.exists("amazon_best_sellers.csv"):
        print("The file exists.")
    else:
        print("The file does not exist.")
    print("Scraping completed. Data saved to CSV")
    driver.quit()

if __name__ == "__main__":
    main()
