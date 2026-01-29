import pandas as pd
import os

def merge_datasets():
    old_path = "backend/data/cleaned_drugs_data.csv"
    new_path = "backend/data/enriched_dosage_data.csv"
    output_path = "backend/data/master_drugs_data.csv"

    if not os.path.exists(old_path) or not os.path.exists(new_path):
        print("Error: Required CSV files not found.")
        return

    print("Loading datasets...")
    old_df = pd.read_csv(old_path)
    new_df = pd.read_csv(new_path)

    # The 'new_df' has 'Search Scientific Name' which matches 'Scientific Name' in 'old_df'
    # and 'Patient Leaflet (AR)' which is what we want to add.
    
    # We'll create a mapping of Scientific Name -> Leaflet
    # To avoid duplicates if one scientific name has multiple leaflets, we'll take the first non-empty one
    # OR we can keep the most complete one.
    print("Preparing leaflet mapping...")
    leaflets = new_df.dropna(subset=['Patient Leaflet (AR)'])
    # Deduplicate by Search Scientific Name to get a clean 1-to-1 mapping for the master list
    leaflets_unique = leaflets.drop_duplicates(subset=['Search Scientific Name'], keep='first')
    
    leaflet_map = leaflets_unique.set_index('Search Scientific Name')['Patient Leaflet (AR)'].to_dict()
    practitioner_map = leaflets_unique.set_index('Search Scientific Name')['Practitioner Leaflet'].to_dict()

    print(f"Applying leaflets to {len(old_df)} rows...")
    # Add the new columns to the master list
    old_df['Patient Leaflet (AR)'] = old_df['Scientific Name'].map(leaflet_map)
    old_df['Practitioner Leaflet'] = old_df['Scientific Name'].map(practitioner_map)

    # 1. Fill missing leaflets with a placeholder if needed, or leave NaN
    # 2. Add other columns from new_df if they are valuable (e.g. 'طريقة الإستعمال' as 'Arabic Administration Route')
    admin_route_map = leaflets_unique.set_index('Search Scientific Name')['طريقة الإستعمال'].to_dict()
    old_df['Administration Route (AR)'] = old_df['Scientific Name'].map(admin_route_map)

    # Save the master dataset
    old_df.to_csv(output_path, index=False)
    print(f"Master Dataset created at {output_path} with {len(old_df)} rows.")
    
    # Verification
    enriched_count = old_df['Patient Leaflet (AR)'].notna().sum()
    print(f"Enrichment Complete: {enriched_count} rows now have detailed clinical leaflets.")

if __name__ == "__main__":
    merge_datasets()
