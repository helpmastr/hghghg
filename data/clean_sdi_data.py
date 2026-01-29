import pandas as pd
import re
import os

def clean_sdi_data(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    print(f"Loading data from {input_file}...")
    # Load with openpyxl engine
    df = pd.read_excel(input_file)

    # 1. Basic Cleaning
    # Drop rows with no patient leaflet and no drug data
    initial_len = len(df)
    df = df.dropna(subset=['Patient Leaflet (AR)', 'الاسم التجاري', 'الاسم العلمي'], how='all')
    print(f"Dropped {initial_len - len(df)} empty rows.")

    # 2. Text Normalization
    def clean_text(text):
        if not isinstance(text, str):
            return text
        # Remove Excel artifacts like _x000D_
        text = text.replace('_x000D_', ' ')
        # Remove literal \r and normalize special characters
        text = text.replace('\r', ' ')
        # Remove excessive newlines and whitespace
        text = re.sub(r'\n\s*\n', '\n', text)
        text = re.sub(r' {2,}', ' ', text)
        return text.strip()

    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(clean_text)

    # 3. Handle duplicates
    # A scientific name might have multiple trade names/variants
    # We keep them for now but we could group them if needed.
    
    # 4. Filter out placeholder text
    placeholders = ["لم يتم إدخال بيانات", "No data", "No specific match found"]
    for col in ['Patient Leaflet (AR)', 'Practitioner Leaflet']:
        if col in df.columns:
            df = df[~df[col].astype(str).str.contains('|'.join(placeholders), na=False)]

    # 5. Save the cleaned data
    df.to_excel(output_file, index=False)
    print(f"Cleaned data saved to {output_file}. Final row count: {len(df)}")

if __name__ == "__main__":
    clean_sdi_data("sdi_dosage_details.xlsx", "cleaned_sdi_dosage_details.xlsx")
