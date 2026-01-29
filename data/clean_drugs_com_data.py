import pandas as pd
import re
import os

INPUT_FILE = "drugs_com_dosage.csv"
OUTPUT_FILE = "cleaned_drugs_com_dosage.csv"

def clean_text(text):
    if pd.isna(text) or text == "" or str(text).lower() == "nan":
        return ""
    
    text = str(text)
    
    # Remove "Additional dosage information" block and everything after (navigation links)
    if "Additional dosage information" in text:
        text = text.split("Additional dosage information")[0]
        
    # Remove leading "for:" (common artifact)
    text = re.sub(r'^for:\s*', '', text, flags=re.IGNORECASE)
    
    # Replace multiple newlines with a single newline or space
    # We want to keep some structure but remove huge gaps
    text = re.sub(r'\n\s*\n+', ' | ', text) # Replace paragraph breaks with pipe for density
    text = re.sub(r'\n', ' ', text) # Replace single newlines with space
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def clean_data():
    if not os.path.exists(INPUT_FILE):
        print(f"File {INPUT_FILE} not found.")
        return

    print(f"Loading {INPUT_FILE}...")
    df = pd.read_csv(INPUT_FILE)
    
    print("Cleaning columns...")
    cols_to_clean = ['Adult Dosage', 'Pediatric Dosage', 'Renal Dose', 'Liver Dose']
    
    for col in cols_to_clean:
        if col in df.columns:
            df[col] = df[col].apply(clean_text)
            
    # Drop rows where ALL dosage info is empty
    mask = (df['Adult Dosage'] == "") & (df['Pediatric Dosage'] == "") & \
           (df['Renal Dose'] == "") & (df['Liver Dose'] == "")
    
    initial_count = len(df)
    df = df[~mask]
    final_count = len(df)
    
    print(f"Removed {initial_count - final_count} empty records.")
    
    # create a "Full Dosage Context" column for RAG
    # This combines all avail info into one readable string
    def combine_context(row):
        parts = []
        if row['Adult Dosage']: parts.append(f"[Adult] {row['Adult Dosage']}")
        if row['Pediatric Dosage']: parts.append(f"[Pediatric] {row['Pediatric Dosage']}")
        if row['Renal Dose']: parts.append(f"[Renal] {row['Renal Dose']}")
        if row['Liver Dose']: parts.append(f"[Liver] {row['Liver Dose']}")
        return " // ".join(parts)
        
    df['Dosage Context'] = df.apply(combine_context, axis=1)
    
    # Save
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved cleaned data to {OUTPUT_FILE} ({len(df)} records).")
    
    # Show sample
    print("\n[Sample Record]")
    print(df.iloc[0]['Dosage Context'][:500])

if __name__ == "__main__":
    clean_data()
