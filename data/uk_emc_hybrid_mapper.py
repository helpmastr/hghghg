import concurrent.futures
import threading
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

# Target: medicines.org.uk
# Approach: Hybrid (Selenium for Cookies + Requests for Speed)
# Speed: Super Fast (50 workers)

INPUT_CSV = "uk_search_terms.csv"
OUTPUT_CSV = "uk_brand_mapping.csv"
NOPECHA_KEY = "sub_1ScqrICRwBwvt6pt9IjRFvuP" 
MAX_WORKERS = 50

# Global state
current_headers = {}
driver_lock = threading.Lock()

def get_cloudflare_cookies():
    print("Launching Standard Selenium (Stealth Mode) to refresh cookies...")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Bypass detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        driver.get("https://www.medicines.org.uk/emc/search")
        time.sleep(8) # Wait for Cloudflare turnstile
        
        title = driver.title
        print(f"Browser Title: {title}")
        
        selenium_cookies = driver.get_cookies()
        cookie_dict = {c['name']: c['value'] for c in selenium_cookies}
        
        headers = {
            'User-Agent': options.arguments[3].split('=', 1)[1], # Parse UA from args
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        }
        
        print(f"Captured {len(cookie_dict)} cookies. Session ready.")
        driver.quit()
        return headers, cookie_dict
    except Exception as e:
        print(f"Browser Error: {e}")
        try: driver.quit()
        except: pass
        return None, None

class FastEMCMapper:
    def __init__(self):
        self.session = requests.Session()
        self.refresh_session()

    def refresh_session(self):
        with driver_lock:
            headers, cookies = get_cloudflare_cookies()
            if headers:
                self.session.headers.update(headers)
                self.session.cookies.update(cookies)
            else:
                print("Failed to get cookies. Retrying...")
                time.sleep(5)
                self.refresh_session()

    def search_brand(self, search_term):
        try:
            params = {'q': search_term}
            # Use quick timeout
            response = self.session.get("https://www.medicines.org.uk/emc/search", params=params, timeout=5)
            
            # Check for Cloudflare block
            if "Just a moment" in response.text or response.status_code in [403, 429]:
                print(f"Blocked on {search_term}. Refreshing cookies...")
                self.refresh_session()
                return self.search_brand(search_term) # Retry
            
            soup = BeautifulSoup(response.text, 'html.parser')
            # Fast check
            product_divs = soup.find_all('div', class_='search-results-product')
            
            results = []
            for div in product_divs[:3]: 
                name_tag = div.find('a', class_='search-results-product-info-title-link')
                ingredients_tag = div.find('div', class_='search-results-product-info-type')
                
                if name_tag and ingredients_tag:
                    results.append({
                        'Search Term': search_term,
                        'UK Brand Name': name_tag.get_text(strip=True),
                        'Active Ingredients': ingredients_tag.get_text(strip=True)
                    })
            return results
        except Exception:
            return []

def run_hybrid_mapper():
    if not os.path.exists(INPUT_CSV): return
    print(f"Loading {INPUT_CSV}...")
    df = pd.read_csv(INPUT_CSV)
    search_terms = df['Search Term'].dropna().unique().tolist()
    
    # Resume logic
    all_results = []
    if os.path.exists(OUTPUT_CSV):
        try:
            existing_df = pd.read_csv(OUTPUT_CSV)
            processed = set(existing_df['Search Term'].unique())
            search_terms = [t for t in search_terms if t not in processed]
            all_results = existing_df.to_dict('records')
            print(f"Resuming: {len(processed)} done. {len(search_terms)} left.")
        except: pass

    if not search_terms:
        print("Done.")
        return

    mapper = FastEMCMapper()
    print(f"Starting SUPER FAST Hybrid Mapper (Workers={MAX_WORKERS})...")

    hits = 0
    misses = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_term = {executor.submit(mapper.search_brand, term): term for term in search_terms}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_term)):
            res = future.result()
            if res:
                all_results.extend(res)
                hits += 1
            else:
                misses += 1
            
            if (i+1) % 50 == 0:
                print(f"Progress: [{i+1}/{len(search_terms)}] | Hits: {hits} | Misses: {misses}")
                # Save chunk
                pd.DataFrame(all_results).to_csv(OUTPUT_CSV, index=False)

    pd.DataFrame(all_results).to_csv(OUTPUT_CSV, index=False)
    print(f"Saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    run_hybrid_mapper()
