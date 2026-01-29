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
import re

# Target: drugs.com/dosage/
# Method: Pure Selenium (4 Workers)

INPUT_CSV = "backend/data/master_drugs_data.csv"
OUTPUT_CSV = "drugs_com_dosage.csv"
MAX_WORKERS = 20 # Aggressive speed

save_lock = threading.Lock()

def create_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def clean_name_for_url(name):
    # "Amoxicillin and Clavulanate" -> "amoxicillin-and-clavulanate"
    # Remove dosage info if present in scientific name (sometimes happens)
    name = str(name).lower().split(' + ')[0] # Split combos if needed? No, drugs.com often has combos
    name = re.sub(r'[^a-z0-9\s-]', '', name)
    name = re.sub(r'\s+', '-', name)
    return name

class DosageWorker:
    def __init__(self):
        self.driver = create_driver()

    def scrape(self, scientific_name):
        slug = clean_name_for_url(scientific_name)
        url = f"https://www.drugs.com/dosage/{slug}.html"
        
        try:
            self.driver.get(url)
            # time.sleep(random.uniform(1.0, 2.0))
            
            if "Page Not Found" in self.driver.title or "404" in self.driver.title:
                return None
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            content = soup.find('div', class_='contentBox') or soup.find('div', {'id': 'content'})
            
            if not content:
                return None
                
            entry = {
                'Scientific Name': scientific_name,
                'Drugs.com URL': url,
                'Adult Dosage': '',
                'Pediatric Dosage': '',
                'Renal Dose': '',
                'Liver Dose': ''
            }
            
            # Simple heuristic extraction based on headers
            text = content.get_text("\n")
            
            # Extract sections (This is rough, but effective for RAG context)
            if "Usual Adult Dose" in text:
                parts = text.split("Usual Adult Dose")
                if len(parts) > 1:
                    entry['Adult Dosage'] = parts[1].split("Usual")[0].strip()[:1000] # Limit length
            
            if "Usual Pediatric Dose" in text:
                parts = text.split("Usual Pediatric Dose")
                if len(parts) > 1:
                    entry['Pediatric Dosage'] = parts[1].split("Usual")[0].strip()[:1000]

            if "Renal Dose Adjustments" in text:
                 parts = text.split("Renal Dose Adjustments")
                 if len(parts) > 1:
                     entry['Renal Dose'] = parts[1].split("\n\n")[0].strip()[:500]

            if "Liver Dose Adjustments" in text:
                 parts = text.split("Liver Dose Adjustments")
                 if len(parts) > 1:
                     entry['Liver Dose'] = parts[1].split("\n\n")[0].strip()[:500]
            
            # Only return if we found something
            if any([entry['Adult Dosage'], entry['Pediatric Dosage']]):
                return entry
            return None

        except Exception as e:
            print(f"Error {slug}: {e}")
            try: self.driver.quit(); self.driver = create_driver()
            except: pass
            return None

    def close(self):
        self.driver.quit()

def worker_routine(names, results_list):
    worker = DosageWorker()
    for i, name in enumerate(names):
        res = worker.scrape(name)
        if res:
            with save_lock:
                results_list.append(res)
                # print(f"Found: {name}")
        
        if (i+1) % 20 == 0:
            print(f"Worker progress: {i+1}/{len(names)}")
    worker.close()

def run_scraper():
    if not os.path.exists(INPUT_CSV):
        print(f"Input file {INPUT_CSV} not found!")
        return

    print("Loading scientific names...")
    df = pd.read_csv(INPUT_CSV)
    # Get unique scientific names
    names = df['Scientific Name'].dropna().unique().tolist()
    
    # Optional: Filter already done
    if os.path.exists(OUTPUT_CSV):
        try:
            done_df = pd.read_csv(OUTPUT_CSV)
            done = set(done_df['Scientific Name'].unique())
            names = [n for n in names if n not in done]
            print(f"Resuming: {len(done)} done. {len(names)} left.")
        except: pass

    print(f"Starting Scraper with {MAX_WORKERS} workers on {len(names)} items...")
    
    chunk_size = len(names) // MAX_WORKERS + 1
    chunks = [names[i:i + chunk_size] for i in range(0, len(names), chunk_size)]
    
    all_results = [] # In-memory storage for this run? No, we need to append to file to be safe
    # Ideally we'd append to file, but we can dump periodically
    
    # Load existing to memory if any (for final dump)
    if os.path.exists(OUTPUT_CSV):
         all_results = pd.read_csv(OUTPUT_CSV).to_dict('records')

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(worker_routine, chunk, all_results) for chunk in chunks]
        
        while not all(f.done() for f in futures):
            time.sleep(15)
            print(f"Total Dosage Records: {len(all_results)}")
            pd.DataFrame(all_results).to_csv(OUTPUT_CSV, index=False)

    pd.DataFrame(all_results).to_csv(OUTPUT_CSV, index=False)
    print(f"Finished. Saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    run_scraper()
