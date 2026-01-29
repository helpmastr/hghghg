import sys
import os

sys.path.append(os.getcwd())
from backend.utils.ner import ClinicalNER

def test_ner():
    print("Initializing ClinicalNER...")
    ner = ClinicalNER()
    
    # Mock Query Object
    class MockQuery:
        symptoms = "صداع / آلام الرأس, حرارة مرتفعة / حمى" # Exact keys
        history = "Panadol"      # Should trigger NEL -> Paracetamol
        medications = "Omnipaque" # Should trigger NEL -> Iohexol
        temperature = ""
        age_weight = ""

    print("\nTesting Extraction...")
    q = MockQuery()
    result = ner.extract_entities(q)
    
    print("\n[Results]")
    print(f"Search Terms (RAG Keys): {result['search_terms']}")
    print(f"Entities: {result['entities']}")
    print(f"International Links (NEL): {result['international_links']}")
    
    # Assertions
    terms = [t.lower() for t in result['search_terms']]
    
    if "paracetamol" in terms: print("✅ Paracetamol linked")
    else: print("❌ Paracetamol missing")
        
    if "iohexol" in terms: print("✅ Iohexol linked")
    else: print("❌ Iohexol missing")
        
    if "headache" in terms: print("✅ Headache mapped")
    else: print("❌ Headache missing")

if __name__ == "__main__":
    test_ner()
