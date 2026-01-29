import pandas as pd
import os

def merge_brand_enrichment():
    master_path = "backend/data/master_drugs_data.csv"
    brand_path = "brand_dosage_details.csv"
    output_path = "backend/data/master_drugs_data.csv" # Overwrite with final version

    if not os.path.exists(master_path) or not os.path.exists(brand_path):
        print("Error: Required CSV files not found.")
        return

    print("Loading datasets...")
    master_df = pd.read_csv(master_path)
    brand_df = pd.read_csv(brand_path)

    # brand_df has 'Search Brand Name' and 'Patient Leaflet (AR)'
    # and also 'طريقة الإستعمال' which we can use for Administration Route (AR)
    
    print("Preparing brand leaflet mapping...")
    # Drop empty leaflets
    leaflets = brand_df.dropna(subset=['Patient Leaflet (AR)'])
    # Deduplicate by Search Brand Name to avoid mapping conflicts
    brand_map = leaflets.drop_duplicates(subset=['Search Brand Name'], keep='first').set_index('Search Brand Name')['Patient Leaflet (AR)'].to_dict()
    admin_map = leaflets.drop_duplicates(subset=['Search Brand Name'], keep='first').set_index('Search Brand Name')['طريقة الإستعمال'].to_dict()

    print(f"Applying brand-specific leaflets to master list...")
    
    # We only fill in gaps (where Patient Leaflet (AR) is still NaN)
    # This preserves the scientific-name mapping if it was already there
    
    count_before = master_df['Patient Leaflet (AR)'].notna().sum()
    
    # Use fillna with mapping
    master_df['Patient Leaflet (AR)'] = master_df['Patient Leaflet (AR)'].fillna(master_df['Trade Name'].map(brand_map))
    master_df['Administration Route (AR)'] = master_df['Administration Route (AR)'].fillna(master_df['Trade Name'].map(admin_map))

    count_after = master_df['Patient Leaflet (AR)'].notna().sum()
    new_hits = count_after - count_before

    # Save the finalized master dataset
    master_df.to_csv(output_path, index=False)
    print(f"Final Master Dataset updated at {output_path}.")
    print(f"Brand Enrichment Results: {new_hits} new leaflets added.")
    print(f"Total Coverage: {count_after} out of {len(master_df)} rows ({ (count_after/len(master_df))*100 :.2f}%)")

if __name__ == "__main__":
    merge_brand_enrichment()
