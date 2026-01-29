import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

def test_sdi_search(query):
    url = f"https://sdi.sfda.gov.sa/Home/DrugSearch?textFilter={query.replace(' ', '+')}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    print(f"Searching: {url}")
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Find the results table or rows
        # Based on read_url_content, it might be links with 'مشاهدة'
        links = soup.find_all('a', string=lambda t: t and 'مشاهدة' in t)
        print(f"Found {len(links)} results.")
        for link in links[:3]:
            href = link.get('href')
            if href:
                full_url = f"https://sdi.sfda.gov.sa{href}"
                print(f"Result detail link: {full_url}")
                fetch_drug_details(full_url)
    else:
        print(f"Search failed: {response.status_code}")

def fetch_drug_details(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Extract fields from the 'بيانات الدواء' (Drug Data) section
        drug_data = {}
        labels = soup.find_all('label', class_='form-label')
        for label in labels:
            key = label.get_text(strip=True)
            value_div = label.find_next('div', class_='form-line')
            if value_div:
                value = value_div.get_text(strip=True)
                drug_data[key] = value
        print(f"Extracted data: {drug_data}")
    else:
        print(f"Failed to fetch details: {response.status_code}")

if __name__ == "__main__":
    test_sdi_search("DOPAMINE HYDROCHLORIDE")
