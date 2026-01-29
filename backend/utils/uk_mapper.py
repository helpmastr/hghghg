import pandas as pd
import os

class UKMapper:
    def __init__(self, csv_path="data/uk_brand_mapping.csv"):
        self.mapping = {}
        self.load_data(csv_path)

    def load_data(self, csv_path):
        # Path resolution strategies
        paths_to_try = [
            csv_path, # Default
            f"backend/{csv_path}", # From root
            "uk_brand_mapping.csv", # Root fallback
            "../uk_brand_mapping.csv" # Dev fallback
        ]
        
        final_path = None
        for p in paths_to_try:
            if os.path.exists(p):
                final_path = p
                break
        
        if not final_path:
            print("Warning: uk_brand_mapping.csv not found.")
            return

        try:
            df = pd.read_csv(final_path)
            for _, row in df.iterrows():
                # Map Search Term (e.g., PANADOL) -> Ingredients
                term = str(row['Search Term']).strip().upper()
                ing = str(row['Active Ingredients']).strip()
                self.mapping[term] = ing
                
                # Map full UK Brand Name (e.g., Panadol Extra) -> Ingredients
                brand = str(row['UK Brand Name']).strip().upper()
                self.mapping[brand] = ing
                
                # Map First Word of Brand (e.g., "PANADOL" from "Panadol Extra")
                first_word = brand.split()[0]
                if len(first_word) > 2: # Avoid tiny words
                    self.mapping[first_word] = ing
        except Exception as e:
            print(f"Error loading UK Map: {e}")

    def resolve(self, query):
        """
        Returns active ingredients string if match found, else None.
        Query should be the brand name (e.g. 'Panadol').
        """
        if not query: return None
        q = query.strip().upper()
        
        # Direct Match
        if q in self.mapping:
            return self.mapping[q]
        
        # Fuzzy / First word check?
        # If user queries "Panadol Extra", and we have "PANADOL" key.
        # But we also key'd the Full UK Brand Name, so "PANADOL EXTRA" should match.
        
        return None
