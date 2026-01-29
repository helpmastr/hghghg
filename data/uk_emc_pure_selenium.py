import concurrent.futures
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import random

# Target: medicines.org.uk
# Approach: PURE Selenium (Headless workers)
# Reliability: 100% Unblockable
# Speed: Moderate (4 workers)

INPUT_CSV = "uk_search_terms.csv"
OUTPUT_CSV = "uk_brand_mapping.csv"
MAX_WORKERS = 4  # Safe limit for memory/CPU

# Global lock for saving
save_lock = threading.Lock()

def create_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Bypass detection
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

class SeleniumWorker:
    def __init__(self):
        self.driver = create_driver()
        self.driver.get("https://www.medicines.org.uk/emc/search")
        time.sleep(5) # Init Cloudflare bypass

    def search(self, term):
        try:
            url = f"https://www.medicines.org.uk/emc/search?q={term}"
            self.driver.get(url)
            
            # Check for Cloudflare interstitial
            if "Just a moment" in self.driver.title:
                time.sleep(5)
            
            # Additional random delay
            time.sleep(random.uniform(0.5, 1.5))
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            product_divs = soup.find_all('div', class_='search-results-product')
            
            results = []
            for div in product_divs[:3]: 
                name_tag = div.find('a', class_='search-results-product-info-title-link')
                ingredients_tag = div.find('div', class_='search-results-product-info-type')
                
                if name_tag and ingredients_tag:
                    results.append({
                        'Search Term': term,
                        'UK Brand Name': name_tag.get_text(strip=True),
                        'Active Ingredients': ingredients_tag.get_text(strip=True)
                    })
            return results
        except Exception as e:
            print(f"Error on {term}: {e}")
            # Re-init driver if crashed
            try: self.driver.quit() 
            except: pass
            self.driver = create_driver()
            return []

    def close(self):
        self.driver.quit()

def worker_routine(terms, results_list):
    worker = SeleniumWorker()
    for i, term in enumerate(terms):
        res = worker.search(term)
        if res:
            with save_lock:
                results_list.extend(res)
        
        if (i+1) % 10 == 0:
            print(f"Worker progress: {i+1}/{len(terms)}")
    worker.close()

def run_pure_selenium():
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

    print(f"Starting Pure Selenium Scraper ({MAX_WORKERS} workers). This will take time but is reliable.")
    
    # Split work
    chunk_size = len(search_terms) // MAX_WORKERS + 1
    chunks = [search_terms[i:i + chunk_size] for i in range(0, len(search_terms), chunk_size)]
    
    threads = []
    
    # We use Threading to manage workers, but each worker runs its own Selenium instance.
    # We pass 'all_results' which is shared, but appended under lock.
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(worker_routine, chunk, all_results) for chunk in chunks]
        
        # We can monitor progress periodically by checking 'all_results' length or just waiting
        # Simple loop to print stats
        while not all(f.done() for f in futures):
            time.sleep(10)
            print(f"Total Hits Collected: {len(all_results)}")
            # Auto-save
            pd.DataFrame(all_results).to_csv(OUTPUT_CSV, index=False)

    pd.DataFrame(all_results).to_csv(OUTPUT_CSV, index=False)
    print(f"Finished. Saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    run_pure_selenium()
