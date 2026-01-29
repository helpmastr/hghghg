import requests
import json

BASE_URL = "http://0.0.0.0:8080/consult"

scenarios = [
    {
        "name": "1. International Brand Link (Panadol)",
        "payload": {
            "symptoms": "Headache",
            "history": "None",
            "medications": "Panadol", # Should map to Paracetamol
            "temperature": "37",
            "age_weight": "Adult"
        }
    },
    {
        "name": "2. Arabic Symptom Map (Flu)",
        "payload": {
            "symptoms": "زكام / إنفلونزا", # Should map to Cold/Flu
            "history": "لا يوجد",
            "medications": "لا يوجد",
            "temperature": "38.5",
            "age_weight": "Adult"
        }
    },
    {
        "name": "3. Pediatric Dosage (Fever)",
        "payload": {
            "symptoms": "حرارة مرتفعة / حمى",
            "history": "None",
            "medications": "None",
            "temperature": "39",
            "age_weight": "Child (20kg)" # Should trigger Pediatric context
        }
    },
    {
        "name": "4. Renal Warnings (Metformin)",
        "payload": {
            "symptoms": "سكري",
            "history": "Kidney Failure", # Key for Renal logic
            "medications": "Metformin",
            "temperature": "37",
            "age_weight": "Adult"
        }
    },
    {
        "name": "5. Edge Case (Gibberish)",
        "payload": {
            "symptoms": "shjkdhfkjsd",
            "history": "None",
            "medications": "None",
            "temperature": "37",
            "age_weight": "Adult"
        }
    }
]

def run_tests():
    print(f"Testing NRG Pipeline at {BASE_URL}...\n")
    
    for i, scen in enumerate(scenarios):
        print(f"--- Scenario {scen['name']} ---")
        try:
            # We must map the dict keys to the Pydantic model
            # Pydantic Query: symptoms, temperature, history, medications, age_weight
            
            resp = requests.post(BASE_URL, json=scen['payload'], timeout=30)
            
            if resp.status_code == 200:
                data = resp.json()
                msg = data.get("message", "")
                print(f"✅ Response ({len(msg)} chars):")
                print(msg[:300].replace("\n", " ") + "...")
                
                # Validation Heuristics
                if "Panadol" in scen['name'] and "Paracetamol" in msg:
                    print("   [PASS] NER linked Panadol -> Paracetamol")
                    
            else:
                print(f"❌ Error {resp.status_code}: {resp.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("\n")

if __name__ == "__main__":
    run_tests()
