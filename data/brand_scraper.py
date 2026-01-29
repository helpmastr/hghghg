import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import concurrent.futures

# Configuration - Ultra High Speed
INPUT_CSV = "backend/data/master_drugs_data.csv"
OUTPUT_CSV = "brand_dosage_details.csv"
MAX_WORKERS = 50  # Turbo speed
DELAY = 0.05      # Minimal delay

class BrandScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = "https://sdi.sfda.gov.sa"

    def get_brand_details(self, brand_name):
        search_url = f"{self.base_url}/Home/DrugSearch?textFilter={brand_name.replace(' ', '+')}"
        try:
            response = self.session.get(search_url, timeout=10)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            # Look for Exact match links if possible, but for now we follow the first 2 results
            result_links = soup.find_all('a', string=lambda t: t and 'مشاهدة' in t)
            
            brand_results = []
            for link in result_links[:2]: # Faster: only follow top 2 brand matches
                detail_href = link.get('href')
                if not detail_href: continue
                
                detail_url = f"{self.base_url}{detail_href}"
                detail_data = self.scrape_detail_page(detail_url)
                if detail_data:
                    detail_data['Search Brand Name'] = brand_name
                    brand_results.append(detail_data)
                time.sleep(DELAY)
                
            return brand_results
        except Exception as e:
            return []

    def scrape_detail_page(self, url):
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            drug_info = {'Detail URL': url}
            
            # Extract Drug Data (D-div)
            drug_data_section = soup.find('div', id='D-div')
            if drug_data_section:
                labels = drug_data_section.find_all('label', class_='form-label')
                for label in labels:
                    key = label.get_text(strip=True)
                    value_div = label.find_next('div', class_='form-line')
                    if value_div:
                        drug_info[key] = value_div.get_text(strip=True)

            # Extract Patient Leaflet (Arabic only for RAG performance)
            section = soup.find('div', id='A-div')
            if section:
                content = section.get_text(separator="\n", strip=True)
                if "لم يتم إدخال بيانات" not in content and len(content) > 10:
                    drug_info['Patient Leaflet (AR)'] = content

            return drug_info
        except Exception as e:
            return None

def run_brand_scraper():
    if not os.path.exists(INPUT_CSV):
        print(f"Error: {INPUT_CSV} not found.")
        return

    print(f"Loading Master Data...")
    df = pd.read_csv(INPUT_CSV)
    brand_names = df['Trade Name'].dropna().unique().tolist()
    print(f"Found {len(brand_names)} unique brands.")
    
    # Logic to Resume if needed
    all_results = []
    if os.path.exists(OUTPUT_CSV):
        try:
            existing_df = pd.read_csv(OUTPUT_CSV)
            processed = set(existing_df['Search Brand Name'].unique())
            brand_names = [b for b in brand_names if b not in processed]
            all_results = existing_df.to_dict('records')
            print(f"Resuming: {len(processed)} brands already done. {len(brand_names)} left.")
        except:
            pass

    if not brand_names:
        print("All brands completed.")
        return

    scraper = BrandScraper()
    
    print(f"Starting Ultra-Fast Scrape (50 threads) for {len(brand_names)} items...")

    checkpoint_size = 50
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_brand = {executor.submit(scraper.get_brand_details, name): name for name in brand_names}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_brand)):
            try:
                results = future.result()
                all_results.extend(results)
                if (i+1) % 10 == 0:
                    print(f"Progress: [{i+1}/{len(brand_names)}]")
                
                # Auto-save every 50 brands
                if (i+1) % checkpoint_size == 0:
                    pd.DataFrame(all_results).to_csv(OUTPUT_CSV, index=False)
            except Exception as exc:
                pass

    if all_results:
        final_df = pd.DataFrame(all_results)
        final_df.to_csv(OUTPUT_CSV, index=False)
        print(f"DONE! Saved {len(all_results)} entries to {OUTPUT_CSV}")

if __name__ == "__main__":
    run_brand_scraper()
