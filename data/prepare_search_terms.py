import pandas as pd
import os
import re

# Goal: Extract the primary brand name (first word) for better UK EMC matching
INPUT_CSV = "backend/data/master_drugs_data.csv"
OUTPUT_CSV = "uk_search_terms.csv"

def simplify_name(name):
    if not isinstance(name, str): return ""
    # Take the first word
    first_word = name.split()[0]
    # Remove non-alphanumeric characters but keep spaces if we want more words (sticking to first word for now)
    first_word = re.sub(r'[^a-zA-Z]', '', first_word)
    return first_word.upper()

def prepare_terms():
    if not os.path.exists(INPUT_CSV):
        print(f"Error: {INPUT_CSV} not found.")
        return

    print("Loading Master Data...")
    df = pd.read_csv(INPUT_CSV)
    
    # Extract unique trade names
    trade_names = df['Trade Name'].dropna().unique()
    
    simplified_data = []
    seen = set()
    
    for original in trade_names:
        simple = simplify_name(original)
        if simple and len(simple) > 2 and simple not in seen:
            simplified_data.append({
                'Original Name': original,
                'Search Term': simple
            })
            seen.add(simple)

    out_df = pd.DataFrame(simplified_data)
    out_df.to_csv(OUTPUT_CSV, index=False)
    print(f"DONE! Saved {len(simplified_data)} unique search terms to {OUTPUT_CSV}")

if __name__ == "__main__":
    prepare_terms()
