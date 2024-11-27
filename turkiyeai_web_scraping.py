from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# Function to initialize the browser
def initialize_driver():
    """Starts the driver in a set window size"""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")  # full screen
    driver = webdriver.Chrome(options=options)
    return driver

# Function to navigate to the Ekosistem section
def navigate_to_ekosistem(driver, base_url):
    driver.get(base_url)
    time.sleep(2)

    # Click on "Ekosistem"
    ekosistem_xpath = "//span[text()='Ekosistem']"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, ekosistem_xpath))).click()
    time.sleep(2)

    # Click on "TRAI Girişimler Haritası"
    trai_xpath = "//span[contains(text(),'TRAI Girişimler Haritası')]"
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, trai_xpath))).click()
    time.sleep(2)

def process_companies(driver):
    try:
        # Locate all the company links in the current category
        company_cards_xpath = "//div[contains(@class, 'portfolio_grid')]//a"
        company_cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, company_cards_xpath))
        )
        print(f"Girişim sayısı: {len(company_cards)}")

        data = []

        for index, card in enumerate(company_cards):
            # Scroll to the company card to make it visible
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
            time.sleep(1)

            # Use JavaScript click instead of Selenium click
            company_url = card.get_attribute("href")
            driver.execute_script("arguments[0].click();", card)
            time.sleep(2)

            # Extract data from the company page
            try:
                title = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "h1"))
                ).text

                # Extract founder and categories
                wpb_wrapper = driver.find_element(By.CLASS_NAME, "wpb_wrapper")
                paragraphs = wpb_wrapper.find_elements(By.TAG_NAME, "p")

                founder = "N/A"
                categories = "N/A"

                for p in paragraphs:
                    text = p.text.strip()
                    if "Kurucu" in text:
                        founder = text.replace("Kurucu:", "").replace("Kurucu Ortak:", "").strip()
                    elif "Kategoriler" in text:
                        categories = text.replace("Kategoriler:", "").strip()

                # Extract "Siteye Git" URL
                site_link_xpath = "//div[contains(@class, 'd-block w-100 text-center')]/a"
                site_link_element = driver.find_element(By.XPATH, site_link_xpath)
                site_url = site_link_element.get_attribute("href")

                data.append({
                    'Title': title,
                    'Company URL': company_url,
                    'Founder': founder,
                    'Categories': categories,
                    'Site URL': site_url
                })
                print(f"Başlık: {title}, Kurucu: {founder}, Kategoriler: {categories}, Site URL: {site_url}")
            except Exception as e:
                print(f"Bilgi alınamadı: {e}")

            # Go back to the main page
            driver.back()
            time.sleep(2)
            company_cards = driver.find_elements(By.XPATH, company_cards_xpath)

        return data
    except Exception as e:
        print(f"Hata oluştu: {e}")
        return []

# Function to save data to Excel
def save_to_excel(data, file_path):
    """Saves data to Excel"""
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)
    print(f"Veriler Excel'e kaydedildi: {file_path}")

# Main function
def main():
    base_url = "https://turkiye.ai/"
    driver = initialize_driver()
    all_data = []  # Initialize data storage

    try:
        # Navigate to TRAI Girişimler Haritası
        navigate_to_ekosistem(driver, base_url)

        # Process all companies under the "All" category
        all_data = process_companies(driver)
    except Exception as e:
        print(f"Hata oluştu: {e}")
    finally:
        if all_data:  # Only save if there is data
            excel_path = "C:/Users/ASUS/Desktop/girisimci_data.xlsx"
            save_to_excel(all_data, excel_path)
        driver.quit()

# Run the code
if __name__ == "__main__":
    main()
