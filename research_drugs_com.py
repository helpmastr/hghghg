from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

# Use the same stealth config as before
def create_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Bypass detection
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

def research():
    driver = create_driver()
    try:
        # 1. Test Main Page
        print("Accessing drugs.com/dosage/...")
        driver.get("https://www.drugs.com/dosage/")
        time.sleep(5)
        print(f"Main Page Title: {driver.title}")
        
        # 2. Test Specific Drug Page (Acetaminophen)
        target_url = "https://www.drugs.com/dosage/acetaminophen.html"
        print(f"Accessing {target_url}...")
        driver.get(target_url)
        time.sleep(5)
        print(f"Drug Page Title: {driver.title}")
        
        # 3. Dump Content for Analysis
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Try to find dosage content
        # Drugs.com usually has a main content block
        content = soup.find('div', class_='contentBox')
        if not content:
            content = soup.find('div', {'id': 'content'})
            
        if content:
            # Look for headers like "Usual Adult Dose"
            headers = content.find_all(['h2', 'h3'])
            print(f"\nFound {len(headers)} Headers:")
            for h in headers[:5]:
                print(f"- {h.get_text(strip=True)}")
                
            # Sample text length
            text = content.get_text(strip=True)
            print(f"\nTotal Text Length: {len(text)} chars")
        else:
            print("Content box not found.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    research()
