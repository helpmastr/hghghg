import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import concurrent.futures

# Target: medicines.org.uk
# Goal: Map ALL Saudi Brands to Ingredients using UK data
# High speed with robust 'No Results' handling

INPUT_CSV = "backend/data/master_drugs_data.csv"
OUTPUT_CSV = "uk_brand_mapping.csv"
MAX_WORKERS = 40  # Optimized for terminal/Railway env
DELAY = 0.05

class EMCMapper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = "https://www.medicines.org.uk/emc/search"

    def search_brand(self, brand_name):
        try:
            params = {'q': brand_name}
            response = self.session.get(self.base_url, params=params, timeout=12)
            if response.status_code != 200:
                return []
            
            # CHECK FOR NO RESULTS
            if "no-results-content" in response.text:
                return []

            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            product_divs = soup.find_all('div', class_='search-results-product')
            
            for div in product_divs[:3]: # Only take top 3 UK variations
                name_tag = div.find('a', class_='search-results-product-info-title-link')
                ingredients_tag = div.find('div', class_='search-results-product-info-type')
                
                if name_tag and ingredients_tag:
                    name = name_tag.get_text(strip=True)
                    ingredients = ingredients_tag.get_text(strip=True)
                    results.append({
                        'Search Query': brand_name,
                        'UK Brand Name': name,
                        'Active Ingredients': ingredients
                    })
            
            return results
        except Exception:
            return []

def run_large_mapper():
    if not os.path.exists(INPUT_CSV):
        print(f"Error: {INPUT_CSV} not found.")
        return

    print("Loading Saudi Master Data...")
    df = pd.read_csv(INPUT_CSV)
    brand_names = df['Trade Name'].dropna().unique().tolist()
    
    # ADD TEST CASE
    brand_names = ["jksdfskl"] + brand_names
    
    print(f"Total Unique Brands to process: {len(brand_names)}")

    all_results = []
    if os.path.exists(OUTPUT_CSV):
        try:
            existing_df = pd.read_csv(OUTPUT_CSV)
            processed = set(existing_df['Search Query'].unique())
            brand_names = [b for b in brand_names if b not in processed]
            all_results = existing_df.to_dict('records')
            print(f"Resuming: {len(processed)} items already done. {len(brand_names)} remaining.")
        except:
            pass

    if not brand_names:
        print("All mapping completed.")
        return

    mapper = EMCMapper()
    print(f"Starting UK Mapper with {MAX_WORKERS} workers...")

    checkpoint_size = 50
    hits = 0
    misses = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_brand = {executor.submit(mapper.search_brand, brand): brand for brand in brand_names}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_brand)):
            try:
                res = future.result()
                if res:
                    all_results.extend(res)
                    hits += 1
                else:
                    misses += 1
                
                if (i+1) % 20 == 0:
                    print(f"Progress: [{i+1}/{len(brand_names)}] | Hits: {hits} | Misses: {misses}")
                
                # Auto-save
                if (i+1) % checkpoint_size == 0:
                    pd.DataFrame(all_results).to_csv(OUTPUT_CSV, index=False)
            except Exception:
                pass

    if all_results:
        pd.DataFrame(all_results).to_csv(OUTPUT_CSV, index=False)
        print(f"\nFINISH! Saved {len(all_results)} UK mappings to {OUTPUT_CSV}")

if __name__ == "__main__":
    run_large_mapper()
