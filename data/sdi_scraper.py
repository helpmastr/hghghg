import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import concurrent.futures

# Configuration
INPUT_CSV = "backend/data/cleaned_drugs_data.csv"
OUTPUT_EXCEL = "sdi_dosage_details.xlsx"
MAX_WORKERS = 25  # Increased for speed
DELAY = 0.1       # Reduced delay

class SDIScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = "https://sdi.sfda.gov.sa"

    def get_drug_details(self, scientific_name):
        search_url = f"{self.base_url}/Home/DrugSearch?textFilter={scientific_name.replace(' ', '+')}"
        try:
            response = self.session.get(search_url, timeout=15)
            if response.status_code != 200:
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            result_links = soup.find_all('a', string=lambda t: t and 'مشاهدة' in t)
            
            drugs_info = []
            # We follow the first 3 links to avoid excessive time for very common results
            for link in result_links[:3]:
                detail_href = link.get('href')
                if not detail_href: continue
                
                detail_url = f"{self.base_url}{detail_href}"
                detail_data = self.scrape_detail_page(detail_url)
                if detail_data:
                    detail_data['Search Scientific Name'] = scientific_name
                    drugs_info.append(detail_data)
                time.sleep(DELAY)
                
            return drugs_info
        except Exception as e:
            print(f"Error searching {scientific_name}: {e}")
            return []

    def scrape_detail_page(self, url):
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            drug_info = {'Detail URL': url}
            
            # 1. Extract Drug Data Tab (D-div)
            drug_data_section = soup.find('div', id='D-div')
            if drug_data_section:
                labels = drug_data_section.find_all('label', class_='form-label')
                for label in labels:
                    key = label.get_text(strip=True)
                    value_div = label.find_next('div', class_='form-line')
                    if value_div:
                        drug_info[key] = value_div.get_text(strip=True)

            # 2. Extract Patient Leaflet Content (A-div / M-div)
            # These usually contain the dosage info in rich text (p tags)
            for div_id, label_prefix in [('A-div', 'Patient Leaflet (AR)'), ('M-div', 'Practitioner Leaflet')]:
                section = soup.find('div', id=div_id)
                if section:
                    content = section.get_text(separator="\n", strip=True)
                    if "لم يتم إدخال بيانات" not in content:
                        drug_info[label_prefix] = content

            return drug_info
        except Exception as e:
            print(f"Error scraping detail {url}: {e}")
            return None

def run_scraper():
    if not os.path.exists(INPUT_CSV):
        print(f"Error: {INPUT_CSV} not found.")
        return

    print(f"Loading data from {INPUT_CSV}...")
    df = pd.read_csv(INPUT_CSV)
    
    # We scrape unique scientific names to be efficient
    scientific_names = df['Scientific Name'].dropna().unique().tolist()
    print(f"Found {len(scientific_names)} unique scientific names.")
    
    # Process the full list of scientific names
    to_scrape = scientific_names
    print(f"Starting full scrape for {len(to_scrape)} items...")

    scraper = SDIScraper()
    
    # Check for existing results to avoid duplicate work if possible
    all_results = []
    if os.path.exists(OUTPUT_EXCEL):
        try:
            existing_df = pd.read_excel(OUTPUT_EXCEL)
            if not existing_df.empty:
                processed_names = set(existing_df['Search Scientific Name'].unique())
                to_scrape = [name for name in to_scrape if name not in processed_names]
                all_results = existing_df.to_dict('records')
                print(f"Resuming: {len(processed_names)} items already done. {len(to_scrape)} remaining.")
        except Exception as e:
            print(f"Could not load existing results: {e}")

    if not to_scrape:
        print("All items completed.")
        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_name = {executor.submit(scraper.get_drug_details, name): name for name in to_scrape}
        for i, future in enumerate(concurrent.futures.as_completed(future_to_name)):
            name = future_to_name[future]
            try:
                results = future.result()
                all_results.extend(results)
                print(f"[{i+1}/{len(to_scrape)}] Finished: {name} (Found {len(results)} variants)")
            except Exception as exc:
                print(f"{name} generated an exception: {exc}")

    if all_results:
        output_df = pd.DataFrame(all_results)
        output_df.to_excel(OUTPUT_EXCEL, index=False)
        print(f"Successfully saved {len(all_results)} entries to {OUTPUT_EXCEL}")
    else:
        print("No results found.")

if __name__ == "__main__":
    run_scraper()
