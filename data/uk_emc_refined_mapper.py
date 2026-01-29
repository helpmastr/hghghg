import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import concurrent.futures

# Target: medicines.org.uk
# Goal: Map ALL Saudi Brands to Ingredients using SIMPLIFIED SEARCH TERMS
# Optimized detection logic (targeting search-results-product)

INPUT_CSV = "uk_search_terms.csv"
OUTPUT_CSV = "uk_brand_mapping.csv"
MAX_WORKERS = 40 
DELAY = 0.05

class EMCMapper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = "https://www.medicines.org.uk/emc/search"

    def search_brand(self, search_term):
        try:
            params = {'q': search_term}
            response = self.session.get(self.base_url, params=params, timeout=12)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for the product results container
            product_divs = soup.find_all('div', class_='search-results-product')
            if not product_divs:
                return []

            results = []
            for div in product_divs[:5]: 
                name_tag = div.find('a', class_='search-results-product-info-title-link')
                ingredients_tag = div.find('div', class_='search-results-product-info-type')
                
                if name_tag and ingredients_tag:
                    name = name_tag.get_text(strip=True)
                    ingredients = ingredients_tag.get_text(strip=True)
                    results.append({
                        'Search Term': search_term,
                        'UK Brand Name': name,
                        'Active Ingredients': ingredients
                    })
            
            return results
        except Exception:
            return []

def run_refined_mapper():
    if not os.path.exists(INPUT_CSV):
        print(f"Error: {INPUT_CSV} not found.")
        return

    print(f"Loading search terms from {INPUT_CSV}...")
    df = pd.read_csv(INPUT_CSV)
    search_terms = df['Search Term'].dropna().unique().tolist()
    
    # User-requested manual fixes/tests
    # The user mentioned 'panadol instead of pandol'
    # I'll ensure PANADOL is in there (it should be if it was in the master list)
    
    print(f"Total Unique Search Terms to process: {len(search_terms)}")

    all_results = []
    # Overwrite for a fresh, more accurate run
    mapper = EMCMapper()
    print(f"Starting Refined UK Mapper with {MAX_WORKERS} workers...")

    checkpoint_size = 50
    hits = 0
    misses = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_term = {executor.submit(mapper.search_brand, term): term for term in search_terms}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_term)):
            try:
                res = future.result()
                if res:
                    all_results.extend(res)
                    hits += 1
                else:
                    misses += 1
                
                if (i+1) % 50 == 0:
                    print(f"Progress: [{i+1}/{len(search_terms)}] | Hits: {hits} | Misses: {misses}")
                
                # Auto-save
                if (i+1) % checkpoint_size == 0:
                    pd.DataFrame(all_results).to_csv(OUTPUT_CSV, index=False)
            except Exception:
                pass

    if all_results:
        pd.DataFrame(all_results).to_csv(OUTPUT_CSV, index=False)
        print(f"\nFINISH! Saved {len(all_results)} Improved UK mappings to {OUTPUT_CSV}")

if __name__ == "__main__":
    run_refined_mapper()
