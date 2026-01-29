import json
import collections

def validate_data():
    input_file = "raw_drugs_data.json"
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    total_count = len(data)
    print(f"Total records: {total_count}")
    
    # 1. Check for duplicate IDs
    ids = [item.get("id") for item in data]
    id_counts = collections.Counter(ids)
    duplicate_ids = {id: count for id, count in id_counts.items() if count > 1}
    
    if duplicate_ids:
        print(f"Found {len(duplicate_ids)} duplicate IDs: {duplicate_ids}")
    else:
        print("No duplicate IDs found.")
        
    # 2. Check for duplicate Register Numbers
    reg_nums = [item.get("registerNumber") for item in data if item.get("registerNumber")]
    reg_counts = collections.Counter(reg_nums)
    duplicate_regs = {reg: count for reg, count in reg_counts.items() if count > 1}
    
    if duplicate_regs:
        print(f"Found {len(duplicate_regs)} duplicate Registration Numbers.")
        # Print a few examples
        examples = list(duplicate_regs.items())[:5]
        print(f"Examples: {examples}")
    else:
        print("No duplicate Registration Numbers found.")
        
    # 3. Check for structural consistency
    fields_count = collections.defaultdict(int)
    for item in data:
        for key in item.keys():
            fields_count[key] += 1
            
    print("\nField presence across records:")
    for field, count in fields_count.items():
        if count < total_count:
            print(f"  Field '{field}' missing in {total_count - count} records")

    # 4. Check for potential data errors (empty critical fields)
    critical_fields = ["tradeName", "scientificName", "registerNumber"]
    for field in critical_fields:
        empty_count = sum(1 for item in data if not item.get(field))
        if empty_count > 0:
            print(f"  Field '{field}' is empty/null in {empty_count} records")

if __name__ == "__main__":
    validate_data()
