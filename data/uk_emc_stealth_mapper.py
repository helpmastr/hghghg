import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import concurrent.futures
import random

# Target: medicines.org.uk
# Goal: Bypass Cloudflare/Bot-detection with stealthy approach
# Reduced workers and increased randomness

INPUT_CSV = "uk_search_terms.csv"
OUTPUT_CSV = "uk_brand_mapping.csv"
MAX_WORKERS = 3  # Stay low to avoid trigger
BASE_DELAY = 1.5   # Respectful delay

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0'
]

class StealthEMCMapper:
    def __init__(self):
        self.session = requests.Session()

    def search_brand(self, search_term):
        time.sleep(random.uniform(BASE_DELAY, BASE_DELAY * 2))
        try:
            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.medicines.org.uk/emc/',
                'DNT': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1'
            }
            
            params = {'q': search_term}
            response = self.session.get("https://www.medicines.org.uk/emc/search", params=params, headers=headers, timeout=15)
            
            if "Just a moment..." in response.text or response.status_code == 403:
                # Still blocked
                return "BLOCKED"
            
            soup = BeautifulSoup(response.text, 'html.parser')
            product_divs = soup.find_all('div', class_='search-results-product')
            if not product_divs:
                return []

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

def run_stealth_mapper():
    if not os.path.exists(INPUT_CSV): return

    print("Loading search terms...")
    df = pd.read_csv(INPUT_CSV)
    search_terms = df['Search Term'].dropna().unique().tolist()
    
    # Logic to Resume
    all_results = []
    if os.path.exists(OUTPUT_CSV):
        try:
            existing_df = pd.read_csv(OUTPUT_CSV)
            processed = set(existing_df['Search Term'].unique())
            search_terms = [t for t in search_terms if t not in processed]
            all_results = existing_df.to_dict('records')
            print(f"Resuming: {len(processed)} terms done. {len(search_terms)} left.")
        except: pass

    if not search_terms:
        print("All done.")
        return

    mapper = StealthEMCMapper()
    print(f"Starting Stealth Mapper (Workers={MAX_WORKERS})...")

    hits = 0
    misses = 0
    blocks = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_term = {executor.submit(mapper.search_brand, term): term for term in search_terms} # FULL RUN
        for i, future in enumerate(concurrent.futures.as_completed(future_to_term)):
            res = future.result()
            if res == "BLOCKED":
                blocks += 1
            elif res:
                all_results.extend(res)
                hits += 1
            else:
                misses += 1
            
            if (i+1) % 10 == 0:
                print(f"Progress: [{i+1}/300] | Hits: {hits} | Misses: {misses} | Blocks: {blocks}")
            
            if blocks > 5:
                print("\nCRITICAL: Too many blocks. Cloudflare is onto us. Saving and exiting.")
                break

    pd.DataFrame(all_results).to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved results to {OUTPUT_CSV}")

if __name__ == "__main__":
    run_stealth_mapper()
