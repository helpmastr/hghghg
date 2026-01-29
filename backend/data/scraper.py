import asyncio
import aiohttp
import json
import os
import time

# Configuration
BASE_URL = "https://www.sfda.gov.sa"
DRUGS_ENDPOINT = f"{BASE_URL}/GetDrugs.php"
AGENTS_ENDPOINT = f"{BASE_URL}/GetDrugAgents.php"
CONCURRENCY_LIMIT = 50  # Increased for speed
RETRY_LIMIT = 3
TIMEOUT = aiohttp.ClientTimeout(total=30)

async def fetch_json(session, url, params=None, retry=0):
    try:
        async with session.get(url, params=params, timeout=TIMEOUT) as response:
            if response.status == 200:
                try:
                    return await response.json()
                except Exception as e:
                    text = await response.text()
                    # Sometimes the API returns invalid JSON or HTML on error
                    print(f"Error parsing JSON from {url}: {e}")
                    return None
            elif response.status == 429: # Rate limited
                wait = (2 ** retry) + 1
                await asyncio.sleep(wait)
                return await fetch_json(session, url, params, retry + 1)
            else:
                print(f"Error fetching {url}: Status {response.status}")
                return None
    except Exception as e:
        if retry < RETRY_LIMIT:
            wait = (2 ** retry) + 1
            await asyncio.sleep(wait)
            return await fetch_json(session, url, params, retry + 1)
        print(f"Failed to fetch {url} after {RETRY_LIMIT} retries: {e}")
        return None

async def fetch_page(session, page_num, semaphore):
    async with semaphore:
        print(f"Fetching page {page_num}...")
        data = await fetch_json(session, DRUGS_ENDPOINT, {"page": page_num})
        if data and "results" in data:
            return data["results"]
        return []

async def fetch_agents(session, register_number, semaphore):
    async with semaphore:
        if not register_number:
            return []
        data = await fetch_json(session, AGENTS_ENDPOINT, {"search": register_number})
        if data and "results" in data:
            return data["results"]
        return []

async def main():
    start_time = time.time()
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    async with aiohttp.ClientSession() as session:
        # 1. Get total page count
        print("Getting initial page count...")
        initial_data = await fetch_json(session, DRUGS_ENDPOINT, {"page": 1})
        if not initial_data or "pageCount" not in initial_data:
            print("Failed to get page count. Exiting.")
            return
        
        total_pages = initial_data["pageCount"]
        print(f"Total pages to fetch: {total_pages}")
        
        # 2. Fetch all pages
        tasks = []
        for i in range(1, total_pages + 1):
            tasks.append(fetch_page(session, i, semaphore))
        
        pages_results = await asyncio.gather(*tasks)
        
        all_drugs = []
        for result in pages_results:
            if result:
                all_drugs.extend(result)
        
        print(f"Fetched {len(all_drugs)} drugs. Now fetching agent details...")
        
        # 3. Fetch agent details for each drug (concurrency)
        agent_tasks = []
        # Mapping to avoid duplicate calls for same register number
        reg_to_agents = {}
        unique_reg_numbers = list(set(d.get("registerNumber") for d in all_drugs if d.get("registerNumber")))
        
        for reg_num in unique_reg_numbers:
            agent_tasks.append(fetch_agents(session, reg_num, semaphore))
        
        agents_results = await asyncio.gather(*agent_tasks)
        
        for reg_num, agents in zip(unique_reg_numbers, agents_results):
            reg_to_agents[reg_num] = agents
            
        # 4. Combine data
        for drug in all_drugs:
            reg_num = drug.get("registerNumber")
            drug["agents"] = reg_to_agents.get(reg_num, [])
            
        # 5. Save to file
        output_file = "raw_drugs_data.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(all_drugs, f, ensure_ascii=False, indent=2)
            
    end_time = time.time()
    duration = end_time - start_time
    print(f"Done! Scraped {len(all_drugs)} drugs in {duration:.2f} seconds.")
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    asyncio.run(main())
