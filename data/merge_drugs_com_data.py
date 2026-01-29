import pandas as pd
import os

MASTER_FILE = "backend/data/master_drugs_data.csv"
DOSAGE_FILE = "cleaned_drugs_com_dosage.csv"

def merge_data():
    if not os.path.exists(MASTER_FILE):
        print("Master file not found.")
        return
    if not os.path.exists(DOSAGE_FILE):
        print("Dosage file not found.")
        return

    print("Loading datasets...")
    master_df = pd.read_csv(MASTER_FILE)
    dosage_df = pd.read_csv(DOSAGE_FILE)
    
    print(f"Master: {len(master_df)} records")
    print(f"Dosage: {len(dosage_df)} records")
    
    # Check if column exists, if so drop it to overwrite
    if 'International Dosage' in master_df.columns:
        master_df = master_df.drop(columns=['International Dosage'])
        
    # We merge on 'Scientific Name'. The scraper used the names relative to the master file.
    # However, duplications might exist in master file.
    
    # Create a mapping dict for faster lookups
    # dosage_df has 'Scientific Name' and 'Dosage Context'
    dosage_map = dict(zip(dosage_df['Scientific Name'], dosage_df['Dosage Context']))
    
    print("Merging...")
    master_df['International Dosage'] = master_df['Scientific Name'].map(dosage_map)
    
    # Fill NaN with empty string
    master_df['International Dosage'] = master_df['International Dosage'].fillna("")
    
    merged_count = master_df[master_df['International Dosage'] != ""].shape[0]
    print(f"Enriched {merged_count} rows with International Dosage data.")
    
    print("Saving...")
    master_df.to_csv(MASTER_FILE, index=False)
    print("Done.")

if __name__ == "__main__":
    merge_data()
