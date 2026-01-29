import json
import csv
import os

def clean_string(s):
    if s is None:
        return ""
    # Remove newlines, carriage returns and extra spaces
    return " ".join(str(s).split()).strip()

def process_data():
    input_file = "raw_drugs_data.json"
    output_file = "cleaned_drugs_data.csv"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    headers = [
        "Trade Name", "Scientific Name", "Registration Number", "Registration Year",
        "Strength", "Dosage Form", "Administration Route", "Price (SAR)",
        "Manufacturer", "Manufacturer Country", "Selling Company", "Company Country",
        "Marketing Status", "Legal Status", "Storage Conditions", "Distribution Area", "Agents"
    ]

    cleaned_data = []

    for item in data:
        # Combine Strength and Unit
        strength = clean_string(item.get("strength"))
        unit = clean_string(item.get("strengthUnit"))
        full_strength = f"{strength} {unit}".strip()
        
        # Remove trailing commas from strength if present
        if full_strength.endswith(","):
            full_strength = full_strength.rstrip(",").strip()

        # Handle Agents - Clean and Unique
        agents_list = item.get("agents", [])
        agents_names = [clean_string(a.get("nameEn")) for a in agents_list if a.get("nameEn")]
        # Unique, sorted, and joined
        agents_str = ", ".join(sorted(list(set(agents_names))))

        # Semantic cleanup for names
        def semantic_clean(name):
            if not name: return ""
            # Fix spacing around commas: "Ing 1 , Ing 2" -> "Ing 1, Ing 2"
            name = ", ".join([part.strip() for part in str(name).split(",")])
            return name.strip()

        trade_name = semantic_clean(item.get("tradeName"))
        scientific_name = semantic_clean(item.get("scientificName"))
        
        # Normalize Price
        price = clean_string(item.get("price"))
        
        # Legal Status - preferring legalStatusEn if available
        legal_status = clean_string(item.get("legalStatusEn")) or clean_string(item.get("legalStatus"))

        row = {
            "Trade Name": trade_name,
            "Scientific Name": scientific_name,
            "Registration Number": clean_string(item.get("registerNumber")),
            "Registration Year": clean_string(item.get("registerYear")),
            "Strength": full_strength,
            "Dosage Form": clean_string(item.get("doesageForm")),
            "Administration Route": clean_string(item.get("administrationRoute")),
            "Price (SAR)": price,
            "Manufacturer": clean_string(item.get("manufacturerName")),
            "Manufacturer Country": clean_string(item.get("manufacturerCountry")),
            "Selling Company": clean_string(item.get("companyName")),
            "Company Country": clean_string(item.get("companyCountryEn")),
            "Marketing Status": clean_string(item.get("marketingStatus")),
            "Legal Status": legal_status,
            "Storage Conditions": clean_string(item.get("storageConditions")),
            "Distribution Area": clean_string(item.get("distributionArea")),
            "Agents": agents_str
        }
        cleaned_data.append(row)

    with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(cleaned_data)

    print(f"Successfully cleaned and converted {len(cleaned_data)} records to {output_file}")

if __name__ == "__main__":
    process_data()
